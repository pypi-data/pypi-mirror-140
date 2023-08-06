# Hello PyPI

## Development Flow without JFrog
### Build & Resolve dependencies
```
$ python3 -m venv venv
$ . venv/bin/activate
(venv) $ python3 -m pip install --upgrade pip
(venv) $ python3 -m pip install Babel
```
### Run
```
(venv) $ python3 src/hello/helloserver.py
```
### Install locally
```
(venv) $ python3 -m pip install --upgrade setuptools wheel
(venv) $ python3 setup.py sdist bdist_wheel
(venv) $ pip install -e .
```
Test
```
(venv) $ python3 -m hello
executing __init__.py in hello
Starting httpd server on localhost:8080 with 640,742
```
### Publish
Create an account on [PyPI](https://pypi.org/)
```
(venv) $ python3 -m pip install --upgrade twine
(venv) $ python3 -m twine upload dist/*
[....]
View at:
https://pypi.org/project/tsuyo-hello/0.0.1/
```

## Development Flow with JFrog
### JFrog Artifactory Configuration
Create repos under a project
```
$ ../artifactory/create_repo.sh -s dev.gcp -u admin -p hello go ./artifactory
artifactory password or token for user <admin>: 
create repos (user: admin, server_id: dev.gcp, project: hello, repo_name: go, repo_conf_dir: ./artifactory)
Successfully created repository 'hello-go-local' 
Successfully created repository 'hello-go-remote' 
Successfully created repository 'hello-go' 
```

### Build and Deploy
Choose the repos for JFrog CLI (select the last repo ("hello-go" in the above case) for all questions below)
```
$ jfrog goc
Resolve dependencies from Artifactory? (y/n) [y]? 
Set Artifactory server ID [dev.gcp]: 
Set repository for dependencies resolution (press Tab for options): hello-go
Deploy project artifacts to Artifactory? (y/n) [y]? 
Set Artifactory server ID [dev.gcp]: 
Set repository for artifacts deployment (press Tab for options): hello-go
21:54:00 [Info] go build config successfully created.
$ jfrog c use dev.gcp
$ sudo rm -fr $GOPATH/pkg/mod # delete local caches to confirm every dependency is resolved via artifactory
```
Build manually
```
$ jfrog go build --project=hello --build-name=hello-go-build --build-number=1
$ jfrog gp v1.0.0 --project=hello --build-name=hello-go-build --build-number=1
$ jfrog rt bce --project=hello hello-go-build 1
$ jfrog rt bag --project=hello hello-go-build 1 ..
$ jfrog rt bp --project=hello hello-go-build 1
```
Or Build with script (the same as above)
```
$ ./build.sh hello hello-go-build 1 v1.0.0
```

### Clean Up
Delete repos once you finish
```
$ ../artifactory/delete_repo.sh hello go
```
