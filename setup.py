import cx_Freeze
import sys
import os
import selenium


base = None

#syspath = r"D:\Users\PB6\AppData\Local\Programs\Python\Python37\DLLs"

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

includes      = []
include_files = [os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'), 
                    os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),'Jnj48.ico', 'chromedriver.exe', 'phantomjs.exe', 'killPhantom.bat', 'killChrome.bat']
#include_files = [syspath + '/tcl86t.dll', syspath + '/tk86t.dll', 'Jnj48.ico', 'chromedriver.exe', 'phantomjs.exe', 'killPhantom.bat', 'killChrome.bat']
excludes = [""]

build_exe_options = {"excludes": excludes,
                                  "includes": includes, 
                                  "include_files": include_files,
                                  "packages":["tkinter","selenium"],
                     "optimize": 2}

if sys.platform == 'win32':
    base = "Win32GUI"


executables = [cx_Freeze.Executable("CATSWeb Automation Tool.py", base=base, icon="Jnj48.ico")]

cx_Freeze.setup(
    name = "CATSWeb Automation Tool",
    options = {"build_exe": build_exe_options},
    version = "1.0",
    description = """CatsWeb complaint handler for Level 1 and Level 2 complaints
    Copyright +\u00a9+ 2019 Tata Consultancy Services Limited""",
    executables = executables
    )
