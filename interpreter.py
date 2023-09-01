import os
import subprocess
import sys
import shutil

pyinstaller_Installed = True

try:
    import PyInstaller.__main__ as PyInstaller
except ImportError:
    pyinstaller_Installed = False

from parse import Parser
from error import Error

version = '1.0.0'


class Interpreter:
    @staticmethod
    def interpret(code):
        subprocess.call(['python', 'output.py'])


def read_code(path):
    if os.path.isfile(path):
        with open(path, 'r') as file:
            return file.read()

    Error('Input file not found')


def handle_args():
    if sys.argv[1] in ['--help', '-h']:
        Error(
            '''
VitScript command line arguments:
--help -h: Print this message
--version -v: Print the interpreter version
--run -r (default) [file]: Run the interpreter on the specified file
--translate -t [file] [address]: Translate the specified file into Python code and save to the specified path
--compile -c [file] [address]: Compile the specified file into an executable file and save it to the specified path
            '''
        )

    elif sys.argv[1] in ['--version', '-v']:
        print('VitScript v1.0.0')

    elif sys.argv[1] in ['--run', '-r']:
        if len(sys.argv) < 3:
            Error('Invalid number of arguments')

        else:
            if os.path.isfile(sys.argv[2]):
                parser = Parser(read_code((sys.argv[2])))

                interpreter = Interpreter()
                interpreter.interpret(parser.code)

            else:
                Error('File not found')

    elif sys.argv[1] in ['--translate', '-t']:
        if len(sys.argv) < 4:
            Error('Invalid number of arguments')

        else:
            if os.path.isfile(sys.argv[2]):
                parser = Parser(read_code((sys.argv[2])))

                with open(sys.argv[3], 'w') as f:
                    f.write(parser.code)

            else:
                Error('Input file not found')

    elif sys.argv[1] in ['--compile', '-c']:
        if not pyinstaller_Installed:
            Error('PyInstaller is not installed \nPlease run "pip install PyInstaller"')

        if len(sys.argv) < 4:
            Error('Invalid number of arguments')

        else:
            if os.path.isfile(sys.argv[2]):
                parser = Parser(read_code((sys.argv[2])))

                filename = sys.argv[3].split('.')[0]

                with open(f'{filename}.py', 'w') as f:
                    f.write(parser.code)

                if os.path.isfile(filename + '.exe'):
                    os.remove(filename + '.exe')

                subprocess.call(['PyInstaller', f'{filename}.py', '-F', '--onefile'])

                os.rename(f'dist/{filename}.exe', f'./{sys.argv[3]}')
                os.remove(filename + '.py')
                os.remove(filename + '.spec')

                shutil.rmtree('build')
                shutil.rmtree('dist')

            else:
                Error('File not found')

    elif os.path.isfile(sys.argv[1]):
        parser = Parser(read_code(sys.argv[1]))
        interpreter = Interpreter()
        interpreter.interpret(parser.code)

    else:
        Error('Invalid argument')

    if os.path.isfile('output.py'):
        os.remove('output.py')


def check_args():
    if len(sys.argv) < 2:
        Error('Invalid number of arguments')

    handle_args()


check_args()
