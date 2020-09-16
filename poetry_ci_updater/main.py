import logging
import re
import subprocess
import sys

import click
import git
from git import Repo

from poetry_ci_updater.providers.gitlab import Gitlab

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


def checkout_branch(repo: Repo, branch_name: str):
    repo.git.fetch()
    try:
        repo.git.branch(D=branch_name)
    except git.exc.GitCommandError:
        pass
    try:
        repo.git.checkout('--track', f'origin/{branch_name}')
    except git.exc.GitCommandError as e:
        repo.git.checkout(b=branch_name)


def check_for_updates():
    poetry_update_pattern = re.compile(r'Updating [a-zA-Z0-9\-_]+ \(.*\)')
    poetry_output = subprocess.run(["poetry", "update", '--dry-run'], stdout=subprocess.PIPE).stdout.decode('utf-8').splitlines()
    logger.debug(poetry_output)
    return [poetry_update_pattern.search(line).group() for line in poetry_output if poetry_update_pattern.search(line)]


def update():
    poetry_output = subprocess.run(["poetry", "update", '--lock'], stdout=subprocess.PIPE).stdout.decode('utf-8').splitlines()
    logger.debug(poetry_output)


def push_update(repo: Repo, branch_name: str):
    try:
        git_add = repo.git.add('poetry.lock')
        logger.debug(git_add)
        git_commit = repo.git.commit(m=f'Update Dependencies.')
        logger.debug(git_commit)
    except git.exc.GitCommandError as e:
        logger.debug(e)
        logger.info('Nothing to commit changed')
    git_push = repo.git.push('-u', 'origin', branch_name)
    logger.debug(git_push)


@click.command()
@click.option('--branch-name', default='python-dependencies', help='Default Branch name to be created')
@click.option('--create-mr', default=True)
@click.option('-v', '--verbose', is_flag=True)
def main(branch_name: str, create_mr: bool, verbose):
    if verbose:
        logger.setLevel(logging.DEBUG)

    repo = Repo()
    updates = check_for_updates()
    if len(updates) > 0:
        logger.info('Available updates found.')
        checkout_branch(repo, branch_name)
        update()
        push_update(repo, branch_name)
        logger.info('Updated the dependencies!')
        if create_mr:
            provider = Gitlab(branch_name, updates)
            provider.run()
    else:
        logger.info('No updates available. Everything is up to date.')


if __name__ == '__main__':
    main()