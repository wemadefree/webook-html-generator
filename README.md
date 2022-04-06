# webook-html-generator

The purpose of the WeBook HTML Generator application is to generate html pages that will be displayed on screens. The application connects to the WeBook API service and collects the necessary data to generate html.

## Evironment file
In order to work properly, you need to rename the .env_sample file to .env and fill in the required variables.

## Poetry
The application relies on the Poetry dependancy management system:
- Install python3.8 version. In linux ```sudo apt install python3.8```
- Install poetry: https://realpython.com/dependency-management-python-poetry/#take-care-of-prerequisites
- In top folder (where poetry.toml file is located) create virtual environment  ```poetry env use python3``` or  ```poetry env use python```
- Select poetry environment in Pycharm or Visual studio code. Optionaly you may need install explicitly all dependancies  ```poetry install``` from top folder
- Further info about work with poetry can be found in: https://realpython.com/dependency-management-python-poetry/#work-with-python-poetry
