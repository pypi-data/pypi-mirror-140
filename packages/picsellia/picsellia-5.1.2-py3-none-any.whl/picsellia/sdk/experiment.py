from functools import partial
import json
import logging
import os
from typing import Any, List, Union
from beartype import beartype
from picsellia.decorators import exception_handler
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao
from picsellia import exceptions
from picsellia import utils
import threading
from picsellia import pxl_multithreading as mlt
from pathlib import Path
import requests
from picsellia.sdk.model import Model

logger = logging.getLogger('picsellia')


class Experiment(Dao):

    def __init__(self, connexion: Connexion, project_token: str, id: str, name: str, files: dict) -> None:
        super().__init__(connexion)
        self.project_token = project_token
        self.id = id
        self.name = name
        self.files = files

    @exception_handler
    @beartype
    def get_resource_url_on_platform(self,) -> str:
        """Get platform url of this resource.

        Examples:
            ```python
                print(foo_dataset.get_resource_url_on_platform())
                >>> https://app.picsellia.com/experiment/62cffb84-b92c-450c-bc37-8c4dd4d0f590
            ```

        Returns:
            Url on Platform for this resource
        """
        if self.connexion.base_url is None:
            raise exceptions.PicselliaError('Could not parse platform url. You cannot get platform link')

        return "{}/experiment/{}".format(self.connexion.base_url, self.id)

    @exception_handler
    @beartype
    def update(self, **kwargs) -> None:
        """Update this experiment with given keys.

        Examples:
            ```python
                my_experiment.update(description="First try Yolov5")
            ```
        """
        assert kwargs != {}, "You shall give some keys to update"
        data = json.dumps(kwargs)
        self.connexion.patch('/experiment/{}'.format(self.id), data=data)

    @exception_handler
    @beartype
    def delete(self,) -> None:
        """Delete this experiment

        Examples:
            ```python
                my_experiment.delete()
            ```
        """
        self.connexion.delete('/experiment/{}'.format(self.id))

    @exception_handler
    @beartype
    def list_artifacts(self,) -> List[dict]:
        """List all stored artifacts in the experiment.

        Examples:
            ```python
                artifacts = my_experiment.list_artifacts()
            ```

        Returns:
            A list of artifact infos as dict like
            {
                'id':str,
                'name':str,
                'object_name':str,
                'large':bool
            }
        """
        r = self.connexion.get(
            '/experiment/{}/artifacts'.format(self.id)).json()
        return r["files"]

    @exception_handler
    @beartype
    def delete_all_artifacts(self,) -> None:
        """Delete all stored artifacts for experiment

        :warning: **DANGER ZONE**: This will definitely remove the artifacts from our servers

        Examples:
            ```python
                experiment.delete_all_artifacts()
            ```
        """
        self.connexion.delete('/experiment/{}/artifacts'.format(self.id))

    @exception_handler
    @beartype
    def _create_file(self, name: str = "", object_name: str = "", large: bool = False) -> dict:
        """Creates artifact and attach it to experiment on Platform.

        Examples:
            ```python
                self._create_file()
            ```
        Arguments:
            name (str, optional): filename. Defaults to "".
            object_name (str, optional): s3 object name. Defaults to "".
            large (bool, optional): >5Mb or not. Defaults to False.

        Returns:
            An artifact info as dict like
            {
                "id":str,
                "name":str,
                "object_name":str,
                "large":bool
            }
        """
        data = json.dumps({'0': {
            'name': name,
            'object_name': object_name,
            'large': large
        }
        })
        r = self.connexion.post(
            '/experiment/{}/artifact'.format(self.id), data=data)
        return r.json()

    @exception_handler
    @beartype
    def _create_or_update_file(self, file_name: str = "", path: str = "", **kwargs) -> None:
        """Decides whether to create or update an artifact

        Examples:
            ```python
                self._create_or_update_file()
            ```
        Arguments:
            file_name (str, optional): filename. Defaults to "".
            path (str, optional): full path to file. Defaults to "".
        """
        try:
            stored = self.get_artifact(file_name)
        except exceptions.ResourceNotFoundError:
            stored = []
        if stored == []:
            self._create_file(
                file_name, kwargs["object_name"], kwargs["large"])
        else:
            self._update_artifact(name=file_name, **kwargs)

    @exception_handler
    @beartype
    def store(self, name: str, path: str = None, zip: bool = False) -> None:
        """Store an artifact and attach it to the experiment.

        Examples:
            ```python
                # Zip and store a folder as an artifact for the experiment
                # you can choose an arbitrary name or refer to our 'namespace'
                # for certain artifacts to have a custom behavior

                trained_model_path = "my_experiment/saved_model"
                experiment.store("model-latest", trained_model_path, zip=True)
            ```
        Arguments:
            name (str): name for the artifact. Defaults to "".
            path (str): path to the file or folder. Defaults to None.
            zip (bool, optional): Whether or not to compress the file to a zip file. Defaults to False.

        Raises:
            FileNotFoundError: No file found at the given path
        """
        if path is not None:
            if zip:
                path = utils.zipdir(path)
            filesize = Path(path).stat().st_size
            if filesize < 5*1024*1024:
                filename = os.path.split(path)[-1]
                if name == 'model-latest':  # pragma: no cover
                    object_name = os.path.join(self.id, '0', filename)
                else:
                    object_name = os.path.join(self.id, filename)
                resp = self.connexion._send_file(path, object_name)
                if resp.status_code == 204:
                    self._create_or_update_file(
                        name, path, object_name=object_name, large=False)
            else:
                filename = os.path.split(path)[-1]
                if name == 'model-latest':  # pragma: no cover
                    object_name = os.path.join(self.id, '0', filename)
                else:
                    object_name = os.path.join(self.id, filename)
                resp = self.connexion._send_large_file(path, object_name)
                if resp.status_code == 201:
                    self._create_or_update_file(
                        name, path, object_name=object_name, large=True)
        else:  # pragma: no cover
            if name == 'config':
                if not os.path.isfile(os.path.join(self.config_dir, "pipeline.config")):
                    raise FileNotFoundError("No config file found")
                path = os.path.join(self.config_dir, "pipeline.config")
                object_name = os.path.join(self.id, "pipeline.config")
                resp = self.connexion._send_file(path, object_name)
                if resp.status_code == 204:
                    self._create_or_update_file(
                        name, path, object_name=object_name, large=False)
            elif name == 'checkpoint-data-latest':
                file_list = os.listdir(self.checkpoint_dir)
                ckpt_id = max([int(p.split('-')[1].split('.')[0])
                              for p in file_list if 'index' in p])
                ckpt_data_file = None
                for f in file_list:
                    if "{}.data".format(ckpt_id) in f:
                        ckpt_data_file = f
                if ckpt_data_file is None:
                    raise exceptions.ResourceNotFoundError(
                        "Could not find matching data file with index")
                path = os.path.join(self.checkpoint_dir, ckpt_data_file)
                object_name = os.path.join(self.id, ckpt_data_file)
                resp = self.connexion._send_large_file(path, object_name)
                if resp.status_code == 201:
                    self._create_or_update_file(
                        name, path, object_name=object_name, large=True)
            elif name == 'checkpoint-index-latest':
                file_list = os.listdir(self.checkpoint_dir)
                ckpt_id = max([int(p.split('-')[1].split('.')[0])
                              for p in file_list if 'index' in p])
                ckpt_index = "ckpt-{}.index".format(ckpt_id)
                path = os.path.join(self.checkpoint_dir, ckpt_index)
                object_name = os.path.join(self.id, ckpt_index)
                resp = self.connexion._send_file(path, object_name)
                if resp.status_code == 204:
                    self._create_or_update_file(
                        name, path, object_name=object_name, large=False)
            elif name == 'model-latest':  # pragma: no cover
                file_path = os.path.join(
                    self.exported_model_dir, 'saved_model')
                path = utils.zipdir(file_path)
                object_name = os.path.join(self.id, '0', 'saved_model.zip')
                resp = self.connexion._send_large_file(path, object_name)
                if resp.status_code == 201:
                    self._create_or_update_file(
                        name, path, object_name=object_name, large=True)

    @exception_handler
    @beartype
    def download(self, name: str, target_path: str = '', large: bool = None) -> None:
        """Download an experiment's artifact to a given target_path.

        Examples:
            ```python
                experiment.download("model-latest", "myDir")
                file_list = os.path.listdir("myDir")
                print(file_list)
                >>> ["saved_model.zip"]
            ```
        Arguments:
            name (str): Name of the artifact to download
            target_path (str, optional): Path to download the file to, default to cwd. Defaults to ''.
            large (bool, optional): If download fail with large=False, try again with large=True.
                Defaults to None.
        """
        # Will raise NotFoundError if name is not found
        f = self.get_artifact(name)

        object_name = f["object_name"]
        if large is None:
            large = f["large"]
        filename = os.path.split(object_name)[-1]
        if self.connexion.download_some_file(large, object_name, os.path.join(target_path, filename)):
            logger.info('{} downloaded successfully'.format(filename))
        else:
            logger.error("Could not download {} file".format(filename))

    @exception_handler
    @beartype
    def get_artifact(self, name: str) -> dict:
        """Retrieve an artifact information.

        Examples:
            ```python
                model_artifact = experiment.get_artifact("model-latest")
                print(model_artifact)
                >>> {
                        "id":137,
                        "name":"model-latest",
                        "object_name":"d67924a0-7757-48ed-bf7a-322b745e917e/saved_model.zip",
                        "large":True
                }
            ```
        Arguments:
            name (str): Name of the artifact to retrieve

        Returns:
            List of artifact info as dict like
            {
                "id":str,
                "name":str,
                "object_name":str,
                "large":bool
            }
        """
        r = self.connexion.get(
            '/experiment/{}/artifact?name={}'.format(self.id, name)).json()
        return r["file"]

    @exception_handler
    @beartype
    def _update_artifact(self, name: str, **kwargs) -> None:
        """Update artifact property

        Examples:
            ```python
                self._update_artifact()
            ```
        Arguments:
            name (str): name of the artifact to update
        """
        data = json.dumps(kwargs)
        self.connexion.patch('/experiment/{}/artifact?name={}'.format(self.id, name), data=data).json()

    @exception_handler
    @beartype
    def delete_artifact(self, name: str) -> None:
        """Delete artifact from experiment

        :warning: The file of the artifact will be removed from our servers.

        Examples:
            ```python
                experiment.delete_artifact("saved-model")
            ```
        Arguments:
            name (str): Name of the artifact
        """
        self.connexion.delete('/experiment/{}/artifact?name={}'.format(self.id, name))

    @exception_handler
    @beartype
    def list_logs(self,) -> list:
        """List everything that has been logged.

        List everything that has been logged to an experiment using the .log() method.

        Examples:
            ```python
                logs = experiment.list_logs()
                print(logs[0])
                >>> {
                    "id":137,
                    "date_created":"2021-09-06T10:47:56.569221Z",
                    "last_update":"2021-09-06T10:47:56.569221Z",
                    "name":"parameters",
                    "type":"table",
                    "data":{
                        "batch_size":4,
                        "epochs":1000
                    }
                }
            ```

        Returns:
            A list of logs objects as dict like {
                "id":int,
                "date_created":str,
                "last_update":str,
                "name":str,
                "type":str,
                "data":Union[list, dict]
            }
        """
        r = self.connexion.get('/experiment/{}/logs'.format(self.id)).json()
        return r["logs"]

    @exception_handler
    @beartype
    def delete_all_logs(self,) -> None:
        """Delete everything that has been logged.

        Delete everything that has been logged (using .log()) into this experiment  method.

        Examples:
            ```python
                experiment.delete_all_logs()
            ```
        """
        self.connexion.delete('/experiment/{}/logs'.format(self.id))

    @exception_handler
    @beartype
    def create_log(self, name: str = "", data: Any = {}, type: str = None) -> None:
        """Create log in a experiment.

        Arguments:
            name (str, optional): Name of data. Defaults to "".
            data (dict, optional): Data content. Defaults to {}.
            type (str, optional): Type of data. Defaults to None.
        """
        data = json.dumps({'0': {
            'name': name,
            'data': data,
            'type': type
        }
        })
        self.connexion.put(
            '/experiment/{}/log'.format(self.id), data=data).json()

    @exception_handler
    @beartype
    def get_log(self, name: str) -> Union[dict, list]:
        """Get data for a given log in this experiment

        Examples:
            ```python
                parameters = experiment.get_log("parameters")
                print(parameters)
                >>> {
                    "batch_size":4,
                    "epochs":1000
                }
            ```
        Arguments:
            name (str): name of the log to retrieve

        Returns:
            A dict or list of the log you logged with given name
        """
        r = self.connexion.get(
            '/experiment/{}/log?name={}'.format(self.id, name)).json()
        data_name = r["log"]["name"]
        if not hasattr(self, "logged_log_names"):
            self.logged_log_names = []
        if data_name not in self.logged_log_names:
            self.logged_log_names.append(data_name)

        return r["log"]["data"]

    @exception_handler
    @beartype
    def append_log(self, name: str, **kwargs) -> None:
        """Appends value to log with given name.

        Arguments:
            name (str): name of the log is mandatory

        """
        data = json.dumps(kwargs)
        self.connexion.post(
            '/experiment/{}/log?name={}'.format(self.id, name), data=data).json()

    @exception_handler
    @beartype
    def update_log(self, name: str, **kwargs):
        """Update log with given name.

        Arguments:
            name (str): name of the log.

        Returns:
            An updated log object as dict like {
                "id":int,
                "date_created":str,
                "last_update":str,
                "name":str,
                "type":str,
                "data":Union[list, dict]
            }
        """
        data = json.dumps(kwargs)
        r = self.connexion.patch(
            '/experiment/{}/log?name={}'.format(self.id, name), data=data).json()
        return r

    @exception_handler
    @beartype
    def delete_log(self, name: str) -> None:
        """Delete log with given name in the experiment

        Examples:
            ```python
                experiment.delete_log("parameters")
            ```
        Arguments:
            name (str): name of the log to delete
        """
        self.connexion.delete(
            '/experiment/{}/log?name={}'.format(self.id, name))

    @exception_handler
    @beartype
    def log(self, name: str, data: Any, type: str = None, replace: bool = False) -> None:
        """Log (record) anything to an experiment.

        Record something to an experiment.
        It will then be saved and displayed.

        Examples:
            ```python
                parameters = {
                    "batch_size":4,
                    "epochs":1000
                }
                exp.log("parameters", parameters, type="table")
            ```
        Arguments:
            name (str): Name of the log.
            data (Any): Data to be saved.
            type (str, optional): Type of the data to log.
                                  This will condition how it is displayed in the experiment dashboard. Defaults to None.
            replace (bool, optional): Whether to replace the current value of the log. Defaults to False.

        Raises:
            Exception: Impossible to upload the file when logging an image.
        """
        try:
            if not hasattr(self, "logged_log_names") or name not in self.logged_log_names:
                stored = self.get_log(name)
            else:
                stored = self.logged_log_names
        except exceptions.ResourceNotFoundError:
            stored = []
        if type == 'value':
            data = {'value': data}
        if type == 'image':
            object_name = os.path.join(self.id, data)
            response = self.connexion.get_presigned_url(
                method='post', object_name=object_name, bucket_model=True)
            with open(data, 'rb') as f:
                files = {'file': (data, f)}
                http_response = requests.post(
                    response['url'], data=response['fields'], files=files)
                if http_response.status_code == 204:
                    data = {'object_name': object_name}
                else:  # pragma: no cover
                    raise Exception(
                        "Impossible to log image, can't upload file, please contact us.")
        if stored == []:
            assert type is not None, \
                "Please specify a type for your data vizualization, check the docs to see all available types"
            self.create_log(name, data=data, type=type)
        elif stored != [] and replace:
            self.update_log(name, data=data, type=type)
        elif stored is not [] and not replace and type == 'line':
            threading.Thread(target=self.append_log,
                             kwargs={'name': name, 'data': data, 'type': type}).start()
        elif stored != [] and not replace and type != 'line':
            self.update_log(name, data=data, type=type)

    @exception_handler
    @beartype
    def send_experiment_logging(self, log: Union[str, list], part: str, final: bool = False, special: Union[str, bool, list] = False) -> None:
        """Send a logging experiment to the experiment .

        Arguments:
            log (str): [Log content]
            part (str): [Logging Part]
            final (bool, optional): [True if Final line]. Defaults to False.
            special (bool, optional): [True if special log]. Defaults to False.

        Raises:
            exceptions.NetworkError: [Picsellia Platform not responding]
        """
        if not hasattr(self, 'line_nb'):
            self.line_nb = 0
        to_send = {
            "experiment_id": self.id,
            "line_nb": self.line_nb,
            "log": log,
            "final": final,
            "part": part,
            "special": special
        }
        self.line_nb += 1
        try:
            self.connexion.post(
                '/experiment/{}/logging'.format(self.id), data=json.dumps(to_send))
        except Exception:  # pragma: no cover
            logger.error("Unable to send logs to platform. Log : {}".format(log))

    @exception_handler
    @beartype
    def start_logging_chapter(self, name: str) -> None:
        """Print a log entry to the log .

        Arguments:
            name (str): Chapter name
        """
        print('--#--' + name)

    @exception_handler
    @beartype
    def start_logging_buffer(self, length: int = 1) -> None:
        """Start logging buffer .

        Arguments:
            length (int, optional): Buffer length. Defaults to 1.
        """
        print('--{}--'.format(str(length)))
        self.buffer_length = length

    @exception_handler
    @beartype
    def end_logging_buffer(self,) -> None:
        """End the logging buffer .
        """
        print('---{}---'.format(str(self.buffer_length)))

    @exception_handler
    @beartype
    def update_job_status(self, status: str) -> None:
        """Update the job status.

        Arguments:
            status (str): [Status to send]

        Raises:
            exceptions.NetworkError: [Picsellia Platform not responding]
        """
        to_send = {
            "status": status,
        }
        self.connexion.patch(
            '/experiment/{}/job_status'.format(self.id), data=json.dumps(to_send))

    @exception_handler
    @beartype
    def _convert_response_to_model(self, response: dict) -> Model:
        return Model(
            self.connexion,
            response["model_id"],
            response["network_name"],
            response["type"],
        )

    @exception_handler
    @beartype
    def publish(self, name: str) -> Model:
        """Publish an Experiment as a Model to your registry.

        Examples:
            ```python
                model = experiment.publish("awesome-model")
                model.update(framework="tensorflow")
            ```
        Arguments:
            name (str): Target Name for the model in the registry.

        Returns:
            A (Model) just created from the experiment
        """
        data = json.dumps({
            "name": name
        })
        r = self.connexion.post(
            '/experiment/{}/publish'.format(self.id), data=data).json()
        model = self._convert_response_to_model(r["network"])
        logger.info("Experiment published as a model with name {}".format(name))
        return model

    @exception_handler
    @beartype
    def launch(self, gpus: int = 0) -> None:
        """Launch a job on a remote environment with this experiment.

        :info: The remote environment has to be setup prior launching the experiment.
        It defaults to our remote training engine.

        Examples:
            ```python
                experiment.launch()
            ```
        Arguments:
            gpus (int, optional): Number of GPU to use for the training. Defaults to 0.
        """
        data = json.dumps({
            "gpus": gpus,
        })
        self.connexion.post('/experiment/{}/launch'.format(self.id), data=data)
        logger.info("Job launched successfully")

    def _setup_dirs(self):
        """Create the directories for the project.
        """
        self.base_dir = self.name
        self.metrics_dir = os.path.join(self.base_dir, 'metrics')
        self.png_dir = os.path.join(self.base_dir, 'images')
        self.checkpoint_dir = os.path.join(self.base_dir, 'checkpoint')
        self.record_dir = os.path.join(self.base_dir, 'records')
        self.config_dir = os.path.join(self.base_dir, 'config')
        self.results_dir = os.path.join(self.base_dir, 'results')
        self.exported_model_dir = os.path.join(self.base_dir, 'exported_model')

        if not os.path.isdir(self.name):
            logger.debug("No directory for this project has been found, creating directory and sub-directories...")
            os.mkdir(self.name)

        self._create_dir(self.base_dir)
        self._create_dir(self.png_dir)
        self._create_dir(self.checkpoint_dir)
        self._create_dir(self.metrics_dir)
        self._create_dir(self.record_dir)
        self._create_dir(self.config_dir)
        self._create_dir(self.results_dir)
        self._create_dir(self.exported_model_dir)

    @exception_handler
    @beartype
    def _create_dir(self, dir_name: str) -> None:
        """Create a directory if it doesn t exist.

        Arguments:
            dir_name (str): [directory name]
        """
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)

    @exception_handler
    @beartype
    def download_annotations(self, option: str = "all"):
        """Download the annotation of the dataset attached to the experiment.
            The method stores the dict containing the annotations in experiment.dict_annotations attribute.

        Examples:
            ```python
                annotation_dict = experiment.download_annotations("accepted")
            ```
        Arguments:
            option (str, optional): Whether to download only accepted annotations or every annotations
                . Defaults to "all".

        Raises:
            exceptions.ResourceNotFoundError: No annotations for the attached dataset.

        Returns:
            A dict containing all the annotations in the Picsellia format.
        """
        logger.info("Downloading annotations ...")
        r = self.connexion.get(
            '/experiment/{}/dl_annotations?type={}'.format(self.id, option))
        self.dict_annotations = r.json()
        if self.dict_annotations == None or len(self.dict_annotations.keys()) == 0 or "error" in self.dict_annotations:
            raise exceptions.ResourceNotFoundError("You don't have any annotations")

    @exception_handler
    @beartype
    def download_pictures(self, nb_threads: int = 20) -> None:
        """Download the picture from the dataset attached to the experiment.
            It download only the pictures corresponding to the annotations fetched with the .download_annotations
            method. This prevent to download unnecessary images from the dataset.
            If you wish to to download the whole dataset, we recommend you to use the
            client methods get_dataset() and .download() on the retrieved object.

        Examples:
            ```python
                experiment.download_pictures()
            ```

        Raises:
            exceptions.ResourceNotFoundError: You have to run the .download_annotations() method first.
        """
        if self.dict_annotations == None or "images" not in self.dict_annotations.keys():
            raise exceptions.ResourceNotFoundError(
                "Please run download_annotations function first")

        logger.info("Downloading images ...")

        if not os.path.isdir(self.png_dir):
            os.makedirs(self.png_dir)

        print("-----")
        images = self.dict_annotations["images"]

        f = partial(mlt.mlt_download_list_external_picture, self.png_dir)
        mlt.do_multiprocess_things(f, images, nb_threads)

        print("--*--")
        logger.info("Images downloaded")

    @exception_handler
    @beartype
    def generate_labelmap(self,) -> None:
        """Generate a labelmap in the pbtxt format.

        Generate labelmap in the current working directory and save the dictionnary in
            experiment.label_map

        Examples:
            ```python
                experiment.generate_labelmap()
            ```

        Raises:
            exceptions.ResourceNotFoundError: You have to call the .download_annotations() first.
            exceptions.ResourceNotFoundError: Path to write labelmap file not found.
        """

        logger.debug("Generating labelmap ...")
        if not hasattr(self, 'base_dir'):
            self.base_dir = ""
        self.label_path = os.path.join(self.base_dir, "label_map.pbtxt")

        if "categories" not in self.dict_annotations:
            raise exceptions.ResourceNotFoundError(
                "Please run download_annotations() first")

        categories = self.dict_annotations["categories"]
        labels = {}
        try:
            with open(self.label_path, "w+") as labelmap_file:
                for k, category in enumerate(categories):
                    name = category["name"]
                    labelmap_file.write(
                        "item {\n\tname: \"" + name + "\"" + "\n\tid: " + str(k + 1) + "\n}\n")
                    labels[str(k + 1)] = name
                labelmap_file.close()
            logger.debug("Label_map.pbtxt created @ {}".format(self.label_path))

        except Exception:  # pragma: no cover
            raise exceptions.ResourceNotFoundError(
                "No directory found, please call checkout_network() or create_network() function first")

        self.label_map = labels

    @exception_handler
    @beartype
    def train_test_split(self, prop: float = 0.8) -> tuple:
        """Train test split

        Examples:
            ```python
                experiment.train_test_split()
            ```
        Arguments:
            prop (float, optional): Percentage of data for training set. Defaults to 0.8.

        Raises:
            exceptions.ResourceNotFoundError: No annotations. You have to run the .download_annotations() first.

        Returns:
            A tuple with all of this information (
                list of train picture files,
                list of test picture files,
                list of train picture ids,
                list of test picture ids,
                dict of repartition of classes for train set,
                dict of repartition of classes for test set,
                list of labels
            )
        """
        if "images" not in self.dict_annotations:
            raise exceptions.ResourceNotFoundError(
                "Please download annotations first")

        train_list = []
        eval_list = []
        train_list_id = []
        eval_list_id = []
        index_url = utils.train_valid_split_obj_simple(self.dict_annotations, prop)

        for info, idx in zip(self.dict_annotations["images"], index_url):
            pic_name = os.path.join(self.png_dir, info['external_picture_url'])
            if idx == 1:
                train_list.append(pic_name)
                train_list_id.append(info["internal_picture_id"])
            else:
                eval_list.append(pic_name)
                eval_list_id.append(info["internal_picture_id"])

        logger.debug("{} images used for training and {} images used for validation"
                     .format(len(train_list_id), len(eval_list_id)))

        label_train, label_test, cate = utils.get_labels_repartition_obj_detection(self.dict_annotations, index_url)
        return train_list, eval_list, train_list_id, eval_list_id, label_train, label_test, cate


    @exception_handler
    @beartype
    def _download_artifacts_and_prepare_tree(self, tree : bool, with_artifacts : bool):
        if tree:
            self._setup_dirs()

        if with_artifacts:
            if tree:
                self._download_artifacts_with_tree_for_experiment()
            else:
                self._download_artifacts_without_tree_for_experiment()

    @exception_handler
    @beartype
    def _download_artifacts_with_tree_for_experiment(self):
        for f in self.files:
            object_name = f["object_name"]
            name = f["name"]
            filename = os.path.split(f["object_name"])[-1]
            if name == 'checkpoint-data-latest':  # pragma: no cover
                path = os.path.join(self.checkpoint_dir, filename)
            elif name == 'checkpoint-index-latest':  # pragma: no cover
                path = os.path.join(self.checkpoint_dir, filename)
            elif name == 'model-latest':  # pragma: no cover
                path = os.path.join(self.exported_model_dir, filename)
            elif name == 'config':  # pragma: no cover
                path = os.path.join(self.config_dir, filename)
            else:
                path = os.path.join(self.base_dir, filename)

            if self.connexion.download_some_file(f["large"], object_name, path):
                logger.info('{} downloaded successfully'.format(filename))
            else:
                logger.error("Could not download {} file".format(filename))
    @exception_handler
    @beartype
    def _download_artifacts_without_tree_for_experiment(self):
        self.base_dir = self.name
        self._create_dir(self.base_dir)
        for f in self.files:
            object_name = f["object_name"]
            filename = os.path.split(f["object_name"])[-1]
            if self.connexion.download_some_file(f["large"], object_name, os.path.join(self.base_dir, filename)):
                logger.info('{} downloaded successfully'.format(filename))
            else:
                logger.error("Could not download {} file".format(filename))