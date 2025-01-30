@ECHO OFF

ECHO Installing libraries in current directory...

cd %~dp0

python -m venv .venv
call .venv\Scripts\activate
pip install numpy
pip install numba
pip install opencv-python
pip install pillow

ECHO Successfully installed libraries in current directory
ECHO run '.venv\Scripts\activate' to activate the virtual environment
Echo then run 'python [name_of_script].py' to run the desired script

PAUSE