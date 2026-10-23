# Phase 4.2 Manual Testing Guide - Step by Step

## Setup Status
```
Frontend:  ✅ Running on http://localhost:3000
Backend:   ⏳ Installing dependencies (will run on http://localhost:8000)
Database:  ✅ BigQuery public dataset configured
```

---

## QUICK START - Test in Your Browser

1. Open http://localhost:3000 in Chrome/Firefox
2. Follow the test scenarios below

---

## TEST SCENARIO 1: UI Components Rendering

### Steps
1. Load the page
2. Look for the **sidebar** with 4 buttons on the left:
   - ❤️ (Favorites)
   - 🕐 (History)
   - 📊 (Analytics)
   - ✏️ (Query Builder)
3. Look for the **chat interface** with:
   - Message input field at bottom
   - Empty message area at top
   - Theme toggle (usually top-right)

### Expected Results
- ✅ All buttons visible and clickable
- ✅ No console errors
- ✅ Theme toggle works
- ✅ All text is readable

---

## TEST SCENARIO 2: Favorites Panel

### Steps
1. Click the ❤️ (Favorites) button
2. Panel should slide in from left
3. Should show "Favorites" heading
4. Should show search field
5. Should show "No favorites yet" message
6. Click ❤️ button again to close

### Expected Results
- ✅ Panel slides in smoothly
- ✅ Panel width ~320px
- ✅ Close/open works
- ✅ Empty state message is helpful

---

## TEST SCENARIO 3: History Panel

### Steps
1. Click the 🕐 (History) button
2. Panel should slide in
3. Should show "Query History" heading
4. Should show "No history yet" message (first time)
5. Close panel

### Expected Results
- ✅ Panel opens/closes smoothly
- ✅ Empty state message present
- ✅ Panel width appropriate (~320px)

---

## TEST SCENARIO 4: Query Builder Panel

### Steps
1. Click the ✏️ (Query Builder) button
2. Panel should open showing:
   - Query textarea
   - Parameter fields (LIMIT, OFFSET, etc.)
   - Quick Templates dropdown
   - Apply Query button
   - Live Preview area

### Expected Results
- ✅ Panel renders completely
- ✅ All input fields present
- ✅ Dropdown has templates listed
- ✅ No JavaScript errors

---

## TEST SCENARIO 5: Analytics Dashboard

### Steps
1. Click the 📊 (Analytics) button
2. Panel should open showing:
   - "Analytics" heading
   - 4 Stat Cards (metrics)
   - Line Chart (7-day trend)
   - Pie Chart (keyword analysis)

### Expected Results
- ✅ Panel renders smoothly
- ✅ All charts visible
- ✅ No chart errors
- ✅ Text is readable

---

## TEST SCENARIO 6: Dark Mode Toggle

### Steps
1. Find the theme toggle (moon/sun icon)
2. Click to toggle to dark mode
3. Observe all panels update colors
4. Toggle back to light mode

### Expected Results
- ✅ All panels update smoothly
- ✅ Text remains readable
- ✅ No jarring color changes
- ✅ Charts colors adjust

---

## TEST SCENARIO 7: Panel Switching

### Steps
1. Open Favorites panel
2. Click History button (should switch panels)
3. Click Analytics button (should switch again)
4. Click Query Builder (should switch)
5. Click any button again (should close)

### Expected Results
- ✅ Only one panel open at a time
- ✅ Smooth transitions between panels
- ✅ Click same button closes panel

---

## TEST SCENARIO 8: Data Persistence Check

### Steps (Check localStorage)
1. Open **Browser DevTools** (F12)
2. Go to **Application** tab
3. Expand **Local Storage**
4. Click localhost:3000
5. Look for `favorites` key
6. Look for `queryHistory` key

### Expected Results
- ✅ Keys exist (may be empty on first load)
- ✅ Data is valid JSON format
- ✅ Both keys present

---

## TEST SCENARIO 9: Responsive Width Test

### Desktop (1920px)
- [ ] All panels fit comfortably
- [ ] Chat area still usable
- [ ] No horizontal scroll

### Tablet (768px via DevTools)
1. Press F12
2. Click Device Toolbar (Ctrl+Shift+M)
3. Select iPad preset
- [ ] Panels resize appropriately
- [ ] Content readable
- [ ] Buttons clickable

### Mobile (375px)
1. Select iPhone preset
- [ ] No horizontal scroll
- [ ] Touch targets > 44px
- [ ] Text readable

---

## TEST SCENARIO 10: Console Error Check

### Steps
1. Press F12 to open DevTools
2. Click **Console** tab
3. Look for any red errors or warnings
4. Perform each test scenario above
5. Check console after each action

### Expected Results
- ✅ No red errors
- ✅ No TypeScript errors
- ✅ Only normal network requests logged
- ✅ No 404 errors

---

## TEST SCENARIO 11: Component Content Check

### Favorites Panel
- [ ] Search field present
- [ ] Filter by tags section present
- [ ] Copy button visible
- [ ] Delete button visible
- [ ] Empty state message shown

### History Panel
- [ ] Search field present
- [ ] Timestamp shown (once data added)
- [ ] Copy button visible
- [ ] Re-run button visible
- [ ] Empty state message shown

### Query Builder
- [ ] Base query textarea present
- [ ] LIMIT field present (numeric)
- [ ] OFFSET field present (numeric)
- [ ] FILTERS field present
- [ ] Quick Templates dropdown present
- [ ] Preview section present
- [ ] Apply Query button present

### Analytics
- [ ] 4 Stat cards present
- [ ] Line chart renders
- [ ] Pie chart renders
- [ ] Chart titles visible
- [ ] Legend visible

---

## Test Results Summary

| Test # | Scenario | Status | Notes |
|--------|----------|--------|-------|
| 1 | UI Components Render | ⏳ | Check all buttons appear |
| 2 | Favorites Panel | ⏳ | Test open/close |
| 3 | History Panel | ⏳ | Test empty state |
| 4 | Query Builder | ⏳ | Test all fields render |
| 5 | Analytics Dashboard | ⏳ | Test charts render |
| 6 | Dark Mode | ⏳ | Test toggle works |
| 7 | Panel Switching | ⏳ | Test navigation |
| 8 | Data Persistence | ⏳ | Check localStorage |
| 9 | Responsive Design | ⏳ | Test on mobile/tablet |
| 10 | Console Errors | ⏳ | Check F12 console |
| 11 | Component Content | ⏳ | Verify all UI elements |

---

## Notes

- Test without backend first (basic UI)
- Backend testing requires CrewAI + BigQuery setup
- Use Chrome or Firefox for best compatibility
- DevTools (F12) essential for verification

