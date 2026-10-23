# Phase 4.2 Testing - Execution Guide

**Date**: 2026-10-22  
**Status**: 🟢 READY FOR TESTING  
**Frontend**: ✅ Running on http://localhost:3000  
**Backend**: ✅ Running on http://localhost:8000

---

## 🎯 Test Execution Plan

Your task now is to perform manual testing of the Phase 4.2 components. Both servers are running and ready.

### What Has Been Set Up

1. **Frontend (Next.js)** - http://localhost:3000
   - All Phase 4.2 components implemented
   - TypeScript strict mode - zero errors
   - Dark mode support
   - localStorage persistence

2. **Backend (FastAPI)** - http://localhost:8000
   - CrewAI agents configured
   - BigQuery integration ready
   - CORS configured for localhost:3000
   - Health endpoint: GET /health

3. **Test Documentation**
   - PHASE_4_2_TESTING.md - Full testing checklist (14 KB)
   - PHASE_4_2_MANUAL_TESTS.md - Step-by-step scenarios (6 KB)

---

## 🚀 Quick Start Testing

### Step 1: Open the Application
```
1. Open http://localhost:3000 in your browser
2. You should see the chat interface
```

### Step 2: Check Core UI (Estimated Time: 5 minutes)

#### Expected to See:
- [ ] Chat interface with message area
- [ ] Input field at bottom
- [ ] 4 sidebar buttons on left:
  - ❤️ Favorites
  - 🕐 History
  - 📊 Analytics
  - ✏️ Query Builder
- [ ] Theme toggle (top right, usually)

#### If Not Visible:
1. Press F12 to open DevTools
2. Check **Console** tab
3. Look for red errors
4. Share screenshot with errors

### Step 3: Test Each Panel (Estimated Time: 10 minutes)

#### 3A: Favorites Panel ❤️
1. Click ❤️ button
2. Panel should slide in from left
3. Should show "Favorites" heading
4. Should show "No favorites yet" message
5. Search field should be visible
6. Click ❤️ again to close

**✅ Pass Criteria**: Panel slides in/out smoothly, no errors

#### 3B: History Panel 🕐
1. Click 🕐 button
2. Panel slides in
3. Shows "Query History" heading
4. Shows "No history yet" message (on first load)
5. Search field visible
6. Click 🕐 again to close

**✅ Pass Criteria**: Panel works like Favorites

#### 3C: Query Builder ✏️
1. Click ✏️ button
2. Panel shows:
   - Query textarea
   - LIMIT field (number)
   - OFFSET field (number)
   - Quick Templates dropdown
   - Apply button
   - Preview section
3. Click ✏️ to close

**✅ Pass Criteria**: All fields render, no errors

#### 3D: Analytics Dashboard 📊
1. Click 📊 button
2. Panel shows:
   - 4 stat cards (metrics)
   - Line chart
   - Pie chart
   - All charts visible
3. Click 📊 to close

**✅ Pass Criteria**: Charts render without errors

### Step 4: Test Dark Mode (Estimated Time: 3 minutes)

1. Find theme toggle (moon/sun icon)
2. Click it once → should go to dark mode
3. All panels should update colors:
   - Background darker
   - Text lighter
   - Charts readable
4. Click again → back to light mode

**✅ Pass Criteria**: Smooth transition, no color issues

### Step 5: Test Panel Switching (Estimated Time: 3 minutes)

1. Open Favorites ❤️
2. Click History 🕐 → should close Favorites, open History
3. Click Analytics 📊 → should close History, open Analytics
4. Click Query Builder ✏️ → close Analytics, open Builder
5. Click Query Builder ✏️ again → should close

**✅ Pass Criteria**: Only one panel open at a time, smooth transitions

### Step 6: Verify localStorage (Estimated Time: 3 minutes)

1. Press **F12** to open DevTools
2. Click **Application** tab
3. On left, expand **Local Storage**
4. Click **http://localhost:3000**
5. Look for two keys:
   - `favorites` (should be empty `[]` initially)
   - `queryHistory` (should be empty `[]` initially)

**✅ Pass Criteria**: Both keys exist with empty arrays

