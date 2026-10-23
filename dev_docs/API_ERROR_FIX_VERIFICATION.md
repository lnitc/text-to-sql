# API Error Fix Verification Guide

## Issue Summary

**Problem:** When sending a message, the UI displayed "Error [object Object]" instead of a meaningful error message.

**Root Cause:** Two mismatches between frontend and backend:
1. **Field Name Mismatch:** Frontend sent `query` field, but backend expected `user_query`
2. **Error Response Format:** Frontend looked for `response.data.detail`, but backend returned `response.data.message`

**Result:** Error response was malformed in transit, causing frontend to display "[object Object]"

---

## What Was Fixed

### Changes Made to `frontend/app/api.ts`

#### 1. Fixed ChatRequest Interface
```typescript
// BEFORE
export interface ChatRequest {
  query: string;
}

// AFTER
export interface ChatRequest {
  user_query: string;
}
```

#### 2. Added ErrorResponse Interface
```typescript
export interface ErrorResponse {
  error: string;
  message: string;
  status_code: number;
  details?: string;
}
```

#### 3. Updated sendQuery Function
```typescript
// BEFORE
const response = await apiClient.post<AgentResponse>('/api/chat', {
  query,
} as ChatRequest);

// AFTER
const response = await apiClient.post<AgentResponse>('/api/chat', {
  user_query: query,
} as ChatRequest);
```

#### 4. Improved Error Extraction Logic
```typescript
// BEFORE
throw new Error(
  axiosError.response?.data?.detail ||
    axiosError.message ||
    'Failed to send query'
);

// AFTER
const errorData = axiosError.response?.data;
let errorMessage = 'Failed to send query';
if (errorData?.message) {
  errorMessage = errorData.message;
} else if (errorData?.details) {
  errorMessage = errorData.details;
} else if (axiosError.message) {
  errorMessage = axiosError.message;
}
throw new Error(errorMessage);
```

---

## Verification Steps

### Step 1: Refresh Browser
1. In your browser, press **Ctrl+F5** (hard refresh)
2. This ensures the updated frontend code loads from the dev server

### Step 2: Verify Frontend Server Has Updated Code
- Open browser DevTools (F12)
- Go to the Network tab
- Refresh the page
- Check that `api.ts` is loaded from the dev server

### Step 3: Send a Test Query
1. Type a question in the chat input
2. Send the message
3. Observe the result

### Expected Behavior

#### If GCP credentials are properly configured:
- ✅ Backend receives request with correct `user_query` field
- ✅ Backend executes the SQL and returns results
- ✅ You see the chart and data visualization

#### If GCP credentials need to be refreshed:
- ✅ Backend returns an error response
- ✅ Frontend now properly extracts the error message
- ✅ You see: **"Error: Pipeline execution failed: RefreshError..."**
- ✅ NOT: "Error [object Object]"

#### If there's any other backend error:
- ✅ You see the actual error message
- ✅ Error message is human-readable and actionable
- ✅ Example: "Error: Query cannot be empty"

---

## Checking GCP Credentials

If you see a RefreshError message, your GCP credentials need attention:

### Option 1: Re-authenticate with gcloud CLI
```bash
gcloud auth application-default login
```

### Option 2: Check Environment Variable
```bash
# Verify GOOGLE_APPLICATION_CREDENTIALS is set
echo $env:GOOGLE_APPLICATION_CREDENTIALS  # PowerShell
echo $GOOGLE_APPLICATION_CREDENTIALS      # Bash

# It should point to your service account JSON file
# Example: C:\path\to\your-service-account-key.json
```

### Option 3: Verify Service Account JSON
```bash
# Check if the file exists and is readable
ls $env:GOOGLE_APPLICATION_CREDENTIALS

# Check if it's valid JSON
Get-Content $env:GOOGLE_APPLICATION_CREDENTIALS | ConvertFrom-Json
```

### Option 4: Restart Backend Server
After fixing credentials:
```bash
# Stop the backend (Ctrl+C in the terminal)
# Then restart it
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Commit Information

**Commit Hash:** 040e7f8  
**Files Changed:** `frontend/app/api.ts`  
**Lines Changed:** 23 insertions, 8 deletions

---

## Testing Checklist

- [ ] Refreshed browser with Ctrl+F5
- [ ] Verified frontend dev server loaded updated code
- [ ] Sent a test query
- [ ] Received an error message (if credentials need refresh) OR successful response (if credentials are valid)
- [ ] Error message is readable (not "[object Object]")
- [ ] If error, followed GCP credential fix steps
- [ ] If credentials fixed, sent query again and got results

---

## Technical Background

### Why "[object Object]" Appeared
When you call `String(error)` or use template literals with an object in JavaScript without accessing its properties, you get `[object Object]`. 

The original code was attempting to handle errors like:
```typescript
throw new Error(
  axiosError.response?.data?.detail  // This was undefined
);
```

When `detail` was undefined, the Error constructor received `undefined`, which when combined with other falsy values, eventually threw an error object itself, not a string. When this object was later converted to a string for display, it became "[object Object]".

### Why This Fix Works
The improved error extraction:
1. Checks the actual error response structure returned by the backend
2. Tries multiple fields in priority order (message, details, axiosError.message)
3. Always falls back to a default message
4. Ensures we always have a string to pass to Error constructor

---

## Prevention Tips

To avoid this type of issue in the future:

1. **Keep interfaces in sync:** When backend changes a field name, update frontend immediately
2. **Document API contracts:** Keep a shared interface definition for all request/response types
3. **Test error paths:** Always test what happens when requests fail
4. **Log error responses:** Log the full error response in the browser console for debugging
5. **Type check:** Use TypeScript strictly to catch mismatches at compile time
6. **Integration tests:** Add tests that verify request/response schemas match

---

## Questions?

If you encounter any issues:
1. Check the browser console (F12) for JavaScript errors
2. Check the Network tab to see the actual backend response
3. Check the backend logs for what it's receiving
4. Ensure both frontend and backend are running on the correct ports (3000 and 8000)

