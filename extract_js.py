#!/usr/bin/env python3
"""
JavaScript Extraction Script
Extracts embedded JavaScript from Jinja2 templates and creates external JS files
"""

import os
import re
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

TEMPLATES_DIR = BASE_DIR / 'stocks' / 'templates' / 'stocks'
JS_DIR = BASE_DIR / 'stocks' / 'static' / 'js'
PAGES_DIR = JS_DIR / 'pages'

# Ensure directories exist
JS_DIR.mkdir(parents=True, exist_ok=True)
PAGES_DIR.mkdir(parents=True, exist_ok=True)


def extract_js_from_template(template_path):
    """Extract JavaScript content from a template file"""
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all <script> tags and their content (excluding script tags with src attribute)
    # Pattern: <script> ... </script> but NOT <script src="...">
    script_pattern = r'<script(?!\s+src)(?:\s+[^>]*)?>(.+?)</script>'
    matches = re.findall(script_pattern, content, re.DOTALL | re.IGNORECASE)
    
    if matches:
        return '\n\n// ==========================================\n\n'.join(matches)
    return None


def extract_and_save_js(template_name, output_name, is_component=False):
    """Extract JavaScript from a template and save to file"""
    template_path = TEMPLATES_DIR / template_name
    if not template_path.exists():
        print(f"⚠️  Template not found: {template_path}")
        return False
    
    print(f"Extracting JavaScript from {template_name}...")
    js_content = extract_js_from_template(template_path)
    
    if js_content:
        # Determine output path
        if is_component:
            output_path = JS_DIR / output_name
        else:
            output_path = PAGES_DIR / output_name
        
        # Add header comment
        header = f"""/* ========================================
   {output_name.upper().replace('.JS', '')} - JavaScript
   Extracted from {template_name}
   ======================================== */

"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(header)
            f.write(js_content)
        
        print(f"✅ Created {output_path}")
        return True
    else:
        print(f"ℹ️  No JavaScript found in {template_name}")
        return False


def update_template_js_reference(template_name, js_file, is_component=False):
    """Update template to use external JavaScript file"""
    template_path = TEMPLATES_DIR / template_name
    
    if not template_path.exists():
        print(f"⚠️  Template not found: {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    backup_path = template_path.parent / f'{template_path.stem}_js_backup{template_path.suffix}'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📦 Backed up {template_name} to {backup_path.name}")
    
    # Remove all <script> tags without src attribute
    script_pattern = r'<script(?!\s+src)(?:\s+[^>]*)?>.*?</script>'
    updated_content = re.sub(script_pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Add reference to external JS file at the end (before </body> if exists, otherwise at end)
    if is_component:
        js_ref = f'<script src="{{{{ static(\'js/{js_file}\') }}}}"></script>'
    else:
        js_ref = f'<script src="{{{{ static(\'js/pages/{js_file}\') }}}}"></script>'
    
    # Try to insert before </body>, otherwise append at end
    if '</body>' in updated_content or '</BODY>' in updated_content:
        updated_content = re.sub(
            r'(</body>)',
            f'{js_ref}\n\\1',
            updated_content,
            flags=re.IGNORECASE
        )
    else:
        # Just append at the end
        updated_content = updated_content.rstrip() + f'\n\n{js_ref}\n'
    
    # Write updated content
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✅ Updated {template_name} to reference {js_file}")
    return True


def main():
    """Main execution"""
    print("=" * 70)
    print("JAVASCRIPT EXTRACTION AND REFACTORING")
    print("=" * 70)
    print()
    
    # Define extractions: (template_name, output_js_name, is_component)
    extractions = [
        # Page-specific JavaScript
        ('home.j2', 'home.js', False),
        ('basket_detail.j2', 'basket-detail.js', False),
        ('basket_create.j2', 'basket-create.js', False),
        ('contact.j2', 'contact.js', False),
        
        # Component JavaScript
        ('_chat_widget.j2', 'chat-widget.js', True),
        ('_language_switcher.j2', 'language-switcher.js', True),
        ('_theme_toggle.j2', 'theme-toggle.js', True),
        ('_scripts.j2', 'common.js', True),
    ]
    
    print("EXTRACTING JAVASCRIPT")
    print("-" * 70)
    for template_name, js_name, is_component in extractions:
        extract_and_save_js(template_name, js_name, is_component)
        print()
    
    print("=" * 70)
    print("UPDATING TEMPLATES")
    print("-" * 70)
    for template_name, js_name, is_component in extractions:
        # Skip _scripts.j2 as it's a special case (already references common scripts)
        if template_name == '_scripts.j2':
            continue
        update_template_js_reference(template_name, js_name, is_component)
        print()
    
    print("=" * 70)
    print("✅ JAVASCRIPT REFACTORING COMPLETE!")
    print("=" * 70)
    print()
    print("Created files:")
    print("  - stocks/static/js/common.js              (Core utilities & theme)")
    print("  - stocks/static/js/chat-widget.js         (Chat widget logic)")
    print("  - stocks/static/js/language-switcher.js   (Language switching)")
    print("  - stocks/static/js/theme-toggle.js        (Theme toggle)")
    print("  - stocks/static/js/pages/home.js          (Home page)")
    print("  - stocks/static/js/pages/basket-detail.js (Basket detail)")
    print("  - stocks/static/js/pages/basket-create.js (Basket create)")
    print("  - stocks/static/js/pages/contact.js       (Contact form)")
    print()
    print("Next steps:")
    print("1. Test all pages to ensure functionality works")
    print("2. Check browser console for any JavaScript errors")
    print("3. Run: python manage.py collectstatic (for production)")
    print()


if __name__ == '__main__':
    main()
