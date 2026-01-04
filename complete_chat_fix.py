#!/usr/bin/env python3
"""
Script to complete the chat support fix by adding missing code snippets.
Run this to finalize the separation of AI and Admin support.
"""

import re

def fix_chat_widget():
    file_path = "stocks/templates/stocks/_chat_widget.j2"
    
    print("Reading chat widget file...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Add CSS styles
    print("Adding CSS styles...")
    css_to_add = """
    /* ===== Support Type Selection Panel ===== */
    .support-type-panel {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: var(--container-bg, #ffffff);
        z-index: 10;
        display: flex;
        flex-direction: column;
    }

    html[data-theme="dark"] .support-type-panel {
        background: #1e293b;
    }

    .support-options {
        flex: 1;
        padding: 30px 20px;
        display: flex;
        flex-direction: column;
        gap: 20px;
        justify-content: center;
    }

    .support-option-btn {
        background: var(--card-bg, #f9fafb);
        border: 2px solid var(--border-color, #e5e7eb);
        border-radius: 16px;
        padding: 24px 20px;
        cursor: pointer;
        transition: all 0.3s;
        text-align: center;
    }

    html[data-theme="dark"] .support-option-btn {
        background: #0f172a;
        border-color: #334155;
    }

    .support-option-btn:hover {
        transform: scale(1.02);
        border-color: #667eea;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.2);
    }

    .support-option-btn .option-icon {
        font-size: 48px;
        display: block;
        margin-bottom: 12px;
    }

    .support-option-btn h3 {
        margin: 0 0 8px 0;
        color: var(--text-primary, #333);
        font-size: 18px;
    }

    html[data-theme="dark"] .support-option-btn h3 {
        color: #e2e8f0;
    }

    .support-option-btn p {
        margin: 0;
        color: var(--text-secondary, #666);
        font-size: 13px;
    }

    .support-option-btn .badge {
        display: inline-block;
        margin-top: 12px;
        padding: 4px 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
    }
"""
    
    # Find </style> and insert before it
    content = content.replace('</style>', css_to_add + '\n</style>')
    
    # 2. Update closeAllPanels function
    print("Updating closeAllPanels function...")
    old_close_all = r"function closeAllPanels\(\) {[^}]+}"
    new_close_all = """function closeAllPanels() {
        groupsPanel.style.display = 'none';
        createGroupPanel.style.display = 'none';
        membersPanel.style.display = 'none';
        supportTypePanel.style.display = 'none';
    }"""
    content = re.sub(old_close_all, new_close_all, content, flags=re.DOTALL)
    
    # 3. Add new functions after closeAllPanels
    print("Adding support type selection functions...")
    functions_to_add = """
    
    // Show Support Type Selector
    function showSupportTypeSelector() {
        closeAllPanels();
        supportTypePanel.style.display = 'flex';
    }
    
    // Select Support Type
    function selectSupportType(type) {
        supportType = type;
        localStorage.setItem('preferredSupportType', type);
        currentGroupId = null;
        if (type === 'ai') {
            updateHeader('AI Assistant', '🤖');
        } else {
            updateHeader('Human Support', '👨‍💼');
        }
        closeAllPanels();
        loadMessages();
    }
    
    // Switch Support Type
    function switchSupportType() {
        localStorage.removeItem('preferredSupportType');
        currentGroupId = null;
        showSupportTypeSelector();
    }
"""
    
    # Insert after closeAllPanels function
    content = content.replace(
        new_close_all + '\r\n    \r\n    // Escape HTML',
        new_close_all + functions_to_add + '\r\n    // Escape HTML'
    )
    
    # 4. Add event listeners
    print("Adding event listeners...")
    listeners_to_add = """
    
    // Support Type Selection Listeners
    aiSupportBtn.addEventListener('click', () => selectSupportType('ai'));
    adminSupportBtn.addEventListener('click', () => selectSupportType('admin'));
    switchSupportBtn.addEventListener('click', switchSupportType);
"""
    
    # Find a good place to add listeners (after closeCreatePanel listener)
    content = content.replace(
        "closeCreatePanel.addEventListener('click', () => {",
        listeners_to_add + "\r\n    closeCreatePanel.addEventListener('click', () => {"
    )
    
    # Save the modified file
    print("Saving modified file...")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Chat widget fix completed successfully!")
    print("\nWhat was done:")
    print("1. Added CSS styles for support type selection panel")
    print("2. Updated closeAllPanels to include supportTypePanel")
    print("3. Added showSupportTypeSelector() function")
    print("4. Added selectSupportType(type) function")
    print("5. Added switchSupportType() function")
    print("6. Added event listeners for support type buttons")
    print("\nTest the chat widget in your browser!")

if __name__ == "__main__":
    try:
        fix_chat_widget()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nManual fix required. Please see CHAT_SUPPORT_FIX.md for instructions.")
