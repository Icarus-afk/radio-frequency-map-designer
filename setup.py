from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 'excludes': []}

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('rfmap.py', base=base, target_name = 'rfmap.exe')
]

setup(name='Radio-Frequency-Chart-Designer',
      version = '1.0.1',
      description = '',
      options = {'build_exe': build_options},
      executables = executables)