### Step 7: Check for Console Errors

1. Keep DevTools open (F12)
2. Click **Console** tab
3. Should see NO red error messages
4. Test steps 3-6 again while watching Console
5. Verify no errors appear

**✅ Pass Criteria**: No red errors, only normal logs

---

## 🧪 Extended Testing (When Ready for Backend)

These tests require the backend to respond to queries:

### Test: Save Query to Favorites

**Prerequisites**: Backend must be responding to queries

1. In chat input, type: `"What is the total number of orders?"`
2. Press Enter or click Send
3. Wait for response from backend
4. In the assistant message, find the **☆ star button**
5. Click star → save form should open
6. Enter tags: `important, orders` (comma-separated)
7. Click **Save**
8. Star should change to **★** (filled)
9. Open Favorites panel ❤️
10. Your query should appear in the list with tags
11. Click on the query to preview it
12. Click **Copy** button → query copied to clipboard

**✅ Pass Criteria**: Query saves, tags persist, copy works

### Test: Query History

1. Execute a few queries (wait for responses)
2. Open History panel 🕐
3. Should see list of past queries with:
   - Query text (truncated)
   - Timestamp (e.g., "just now", "5 min ago")
   - Result count
4. Click **Copy** on one → query copied
5. Click **▶️ Re-run** → query appears in input
6. Click **☆ Star** on one → should save to Favorites
7. Search for keywords in search field
8. Results should filter in real-time

**✅ Pass Criteria**: All features work, no errors

### Test: Analytics Dashboard Updates

1. Execute 3-5 queries in chat
2. Open Analytics panel 📊
3. Check stat cards:
   - **Total Queries**: should show count
   - **Success Rate**: % of successful queries
   - **Avg Response Time**: average ms
   - **Most Used Keywords**: top words from your queries
4. Line Chart (7-day trend):
   - X-axis: dates (last 7 days)
   - Y-axis: query count
   - Should show activity spike today
5. Pie Chart (keyword analysis):
   - Shows keyword distribution
   - Percentages add up to 100%

**✅ Pass Criteria**: All calculations correct, charts readable

### Test: Query Builder

1. Open Query Builder panel ✏️
2. Click **Quick Templates** dropdown
3. Select "Basic Select"
4. Fields should auto-fill:
   - BASE_QUERY: SELECT * FROM orders
   - LIMIT: 100
5. Modify LIMIT to 50
6. **Live Preview** should update immediately
7. Click **Apply Query**
8. Query should appear in chat input
9. Click Send
10. Backend should execute it

**✅ Pass Criteria**: Template loads, preview updates, query executes

---

## 📊 Test Report Template

When you're done testing, use this template to report results:

```
# Phase 4.2 Test Results

## Environment
- Date: [Today's date]
- Browser: [Chrome/Firefox/Safari/Edge]
- OS: [Windows/Mac/Linux]
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## Test Results

### Core UI Components
- [ ] Chat interface loads
- [ ] Sidebar buttons render (4 icons)
- [ ] All panels render without errors
- [ ] Dark mode toggle works
- [ ] Panel switching works correctly

**Issues Found**: [List any issues or errors]

### Favorites Panel
- [ ] Panel opens/closes on click
- [ ] Search filters results
- [ ] Tags can be added/removed
- [ ] Save to favorites works (if backend ready)
- [ ] Copy button functional
- [ ] Delete button removes query

**Issues Found**: [List any issues]

### History Panel
- [ ] Displays query history
- [ ] Search filters history
- [ ] Re-run button works
- [ ] Mark favorite works
- [ ] Timestamps display correctly

**Issues Found**: [List any issues]

### Query Builder
- [ ] All input fields present
- [ ] Templates load correctly
- [ ] Live preview updates
- [ ] Apply button sends query

**Issues Found**: [List any issues]

### Analytics Dashboard
- [ ] 4 stat cards display
- [ ] Line chart renders
- [ ] Pie chart renders
- [ ] Data updates on new queries

**Issues Found**: [List any issues]

### Data Persistence
- [ ] localStorage keys exist
- [ ] Data persists after reload
- [ ] Tags saved correctly
- [ ] No corruption on edge cases

**Issues Found**: [List any issues]

## Overall Status
- **✅ PASS** - All tests passed, no critical issues
- **⚠️ PASS WITH ISSUES** - Mostly works, minor issues found
- **❌ FAIL** - Critical issues prevent full testing

## Critical Issues (if any)
1. [Issue description]
2. [Issue description]

## Nice-to-Have Improvements (if any)
1. [Suggestion]
2. [Suggestion]

## Notes
[Any additional observations]

---
Tested by: [Your name]
```

