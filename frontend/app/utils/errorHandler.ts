/**
 * Error handling and parsing utilities
 * Converts technical errors into user-friendly messages
 */

export interface ParsedError {
  title: string;
  message: string;
  details?: string;
  suggestions?: string[];
  type: 'sql' | 'auth' | 'network' | 'unknown';
}

/**
 * Parse backend error messages and extract useful information
 */
export function parseErrorMessage(error: string): ParsedError {
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

  return recoverablePatterns.some((pattern) =>
    error.toLowerCase().includes(pattern.toLowerCase())
  );
}
