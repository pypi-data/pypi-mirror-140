import base64
from datetime import datetime, timezone
import enum
import io
import json
import logging
from re import I
from typing import Dict, List, Union
from beartype import beartype
from picsellia.decorators import exception_handler
from picsellia.exceptions import ImpossibleAction
from picsellia.sdk import service_connexion
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dataset import Dataset
from picsellia.sdk.project import Project
from picsellia.sdk.model import Model
from picsellia.sdk.dao import Dao
from picsellia.sdk.model import Model
from picsellia.sdk.service_connexion import ServiceConnexion
from picsellia.types.prediction_format import PredictionFormat
import os

logger = logging.getLogger('picsellia')

class ServiceMetrics(str, enum.Enum):

    def __new__(cls, *args, **kargs):
        value = len(cls.__members__) + 1
        obj = str.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, service, is_aggregation):
        self.service = service
        self.is_aggregation = is_aggregation
        return

    PREDICTIONS_OUTLYING_SCORE = 'ae_outlier', False
    PREDICTIONS_DATA = 'metrics', False
    REVIEWS_OBJECT_DETECTION_STATS = 'object_detection', False
    REVIEWS_CLASSIFICATION_STATS = 'classification', False
    REVIEWS_LABEL_DISTRIBUTION_STATS = 'label_distribution', False

    AGGREGATED_LABEL_DISTRIBUTION = 'label_distribution', True
    AGGREGATED_OBJECT_DETECTION_STATS = 'object_detection', True
    AGGREGATED_PREDICTIONS_DATA = 'metrics', True
    AGGREGATED_DRIFTING_PREDICTIONS = 'ks_drift', True