---

## 🔧 Troubleshooting

### Frontend Not Loading
```
1. Check terminal: Next.js should say "Ready in XXXms"
2. If error: kill npm process, run `npm run dev` again
3. Check http://localhost:3000
4. If 404: wait for Turbopack to compile (can take 10-15 seconds)
```

### Backend Not Responding
```
1. Check terminal: Should say "Uvicorn running on http://0.0.0.0:8000"
2. If error about imports: missing dependencies
3. Check: curl http://localhost:8000/health
4. If timeout: server still starting (wait 10 seconds)
```

### Components Not Rendering
```
1. Press F12 → Console tab
2. Look for red error messages
3. Screenshot errors
4. Check if TypeScript errors are present
5. Verify all files were created in /frontend/app/components/
```

### Dark Mode Not Working
```
1. Check if toggle button is visible
2. Verify it's clickable
3. Check Console for JavaScript errors
4. Refresh page with Ctrl+Shift+Delete
5. Verify `isDark` variable updates
```

### localStorage Empty
```
1. Open DevTools → Application tab
2. Clear All from Local Storage
3. Reload page
4. Check if keys are created (should show empty arrays)
5. Execute a query (if backend ready)
6. Data should populate
```

---

## 📋 Checklist for Sign-Off

When testing is complete, verify:

- [ ] All core UI components render
- [ ] All 4 sidebar panels open/close
- [ ] Dark mode works throughout
- [ ] No red console errors
- [ ] localStorage keys exist
- [ ] Panel switching works
- [ ] Search/filter functionality works
- [ ] Copy buttons copy text
- [ ] No crashes or hangs
- [ ] Application is responsive
- [ ] Timestamps format correctly
- [ ] Charts render (if data present)

---

## ✅ Expected Phase 4.2 Status

Once all tests pass:

```
Frontend:              ✅ READY FOR PRODUCTION
  - All components:    ✅ Rendering
  - Dark mode:         ✅ Working
  - Data persistence:  ✅ localStorage active
  - TypeScript:        ✅ Strict mode, zero errors
  - Performance:       ✅ < 3 second load

Backend:               ✅ READY FOR INTEGRATION
  - Health check:      ✅ Responding
  - CORS:              ✅ Configured
  - Endpoints:         ✅ Available
  - CrewAI:            ✅ Ready
  - BigQuery:          ✅ Connected

Integration:           ⏳ READY FOR PHASE 5
  - Both servers:      ✅ Running
  - Communication:     ⏳ Docker next
  - Deployment:        ⏳ Phase 6
```

---

## 🎓 What Comes Next?

After Phase 4.2 testing is complete:

**Phase 5: Docker Compose Integration** (1-2 hours)
- Containerize frontend (Next.js in Docker)
- Containerize backend (FastAPI in Docker)
- Set up docker-compose.yml
- Configure networking
- Volume management for development
- Test full multi-container setup

**Phase 6: Production Deployment** (2-3 hours)
- Deploy frontend to Vercel
- Deploy backend to Google Cloud Run
- Configure environment variables
- Set up monitoring
- End-to-end testing

---

## 📞 Questions or Issues?

If you encounter any issues during testing:

1. **Document the issue**: Take a screenshot
2. **Capture error**: Get the full error message
3. **Include environment**: Browser, OS, timestamps
4. **Describe steps**: What you did when error occurred
5. **Include logs**: Console errors from DevTools

---

**Good luck with testing! Once complete, we'll move to Phase 5: Docker Compose integration.** 🚀

