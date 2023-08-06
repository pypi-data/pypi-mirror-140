from datetime import datetime
import json
import logging
from picsellia import exceptions
from picsellia.sdk.connexion import Connexion
import requests

from picsellia.utils import check_status_code

logger = logging.getLogger('picsellia')


class ServiceConnexion:

    def __init__(self, service : str, api_token: str, host : str, deployment_id : str) -> None:
        self.service = service
        self.api_token = api_token
        self.host = host
        self.deployment_id = deployment_id
        self.jwt, self.expires_in = self.generate_jwt()
        

    def wrapped_request(f):
        def decorated(self, *args, regenerate_jwt=True, **kwargs):
            try:
                resp = f(self, *args, **kwargs)
            except Exception:
                raise exceptions.NetworkError(
                    "Server is not responding, please check your host.")
            
            if resp.status_code == 401:
                res = resp.json()
                if regenerate_jwt and "expired" in res and res["expired"]:
                    self.jwt, self.expires_in = self.generate_jwt()
                    return decorated(self, *args,  regenerate_jwt=False, **kwargs)
                else:
                    raise exceptions.UnauthorizedError("You are not authorized to do this.")
            else:
                check_status_code(resp)
                
            return resp
        return decorated


    def generate_jwt(self):
        url = "".join([self.host, '/login'])
        data = {
            "api_token": self.api_token,
            "deployment_id": self.deployment_id
        }
        response = requests.post(url=url, data=json.dumps(data))
        if response.status_code == 200:
            try:
                response = response.json()
                return response["jwt"], response["expires"]
            except Exception:
                raise exceptions.UnauthorizedError("Can't connect to Deployment service {}. Please contact support.".format(self.service))
        else:
            raise exceptions.UnauthorizedError("Unauthorized action on the deployment services")
    
    def _build_headers(self):
        return { "Authorization": "Bearer {}".format(self.jwt)}

    @wrapped_request
    def get(self, path: str, data: dict = None, params: dict = None, stream=False):
        url = "".join([self.host, path])
        return requests.get(url=url, data=data, headers=self._build_headers(), params=params, stream=stream)

    @wrapped_request
    def post(self, path: str, data: dict = None, params: dict = None, files=None):
        url = "".join([self.host, path])
        return requests.post(url=url, data=data, headers=self._build_headers(), params=params, files=files)

    @wrapped_request
    def put(self, path: str, data: dict = None, params: dict = None):
        url = "".join([self.host, path])
        return requests.put(url=url, data=data, headers=self._build_headers(), params=params)

    @wrapped_request
    def delete(self, path: str, data: dict = None, params: dict = None):
        url = "".join([self.host, path])
        return requests.delete(url=url, data=data, headers=self._build_headers(), params=params)
