# {{ cookiecutter.project_name }}

## Overview

This is your new Dockerized Django project, which was generated using `GreenDeploy {{ cookiecutter.greendeploy_version }}`.

Take a look at the [GreenDeploy documentation](https://greendeploy.readthedocs.io) to get started.

## Rules and guidelines

In order to get the best out of the template:

* Don't remove any lines from the `.gitignore` file we provide
* Make sure your results can be reproduced by following a [data engineering convention](https://greendeploy.readthedocs.io/en/stable/12_faq/01_faq.html#what-is-data-engineering-convention)
* Don't commit data to your repository
* Don't commit any credentials or your local configuration to your repository. Keep all your credentials and local configuration in `conf/local/`

## How to install dependencies

Declare any dependencies in `src/requirements.txt` for `pip` installation and `src/environment.yml` for `conda` installation.

To install them, run:

```
greendeploy install
```

## How to run your GreenDeploy pipeline

You can run your Dockerized Django project with:

```
greendeploy run
```

## How to test your Dockerized Django project

Have a look at the file `src/tests/test_run.py` for instructions on how to write your tests. You can run your tests as follows:

```
greendeploy test
```

To configure the coverage threshold, go to the `.coveragerc` file.

## Project dependencies

To generate or update the dependency requirements for your project:

```
greendeploy build-reqs
```

This will copy the contents of `src/requirements.txt` into a new file `src/requirements.in` which will be used as the source for `pip-compile`. You can see the output of the resolution by opening `src/requirements.txt`.

After this, if you'd like to update your project requirements, please update `src/requirements.in` and re-run `greendeploy build-reqs`.

[Further information about project dependencies](https://greendeploy.readthedocs.io/en/stable/04_greendeploy_project_setup/01_dependencies.html#project-specific-dependencies)

## How to work with GreenDeploy and notebooks

> Note: Using `greendeploy jupyter` or `greendeploy ipython` to run your notebook provides these variables in scope: `context`, `catalog`, and `startup_error`.
>
> Jupyter, JupyterLab, and IPython are already included in the project requirements by default, so once you have run `greendeploy install` you will not need to take any extra steps before you use them.

### Jupyter
To use Jupyter notebooks in your Dockerized Django project, you need to install Jupyter:

```
pip install jupyter
```

After installing Jupyter, you can start a local notebook server:

```
greendeploy jupyter notebook
```

### JupyterLab
To use JupyterLab, you need to install it:

```
pip install jupyterlab
```

You can also start JupyterLab:

```
greendeploy jupyter lab
```

### IPython
And if you want to run an IPython session:

```
greendeploy ipython
```

### How to convert notebook cells to nodes in a Dockerized Django project
You can move notebook code over into a Dockerized Django project structure using a mixture of [cell tagging](https://jupyter-notebook.readthedocs.io/en/stable/changelog.html#release-5-0-0) and GreenDeploy CLI commands.

By adding the `node` tag to a cell and running the command below, the cell's source code will be copied over to a Python file within `src/<package_name>/nodes/`:

```
greendeploy jupyter convert <filepath_to_my_notebook>
```
> *Note:* The name of the Python file matches the name of the original notebook.

Alternatively, you may want to transform all your notebooks in one go. Run the following command to convert all notebook files found in the project root directory and under any of its sub-folders:

```
greendeploy jupyter convert --all
```

### How to ignore notebook output cells in `git`
To automatically strip out all output cell contents before committing to `git`, you can run `greendeploy activate-nbstripout`. This will add a hook in `.git/config` which will run `nbstripout` before anything is committed to `git`.

> *Note:* Your output cells will be retained locally.

## Package your Dockerized Django project

[Further information about building project documentation and packaging your project](https://greendeploy.readthedocs.io/en/stable/03_tutorial/05_package_a_project.html)