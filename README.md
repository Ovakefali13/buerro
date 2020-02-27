# buerro
This is a super cool PDA GitHub from super cool people.

![yummy burrito](https://lovingitvegan.com/wp-content/uploads/2018/11/Vegan-Burrito-11.jpg =250x "Yummy burrito")

required:

- Python 3.7

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
pip install -r requirements.txt
```

Activate the virtual environment (do this every time you start working on it).

```
source venv/bin/activate
```

Change some code, until you want to use some packages. If you do, just `pip install` them.

Once you've finished working on it for that shell session, make sure to persist your virtual environment. You can skip this step if you didn't install any new packages this session. The `venv/` folder should not be tracked by source control (it contains binaries). Instead you can freeze your current state into a `requirements.txt`.

```
pip freeze > requirements.txt
```

To exit your environment (switch to other adapter or finish a session):

```
deactivate
```

