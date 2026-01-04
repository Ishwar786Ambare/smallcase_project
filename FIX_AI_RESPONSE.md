# 🔍 AI Response Debugging - Step by Step

## Issue
AI responses are not appearing when you send messages in AI support chat.

---

## ✅ Quick Test Instructions

### Step 1: Clear Everything
1. Open browser console (`F12` → Console tab)
2. Run this command:
```javascript
localStorage.clear();
location.reload();
```

### Step 2: Open Chat Widget
1. Click the chat button (💬) in bottom right
2. You should see a **choice screen** with two buttons:
   - 🤖 AI Assistant
   - 👨‍💼 Human Support

### Step 3: Select AI Assistant
1. Click "AI Assistant" button
2. **CHECK CONSOLE** - You should see:
```
🎯 selectSupportType called with type: ai
✅ supportType set to: ai | localStorage: ai
```

### Step 4: Send a Test Message
1. Type: "hello"
2. Press Enter
3. **CHECK CONSOLE** - You should see:
```
🔍 AI Check - supportType: ai currentGroupType: support
✅ Calling AI - conditions met!
```

### Step 5: Check AI Response
- AI should respond within 2-3 seconds
- If not, check console for errors

---

## 🐛 If AI Still Doesn't Respond

### Check 1: Console Logs
**What you should see:**
```
🎯 selectSupportType called with type: ai
✅ supportType set to: ai | localStorage: ai
🔍 AI Check - supportType: ai currentGroupType: support
✅ Calling AI - conditions met!
```

**If you see ❌ Skipping AI:**
Look at the reason printed below it.

### Check 2: Common Issues

**Issue A: "Reason: supportType is not 'ai'"**
```javascript
// Fix: Manually set it
supportType = 'ai';
localStorage.setItem('preferredSupportType', 'ai');
```

**Issue B: "Reason: currentGroupType is not 'support'"**
```javascript
// Check what it is
console.log('currentGroupType:', currentGroupType);
// It might be 'group' or something else
// Try refreshing and selecting AI again
```

**Issue C: No console logs at all**
- Hard refresh: `Ctrl + Shift + R`
- Clear cache completely
- Restart browser

### Check 3: Verify AI Endpoint
Run this in console:
```javascript
fetch('/api/ai/chat/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.cookie.split('csrftoken=')[1]?.split(';')[0]
    },
    body: JSON.stringify({message: 'test'})
})
.then(r => r.json())
.then(d => console.log('AI Response:', d))
.catch(e => console.error('AI Error:', e));
```

**Expected:** Some response (even if error about user context)
**Bad:** 404 Not Found (endpoint missing)

### Check 4: Django Console
In your terminal where Django is running, you should see:
```
AI Chat - User: <email>, ID: <id>
AI Chat - User has X baskets
```

If you don't see this, the frontend isn't calling the backend.

---

## 🎯 Force AI Mode (Emergency Fix)

If nothing works, run this in browser console:
```javascript
// Force AI mode
window.supportType = 'ai';
window.currentGroupType = 'support';
localStorage.setItem('preferredSupportType', 'ai');

// Override the check function temporarily
const originalGetAI = window.getAIResponse || getAIResponse;
window.getAIResponse = function(msg) {
    console.log('🚨 FORCE: Getting AI response for:', msg);
    return originalGetAI(msg);
};

console.log('✅ AI mode FORCED. Try sending a message.');
```

Then send a message - AI should respond.

---

## 📊 Expected Full Console Log Sequence

When everything works correctly:

```
1. User clicks "AI Assistant":
   🎯 selectSupportType called with type: ai
   ✅ supportType set to: ai | localStorage: ai

2. User sends message "hello":
   🔍 AI Check - supportType: ai currentGroupType: support
   ✅ Calling AI - conditions met!

3. AI processes:
   [AI Service] generate_response called for user: user@email.com
   [AI Service] Found 0 baskets for user...

4. AI responds:
   (Message appears in chat)
```

---

## 🔧 Still Not Working?

1. **Take screenshot of console logs** and share them
2. **Check Django terminal** - any errors?
3. **Try in incognito/private window** - cache issue?
4. **Check browser:** Works in Chrome? Try Firefox?

---

## ✨ Quick Checks Summary

| Check | Command | Expected Result |
|-------|---------|-----------------|
| localStorage | `localStorage.getItem('preferredSupportType')` | `"ai"` |
| supportType | Check console when sending message | `"ai"` |
| currentGroupType | Check console when sending message | `"support"` |
| AI endpoint | `fetch('/api/ai/chat/')` | Not 404 |
| Console logs | Send message | Should see 🔍 and ✅ emojis |

---

**After following these steps, AI responses should work!** 🎉
