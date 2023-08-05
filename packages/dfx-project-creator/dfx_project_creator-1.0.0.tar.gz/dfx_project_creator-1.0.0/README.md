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
```

---

### How to Run

#### Locally

``` shell
cd src
# Test library
python -m create_gitlab_project --token="<insert-here>" --group_id=<insert-here> --pipeline_type="containerPipeline" --project_type="maven-image" --app_name="test-app" --namespace="security"
python -m create_jenkins_pipeline --gitlab_token="<insert-here>" --project_id=<insert-here> --jenkins_url="<insert-here>" --jenkins_username="<insert-here>" --jenkins_password="<insert-here>"
```





##### Docker

``` shell
# Build
docker build -t deneme .

# Get into docker image
docker run -it deneme bin/sh
python -m create_gitlab_project --token="<insert-here>" --group_id=<insert-here> --pipeline_type="containerPipeline" --project_type="maven-image" --app_name="test-app" --namespace="security"
python -m create_jenkins_pipeline --gitlab_token="<insert-here>" --project_id=<insert-here> --jenkins_url="<insert-here>" --jenkins_username="<insert-here>" --jenkins_password="<insert-here>"
```

---

#### How to Build / Manual Test / Publish

* Create a build
    * dist / *
    * src/<module_name>.egg-info

``` shell
python3 -m build
```

``` shell
# Directory Tree

├───create_gitlab_project
│   ├───template
├───create_jenkins_pipeline
│   ├───template
├───dfx_project_creator.egg-info
└───dist


```

* <u>*Install package locally and test it before pushing to a pip repository.*</u>

``` shell
pip install ./dist/<name>-<version>.tar.gz
```

* Publish

``` shell
# nexus
python3 -m twine upload dist/* --repository nexus
```

---

#### How to Install This Library and Use It

``` shell
# Install from nexus
pip install -i http://definexappsrv.westeurope.cloudapp.azure.com:9080/repository/pypi-group/simple --trusted-host=definexappsrv.westeurope.cloudapp.azure.com dfx_project_creator==0.0.1
```

#### Library Urls

Nexus = http://definexappsrv.westeurope.cloudapp.azure.com:9080/#browse/browse:pi-release


###### gitlab.const values for branch protection
``` python
NO_ACCESS: int = 0
MINIMAL_ACCESS: int = 5
GUEST_ACCESS: int = 10
REPORTER_ACCESS: int = 20
DEVELOPER_ACCESS: int = 30
MAINTAINER_ACCESS: int = 40
OWNER_ACCESS: int = 50
```