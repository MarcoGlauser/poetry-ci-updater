# Poetry CI Updater

## Not maintained anymore use [renovate](https://github.com/renovatebot/renovate) instead

This package is intended to help integrating poetry with your CI.

It will create a new branch where it will push the updated poetry.lock to.
If your git provider is supported, it will also create a pull/merge request.

## Installation
### Pypi
```yaml
poetry add --dev poetry-ci-updater
```

### Git
```shell
poetry add --dev git+https://github.com/MarcoGlauser/poetry-ci-updater@master
```


## Usage
### Gitlab
Because Gitlab currently can't write to the repository with the $CI_JOB_TOKEN, you will need 
to define a secret enviroment variable  with the name PERSONAL_ACCESS_TOKEN.
```yaml
update-dependencies:
  stage: build
  image: python:3.8
  before_script:
    - git config user.email "{$GITLAB_USER_EMAIL}"
    - git config user.name "${GITLAB_USER_NAME}"
  script:
    - pip install poetry
    - poetry install
    - git remote rm origin
    - git remote add origin https://gitlab-ci-token:${PERSONAL_ACCESS_TOKEN}@${CI_SERVER_HOST}:${CI_SERVER_PORT}/${CI_PROJECT_PATH}.git
    - CI_JOB_TOKEN=${PERSONAL_ACCESS_TOKEN} poetry run poetry-ci-updater
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
```

## TODO
* Github Actions support
* Tests
* Provider Options
* Keep update branch up to date
