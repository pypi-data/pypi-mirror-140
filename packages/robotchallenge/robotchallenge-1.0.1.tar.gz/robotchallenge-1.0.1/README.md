# RobotChallenge
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![codecov](https://codecov.io/gh/sheecegardezi/RobotChallenge/branch/main/graph/badge.svg)](https://codecov.io/gh/sheecegardezi/RobotChallenge)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI test](https://github.com/sheecegardezi/RobotChallenge/actions/workflows/actions.yml/badge.svg)](https://github.com/sheecegardezi/RobotChallenge/actions)
[![PyPI version](https://badge.fury.io/py/robotchallenge.svg)](https://pypi.org/project/robotchallenge/)


Robot Challenge

--------------------------------------------------------------------------------
## Summary


An attempt at Robot Challenge.


--------------------------------------------------------------------------------
## How to Install

    # download and install python >=3.7 fromhttps://www.python.org/downloads/
    # download source code using git
    git clone https://github.com/sheecegardezi/RobotChallenge.git
    cd RobotChallenge

    # install create a virtual environment
    python -m venv venv

    # activate the virtual environment on Linux
    source venv/bin/activate
    # activate the virtual environment on windows
    # source venv\Scripts\activate

    # install the requirements
    pip install -r requirements.txt

    # install the software
    pip install -e .

    # run the tests
    pytest --cov=robotchallenge -rx -s tests


--------------------------------------------------------------------------------
## Running Software Locally


    robotchallenge --help
    robotchallenge -f "`pwd`/tests/test_data/sample_problems.txt"


--------------------------------------------------------------------------------
## Usage of the Software

    # Create a file with a new commond is each line eg. input_file.txt:
    
        PLACE 1,2,EAST
        MOVE
        MOVE
        LEFT
        MOVE
        REPORT
        Output: 3,3,NORTH
    
    # Run the software with the above file
    
        robotchallenge -f "`pwd`/input_file.txt"    


--------------------------------------------------------------------------------
## Running Software in Docker 

    # clone repo
    git clone https://github.com/sheecegardezi/RobotChallenge.git
    cd RobotChallenge
    
    # building image locally
    docker build -t robotchallenge .

    # printing help
    docker run -it --rm robotchallenge -h

    # using existing test file 
    docker run -it --rm robotchallenge -f "/app/tests/test_data/sample_problems.txt"
    
    # using new test file 
    docker run -it --rm -v "`pwd`/tests/test_data/sample_problems.txt":"/app/tests/test_data/sample_problems.txt" robotchallenge -f "/app/tests/test_data/sample_problems.txt"
    


--------------------------------------------------------------------------------
## Running Software using prebaked Docker Image


    # pulling image from repo
    docker image pull sheecegardezi/robotchallenge:latest

    # printing help
    docker run -it --rm sheecegardezi/robotchallenge:latest -h

    # using existing test file 
    docker run -it --rm sheecegardezi/robotchallenge:latest -f "/app/tests/test_data/sample_problems.txt"

    # using new test file 
    docker run -it --rm -v "`pwd`/tests/test_data/sample_problems.txt":"/app/tests/test_data/sample_problems.txt" sheecegardezi/robotchallenge:latest -f "/app/tests/test_data/sample_problems.txt"

--------------------------------------------------------------------------------    
### Running Testing

    pytest --cov=robotchallenge -rx -s tests
