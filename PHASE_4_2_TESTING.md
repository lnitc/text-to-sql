# Phase 4.2 Testing Documentation

## Test Execution Date
2026-10-22

## Environment Setup
- **Frontend**: Next.js 16 running on http://localhost:3000
- **Backend**: FastAPI running on http://localhost:8000
- **Database**: BigQuery public dataset (thelook_ecommerce)

---

## 1. CORE UI COMPONENTS

### 1.1 Chat Interface Loads
- [ ] Page loads without errors
- [ ] Main chat input field visible
- [ ] Message history area visible
- [ ] Sidebar buttons visible (4 icons)
- [ ] All buttons properly aligned

### 1.2 Sidebar Button Bar
- [ ] Favorites button (heart icon) visible
- [ ] History button (clock icon) visible
- [ ] Analytics button (chart icon) visible
- [ ] Query Builder button (edit icon) visible
- [ ] Buttons are 12px wide and properly spaced
- [ ] Buttons have hover effects

### 1.3 Dark Mode Toggle
- [ ] Dark mode button present in header
- [ ] Click toggles between light/dark mode
- [ ] All panels update colors correctly
- [ ] Background colors transition smoothly
- [ ] Text remains readable in both modes

### 1.4 Message Display
- [ ] User messages appear with correct styling
- [ ] Assistant messages display properly
- [ ] Messages stack vertically
- [ ] Scrollbar appears when messages overflow
- [ ] Auto-scroll to latest message

---

## 2. FAVORITES PANEL

### 2.1 Panel Toggle
- [ ] Clicking Favorites button opens panel
- [ ] Panel slides in from left
- [ ] Panel width is ~320px
- [ ] Clicking button again closes panel
- [ ] Panel is semi-transparent behind chat area

### 2.2 Panel Content
- [ ] "Favorites" heading visible
- [ ] Search input field present
- [ ] Filter by tags section visible
- [ ] Empty state message displays when no favorites
- [ ] "No favorites yet..." message is helpful

### 2.3 Search Functionality
- [ ] Type in search field filters results
- [ ] Filters work in real-time
- [ ] Case-insensitive search
- [ ] Partial matches work
- [ ] Clear search returns all results

### 2.4 Tag Filtering
- [ ] Tag pills display below search
- [ ] Clicking tag filters by that tag
- [ ] Multiple tags can be selected
- [ ] Selected tags show highlighted state
- [ ] "Clear all tags" button works
- [ ] Tag count displays correctly

### 2.5 Favorite Items
- [ ] Query text displays in full
- [ ] Created date shows correctly
- [ ] Tags display as pills
- [ ] Copy button (📋) works
- [ ] Delete button (🗑️) removes favorite
- [ ] Mark as favorite button works

### 2.6 Save to Favorites (from ChatMessage)
- [ ] Star button (☆) appears in assistant messages
- [ ] Clicking star opens save form
- [ ] Form has query text field (pre-filled)
- [ ] Form has tag input field
- [ ] Can add multiple tags (comma-separated)
- [ ] Save button adds to favorites
- [ ] Star becomes filled (★) after saving
- [ ] Clicking filled star removes from favorites

### 2.7 Dark Mode in Favorites Panel
- [ ] Background color changes in dark mode
- [ ] Text color is readable
- [ ] Search field is styled correctly
- [ ] Tags display with proper contrast
- [ ] Delete/copy buttons visible in both modes

---

## 3. HISTORY PANEL

### 3.1 Panel Toggle
- [ ] Clicking History button opens panel
- [ ] Panel appears on left side
- [ ] Panel closes on second click
- [ ] Only one panel visible at a time

### 3.2 Panel Content
- [ ] "Query History" heading visible
- [ ] Search input field present
- [ ] History list displays
- [ ] Empty state shows when no history
- [ ] Max 20 items in history

### 3.3 History List Display
- [ ] Query text truncated appropriately
- [ ] Timestamp displays (e.g., "2 hours ago")
- [ ] Result count shows (e.g., "↳ 245 results")
- [ ] Older queries appear at bottom
- [ ] List is scrollable if >20 items

