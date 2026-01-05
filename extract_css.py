#!/usr/bin/env python3
"""
CSS Extraction Script
Extracts embedded CSS from Jinja2 templates and creates external CSS files
"""

import os
import re
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

TEMPLATES_DIR = BASE_DIR / 'stocks' / 'templates' / 'stocks'
CSS_DIR = BASE_DIR / 'stocks' / 'static' / 'css'
PAGES_DIR = CSS_DIR / 'pages'

# Ensure directories exist
CSS_DIR.mkdir(parents=True, exist_ok=True)
PAGES_DIR.mkdir(parents=True, exist_ok=True)


def extract_css_from_template(template_path):
    """Extract CSS content from a template file"""
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all <style> tags and their content
    style_pattern = r'<style>(.*?)</style>'
    matches = re.findall(style_pattern, content, re.DOTALL)
    
    if matches:
        return '\n'.join(matches)
    return None


def extract_chat_widget_css():
    """Extract CSS from chat widget template"""
    print("Extracting chat widget CSS...")
    template_path = TEMPLATES_DIR / '_chat_widget.j2'
    css_content = extract_css_from_template(template_path)
    
    if css_content:
        output_path = CSS_DIR / 'chat-widget.css'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("/* ========================================\n")
            f.write("   CHAT WIDGET STYLES\n")
            f.write("   Extracted from _chat_widget.j2\n")
            f.write("   ======================================== */\n\n")
            f.write(css_content)
        print(f"✅ Created {output_path}")
        return True
    return False


def update_chat_widget_template():
    """Update chat widget template to use external CSS"""
    print("Updating chat widget template...")
    template_path = TEMPLATES_DIR / '_chat_widget.j2'
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace <style>...</style> with link to external CSS
    style_pattern = r'<style>.*?</style>'
    replacement = '''{% load static %}
<link rel="stylesheet" href="{% static 'css/chat-widget.css' %}">'''
    
    updated_content = re.sub(style_pattern, replacement, content, flags=re.DOTALL)
    
    # Backup original
    backup_path = template_path.parent / f'{template_path.stem}_backup{template_path.suffix}'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📦 Backed up to {backup_path}")
    
    # Write updated content
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    print(f"✅ Updated {template_path}")


def update_styles_template():
    """Update _styles.j2 to reference external CSS files"""
    print("Updating _styles.j2 template...")
    template_path = TEMPLATES_DIR / '_styles.j2'
    
    new_content = '''{% load static %}
<link rel="stylesheet" href="{% static 'css/base.css' %}">
<link rel="stylesheet" href="{% static 'css/components.css' %}">
'''
    
    # Backup original
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    backup_path = template_path.parent / f'{template_path.stem}_backup{template_path.suffix}'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📦 Backed up to {backup_path}")
    
    # Write new content
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"✅ Updated {template_path}")


def main():
    """Main execution"""
    print("=" * 60)
    print("CSS EXTRACTION AND REFACTORING")
    print("=" * 60)
    print()
    
    # Extract chat widget CSS
    extract_chat_widget_css()
    print()
    
    # Update templates
    print("UPDATING TEMPLATES")
    print("-" * 60)
    update_chat_widget_template()
    print()
    update_styles_template()
    print()
    
    print("=" * 60)
    print("✅ CSS REFACTORING COMPLETE!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Test all pages to ensure styles load correctly")
    print("2. Run: python manage.py collectstatic")
    print("3. Check browser console for any CSS loading errors")
    print()


if __name__ == '__main__':
    main()