class Deployment(Dao):

    def __init__(self, connexion: Connexion, id: str, name: str, oracle_host : str = None, serving_host : str = None):
        super().__init__(connexion)
        self.id = id
        self.name = name
        
        if oracle_host != None:
            self.oracle_connexion = ServiceConnexion('oracle', self.connexion.api_token, oracle_host, id)

        if serving_host != None:
            self.serving_connexion = ServiceConnexion('serving', self.connexion.api_token, serving_host, id)

    def retrieve_information(self) -> dict:
        """Retrieve some information about this deployment from service.

        Examples:
            ```python
                print(my_deployment.retrieve_information())
                >>> {

                }
            ```
        """
        assert self.oracle_connexion != None, 'This action cannot be done'

        return self.oracle_connexion.get(path='/deployment/{}'.format(self.id)).json()

    def delete(self,) -> None:
        self.connexion.delete('/deployment/{}/delete'.format(self.id))
        logging.info("Deployment {} deleted.".format(self.name))
        return None

    def predict(self, fpath: str) -> dict:
        """_summary_

        Examples:
            ```python
                deployment = client.get_deployment(
                    name="awesome-deploy"
                )
                deployment.predict()
            ```
        Arguments:
            fpath (str): path to the image to predict

        Returns:
            (dict): _description_
        """        
        assert self.serving_connexion != None, 'This action cannot be done'

        try:
            files = {'media': open(fpath, 'rb')}
        except FileNotFoundError as e:
            logging.error("File {} does not exists".format(fpath))
        return self.serving_connexion.post(path='/predict/{}'.format(self.id), files=files).json()

    def init_feedback_loop(self, dataset: Dataset) -> None:
        """Initialize the Feedback Loop for a Deployment.
        This way, you will be able to attached reviewed predictions to the Dataset.
        This is a great option to increase your training set with quality data.

        Examples:
            ```python
                dataset = client.get_dataset(
                    name="my-dataset",
                    version="latest"
                )
                deployment = client.get_deployment(
                    name="awesome-deploy"
                )
                deployment.init_feedback_loop(
                    dataset
                )
            ```
        Arguments:
            dataset (Dataset): a connected (Dataset)
        """        
        data = {
            "dataset_id": dataset.id,
        }
        self.connexion.post('/deployment/{}/pipeline/feedback_loop'.format(self.id), data=json.dumps(data))
        logger.info("Feedback loop setup for deployment {}\nNow you will be able to add predictions\nto dataset: {}/{}".format(self.name, dataset.name, dataset.version))
        return

    def update_feedback_loop(self, dataset: Dataset) -> None:
        """Update the Feedback Loop for a Deployment.
        This way, you will be able to attached reviewed predictions to the updated Dataset.
        This is a great option to increase your training set with quality data.

        Examples:
            ```python
                dataset = client.get_dataset(
                    name="my-dataset",
                    version="new-version"
                )
                deployment = client.get_deployment(
                    name="awesome-deploy"
                )
                deployment.update_feedback_loop(
                    dataset
                )
            ```
        Arguments:
            dataset (Dataset): a connected (Dataset)
        """        
        data = {
            "dataset_id": dataset.id,
            "disable": False
        }
        self.connexion.post('/deployment/{}/pipeline/feedback_loop/edit'.format(self.id), data=json.dumps(data))
        logger.info("Feedback loop setup for deployment {}\nNow you will be able to add predictions\nto dataset: {}/{}".format(self.name, dataset.name, dataset.version))
        return

    
    def init_continuous_training(self, project: Project, dataset: Dataset, model: Model, 
                                    parameters: dict, training_type: str = None, 
                                        scan_config : dict = None, policy: str = None, 
                                                feedback_loop_trigger: int = None) -> None:
        """Initiliaze and activate the continuous features of picsellia. 🥑
           A Training will be triggered using the configured Dataset
           and Model as base whenever your Deployment pipeline hit the trigger.

        Examples:
            # Let's initialize a continuous training pipeline that will be trigger 
            # every 150 new predictions reviewed by your team. 
            # We will use the same training parameters as those used when building the first model.

            ```python
                project = client.get_project(name="my-project")
                dataset = project.get_dataset(name="my-dataset", version="latest")
                model = client.get_model(name="my-model")
                deployment = client.get_deployment("awesome-deploy")
                experiment = model.get_source_experiment()
                parameters = experiment.get_log('parameters')
                training_type = "experiment"
                feedback_loop_trigger = 150
                deployment.init_continuous_training(
                    project, dataset, model,
                    parameters, training_type, 
                    feedback_loop_trigger=feedback_loop_trigger
                )
            ```

        Arguments:
            project (Project): The project that will host your pipeline. 
            dataset (Dataset): The Dataset that will be used as training data for your training.
            model (Model): The exported Model to perform transfert learning from.
            parameters (dict): Training parameters.
            training_type (str, optional): Either `experiment` or `scan`.
            scan_config (dict, optional): Scan configuration dict. [more info](https://doc.picsellia.com/docs/initialize-a-scan)
            policy (str, optional): Early Stopping policy.
            feedback_loop_trigger (int, optional): Number of images that need to be review to trigger the training.
        """        
        data = {
            "project_id": project.id,
            "dataset_id": dataset.id,
            "model_id": model.id,
            "parameters": parameters,
            "training_type": training_type,
            "scan_config": scan_config,
            "policy": policy,
            "fl_trigger": feedback_loop_trigger
        }
        
        self.connexion.post('/deployment/{}/pipeline/continuous_training'.format(self.id), data=json.dumps(data))
        logger.info("Continuous training setup for deployment {}\nNow you will be able to add predictions\nto dataset: {}/{}".format(self.name, dataset.name, dataset.version))
        return

    def activate_continuous_training(self,):
        """Activate your continuous training pipeline.

        Examples:
            ```python
                deployment = client.get_deployment("awesome-deploy")
                deployment.activate_continuous_training()
            ```
        """
        data = {
            "active": True
        }
        self.connexion.post('/deployment/{}/pipeline/continuous_training/toggle'.format(self.id), data=json.dumps(data))
        logger.info("Continuous training for deployment {} activated.".format(self.name))
        return

    def deactivate_continuous_training(self,):
        """Deactivate your continuous training pipeline.

        Examples:
            ```python
                deployment = client.get_deployment("awesome-deploy")
                deployment.deactivate_continuous_training()
            ```
        """
        data = {
            "active": False
        }   
        self.connexion.post('/deployment/{}/pipeline/continuous_training/toggle'.format(self.id), data=json.dumps(data))
        logger.info("Continuous training for deployment {} deactivated.".format(self.name))
        return

    def get_stats(self, service : ServiceMetrics, model: Model = None, from_timestamp: float = None, to_timestamp: float = None,
                  since: int = None, includes : List[str] = None, excludes : List[str] = None, tags : str = None) -> dict:
        """Retrieve stats of this deployment stored in Picsellia environment.

        Mandatory param is "service" an enum of type ServiceMetrics. Values possibles are : 
            PREDICTIONS_OUTLYING_SCORE
            PREDICTIONS_DATA
            REVIEWS_OBJECT_DETECTION_STATS
            REVIEWS_CLASSIFICATION_STATS
            REVIEWS_LABEL_DISTRIBUTION_STATS

            AGGREGATED_LABEL_DISTRIBUTION
            AGGREGATED_OBJECT_DETECTION_STATS
            AGGREGATED_PREDICTIONS_DATA
            AGGREGATED_DRIFTING_PREDICTIONS

        For aggregation, computation may not have been done by the past.
        You will need to force computation of these aggregations and retrieve them again.


        Examples:
            ```python
                my_deployment.get_stats(ServiceMetrics.PREDICTIONS_DATA)
                my_deployment.get_stats(ServiceMetrics.AGGREGATED_DRIFTING_PREDICTIONS, since=3600)
                my_deployment.get_stats(ServiceMetrics.AGGREGATED_LABEL_DISTRIBUTION, model_id=1239012)

            ```
        Arguments:
            service (str): service queried
            model (Model, optional): Model that shall be used when retrieving data. Defaults to None.
            from_timestamp (float, optional): System will only retrieve prediction data after this timestamp. Defaults to None.
            to_timestamp (float, optional): System will only retrieve prediction data before this timestamp. Defaults to None.
            since (int, optional): System will only retrieve prediction data that are in the last seconds given by this value. Defaults to None.
            includes (List[str], optional): Research will includes these ids and excludes others. Defaults to None.
            excludes (List[str], optional): Research will excludes these ids. Defaults to None.
            tags (str, optional): Research will be done filtering by tags. Defaults to None.
                                  tags need to be parsable like "tag1:value,tag2:value2"

        Returns:
            A dict with queried statistics about the service you asked
        """
        assert self.oracle_connexion != None, "You can't use this function with this deployment. Please contact the support."
        
        filter = self._build_filter(service=service.service, model=model, from_timestamp=from_timestamp, to_timestamp=to_timestamp,
                                    since=since, includes=includes, excludes=excludes, tags=tags)

        if service.is_aggregation:
            resp = self.oracle_connexion.get('deployment/{}/stats'.format(self.id), data=filter)
            if "infos" in resp and "info" in resp["infos"]:
                logging.info('This computation is outdated or has never been done.\n" \
                             You can compute it again by calling launch_computation with exactly the same params.')
        else:
            return self.oracle_connexion.get('deployment/{}/predictions/stats'.format(self.id), data=filter)


    def _build_filter(service : str, model : Model = None, from_timestamp: float = None, to_timestamp: float = None,
                  since: int = None, includes : List[str] = None, excludes : List[str] = None, tags : str = None) -> dict:
        
        filter = { "service" : service }

        if model != None:
            filter["model_id"] = model.id

        if from_timestamp != None:
            filter["from_timestamp"] = from_timestamp

        if to_timestamp != None:
            filter["to_timestamp"] = to_timestamp

        if since != None:
            filter["since"] = since

        if includes != None:
            filter["includes"] = includes

        if excludes != None:
            filter["excludes"] = excludes

        if tags != None:
            filter["tags"] = tags

        return filter


    def monitor(self, model : Model, image_path : str, latency : float, picture_id : str, filename: str, height : int, width: int,
                source : str, tags: Dict[str, Union[str, int, float]], prediction : PredictionFormat,
                shadow_model : Model = None, shadow_latency : float = None, shadow_raw_predictions : PredictionFormat = None):
        with open(image_path, "rb") as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode('utf-8')

        data = {
            "picture_id": picture_id,
            "filename": filename,
            "raw_predictions": prediction.to_payload(),
            "latency": latency,
            'height': height,
            'width': width,
            'source': source,
            'model_type': model.type,
            "model": model.id,
            "timestamp": str(datetime.now(datetime.timezone.utc).timestamp()),
            "tags": tags,
            "image": encoded_image
        }

        if shadow_model != None:
            if shadow_latency == None or shadow_raw_predictions == None:
                raise ImpossibleAction('Shadow latency and shadow raw predictions shall be defined if you want to push a shadow model result')
            data["shadow_model"] = shadow_model.id
            data["shadow_latency"] = shadow_latency
            data["shadow_raw_predictions"] = shadow_raw_predictions


        return self.oracle_connexion.get('deployment/{}/add'.format(self.id), data=data)
