import os

import requests

from poetry_ci_updater.providers.provider import Provider


class Gitlab(Provider):
    merge_request_title = 'Python Dependency update'

    def run(self):
        self.token = os.getenv('CI_JOB_TOKEN')
        self.project_id = os.getenv('CI_PROJECT_ID')
        merge_request = self.search_for_merge_request()
        if merge_request:
            self.add_note(merge_request)
        else:
            self.create_merge_request()

    def add_note(self, merge_request):
        url = f'https://gitlab.com/api/v4/projects/{self.project_id}/merge_requests/{merge_request["iid"]}/notes'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        data = {
            'body': self.updates_string()
        }
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()

    def search_for_merge_request(self):
        url = f'https://gitlab.com/api/v4/projects/{self.project_id}/merge_requests'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        params = {
            'state': 'opened',
            'source_branch': self.branch_name,
            'search': self.merge_request_title,
            'in': 'title'
        }
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        open_merge_requests = response.json()
        try:
            return open_merge_requests[0]
        except IndexError:
            return None

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
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()