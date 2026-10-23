# Favorites Panel - Test Verification Guide

**Date:** 2026-10-23  
**Status:** Ready for Testing  
**Commit:** c009fe6

---

## Quick Test (5 minutes)

Follow these steps to verify the fix works:

### 1. Restart Frontend Server
```bash
# In frontend directory
npm run dev
# Should start on http://localhost:3000
```

### 2. Refresh Browser
- Open http://localhost:3000 in browser
- Press **Ctrl+F5** to do a hard refresh (clear cache)
- Verify page loads without errors

### 3. Send a Query
- Type: "How many orders were placed in the last 30 days?"
- Press Enter or click Send
- Wait for results to display (should take 3-5 seconds)
- Verify chart and SQL query appear

### 4. Add to Favorites
- Click the star icon (☆) in the Visualization section
- "Save to Favorites" form should appear
- Click "Add to Favorites" button
- **Check 1:** Star should become filled (★)
- **Check 2:** Click Favorites icon in left sidebar (heart icon)
- **Check 3:** Your query should appear in the Favorites Panel

### 5. Verify Persistence
- Close Favorites Panel (click button again or outside)
- Send a different query
- Star icon should be empty (☆) for new query
- Click Favorites icon again
- Your first query should still be there

### 6. Remove from Favorites
- Click star (★) of your favorite query
- "Remove from Favorites" button should appear
- Click it
- **Check:** Star becomes empty (☆) again
- **Check:** Query disappears from Favorites Panel

---

## Detailed Test Checklist

### Section A: Basic Functionality

- [ ] **A1** - App loads without errors in browser console
- [ ] **A2** - Can send a query and get results
- [ ] **A3** - Star icon appears on assistant message
- [ ] **A4** - Clicking star opens save form

### Section B: Add to Favorites (PRIMARY FIX)

- [ ] **B1** - "Add to Favorites" button is clickable
- [ ] **B2** - After clicking, star becomes filled (★)
- [ ] **B3** - Favorites Panel now shows the query
- [ ] **B4** - Query text is correct and complete
- [ ] **B5** - Query is still there after panel closes/reopens
- [ ] **B6** - Multiple queries can be added to favorites
- [ ] **B7** - Favorites count in header increases

### Section C: Remove from Favorites

- [ ] **C1** - Clicking filled star (★) shows "Remove from Favorites" button
- [ ] **C2** - Clicking remove button changes star to empty (☆)
- [ ] **C3** - Query disappears from Favorites Panel
- [ ] **C4** - Favorites count decreases correctly

### Section D: Tags (Uses Favorites Internally)

- [ ] **D1** - "Add a tag..." field appears after favoriting
- [ ] **D2** - Can type tag name and press Enter
- [ ] **D3** - Tag appears as pill under query in Favorites Panel
- [ ] **D4** - Can add multiple tags to same query
- [ ] **D5** - Tag filtering works (click tag to filter)
- [ ] **D6** - Clear tags returns to full list

### Section E: Search & Filter

- [ ] **E1** - Search field in Favorites Panel works
- [ ] **E2** - Typing query text filters favorites
- [ ] **E3** - Search is case-insensitive
- [ ] **E4** - Partial matches work (typing "order" finds "How many orders")
- [ ] **E5** - Clearing search shows all favorites again

### Section F: Persistence (LocalStorage)

- [ ] **F1** - Refresh page (Ctrl+F5)
- [ ] **F2** - All favorites still appear
- [ ] **F3** - Stars are still filled (★) for favorited queries
- [ ] **F4** - Tags are preserved after refresh
- [ ] **F5** - Close browser tab and reopen
- [ ] **F6** - Favorites are still there (localStorage persisted)

### Section G: Dark Mode

- [ ] **G1** - Toggle dark mode button in header
- [ ] **G2** - Favorites Panel background changes color
- [ ] **G3** - Text remains readable in both light and dark modes
- [ ] **G4** - Favorites Panel colors match chat interface theme
- [ ] **G5** - All buttons/icons visible in both modes

### Section H: Edge Cases

- [ ] **H1** - Send query with special characters: "What's the top 5?"
  - Verify: Can favorite and retrieve correctly
- [ ] **H2** - Send very long query (50+ words)
  - Verify: Query displays in full in Favorites Panel
