#!/usr/bin/env python3
"""Quick fix to add missing support type functions"""

file_path = "stocks/templates/stocks/_chat_widget.j2"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with "// Escape HTML" 
insert_position = None
for i, line in enumerate(lines):
    if '// Escape HTML' in line and i > 1500:  # Make sure we're in the right section
        insert_position = i
        break

if insert_position:
    # Functions to insert before "// Escape HTML"
    new_functions = """    
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
    
    # Insert the functions
    lines.insert(insert_position, new_functions)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Added missing support type functions!")
    print(f"   Inserted at line {insert_position + 1}")
else:
    print("❌ Could not find insertion point")
