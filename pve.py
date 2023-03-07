"""
Entrypoint similar to what setup.py defines - but digestible for pyinstaller.
"""
from pve_exporter.cli import main

if __name__ == '__main__':
    main()
