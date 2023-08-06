import requests
from .secrets_manager import SecretsManager
from .exceptions import APIKeyNotFound, DomainNameNull
from requests.exceptions import HTTPError
import json


class CanvasApiClient:
    def __init__(self, domain, version='v1', **kwargs):
        api_token = kwargs.get('api_token')
        self.domain = domain
        self.version = version
        self.api_key = api_token if api_token else CanvasApiClient.get_api_token(domain)
        self.base_url = f"https://{domain}/api/{version}"

    def get_headers(self):
        return {
            'Authorization': 'Bearer {}'.format(self.api_key),
            'Content-Type': 'application/json'
        }

    def get_paginated_response(self, path):
        current_response = self.get(path)
        final_response = current_response.json()
        while "next" in current_response.links:
            next_url = current_response.links['next']['url'].replace(f"{self.base_url}/", "")
            current_response = self.get(next_url)
            final_response.extend(current_response.json())
        return final_response

    def get(self, path):
        try:
            response = requests.get(
                f"{self.base_url}/{path}",
                headers=self.get_headers()
            )
            response.raise_for_status()
        except HTTPError as e:
            raise HTTPError(f"Unsuccessful GET: {response.text}") from e
        return response

    def get_json(self, path):
        return self.get(path).json()

    def put(self, path, body):
        try:
            response = requests.put(
                f"{self.base_url}/{path}",
                headers=self.get_headers(),
                data=body
            )
            response.raise_for_status()
        except HTTPError as e:
            raise HTTPError(f"Unsuccessful PUT: {response.text}") from e
        return response

    def post(self, path, body):
        try:
            response = requests.post(
                f"{self.base_url}/{path}",
                headers=self.get_headers(),
                json=body
            )
            response.raise_for_status()
        except HTTPError as e:
            raise HTTPError(f"Unsuccessful POST: {response.text}") from e
        return response

    def post_graphql(self, body):
        try:
            response = requests.post(
                f"https://{self.domain}/api/graphql",
                headers=self.get_headers(),
                json=body
            )
            response.raise_for_status()
        except HTTPError as e:
            raise HTTPError(f"Unsuccessful Query: {response.text}") from e
        return response

    def delete(self, path, body=None):
        try:
            if body:
                response = requests.delete(
                    f"{self.base_url}/{path}",
                    headers=self.get_headers(),
                    json=body
                )
            else:
                response = requests.delete(
                    f"{self.base_url}/{path}",
                    headers=self.get_headers()
                )
            response.raise_for_status()
        except HTTPError as e:
            raise HTTPError(f"Unsuccessful DELETE: {response.text}") from e
        return response

    @staticmethod
    def get_api_token(domain_name):
        """
        Get the right API key from secrets manager
        """
        secret = json.loads(SecretsManager.get('canvas_api_keys'))
        if domain_name == "":
            raise DomainNameNull("domain_name can't be None")

        if domain_name in secret:
            return secret[domain_name]
        else:
            raise APIKeyNotFound(f"{domain_name} not found in secrets manager.")
