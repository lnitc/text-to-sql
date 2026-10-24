# Error Handling Testing Guide - Phase 4.2

This guide covers testing all the improved error handling features, including the new model deprecation handling.

## Prerequisites
- Backend running: `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000`
- Frontend running: `npm run dev`
- Both services accessible at their default ports

---

## Test 1: Model Availability Error

### Scenario
Test that the application properly handles deprecated or unavailable OpenAI models.

### Setup
1. Modify `.env.local` in the backend directory
2. Change: `OPENAI_MODEL=gpt-3.5-turbo` (deprecated model)
3. Restart backend server
4. Refresh frontend

### Test Steps
1. Go to http://localhost:3000
2. Type a query: "What are the top 5 products by revenue?"
3. Click Send

### Expected Behavior
- ✅ Error message appears with title: "Model Unavailable"
- ✅ Message explains the model "gpt-3.5-turbo" is not available
- ✅ Suggestions include:
  - "Ask your system administrator..."
  - "Valid models: gpt-4o-mini (recommended), gpt-4o, gpt-4-turbo"
  - "Check OpenAI API documentation..."
  - "Restart the backend server..."
- ✅ Error is NOT marked as recoverable (no "Try Rephrasing" suggestion)
- ✅ Technical details collapsible and show full error

### Verification
- Check backend logs: Should show "[Chat] Model not found error:"
- Check frontend console: No hydration errors
- Backend response: HTTP 500 with detailed error message

---

## Test 2: Valid Model Works

### Setup
Ensure `.env.local` has: `OPENAI_MODEL=gpt-4o-mini`

### Test Steps
1. Restart backend server
2. Refresh frontend
3. Type query: "How many orders were placed today?"
4. Click Send

### Expected Behavior
- ✅ Request processes successfully
- ✅ Returns SQL query, chart, and analysis
- ✅ No error messages displayed
- ✅ "Processing your query..." message disappears once complete

### Verification
- Backend logs show: "SQL generation failed" should NOT appear
- Backend should log the generated SQL and execution time
- Chart renders with data

---

## Test 3: SQL Syntax Error Handling

### Test Steps
1. Type query: "What were the top 7 product categories by revenue last week?"
2. Click Send

### Expected Behavior
- ✅ Error displays with title: "SQL Syntax Error"
- ✅ Message mentions: "TIMESTAMP_SUB does not support the WEEK date part"
- ✅ Suggestions include:
  - "Try: 'top categories by revenue in the last 7 days' (use days instead of weeks)"
  - "Try: 'top categories by revenue last month'"
  - "Try: 'top categories by revenue in the last 30 days'"
- ✅ Error IS marked as recoverable (suggestions show "Try Rephrasing:")
- ✅ Error is NOT blocking (user can try a different query)

### Verification
- Error color: Red/pink background
- "Try Rephrasing:" label visible
- Each suggestion is clickable/copyable

---

## Test 4: Empty Query Validation

### Test Steps
1. Leave input field empty
2. Click Send (or press Enter)

### Expected Behavior
- ✅ Query is not sent
- ✅ No network request made
- ✅ Input field remains empty
- ✅ No error message displayed (validation is client-side)

### Verification
- Network tab shows no request to `/api/chat`
- No loading message appears

---

## Test 5: Connection Error Handling

### Test Steps
1. Stop the backend server (Ctrl+C in backend terminal)
2. In frontend, type any query
3. Click Send

### Expected Behavior
- ✅ Error displays with title: "Connection Error"
- ✅ Message: "Backend server is not responding..."
- ✅ Suggestions include:
  - "Verify backend is running on http://localhost:8000"
  - "Check for connection errors in the backend terminal"
  - "Try refreshing the page"
- ✅ Loading message appears, then replaced with error
- ✅ "Backend Ready" indicator shows red in header

### Verification
- Backend status in header shows red pulsing dot
- Error is clearly distinguished from SQL/model errors
- No data partially rendered

### Cleanup
Restart backend: `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000`

---

## Test 6: Error Recovery - Rephrasing SQL

### Test Steps
1. Send query: "What were the top 7 product categories by revenue last week?"
2. See error about TIMESTAMP_SUB and WEEK
3. Click one of the suggested alternative queries
4. Send it

### Expected Behavior
- ✅ Alternative query processes successfully
- ✅ Returns results with proper chart
- ✅ No error on the retry
- ✅ Original error message still visible in history

### Verification
- New message appears below error
- Both error and success responses stay in conversation
- Chart renders successfully

---

## Test 7: Favorites Still Work with Errors

