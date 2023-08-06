import logging
import os
from pathlib import Path
import sys
from typing import Any
from beartype import beartype
import requests
import json
from picsellia.decorators import exception_handler, retry
from picsellia.utils import check_status_code, print_line_return, print_next_bar
import picsellia.exceptions as exceptions
from urllib.parse import urlsplit

logger = logging.getLogger('picsellia')


class Connexion:

    def __init__(
            self, host, api_token: str = None) -> None:
        self.host = host
        if host[-1] == "/":
            self.host = host[:-1]

        if api_token is None:
            if "PICSELLIA_TOKEN" in os.environ:
                token = os.environ["PICSELLIA_TOKEN"]
            else:
                raise Exception(
                    "Please set up the PICSELLIA_TOKEN environement variable or specify your token")
        else:
            token = api_token

        self.api_token = token
        self.content_type = "application/json"
        self.headers = {"Authorization": "Token " + token, "Content-type": self.content_type}

        try:
            splitted_url = urlsplit(self.host)
            self.base_url = "{}://{}".format(splitted_url.scheme, splitted_url.netloc)
        except Exception:
            self.base_url = None

    def wrapped_request(f):
        def decorated(*args, **kwargs):
            try:
                resp = f(*args, **kwargs)
            except Exception:
                raise exceptions.NetworkError(
                    "Server is not responding, please check your host.")
            check_status_code(resp)
            return resp

        return decorated

    @wrapped_request
    def get(self, path: str, data: dict = None, params: dict = None, stream=False):
        url = "".join([self.host, path])
        return requests.get(url=url, data=data, headers=self.headers, params=params, stream=stream)

    @wrapped_request
    def post(self, path: str, data: dict = None, params: dict = None, files: Any = None):
        url = "".join([self.host, path])
        return requests.post(url=url, data=data, headers=self.headers, params=params, files=files)

    @wrapped_request
    def put(self, path: str, data: dict = None, params: dict = None):
        url = "".join([self.host, path])
        return requests.put(url=url, data=data, headers=self.headers, params=params)

    @wrapped_request
    def patch(self, path: str, data: dict = None, params: dict = None):
        url = "".join([self.host, path])
        return requests.patch(url=url, data=data, headers=self.headers, params=params)

    @wrapped_request
    def delete(self, path: str, data: dict = None, params: dict = None):
        url = "".join([self.host, path])
        return requests.delete(url=url, data=data, headers=self.headers, params=params)

    @exception_handler
    @beartype
    def get_presigned_url(self, method: str, object_name: str, bucket_model: bool = False) -> dict:
        to_send = {
            "method": method,
            "object_name": object_name,
            "bucket_model": bucket_model
        }
        data = json.dumps(to_send)
        url = self.host + '/generate_presigned_url'
        r = requests.post(url, data=data, headers=self.headers)

        if r.status_code != 200:
            raise exceptions.PicselliaError("Errors while getting a presigned url")

        r = r.json()
        if "url" not in r:
            raise exceptions.PicselliaError("Errors while getting a presigned url. Unparsable response")

        return r

    @retry((KeyError, ValueError, exceptions.PicselliaError), total_tries=4)
    @exception_handler
    @beartype
    def push_to_s3(self, path: str, internal_key: str) -> requests.Response:
        response = self.get_presigned_url("post", object_name=internal_key)
        with open(path, 'rb') as file:
            r = requests.post(response["url"], data=response["fields"], files={'file': (internal_key, file)})

        if r.status_code != 204:
            raise exceptions.PicselliaError("Could not retrieve presigned url")

        return r

    @exception_handler
    @beartype
    def download_some_file(self, is_large: bool, object_name: str, path: str, bucket_model: bool = True):

        if is_large:
            return self._download_large_file(object_name, path, bucket_model)
        
        # If file shall not be large
        try:
            return self._download_file(object_name, path, bucket_model)
        except Exception:
            return self._download_large_file(object_name, path, bucket_model)
    
    @exception_handler
    @beartype
    def _download_file(self, object_name: str, target_path: str, bucket_model: bool = True) -> bool:
        """Download a file from S3.

        Arguments:
            object_name (str): Object s3 Key name to download
            target_path (str): Target path of file to download object
        """
        response = self.get_presigned_url('get', object_name, bucket_model=bucket_model)

        parent_path = Path(target_path).parent.absolute()
        if not os.path.exists(parent_path):
            os.makedirs(parent_path)

        with open(target_path, 'wb') as handler:
            response = requests.get(response["url"])
            total_length = response.headers.get('content-length')
            if total_length is None:
                return False

            handler.write(response.content)
            return True

    @exception_handler
    @beartype
    def _download_large_file(self, object_name: str, path: str, bucket_model: bool = True) -> bool:
        """Downloads a large file from the server.

        Arguments:
            object_name (str): [Object s3 Key name to download]
            path (str): [Direction to download it]
        """

        response = self.get_presigned_url('get', object_name, bucket_model=bucket_model)

        parent_path = Path(path).parent.absolute()
        if not os.path.exists(parent_path):
            os.makedirs(parent_path)
            
        sys.stdout.write("-----")
        with open(path, 'wb') as handler:
            response = requests.get(response["url"], stream=True)
            total_length = response.headers.get('content-length')
            if total_length is None:
                return False
            total_length = int(total_length)
            dl = 0
            count = 0
            last_done = -1
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                handler.write(data)
                done = int(50 * dl / total_length)
                if done != last_done:
                    print_next_bar(dl, total_length)
                    last_done = done
                count += 1
        sys.stdout.write("--*--")
        print_line_return()
        return True

    @exception_handler
    @beartype
    def _init_multipart(self, object_name: str) -> str:
        """Initialize a multipart push

        Arguments:
            object_name (str): object name to download

        Returns:
            The upload id if everything went well
        """

        to_send = {"object_name": object_name}
        url = self.host + '/init_multipart_upload'

        try:
            r = requests.get(url, data=json.dumps(to_send))
        except Exception:
            raise exceptions.NetworkError("Server is not responding, please check your host.")

        if r.status_code != 200 or "upload_id" not in r.json():
            raise exceptions.NetworkError(
                "Impossible to init a multipart upload because :\n{}".format(r.text))

        r = r.json()
        if "upload_id" not in r:
            raise exceptions.NetworkError("Response when initiating multipart is unparsable")

        return r["upload_id"]

    @exception_handler
    @beartype
    def _get_url_for_part(self, upload_id, no_part, object_name) -> str:
        """Get a pre-signed url to upload a part of Checkpoints or SavedModel
        Raises:
            NetworkError: If it impossible to initialize upload

        """
        to_send = {
            "object_name": object_name,
            "upload_id": upload_id,
            "part_no": no_part
        }
        url = self.host + '/generate_post_part_url'
        try:
            r = requests.post(url, data=json.dumps(to_send))
        except Exception:
            raise exceptions.NetworkError("Impossible to get an url for part")

        if r.status_code != 200:
            raise exceptions.NetworkError("Impossible to get an url.. because :\n{}".format(r.text))

        r = r.json()
        if "url" not in r:
            raise exceptions.NetworkError("Response when getting an url for a part is unparsable")

        return r["url"]

    @exception_handler
    @beartype
    def _upload_parts(self, upload_id, file_path, object_name):
        if not os.path.exists(file_path):
            raise exceptions.PicselliaError("Impossible to upload part in an empty filepath")

        max_size = 5 * 1024 * 1024
        file_size = os.path.getsize(file_path)
        upload_by = int(file_size / max_size) + 1
        sys.stdout.write("-----")
        with open(file_path, 'rb') as f:

            parts = []
            for part in range(1, upload_by + 1):
                url = self._get_url_for_part(upload_id, part, object_name)
                try:
                    file_data = f.read(max_size)
                except Exception:
                    raise exceptions.NetworkError("Impossible to put part no {}".format(part))

                try:
                    res = requests.put(url, data=file_data)
                except Exception:
                    raise exceptions.NetworkError("Impossible to get an url for part")

                if res.status_code != 200:
                    raise exceptions.NetworkError(
                        "Impossible to put part no {}\n because {}".format(part, res.text))
                etag = res.headers['ETag']
                parts.append({'ETag': etag, 'PartNumber': part})
                print_next_bar(part, upload_by)
        sys.stdout.write("--*--")
        print_line_return()
        return parts

    @exception_handler
    @beartype
    def _complete_part_upload(self, upload_id, parts, object_name):
        """
            Complete the upload a part of Checkpoints or SavedModel
            Raises:
                NetworkError: If it impossible to initialize upload
        """
        to_send = {
            "object_name": object_name,
            "upload_id": upload_id,
            "parts": parts,
        }
        url = self.host + '/complete_part_upload'
        try:
            r = requests.post(url, data=json.dumps(to_send), headers=self.headers)
        except Exception:
            raise exceptions.NetworkError("Impossible to get an url..")

        if r.status_code != 201:
            raise exceptions.NetworkError("Impossible to get an url.. because :\n{}".format(r.text))

        return r

    @exception_handler
    @beartype
    def _send_large_file(self, path: str = None, object_name: str = None):
        """Uploads a large file to the experiment.

        Arguments:
            path (str, optional): [Path to the file to upload]. Defaults to None.
            name (str, optional): [Name of the file]. Defaults to None.
            object_name (str, optional): [Key name for S3 storage]. Defaults to None.
        """
        upload_id = self._init_multipart(object_name)
        parts = self._upload_parts(upload_id, path, object_name)
        response = self._complete_part_upload(upload_id, parts, object_name)
        return response

    @exception_handler
    @beartype
    def _send_file(self, path: str, object_name: str):
        """Uploads a small file to the experiment.

        Arguments:
            path (str, optional): [Path to the file to upload]
            name (str, optional): [Name of the file]
            object_name (str, optional): [Key name for S3 storage]
            network_id (str, optional): [ID of the network to attach file]
        """
        if not os.path.isfile(path):
            raise FileNotFoundError("{} not found".format(path))

        response = self.get_presigned_url(method='post', object_name=object_name, bucket_model=True)

        with open(path, 'rb') as f:
            files = {'file': (path, f)}
            try:
                http_response = requests.post(response['url'], data=response['fields'], files=files)
            except Exception:
                raise exceptions.NetworkError("Impossible to get an url for part")

        return http_response

    @exception_handler
    @beartype
    def upload_file(self, path: str, object_name: str) -> requests.Response:
        """Upload a single file to the server.
        If file is bigger than 5Mb, it will send it by multipart.

        Arguments:
            path (str): [Absolute path to the file]
            object_name (str): [Bucket prefix s3]

        Raises:
            FileNotFoundError: [File does not exists]
            exceptions.NetworkError: [Platform does not respond]

        Returns:
            A requests.Response of the send file http request
        """
        if not os.path.isfile(path):
            raise FileNotFoundError("{} not found".format(path))

        filesize = Path(path).stat().st_size
        if filesize <= 5*1024*1024:
            response = self._send_file(path, object_name)
            if response.status_code != 204:
                raise exceptions.PicselliaError("Could not upload file : {}".format(response.text))
        else:
            upload_id = self._init_multipart(object_name)
            parts = self._upload_parts(upload_id, path, object_name)
            response = self._complete_part_upload(upload_id, parts, object_name)

        return response
