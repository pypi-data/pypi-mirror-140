"""
Module Description.


"""
import json
import logging
import os
from pathlib import Path

CWD = Path.cwd()
logger = logging.getLogger(__name__)


def initialise(projectname: str) -> None:
    PROJDIR = CWD.absolute() / projectname
    # Change to project DIR
    os.chdir(PROJDIR)
    # Install with pipenv
    os.system('pipenv install -d')

    vscode_settings = {"python.formatting.provider": "yapf", "python.linting.flake8Enabled": True}

    VSDIR = PROJDIR / '.vscode'
    VSDIR.mkdir(exist_ok=True, parents=True)
    with open(VSDIR / 'settings.json', 'w') as f:
        json.dump(vscode_settings, f)

    # Init GIT
    git_init = ['git init', 'git add -A', 'git commit -m "first commit"']
    for cmd in git_init:
        os.system(cmd)
