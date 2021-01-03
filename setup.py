from cx_Freeze import setup, Executable
import sys

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [],
                    excludes = ['email', 'html', 'http', 'logging', 'pydoc_data', 'unittest', 'urllib', 'xml', 'numpy'],
                    include_files = ['README.md', 'examples/', 'tools/'])

bdist_msi_options = {
    'upgrade_code': '{555c685a-f4ff-4d2b-a6e2-77e4ed4df05a}',
    'add_to_path': False,
    'initial_target_dir': r'[ProgramFilesFolder]\artemis',
    'all_users': True,
    'install_icon': 'icon.ico'
}

base = 'Win32GUI' if sys.platform == 'win32' else None
executables = [
    Executable('interpreter.py', base=base, targetName="artemis",
               icon="icon.ico", shortcutName="Artemis",
               shortcutDir="DesktopFolder")
]

setup(name='Artemis',
      version = '0.6',
      description = '',
      options = {'bdist_msi': bdist_msi_options,
                 'build_exe': buildOptions},
      executables = executables)
