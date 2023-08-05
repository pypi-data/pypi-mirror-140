## Git dependency python
A packaged used to manage dependencies in git repositories for python projects.

### Prepare your project

#### Install script
Your projects need to contain bash installation file which looks like this:

```bash
#!/usr/bin/env bash

PYTHON=$1
ENVIRONMENT=$2
CHILD=$3
DIR_NAME=$(dirname $0)
CURRENT_PATH=$(pwd)

# Remove previous failed builds.
rm -rf *.egg-info build dist

set -e

if [[ "$ENVIRONMENT" = "dev" || "$ENVIRONMENT" = "prod" ]]
then
    echo "Running installation with python '$PYTHON' and path (script: '$DIR_NAME', pwd: $CURRENT_PATH) in '$ENVIRONMENT' environment."
    ${PYTHON} -m pip install git-dependency-installer --upgrade --force-reinstall
    ${PYTHON} $DIR_NAME/setup.py sdist
    
    if [[ "$CHILD" = "--child" ]]
    then
        ${PYTHON} -m pip install dist/* --install-option=--environment="$ENVIRONMENT" --install-option="$CHILD"
    else
        ${PYTHON} -m pip install dist/* --install-option=--environment="$ENVIRONMENT"
    fi

else
    echo "Unsupported environment!"
    exit 1
fi

# Remove build leftovers.
rm -rf *.egg-info build dist
```

#### Setup.py file
Also, you need to modify your projects' setup.py files to:

```python
from git_dependency_installer.setup_helper import prepare_setup, install_deps

PACKAGE_VERSION = 'major.minor.bugfix'  # Example: 1.0.0.
PROJECT_NAME = '<your-project-name>'  # Example: my-cool-s3-dependency.
DESCRIPTION = '<your-project-description>'  # Example: Library used to work with S3 buckets.
PARENT_PROJECT_NAME = '<your-main(parent)-project-name>'  # Example: my-cool-project.

INTERNAL_DEPENDENCIES = [
    ['my-cool-other-dependency', '2.*.*', 'my-team/my-cool-other-dependency'],
    ...
]

EXTERNAL_DEPENDENCIES = [
    'requests==2.18.4',
    'Django==2.0.3',
    ...
]

prepare_setup(PACKAGE_VERSION, PROJECT_NAME, DESCRIPTION, PARENT_PROJECT_NAME)
install_deps(EXTERNAL_DEPENDENCIES, INTERNAL_DEPENDENCIES)

```

### Prepare your git

#### Tagging
Start git-tagging your commits. Example, for development tag your commits like this dev-2.1.0, for production tag your commits like this: 2.1.0.

#### Using ssh
Setup SSH file for your git repositories and start using SSH over HTTPS.

#### Credits
This package is a direct copy of the package git-dependency-python by Laimonas Sutkus, except pip version assertion is removed, as the asserted version (18.1) is outdated and doesn't allow installation of some newer packages.