### 3.4 History Search
- [ ] Search field filters results
- [ ] Real-time filtering
- [ ] Case-insensitive search
- [ ] Clear search shows all history

### 3.5 History Actions
- [ ] Copy button (📋) copies query
- [ ] Re-run button (▶️) sends query to chat
- [ ] Favorite button (☆) saves to favorites
- [ ] Favorite button (★) appears after marked
- [ ] Delete/Clear buttons available

### 3.6 Re-run Query
- [ ] Clicking re-run sends query to input
- [ ] Query appears in message history
- [ ] Backend processes query
- [ ] Results display in chat

### 3.7 Dark Mode
- [ ] Panel background is dark
- [ ] Text is readable
- [ ] Buttons visible and clickable
- [ ] Timestamp text has good contrast

---

## 4. QUERY PARAMS EDITOR

### 4.1 Panel Toggle
- [ ] Clicking Query Builder button opens panel
- [ ] Panel slides in from left
- [ ] Panel closes on second click

### 4.2 Panel Layout
- [ ] "Query Builder" heading visible
- [ ] Parameter input fields render
- [ ] Query textarea displays
- [ ] Preview section visible
- [ ] Apply button at bottom

### 4.3 Input Fields
- [ ] "BASE_QUERY" field shows
- [ ] "LIMIT" numeric field present
- [ ] "OFFSET" numeric field present
- [ ] "FILTERS" text field present
- [ ] "GROUP_BY" field present
- [ ] "ORDER_BY" field present
- [ ] Each field has placeholder text
- [ ] Fields accept input

### 4.4 Parameter Validation
- [ ] LIMIT field only accepts numbers
- [ ] OFFSET field only accepts numbers
- [ ] Fields validate in real-time
- [ ] Error messages display for invalid input
- [ ] Save disabled if validation fails

### 4.5 Quick Templates
- [ ] Template button visible
- [ ] "Quick Templates" dropdown/menu present
- [ ] Templates include:
  - [ ] Basic Select
  - [ ] With Limit
  - [ ] With Date Range
  - [ ] Include Metrics
- [ ] Clicking template populates fields
- [ ] Can chain templates together

### 4.6 Live Preview
- [ ] Preview section updates in real-time
- [ ] Shows constructed query
- [ ] Displays formatted SQL
- [ ] Syntax highlighting (if available)
- [ ] Copy preview button works

### 4.7 Apply Query
- [ ] "Apply Query" button present
- [ ] Clicking sends query to chat
- [ ] Query appears in message history
- [ ] Spinner shows while processing
- [ ] Error message if query invalid

### 4.8 Dark Mode
- [ ] Panel background is dark
- [ ] Text fields visible
- [ ] Preview text readable
- [ ] Buttons have good contrast

---

## 5. ANALYTICS DASHBOARD

### 5.1 Panel Toggle
- [ ] Clicking Analytics button opens panel
- [ ] Panel appears on left side
- [ ] Panel closes on second click

### 5.2 Panel Layout
- [ ] "Analytics" heading visible
- [ ] Stat cards display
- [ ] Line chart visible
- [ ] Pie chart visible
- [ ] Panel scrolls if content overflows

### 5.3 Stat Cards (4 total)
- [ ] "Total Queries" card shows count
- [ ] "Success Rate" card shows percentage
- [ ] "Avg Response Time" card shows ms
- [ ] "Most Used Keywords" card shows list
- [ ] Each card has icon and label
- [ ] Numbers update in real-time

### 5.4 7-Day Trend Chart (Line Chart)
- [ ] Chart title displays
- [ ] X-axis shows dates (last 7 days)
- [ ] Y-axis shows query count
- [ ] Line connects data points
- [ ] Hover tooltip shows values
- [ ] Chart is responsive
- [ ] Axes labeled correctly

### 5.5 Keyword Analysis (Pie Chart)
- [ ] Chart title displays
- [ ] Pie slices for each keyword
- [ ] Colors are distinct
- [ ] Legend shows below chart
- [ ] Percentages display correctly
- [ ] Hover shows keyword and count

