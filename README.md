# buerro 🌯

This is a super cool PDA from super cool people.

required:

- Python 3.7

## Install

```
make install
```

## Test

```
make test
```

## Deploy

```
make frontend &
make backend
```

## Git Workflow

We use Feature Branches. Refer to [`doc/git_workflow.md`](doc/git_workflow.md) for instructions and [attlasion.com](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow) for a more in-depth explanation.

## Python Package Management

required:

- `pip install virtualenv`

Setup up a virtual environment in your project folder.

[docs.python-guide.org/virtualenvs](https://docs.python-guide.org/dev/virtualenvs/#basic-usage)

Create a new local virtual environment and install the packages in `requirements.txt`.

```
virtualenv -p python3.7 venv
```

Activate the virtual environment (do this every time you start working on it).

```
source venv/bin/activate
```

Install the required python packages:

```
pip install -r requirements.txt
```

Change some code, until you want to use some packages. If you do, just install them and refresh the `requirements.txt`:

```
pip install some_package
pip freeze > requirements.txt
```

To exit your environment:

```
deactivate
```

## Unit Testing in Python

See the [documentation](https://docs.python.org/3/library/unittest.html).

Test functions need to start with `test*`.

### Discovering tests automatically

All tests can be discovered automatically using `cd <directory && python -m unittest discover`. This only works if all directories on the way to the test directory are importable as python modules (they contain a `__init__.py`).

All test files need to start with `test*.py` or provide a different `-p` option to discover.

Use the target `make test` to discover tests within a module tracking coverage. The tests are run from the virtual environment, you don't have to activate it, before running `make`.

### Debugging

Insert this line anywhere in your code: this will add a breakpoint during unittest execution.

```py
breakpoint()
```
