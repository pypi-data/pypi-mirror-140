# Python Project Template

A Python Template to start quickly a new project. Generate doxygen for html and latex (PDF) with single<br>
command in the project directory with the CLI. As well an program (.exe) for Windows can be generated with<br>
a single instruction.

*Note*: Section Links not working with Pycharm markdown preview.

## Getting started
Make sure you have installed python on your machine. If working with vscode, see at the tasks first (ctrl+shit+P -> task). There are some automation scripts in *.vscode/scripts* to execute several commands. This project and the scripts are optimized for using in a virtual environment (venv). Just run task `Run (main.py)` and the rest will be done automatically for you (consider notification or desired actions in terminal output).<br>

Use the appropriate task to execute commands in virtual environment, such as *pip list* or *pip install <PACKAGE_NAME>*<br>


### Project setup (This section is just for template documentation, delete on release)
1. Setup the PROJECT_NAME in docs/doxyfile
___


## Deploy Project
If the application want to execute from everywhere, you have to generate an
executable (.exe) with py2exe.

### py2exe
Use [py2exe](https://pypi.org/project/py2exe/) to generate the
executable file.<br>
First install py2exe, then run `python generate_bin.py` from root folder.<br>
This script contains following three steps:

1. navigate to project's directory with CLI
1. run `python setup.py py2exe -d ./bin`

*Note*: Using py2exe every "folder" (here programs) must be a package. Otherwise py2exe don't include these modules
for executable file.  
___


## Generate documentation
Run doxygen in docs-folder because relative paths in doxygen-config-file are relative to the directory from which
doxygen is run. <br>
Navigate to *./docs* and run just `doxygen doxyfile`

Edit ./docs/doxyfile and change PROJECT_NAME to the desired name. 
___