### 5.6 Data Accuracy
- [ ] Total queries = count of user messages
- [ ] Success rate calculates correctly
- [ ] Response time is reasonable
- [ ] Keywords extracted from queries
- [ ] 7-day data uses correct date range

### 5.7 Dark Mode
- [ ] Background is dark
- [ ] Chart text readable
- [ ] Lines/slices visible with contrast
- [ ] Legend readable
- [ ] Axes labels visible
- [ ] Grid lines (if shown) visible but subtle

### 5.8 Real-time Updates
- [ ] Charts update when new query executed
- [ ] Stats refresh automatically
- [ ] No manual refresh needed
- [ ] Updates are smooth (no flickering)

---

## 6. DATA PERSISTENCE

### 6.1 localStorage Storage
- [ ] Browser DevTools > Application > localStorage
- [ ] Key "favorites" exists
- [ ] Key "queryHistory" exists
- [ ] Data is valid JSON
- [ ] Max 50 favorites stored
- [ ] Max 20 history items stored

### 6.2 Save & Retrieve Favorites
- [ ] Save favorite query
- [ ] Open DevTools > localStorage > "favorites"
- [ ] New query appears in JSON
- [ ] Reload page
- [ ] Favorite still appears in panel
- [ ] Tags preserved
- [ ] Timestamps correct

### 6.3 Save & Retrieve History
- [ ] Execute query
- [ ] Check localStorage > "queryHistory"
- [ ] Query appears in array
- [ ] Reload page
- [ ] Query appears in History panel
- [ ] Timestamp preserved
- [ ] Result count preserved

### 6.4 Tag Persistence
- [ ] Save query with tags
- [ ] Reload page
- [ ] Tags still associated
- [ ] Can search by tag
- [ ] Can filter by tag

### 6.5 Storage Limits
- [ ] Add 51 favorites
- [ ] Check if oldest is removed
- [ ] Add 21 history items
- [ ] Check if oldest is removed
- [ ] Storage handles overflow correctly

---

## 7. RESPONSIVENESS & UX

### 7.1 Viewport Width (Desktop)
- [ ] On 1920px width: all panels fit
- [ ] Chat area still usable with panel open
- [ ] No horizontal scroll
- [ ] Text doesn't wrap awkwardly

### 7.2 Viewport Width (Tablet)
- [ ] On 768px width: panels resize
- [ ] Content still readable
- [ ] Buttons still clickable
- [ ] No layout breaks

### 7.3 Viewport Width (Mobile)
- [ ] On 375px width: panels stack or overlap
- [ ] Touch targets > 44px
- [ ] Text readable without zoom
- [ ] No horizontal scroll

### 7.4 Transitions & Animations
- [ ] Panel slide-in is smooth (300ms)
- [ ] Panel slide-out is smooth
- [ ] Dark mode transition is smooth
- [ ] No lag or stuttering
- [ ] Animations feel natural

### 7.5 Keyboard Navigation
- [ ] Tab moves through inputs
- [ ] Enter submits forms
- [ ] Escape closes panels
- [ ] Arrow keys work in dropdowns (if present)

### 7.6 Copy to Clipboard
- [ ] Copy button shows feedback
- [ ] Text actually copies
- [ ] Notification appears
- [ ] Works in all browsers

---

## 8. ERROR HANDLING & EDGE CASES

### 8.1 Empty States
- [ ] Empty Favorites: shows helpful message
- [ ] Empty History: shows helpful message
- [ ] No search results: shows "No results found"
- [ ] All analytics: handle zero queries gracefully

### 8.2 Large Data
- [ ] Long query text truncates/wraps
- [ ] Many tags display properly
- [ ] Many favorites load without lag
- [ ] Large history doesn't cause slowdown
- [ ] Charts handle large numbers

### 8.3 Invalid Input
- [ ] Invalid tag characters handled
- [ ] Whitespace trimmed
- [ ] Empty query rejected with message
- [ ] Invalid JSON handled gracefully
- [ ] Corrupted localStorage handled

