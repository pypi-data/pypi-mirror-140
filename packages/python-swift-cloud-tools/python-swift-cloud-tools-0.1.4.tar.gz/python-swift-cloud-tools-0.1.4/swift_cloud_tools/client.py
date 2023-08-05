# Copyright 2021 Grupo Globo
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
import logging
import json

logger = logging.getLogger('swift-cloud-tools')


class SCTClient(object):

    def __init__(self, sct_host, sct_api_key):
        self.sct_url = '{}/v1'.format(sct_host)
        self.sct_api_key = sct_api_key

    def expirer_create(self, account, container, obj, date):
        headers = {
            'Content-type': 'application/json',
            'X-Auth-Token': self.sct_api_key
        }

        data = {
            "account": account,
            "container": container,
            "object": obj,
            "date": date
        }

        response = requests.post(
            '{}/expirer/'.format(self.sct_url),
            data=json.dumps(data),
            headers=headers
        )
        return response

    def expirer_delete(self, account, container, obj):
        headers = {
            'Content-type': 'application/json',
            'X-Auth-Token': self.sct_api_key
        }

        data = {
            "account": account,
            "container": container,
            "object": obj
        }

        response = requests.delete(
            '{}/expirer/'.format(self.sct_url),
            data=json.dumps(data),
            headers=headers
        )
        return response

    def transfer_create(self, project_id, project_name, environment):
        headers = {
            'Content-type': 'application/json',
            'X-Auth-Token': self.sct_api_key
        }

        data = {
            "project_id": project_id,
            "project_name": project_name,
            "environment": environment
        }

        response = requests.post(
            '{}/transfer/'.format(self.sct_url),
            data=json.dumps(data),
            headers=headers
        )
        return response

    def transfer_get(self, project_id):
        headers = {
            'Content-type': 'application/json',
            'X-Auth-Token': self.sct_api_key
        }

        response = requests.get(
            '{}/transfer/{}'.format(self.sct_url, project_id),
            headers=headers
        )
        return response

    def transfer_status(self, project_id):
        headers = {
            'Content-type': 'application/json',
            'X-Auth-Token': self.sct_api_key
        }

        response = requests.get(
            '{}/transfer/status/{}'.format(self.sct_url, project_id),
            headers=headers
        )
        return response

    def transfer_status_all(self, page=1, per_page=50):
        headers = {
            'Content-type': 'application/json',
            'X-Auth-Token': self.sct_api_key
        }

        response = requests.get(
            '{}/transfer/status?page={}&per_page={}'.format(self.sct_url, page, per_page),
            headers=headers
        )
        return response

    def transfer_status_by_projects(self, project_ids):
        headers = {
            'Content-type': 'application/json',
            'X-Auth-Token': self.sct_api_key
        }

        response = requests.post(
            '{}/transfer/status'.format(self.sct_url),
            data=json.dumps(project_ids),
            headers=headers
        )
        return response
