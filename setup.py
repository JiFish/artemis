from cx_Freeze import setup, Executable
import sys

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [],
                    excludes = ['email', 'html', 'http', 'logging', 'pydoc_data', 'unittest', 'urllib', 'xml'],
                    include_files = ['README.md'])

base = 'Win32GUI' if sys.platform == 'win32' else None
executables = [
    Executable('interpreter.py', base=base)
]

setup(name='Artemis',
      version = '0.5',
      description = '',
      options = dict(build_exe = buildOptions),
      executables = executables)
