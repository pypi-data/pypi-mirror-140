import json
import logging
from typing import List
from xml.sax.handler import property_declaration_handler
from beartype import beartype
from picsellia.decorators import exception_handler
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao
from picsellia.sdk.dataset import Dataset
import picsellia.utils as utils
from pathlib import Path
import os
import picsellia.exceptions as exceptions

logger = logging.getLogger('picsellia')


class Model(Dao):

    def __init__(self, connexion: Connexion, id: str, name: str, type: str):
        super().__init__(connexion)
        self.id = id
        self.name = name
        self.type = type

    @exception_handler
    @beartype
    def get_resource_url_on_platform(self,) -> str:
        """Get platform url of this resource.

        Examples:
            ```python
                print(foo_dataset.get_resource_url_on_platform())
                >>> https://app.picsellia.com/model/62cffb84-b92c-450c-bc37-8c4dd4d0f590
            ```

        Returns:
            Url on Platform for this resource
        """
        if self.connexion.base_url is None:
            raise exceptions.PicselliaError('Could not parse platform url. You cannot get platform link')

        return "{}/model/{}".format(self.connexion.base_url, self.id)

    @exception_handler
    @beartype
    def _convert_response_to_deployment(self, response: dict):
        from picsellia.sdk.deployment import Deployment
        return Deployment(
            self.connexion,
            response["pk"],
            response["name"],
            response["oracle_url"] if "oracle_url" in response else None,
            response["serving_url"] if "serving_url" in response else None
        )

    @exception_handler
    @beartype
    def _convert_response_to_dataset(self, response):
        dataset_id = response['dataset_id']
        dataset_name = response['dataset_name']
        dataset_version = response['version']
        return Dataset(self.connexion, dataset_id, dataset_name, dataset_version)

    @exception_handler
    @beartype
    def get_source_dataset(self) -> Dataset:
        """Get source Dataset for an Exported Modela

        Examples:
            ```python
            model = client.get_model(name="my-model")
            dataset = model.get_source_dataset()
            ```

        Returns:
            A (Dataset) that you can use and manipulate
        """
        r = self.connexion.get('/model/{}/source?name={}'.format(self.id, "dataset")).json()
        return self._convert_response_to_dataset(r["dataset"])

    @exception_handler
    @beartype
    def _convert_response_to_experiment(self, response: dict):
        from picsellia.sdk.experiment import Experiment
        return Experiment(
            self.connexion,
            self.id,
            response["id"],
            response["name"],
            response["files"]
        )

    @exception_handler
    @beartype
    def _get_experiment(self, identifier: str,
                        with_artifacts: bool = False, with_logs: bool = False):
        data = {
            'with_artifacts': with_artifacts,
            'with_logs': with_logs
        }
        r = self.connexion.get(
            '/model/{}/source?name={}'.format(self.id, "experiment"), data).json()

        return self._convert_response_to_experiment(r["experiment"])

    @exception_handler
    @beartype
    def get_source_experiment(self, tree: bool= False, with_artifacts: bool = False, with_logs: bool = False):
        """Retrieve an existing experiment.

        You can also to download attached files and setup according project folder tree.

        You must specify either the Experiment's name or its id.

        Examples:
            ```python
                model = client.get_model(name="my-model")
                source_experiment = model.get_source_model(with_artifacts=False, with_logs=False)
            ```
        Arguments:
            tree (bool, optional): Whether to create folder tree or not. Defaults to False.
            with_artifacts (bool, optional): Whether to download every experiment's Artifacts or not. Defaults to False.
            with_logs (bool, optional): Whether to retrieve experiment's Logs or not. Defaults to False.

        Raises:
            Exception: Experiment not found

        Returns:
            An (Experiment) object that you can manipulate
        """
        
        experiment = self._get_experiment(identifier=self.id, with_artifacts=with_artifacts, with_logs=with_logs)

        experiment._download_artifacts_and_prepare_tree(tree, with_artifacts)
        
        return experiment

    @exception_handler
    @beartype
    def delete(self,) -> None:
        """Delete model.

        Delete the model in Picsellia database

        Examples:
            ```python
                model.delete()
            ```
        """
        self.connexion.delete('/model/{}'.format(self.id))
        logger.info("Model {} deleted.".format(self.name))

    @exception_handler
    @beartype
    def update(self, name: str = None, tag: List[str] = None, framework: str = None, private: bool = None, 
                description: str = None, type: str = None, source_dataset: Dataset = None, source_experiment=None, 
                thumb_object_name : str = None, labels: dict = None, base_parameters: dict = None,
                notebook_link: str = None, docker_image: str=None) -> None:
        """Update model.

        Update model parameters in Picsellia database

        Examples:
            ```python
                model.update(description="Very cool model")
            ```
        """
        payload = {
            "network_name": name,
            "tag": tag,
            "framework": framework,
            "private": private,
            "description": description,
            "type": type,
            "dataset": source_dataset.id if source_dataset != None else None,
            "source_experiment": source_experiment.id if source_experiment != None else None,
            "thumb_object_name": thumb_object_name,
            "labels": labels,
            "base_parameters": base_parameters,
            "notebook_link": notebook_link,
            "image_url": docker_image
        }
        filtered = {k:v for k,v in payload.items() if v is not None}
        self.connexion.patch(
            '/model/{}'.format(self.id),
            data=json.dumps(filtered)).json()
        logger.info("Model {} updated.".format(self.name))

    @exception_handler
    @beartype
    def download(self, name: str, dir_path: str = None) -> None:
        """Download file with given name stored in model.

        Examples:
            ```python
                model.download("model-latest", "./data/")
            ```
        Arguments:
            name (str): Name of the file to download
            padir_pathth (str): Directory path where file will be downloaded
        """
        r = self.connexion.get('/model/{}'.format(self.id)).json()
        try:
            object_name = r["model"]["files"][name]
        except KeyError:
            raise FileNotFoundError("Could not find {} into model {}.".format(name, self.name))

        if dir_path is None:
            dir_path = './'

        path = os.path.join(dir_path, object_name)
        if self.connexion.download_some_file(False, object_name, path):
            logger.info('{} downloaded successfully'.format(object_name))
        else:
            logger.error("Could not download {} file".format(object_name))

    @exception_handler
    @beartype
    def store(self, name: str, path: str, zip: bool = False) -> None:
        """Store a file of picsellia into S3.

        Store a file into S3 database.

        Examples:
            ```python
                model.store("model-latest", "lg_test_file.pb")
            ```
        Arguments:
            name (str): Name of file
            path (str): Path of file to store
            zip (bool, optional): If true, zip directory to store it. Defaults to False.

        Raises:
            FileNotFoundError: If file not found in your path
        """
        if not os.path.exists(path):
            raise FileNotFoundError("{} not found".format(path))

        if zip:
            path = utils.zipdir(path)

        filename = os.path.split(path)[-1]
        if name == 'model-latest':
            object_name = os.path.join(self.id, '0', filename)
        else:
            object_name = os.path.join(self.id, filename)

        self.connexion.upload_file(path, object_name)

        data = {
            "filename": name,
            "object_name": object_name
        }
        self.connexion.post('/model/{}/store'.format(self.id), data=json.dumps(data))
        logger.info("File {} stored for model {}".format(name, self.name))

    @exception_handler
    @beartype
    def update_thumbnail(self, thumb_path: str) -> None:
        """Updates the model thumbnail.

        Update the model thumbnail with given file.
        File size shall be less than 5Mb.

        Examples:
            ```python
                model.update_thumb("test.png")
            ```
        Arguments:
            path (str): Path of the thumbnail you want to push

        Raises:
            FileNotFoundError: If there is no file in given path
            exceptions.InvalidQueryError: If file is too large
            exceptions.PicselliaError: If an unexpected error ocurred while uploading file
        """
        if not os.path.isfile(thumb_path):
            raise FileNotFoundError("{} not found".format(thumb_path))

        filesize = Path(thumb_path).stat().st_size

        if filesize > 5*1024*1024:
            raise exceptions.InvalidQueryError("File too large limit is 5Mb")

        filename = os.path.split(thumb_path)[-1]
        object_name = os.path.join(self.id, filename)

        http_response = self.connexion.upload_file(thumb_path, object_name)
        if http_response.status_code != 204:
            raise exceptions.PicselliaError("Could not upload file : {}".format(http_response.text))

        self.update(thumb_object_name=object_name)

    @exception_handler
    @beartype
    def deploy(self, config: dict):
        """Create a (Deployment) for a model. 

        This method allows you to create a (Deployment) on Picsellia. You will then have 
        access to the monitoring dashboard and the model management part!
        If you use our serverless solution, you need to set a `min_det_threshold``
        which correspond to the confidence filter we'll apply to your predictions.
        If you want to visualize and receive 100% of the predictions, set it to 0.0

        Examples:
            Create a serverless deployment whith a min threshold of 0.2
            ```
                model = client.get_model(name="my-awesome-model")
                config = {
                    "min_det_threshold": 0.2
                }
                deployment = model.create_deployment(
                    config=config,
                    )
            ```

        Arguments:
            config (dict): Configuration file for your deployment. You can update it later.


        Returns:
            A (Deployment) that you can manipulate, connected to Picsellia
        """

        data = json.dumps({
            'config': config,
        })
        r = self.connexion.post(
            '/model/{}/deploy'.format(self.id), data=data).json()
        logger.info("Deployment {} created".format(r["deployment"]["name"]))

        return self._convert_response_to_deployment(r["deployment"])

    
