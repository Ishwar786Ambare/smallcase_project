# Debug Instructions for AI Response Issue

## Problem
AI responses are not coming through when user sends messages in AI support chat.

## Debug Steps

### 1. Open Browser Console (F12)
When you send a message in AI support chat, check for these console logs:

**Expected logs:**
```
Getting AI response for AI support chat
supportType: ai
currentGroupType: support
```

**If you see:**
```
Skipping AI response - supportType: admin groupType: support
```
→ Problem: supportType is 'admin' instead of 'ai'

**If you see:**
```
Skipping AI response - supportType: ai groupType: group
```
→ Problem: currentGroupType is wrong

### 2. Check localStorage
In browser console, run:
```javascript
localStorage.getItem('preferredSupportType')
```

**Should return:** `"ai"` if you selected AI Assistant
**Should return:** `null` if first time

### 3. Check JavaScript Variables
In browser console, while chat is open, run:
```javascript
console.log('supportType:', supportType);
console.log('currentGroupType:', currentGroupType);
console.log('currentGroupId:', currentGroupId);
```

**For AI support, should show:**
```
supportType: "ai"
currentGroupType: "support"  
currentGroupId: <some number>
```

### 4. Check if selectSupportType is Called
When you click "AI Assistant" button, you should see:
```
AI Assistant selected
supportType saved: ai
```

### 5. Common Issues & Fixes

**Issue 1: supportType is undefined or null**
Fix: Clear localStorage and reload
```javascript
localStorage.clear();
location.reload();
```

**Issue 2: selectSupportType function not found**
Fix: Hard refresh browser
- Chrome: Ctrl + Shift + R
- Or: Clear cache and reload

**Issue 3: getAIResponse function errors**
Check console for:
- CSRF token errors
- 403 Forbidden
- Network errors

**Issue 4: AI endpoint not responding**
Check if `/api/ai/chat/` exists:
```javascript
fetch('/api/ai/chat/', {method: 'POST', headers: {'Content-Type': 'application/json'}})
  .then(r => console.log('Status:', r.status))
```

Should return: `Status: 403` (because no CSRF, but endpoint exists)
If `404`: Backend route missing

### 6. Quick Fix Script
Run this in browser console to force AI mode:
```javascript
// Force AI support type
supportType = 'ai';
currentGroupType = 'support';
localStorage.setItem('preferredSupportType', 'ai');
console.log('Forced AI mode. Try sending a message now.');
```

### 7. Check Backend
If frontend looks good, check Django console for:
```
AI Chat - User: <email>, ID: <id>
AI Chat - User has X baskets
```

If you don't see these logs, the `/api/ai/chat/` view isn't being called.

---

## Most Likely Issues

1. **LocalStorage has wrong value** → Clear it
2. **Cache issue** → Hard refresh (Ctrl+Shift+R)
3. **selectSupportType not executed** → Check if function exists
4. **currentGroupType is 'group' not 'support'** → Check group creation

---

## Test Sequence

1. Clear localStorage: `localStorage.clear()`
2. Reload page
3. Open chat widget
4. Should see support type selector
5. Click "AI Assistant"
6. Console should log: "AI mode selected"
7. Send message: "test"
8. Console should log: "Getting AI response for AI support chat"
9. AI should respond

If step 8 doesn't happen → Run debug steps above.
