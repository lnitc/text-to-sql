/**
 * Error handling and parsing utilities
 * Converts technical errors into user-friendly messages
 */

export interface ParsedError {
  title: string;
  message: string;
  details?: string;
  suggestions?: string[];
  type: 'sql' | 'auth' | 'network' | 'model' | 'unknown';
}

/**
 * Parse backend error messages and extract useful information
 */
export function parseErrorMessage(error: string): ParsedError {
  // Model/LLM errors
  if (error.includes('model') && error.includes('not found')) {
    return parseModelError(error);
  }

  if (error.includes('OpenAI') && error.includes('authentication')) {
    return {
      title: 'OpenAI Authentication Error',
      message: 'Unable to authenticate with OpenAI API.',
      details: 'Please verify that OPENAI_API_KEY is set correctly in your backend configuration.',
      suggestions: [
        'Check that OPENAI_API_KEY environment variable is set',
        'Verify your OpenAI API key is valid and has appropriate permissions',
        'Restart the backend server after updating credentials',
        'Check OpenAI status at https://status.openai.com',
      ],
      type: 'auth',
    };
  }

  if (error.includes('rate limit') || error.includes('rate_limit_exceeded')) {
    return {
      title: 'OpenAI Rate Limit',
      message: 'Too many requests to OpenAI API. Please wait and try again.',
      suggestions: [
        'Wait a minute before trying again',
        'Try with a simpler query',
        'Check your OpenAI account usage at https://platform.openai.com/account/billing/usage',
      ],
      type: 'unknown',
    };
  }

  // SQL errors
  if (error.includes('SQL Error') || error.includes('invalidQuery')) {
    return parseSqlError(error);
  }

  // Authentication errors
  if (error.includes('RefreshError') || error.includes('reauthentication')) {
    return {
      title: 'Authentication Error',
      message: 'Unable to connect to Google Cloud. Credentials may have expired.',
      details: error.includes('Reauthentication')
        ? 'Run: gcloud auth application-default login'
        : undefined,
      suggestions: [
        'Refresh your Google Cloud credentials',
        'Run: gcloud auth application-default login',
        'Restart the backend server',
      ],
      type: 'auth',
    };
  }

  // Network errors
  if (error.includes('timeout') || error.includes('connection')) {
    return {
      title: 'Connection Error',
      message: 'Backend server is not responding. Please check if it\'s running.',
      suggestions: [
        'Verify backend is running on http://localhost:8000',
        'Check for connection errors in the backend terminal',
        'Try refreshing the page',
      ],
      type: 'network',
    };
  }

  // Default unknown error
  return {
    title: 'Query Error',
    message: 'An unexpected error occurred while processing your query.',
    details: error.length > 200 ? error.substring(0, 200) + '...' : error,
    suggestions: [
      'Check the browser console (F12) for more details',
      'Try a simpler query',
      'Check the backend logs for errors',
    ],
    type: 'unknown',
  };
}

/**
 * Parse model-related errors
 */
function parseModelError(error: string): ParsedError {
  // Extract model name if possible
  const modelMatch = error.match(/model['\s:]+([^\s']+)/i);
  const modelName = modelMatch ? modelMatch[1] : 'OpenAI model';

  return {
    title: 'Model Unavailable',
    message: `The configured AI model "${modelName}" is not available. This model may have been deprecated or your API key doesn't have access to it.`,
    details:
      'Contact your system administrator to update the OPENAI_MODEL configuration to a valid model like "gpt-4o-mini" or "gpt-4o".',
    suggestions: [
      'Ask your system administrator to update the OpenAI model configuration',
      'Valid models: gpt-4o-mini (recommended), gpt-4o, gpt-4-turbo',
      'Check OpenAI API documentation for available models: https://platform.openai.com/docs/models',
      'Restart the backend server after the configuration is updated',
    ],
    type: 'model',
  };
}


/**
 * Parse SQL-specific errors and provide suggestions
 */
function parseSqlError(error: string): ParsedError {
  // TIMESTAMP_SUB errors
  if (error.includes('TIMESTAMP_SUB') && error.includes('WEEK')) {
    return {
      title: 'SQL Syntax Error',
      message:
        'The SQL query used TIMESTAMP_SUB with WEEK, which BigQuery doesn\'t support.',
      details:
        'TIMESTAMP_SUB does not support the WEEK date part when the argument is TIMESTAMP type',
      suggestions: [
        'Try: "top categories by revenue in the last 7 days" (use days instead of weeks)',
        'Try: "top categories by revenue last month"',
        'Try: "top categories by revenue in the last 30 days"',
      ],
      type: 'sql',
    };
  }

  // Generic date part errors
  if (error.includes('does not support') && error.includes('date part')) {
    const match = error.match(/does not support the (\w+) date part/);
    const datePart = match ? match[1].toUpperCase() : 'DATE PART';
    return {
      title: 'SQL Syntax Error',
      message: `The query used an unsupported date part: ${datePart}`,
      suggestions: [
        'Try using: DAY, MONTH, YEAR, QUARTER',
        'Avoid: WEEK, DECADE, CENTURY',
        'Rephrase the question using supported time periods',
      ],
      type: 'sql',
    };
  }

  // Invalid column errors
  if (error.includes('Unrecognized name')) {
    const match = error.match(/Unrecognized name: (\w+)/);
    const column = match ? match[1] : 'unknown column';
    return {
      title: 'Column Not Found',
      message: `The query referenced a column that doesn't exist: ${column}`,
      suggestions: [
        'Check the column name spelling',
        'Try asking about different fields',
        'Ask about: product_id, category, revenue, created_date, status',
      ],
      type: 'sql',
    };
  }

  // Generic SQL error
  return {
    title: 'SQL Error',
    message: 'The generated SQL query is invalid for BigQuery.',
    details: extractSqlErrorMessage(error),
    suggestions: [
      'Try rephrasing your question',
      'Use simpler time periods (today, this month, etc)',
      'Ask about specific columns or time ranges',
    ],
    type: 'sql',
  };
}

/**
 * Extract the main error message from a SQL error
 */
function extractSqlErrorMessage(error: string): string {
  // Try to find the main error message
  const match = error.match(/reason: (\w+),\s*message: ([^,\[\]]+)/);
  if (match) {
    return match[2].trim();
  }

  // Fallback: return first 300 chars
  return error.length > 300 ? error.substring(0, 300) + '...' : error;
}

/**
 * Check if an error is recoverable (user can retry with different input)
 */
export function isRecoverableError(error: string): boolean {
  const recoverablePatterns = [
    'SQL Error',
    'invalidQuery',
    'TIMESTAMP_SUB',
    'Unrecognized name',
    'does not support',
    'invalid column',
  ];

  // Model errors are NOT recoverable by the user (need admin action)
  if (error.includes('model') && error.includes('not found')) {
    return false;
  }

  return recoverablePatterns.some((pattern) =>
    error.toLowerCase().includes(pattern.toLowerCase())
  );
}
