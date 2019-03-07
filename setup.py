import cx_Freeze
import sys
import os
import selenium


base = None

os.environ['TCL_LIBRARY'] = r'D:\Users\PB6\AppData\Local\Programs\Python\Python37\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'D:\Users\PB6\AppData\Local\Programs\Python\Python37\tcl\tk8.6'


syspath = r"D:\Users\PB6\AppData\Local\Programs\Python\Python37\DLLs"

includes      = []
include_files = [syspath + '/tcl86t.dll', syspath + '/tk86t.dll', 'Jnj48.ico', 'chromedriver.exe', 'phantomjs.exe', 'killPhantom.bat', 'killChrome.bat']
excludes = [""]

build_exe_options = {"excludes": excludes,
                                  "includes": includes, 
                                  "include_files": include_files,
                                  "packages":["tkinter","selenium"],
                     "optimize": 2}
'''
if sys.platform == 'win32':
    base = "Win32GUI"
'''

executables = [cx_Freeze.Executable("CATSWeb Automation Tool.py", base=base, icon="Jnj48.ico")]

cx_Freeze.setup(
    name = "CATSWeb Automation Tool",
    options = {"build_exe": build_exe_options},
    version = "1.0",
    description = """CatsWeb complaint handler for Level 1 and Level 2 complaints
    Copyright +\u00a9+ 2019 Tata Consultancy Services Limited""",
    executables = executables
    )