- [ ] **H3** - Add maximum tags (10+) to single query
  - Verify: All tags display and filter works
- [ ] **H4** - Have no favorites in panel
  - Verify: "No favorites yet..." message displays
- [ ] **H5** - Have 20+ favorites
  - Verify: Panel scrolls and displays all
  - Verify: Search/filter still works efficiently

---

## Test Results Template

### Date: _____________
### Tester: _____________
### Environment: 
- [ ] Windows [ ] Mac [ ] Linux
- Browser: _____________
- Backend: Running [ ] Not Running

### Quick Test (5 min)
Result: [ ] PASS [ ] FAIL  
Notes: _________________________________________________________________

### Full Checklist
- Section A (Basic): [ ] PASS [ ] FAIL (failures: ___)
- Section B (Add): [ ] PASS [ ] FAIL (failures: ___)
- Section C (Remove): [ ] PASS [ ] FAIL (failures: ___)
- Section D (Tags): [ ] PASS [ ] FAIL (failures: ___)
- Section E (Search): [ ] PASS [ ] FAIL (failures: ___)
- Section F (Persist): [ ] PASS [ ] FAIL (failures: ___)
- Section G (Dark): [ ] PASS [ ] FAIL (failures: ___)
- Section H (Edge): [ ] PASS [ ] FAIL (failures: ___)

### Overall Result
[ ] FULLY WORKING - All tests pass
[ ] MOSTLY WORKING - Minor issues only
[ ] BROKEN - Critical functionality broken

### Issues Found
1. ___________________________________________________________________
2. ___________________________________________________________________
3. ___________________________________________________________________

### Sign-Off
Tester: _________________________ Date: _____________
Status: [ ] Approved [ ] Needs Fixes [ ] Blocked

---

## Troubleshooting

### Issue: Favorites still empty after clicking "Add to Favorites"

**Checks:**
1. Did you see the star change to filled (★)? If no, fix didn't load.
   - Solution: Restart frontend `npm run dev` and refresh page Ctrl+F5
2. Is backend running? Check `http://localhost:8000/health`
   - If not running: Start with `python -m uvicorn main:app --reload`
3. Any errors in browser console? Check browser dev tools (F12)
   - Check Network tab to see if request succeeded
4. Check browser localStorage is enabled
   - DevTools → Application → Local Storage

### Issue: Star changes to filled but then changes back to empty

**Possible causes:**
1. Page is refreshing/reloading unintentionally
   - Check if there's an error causing reload
2. Multiple instances of the app running
   - Close all browser tabs and clear cache
3. LocalStorage not working
   - Check privacy settings or incognito mode

### Issue: TypeScript build errors after pulling changes

**Solution:**
```bash
cd frontend
npm install  # Reinstall dependencies
npm run build  # Rebuild
npm run dev  # Run dev server
```

### Issue: Star icon not appearing on assistant messages

**Checks:**
1. Is message an assistant message? (Check: should be on left side, gray background)
2. Is there a chart/visualization? Star appears in visualization section
3. Check console for JavaScript errors
4. Try restarting frontend server: `npm run dev`

---

## Performance Notes

- Favorites stored in browser localStorage (not backend)
- Max 50 favorites enforced by useFavorites hook
- Max 20 history items enforced by useFavorites hook
- Search/filter operations are in-memory (instant)
- No database queries needed for favorites operations

---

## Related Files

- **Implementation:** `frontend/app/store.ts`, `frontend/app/ChatInterface.tsx`, `frontend/app/ChatMessage.tsx`
- **Logic:** `frontend/app/hooks/useFavorites.ts`
- **UI:** `frontend/app/components/FavoritesPanel.tsx`
- **Bug Details:** `dev_docs/FAVORITES_PANEL_FIX.md`

---

## Success Criteria

✅ **All Criteria Must Be Met:**
1. Clicking "Add to Favorites" adds query to Favorites Panel (not empty)
2. Query text is complete and correct
3. Star icon fills (★) after adding
4. Favorites persist after closing panel
5. Favorites persist after page refresh
6. Can remove favorites by clicking filled star
7. Multiple favorites can be managed simultaneously
8. Tags can be added to favorites
9. Search/filter work on favorites
10. Works in both light and dark modes
