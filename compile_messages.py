"""
Compile translation files (.po to .mo) using polib
This is a workaround for when GNU gettext tools are not installed
"""
import polib
import os
from pathlib import Path

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent
LOCALE_DIR = BASE_DIR / 'locale'

def compile_translations():
    """Compile all .po files to .mo files"""
    languages = ['hi', 'mr']
    
    for lang in languages:
        po_file = LOCALE_DIR / lang / 'LC_MESSAGES' / 'django.po'
        mo_file = LOCALE_DIR / lang / 'LC_MESSAGES' / 'django.mo'
        
        if po_file.exists():
            print(f"Compiling {lang}... ", end='')
            try:
                po = polib.pofile(str(po_file))
                po.save_as_mofile(str(mo_file))
                print(f"✓ Created {mo_file}")
            except Exception as e:
                print(f"✗ Error: {e}")
        else:
            print(f"✗ {po_file} not found")

if __name__ == '__main__':
    print("=" * 60)
    print("Compiling Translation Files")
    print("=" * 60)
    compile_translations()
    print("\n✓ Translation compilation complete!")
