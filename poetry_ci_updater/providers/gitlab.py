import os

import requests

from poetry_ci_updater.providers.provider import Provider


class Gitlab(Provider):
    merge_request_title = 'Python Dependency update'

    def run(self):
        self.token = os.getenv('CI_JOB_TOKEN')
        self.project_id = os.getenv('CI_PROJECT_ID')
        if self.search_for_merge_request() < 1:
            self.create_merge_request()

    def search_for_merge_request(self):
        url = f'https://gitlab.com/api/v4/projects/{self.project_id}/merge_requests'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        params = {
            'state': 'opened'
        }
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        open_merge_requests = [True for merge_request in response.json() if merge_request['title'] == self.merge_request_title]
        return len(open_merge_requests)

    def create_merge_request(self):
        url = f"https://gitlab.com/api/v4/projects/{self.project_id}/merge_requests"
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        data = {
            'id': None,
            'source_branch': self.branch_name,
            'target_branch': 'master',
            'title': self.merge_request_title,
            'description': self.updates_string(),
            'remove_source_branch': True,
            'squash': True,
        }
        requests.post(url, json=data, headers=headers)