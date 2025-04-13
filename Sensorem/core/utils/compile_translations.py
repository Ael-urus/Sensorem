import os
import subprocess
from pathlib import Path

LOCALE_DIR = Path('../locale')

for lang in os.listdir(LOCALE_DIR):
    lang_dir = LOCALE_DIR / lang / 'LC_MESSAGES'
    po_file = lang_dir / 'messages.po'
    mo_file = lang_dir / 'messages.mo'

    if po_file.exists():
        subprocess.run([
            'msgfmt',
            str(po_file),
            '-o',
            str(mo_file)
        ])