### 8.4 Browser Compatibility
- [ ] Chrome: all features work
- [ ] Firefox: all features work
- [ ] Safari: all features work
- [ ] Edge: all features work
- [ ] Mobile browsers: all features work

### 8.5 localStorage Quota
- [ ] If localStorage full: graceful degradation
- [ ] Show message to user
- [ ] Don't crash application
- [ ] Offer to clear old data

---

## 9. INTEGRATION TESTS

### 9.1 Save & Re-run Workflow
- [ ] Execute query in chat
- [ ] Save as favorite with tags
- [ ] Navigate to Favorites panel
- [ ] Click re-run on favorite
- [ ] Query executes and shows results
- [ ] Result appears in History
- [ ] Favorite still saved

### 9.2 History to Favorites Workflow
- [ ] Execute several queries
- [ ] Open History panel
- [ ] Mark one as favorite
- [ ] Open Favorites panel
- [ ] Query appears in Favorites
- [ ] Tags can be added/edited
- [ ] Query appears in both panels

### 9.3 Query Builder Workflow
- [ ] Open Query Builder
- [ ] Load a template
- [ ] Modify parameters
- [ ] Click Apply
- [ ] Query sends to chat
- [ ] Results appear
- [ ] Query appears in History

### 9.4 Analytics Workflow
- [ ] Execute multiple queries
- [ ] Open Analytics panel
- [ ] Check metrics update
- [ ] Line chart shows activity
- [ ] Pie chart shows keywords
- [ ] Execute more queries
- [ ] Charts update in real-time

### 9.5 Dark Mode Workflow
- [ ] Toggle dark mode
- [ ] Open each panel
- [ ] Verify styling in each:
  - [ ] Favorites
  - [ ] History
  - [ ] Query Builder
  - [ ] Analytics
- [ ] Toggle back to light
- [ ] All panels still styled correctly

---

## 10. PERFORMANCE

### 10.1 Load Time
- [ ] Frontend loads in < 3 seconds
- [ ] Initial page interactive in < 2 seconds
- [ ] Panels open in < 100ms
- [ ] No jank or stuttering

### 10.2 Panel Operations
- [ ] Search filters instantly (< 100ms)
- [ ] Tag filter updates < 100ms
- [ ] Sort/reorder < 50ms
- [ ] Copy button feedback instant

### 10.3 Charts & Calculations
- [ ] Analytics calculations < 200ms
- [ ] Chart rendering < 300ms
- [ ] No lag when adding data
- [ ] Smooth animations

### 10.4 localStorage Operations
- [ ] Save favorite < 10ms
- [ ] Load favorites < 50ms
- [ ] No UI blocking
- [ ] Async operations where appropriate

---

## Test Results Summary

### Issues Found
1. [ ] No critical issues
2. [ ] No high-priority issues
3. [ ] No medium-priority issues
4. [ ] No low-priority issues

### Component Status
- [ ] Favorites Panel: ✅ PASS / ⚠️ NEEDS WORK / ❌ FAIL
- [ ] History Panel: ✅ PASS / ⚠️ NEEDS WORK / ❌ FAIL
- [ ] Query Builder: ✅ PASS / ⚠️ NEEDS WORK / ❌ FAIL
- [ ] Analytics Dashboard: ✅ PASS / ⚠️ NEEDS WORK / ❌ FAIL
- [ ] Chat Interface: ✅ PASS / ⚠️ NEEDS WORK / ❌ FAIL
- [ ] Dark Mode: ✅ PASS / ⚠️ NEEDS WORK / ❌ FAIL
- [ ] Data Persistence: ✅ PASS / ⚠️ NEEDS WORK / ❌ FAIL

### Overall Result
**Status**: ⏳ Testing in Progress

---

## Notes
- Testing environment: Windows 11, Chrome/Firefox
- Backend status: Starting/installing dependencies
- Frontend status: Running on port 3000
- All components built with TypeScript strict mode
- Zero compilation errors

