## Debugging AI Chat Issue

### Steps to Debug:

1. **Open your browser and navigate to:** `http://localhost:1234/`

2. **Open the browser developer console:**
   - Press `F12` or
   - Right-click → Inspect → Console tab

3. **Open the chat widget:**
   - Click the chat button in the bottom right corner

4. **Check the AI toggle:**
   - Make sure the toggle is set to AI (the 🤖 icon should be visible/highlighted)
   - If not, click the toggle to switch to AI mode

5. **Send a test message:**
   - Type "Hello" and press Enter

6. **Watch the console logs carefully**. You should see:
   ```
   💬 Loaded chat - Group ID: X, AI-only: true, Support type: ai
   🔍 AI Check - isAIOnly: true, supportType: ai, currentGroupType: support
   ✅ Calling AI - conditions met!
   🤖 getAIResponse called with message: Hello
   📡 Calling /api/ai/chat/ endpoint...
   📡 Response status: 200
   📡 Response data: {success: true, response: "..."}
   ✅ AI response received, saving to chat...
   💾 Save response: {success: true, ...}
   ```

### What to Look For:

#### If you see `❌ Skipping AI - isAIOnly: false`
- The frontend is getting `is_ai_only=false` from the backend
- **Check:** The support_type parameter is being passed correctly

#### If you see `🤖 getAIResponse called` but then an error:
- The AI endpoint is being called but failing
- **Check the error message** in the console

#### If `/api/ai/chat/` returns an error:
- **Check the Django terminal** for backend errors
- Possible issues:
  - Missing GROQ_API_KEY environment variable
  - Groq API connection issues
 - Invalid API key

#### If the response says `success: false`:
- **Check the error field** in the response data
- **Check Django terminal** for Python errors

### Quick Test Commands:

**Check if GROQ_API_KEY is set:**
```powershell
$env:GROQ_API_KEY
```

**If not set, set it (replace with your actual key):**
```powershell
$env:GROQ_API_KEY = "your_groq_api_key_here"
```

**Then restart the Django server:**
- Stop the current server (Ctrl+C in the terminal)
- Run: `.\venv\Scripts\python.exe manage.py runserver 1234`

### Common Issues & Fixes:

1. **Environment variable not set:** Set GROQ_API_KEY as shown above
2. **Wrong toggle state:** Make sure AI toggle is ON  (🤖 should be visible)
3. **Old cached chat:** Click the toggle to switch to Human, then back to AI to create a fresh AI-only chat
4. **Browser cache:** Hard refresh the page (Ctrl+Shift+R)

### Report Back:

Please copy and paste:
1. **All console logs** from the browser console (especially the lines starting with emoji)
2. **Any error messages** from the Django terminal
3. **The response from `/api/ai/chat/`** (you can see this in the Network tab → click on `chat/` → Response)
