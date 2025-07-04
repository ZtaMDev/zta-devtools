import sys

STANDARD_MODULES = {
    'abc', 'argparse', 'array', 'asyncio', 'base64', 'binascii', 'bisect', 'builtins',
    'calendar', 'cmath', 'collections', 'concurrent', 'contextlib', 'copy', 'csv',
    'datetime', 'decimal', 'difflib', 'dis', 'email', 'enum', 'errno', 'faulthandler',
    'fnmatch', 'fractions', 'functools', 'gc', 'getopt', 'getpass', 'gettext', 'glob',
    'gzip', 'hashlib', 'heapq', 'hmac', 'html', 'http', 'imaplib', 'imp', 'importlib',
    'inspect', 'io', 'ipaddress', 'itertools', 'json', 'keyword', 'linecache', 'locale',
    'logging', 'lzma', 'math', 'mimetypes', 'msvcrt', 'numbers', 'operator', 'os',
    'pathlib', 'pickle', 'pkgutil', 'platform', 'plistlib', 'pprint', 'profile',
    'pstats', 'pty', 'pwd', 'pyclbr', 'pydoc', 'queue', 'random', 're', 'readline',
    'resource', 'sched', 'select', 'selectors', 'shelve', 'shlex', 'shutil', 'signal',
    'site', 'socket', 'sqlite3', 'ssl', 'stat', 'statistics', 'string', 'stringprep',
    'struct', 'subprocess', 'sunau', 'symbol', 'symtable', 'sys', 'sysconfig', 'tabnanny',
    'tarfile', 'tempfile', 'termios', 'textwrap', 'threading', 'time', 'timeit',
    'tkinter', 'token', 'tokenize', 'trace', 'traceback', 'tracemalloc', 'tty',
    'types', 'typing', 'unittest', 'urllib', 'uuid', 'venv', 'warnings', 'wave',
    'weakref', 'webbrowser', 'xml', 'xmlrpc', 'zipapp', 'zipfile', 'zipimport', 'zlib'
}

def is_stdlib_module(module_name: str) -> bool:
    return module_name.lower() in STANDARD_MODULES

from pathlib import Path
import os

def detect_venv() -> str | None:
    """Devuelve la ruta al ejecutable de Python del venv si existe."""
    if os.name == "nt":
        venv_python = Path("venv/Scripts/python.exe")
    else:
        venv_python = Path("venv/bin/python")
    
    return str(venv_python) if venv_python.exists() else None
