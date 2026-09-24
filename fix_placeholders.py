"""
Script untuk fix placeholder %s → ? di file Python.
Ganti otomatis semua file yang masih pakai placeholder MySQL.

Jalankan: python fix_placeholders.py
"""
import os
import re
from pathlib import Path


def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Ganti placeholder %s → ? (hanya dalam string SQL)
    # Cari pattern "(%s)" atau "%s," atau "%s)"
    # Tidak semua %s, hanya yang dalam konteks SQL query
    # Strategi: cari string di dalam triple-quoted atau single-quoted
    # yang mengandung INSERT/UPDATE/DELETE/SELECT

    def replace_placeholder(text):
        # Cari semua string literal yang mengandung SQL keywords
        pattern = r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"[^"]*?"|\'[^\']*?\')'

        def repl(m):
            s = m.group(0)
            if any(kw in s.upper() for kw in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WHERE']):
                # Ganti %s jadi ?
                s = s.replace('%s', '?')
            return s

        return re.sub(pattern, repl, text)

    content = replace_placeholder(content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    print("Fixing placeholder %s → ? ...")
    print("=" * 60)

    fixed_count = 0
    for root, dirs, files in os.walk('.'):
        # Skip venv & __pycache__
        dirs[:] = [d for d in dirs if d not in ('venv', '__pycache__', '.git', 'instance')]

        for file in files:
            if not file.endswith('.py'):
                continue

            filepath = os.path.join(root, file)
            try:
                if fix_file(filepath):
                    print(f"  FIXED: {filepath}")
                    fixed_count += 1
            except Exception as e:
                print(f"  ERROR: {filepath} — {e}")

    print("=" * 60)
    print(f"Selesai. {fixed_count} file diperbaiki.")


if __name__ == '__main__':
    main()