### Test Steps
1. Send a query that results in an error
2. Wait for error to display
3. Try to add error message to favorites
4. Check favorites panel

### Expected Behavior
- ✅ "Add to Favorites" button visible in error message
- ✅ Clicking adds the query to favorites
- ✅ Star icon fills when favorited
- ✅ Query appears in Favorites panel
- ✅ Can click favorite to re-run failed query

### Verification
- Favorites panel updates immediately
- localStorage has the query stored
- Star icon reflects favorited state

---

## Test 8: Persistent Error Display

### Test Steps
1. Send a query that produces an error
2. Close browser (or close tab)
3. Reopen application

### Expected Behavior
- ✅ Error message still displays
- ✅ Error message text is preserved
- ✅ User query that caused error is visible

### Verification
- Conversation history includes error
- Error still shows full details and suggestions
- No loss of error information on page refresh

---

## Backend Error Categorization Verification

Check logs while running queries. Backend should log one of:

```
[Chat] Model not found error: ...
[Chat] Authentication error: ...
[Chat] Rate limit error: ...
[Chat] SQL execution error: ...
[Chat] Pipeline error: ...
```

### Verify by Logs

1. **Model Error:**
   ```
   [Pipeline] SQL generation failed: Error code: 404 - ...model...not found...
   [Chat] Model not found error: ...
   ```

2. **SQL Error:**
   ```
   [BigQueryTool] SQL Error: 400 TIMESTAMP_SUB does not support...
   [Chat] SQL execution error: ...
   ```

3. **Connection Error:**
   ```
   [Chat] Processing query: ...
   [POST] /api/chat - Status: 500
   (No specific log for connection, caught by frontend)
   ```

---

## Error Handling Checklist

Run through this checklist to verify all error handling works:

### UI Display
- [ ] Error messages have red/pink background
- [ ] Error title is clear and specific
- [ ] Error message explains the problem
- [ ] "Try Rephrasing:" label shows for recoverable errors
- [ ] "Suggestions:" label shows for non-recoverable errors
- [ ] Technical Details collapsible section exists
- [ ] Error doesn't break page layout
- [ ] Error doesn't cause hydration warnings in console

### Message Content
- [ ] Error message is user-friendly, not raw Python exceptions
- [ ] Suggestions are actionable and specific
- [ ] Links to documentation included where relevant
- [ ] Configuration file names mentioned for admin-level fixes
- [ ] Command examples provided (e.g., gcloud commands)

### Backend Logging
- [ ] Errors are categorized in logs (model/auth/rate/sql/unknown)
- [ ] Log messages include error type prefix: [Chat] Model..., [Chat] Auth..., etc.
- [ ] Full error details logged for debugging
- [ ] Execution time still logged for successful queries

### User Recovery
- [ ] Recoverable errors allow user to retry with different input
- [ ] Non-recoverable errors guide to admin/documentation
- [ ] Users can still see error history in favorites/messages
- [ ] Error messages persist across page refreshes
- [ ] No partial/corrupted UI when errors occur

---

## Advanced Testing: Rate Limiting

To test rate limit handling (requires OpenAI API rate limit trigger):

1. Rapidly send many queries in succession
2. Eventually hit OpenAI rate limit
3. Check error displays correctly

Expected: Error with title "OpenAI Rate Limit" and suggestion to wait.

---

## Performance Impact Testing

### Before & After
Compare response times before and after error handling improvements:

1. Successful query: ~4-5 seconds (BigQuery execution time)
   - Error detection: <10ms
   - No noticeable impact

2. Failed query (model error): ~500ms
   - Error detection: <5ms
   - Response: < 1 second total

### Verification
Check X-Process-Time header in network tab to see backend processing time.

---

## Rollback Instructions (If Needed)

If error handling needs to be reverted:

```bash
git log --oneline | grep -i error
# Find: be0e43d - Improve error handling...

git revert be0e43d
git push
```

Then restart backend and frontend.

---

## Documentation Updates

Error handling improvements are documented in:
- Backend: config.py (model selection)
- Backend: agents/simplified_pipeline.py (error detection)
- Backend: main.py (error categorization)
- Frontend: utils/errorHandler.ts (error parsing and suggestions)
- Frontend: ChatMessage.tsx (error display UI)

All error types and their handling are documented with comments.

---

## Conclusion

Error handling is a critical part of user experience. These tests verify:
- ✅ Errors are detected accurately
- ✅ Users receive clear, actionable guidance
- ✅ Application doesn't crash or show corrupt state
- ✅ Error history is preserved
- ✅ Recovery paths are available where appropriate
