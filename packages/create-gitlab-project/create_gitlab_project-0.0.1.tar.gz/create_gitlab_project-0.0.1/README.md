### Before you begin, ensure that:

- python3 and pip3 are installed
- below packages are up-to-date
    - pip
    - build
    - twine

``` shell
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade build
python3 -m pip install --upgrade twine
```

- *<home_directory>/.pypirc* example file content

```
[distutils]
index-servers=
    nexus

# nexus pypi repository
[nexus]
    repository = http://definexappsrv.westeurope.cloudapp.azure.com:9080/repository/pi-release/
    username = <username>
    password = <password>

# pypi
[pypi]
    username = __token__
    password = <access token>

# testpypi 
[testpypi]
    username = __token__
    password = <access token>
```

---

### How to Run

#### Locally

``` shell
cd src
# Test library
python -m create_gitlab_project --token="glpat--zLJua6SdYsxVxMgGs-1" --group_id=16317464 --pipeline_type="containerPipeline" --project_type="maven-image" --app_name="test-app4" --namespace="security"
```

#### gitlab.const values for branch protection
``` python
NO_ACCESS: int = 0
MINIMAL_ACCESS: int = 5
GUEST_ACCESS: int = 10
REPORTER_ACCESS: int = 20
DEVELOPER_ACCESS: int = 30
MAINTAINER_ACCESS: int = 40
OWNER_ACCESS: int = 50
```







#### Docker

``` shell
# Build
docker build -t semver .

# Get into docker image
docker run -it semver bin/sh
python -m semver_gitlab -b develop -p 33461475 --token="glpat-xFYe3UqanN3SUsH4BbHT"
```

---

### How to Build / Manual Test / Publish

* Create a build
    * dist / *
    * src/<module_name>.egg-info

``` shell
python3 -m build
```

``` shell
# Directory Tree

├───dist
├───src
│   ├───create_gitlab_project
│   └───create_gitlab_project.egg-info
└───template-files

```

* <u>*Install package locally and test it before pushing to a pip repository.*</u>

``` shell
pip install ./dist/<name>-<version>.tar.gz
```

* Publish

``` shell
# nexus
python3 -m twine upload dist/* --repository nexus
# (Deprecated) pypi
python3 -m twine upload dist/*
# (Deprecated) testpypi
python3 -m twine upload --repository testpypi dist/*
```

---

### How to Install This Library and Use It

``` shell
# Install from nexus
pip install -i http://definexappsrv.westeurope.cloudapp.azure.com:9080/repository/pypi-group/simple --trusted-host=definexappsrv.westeurope.cloudapp.azure.com semver-gitl
ab==0.0.4

# (Deprecated) Install from pypi
# pip install semver-gitlab==0.0.4

# Test library
python -m semver_gitlab -b develop -p 33461475 --token="glpat-xFYe3UqanN3SUsH4BbHT"
```

### Library Urls

Nexus = http://definexappsrv.westeurope.cloudapp.azure.com:9080/#browse/browse:pi-release

(*Deprecated*) Production = https://pypi.org/project/semver-gitlab/

(*Deprecated*) Test = https://pypi.org/project/semver-gitlab-dfx-test/