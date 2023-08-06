from functools import partial
import json
import logging
from typing import List, Union
from beartype import beartype
from picsellia.exceptions import PicselliaError
import picsellia.pxl_multithreading as mlt
import picsellia
from picsellia.decorators import exception_handler
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.data import Data, MultiData
from picsellia.sdk.datalake import Datalake
from picsellia.sdk.dataset import Dataset
from picsellia.sdk.deployment import Deployment
from picsellia.sdk.model import Model
from picsellia.sdk.organization import Organization
from picsellia.sdk.project import Project
from picsellia.utils import bcolors

logger = logging.getLogger('picsellia')


class Client:
    """
    Picsellia SDK Client shall be used to communicate with Picsellia services.

    You need an API Token, available on web platform.

    Examples:
        ```python
        client = Client(api_token="a0c9f3bbf7e8bc175494fc44bfc6f89aae3ebcd0", "https://app.picsellia.com/sdk/v1")
        ```

    Attributes:
        organization: current connected (Organization)
        datalake: current connected (Datalake)
    """
    def __init__(self, api_token=None, organization=None,
                 host="https://app.picsellia.com/sdk/v1"):
        """Initialize a connexion to Picsellia platform.

        Arguments:
            api_token (uuid4): Your API token accessible in Profile Page.
                               Defaults to None, Client will try to read environment variable PICSELLIA_TOKEN.
            organization (str, optional): Specify an organization.
                                          Defaults to None, you will be connected to your main Organization.
            host (str, optional): Define a custom host used for platform.
                                  Defaults to "https://app.picsellia.com/sdk/v1".

        Raises:
            exceptions.NetworkError: If Picsellia platform is not responding
        """
        self.connexion = Connexion(host, api_token)

        # Ping platform to get username and version matching api_token
        try:
            ping_response = self.connexion.get('/ping').json()
        except Exception as e:
            raise PicselliaError("Cannot connect to the platform. Please check api_token, organization and host given.\n Error is : {}".format(str(e)))

        sdk_version = ping_response["sdk_version"]

        if sdk_version != picsellia.__version__:
            logger.warning("\033[93mYou are using an outdated version of the picsellia package ({})\033[0m"
                           .format(picsellia.__version__))
            logger.warning("\033[93mPlease consider upgrading to {} with pip install picsellia --upgrade\033[0m"
                           .format(sdk_version))

        # Ask organization to platform
        if organization is not None:
            organization_response = self.connexion.get(
                '/organization?name={}'.format(organization)).json()
        else:
            organization_response = self.connexion.get('/organization').json()
        self.organization = Organization(
            self.connexion, organization_response["organization_id"], organization_response["organization_name"])
        self.datalake = Datalake(
            self.connexion, organization_response["datalake_id"])

        organization_name = "your" if ping_response["username"] == self.organization.name else self.organization.name + "'s"
        logger.info("Hi {}{}{}, welcome back. 🥑\nWorkspace: {}{}{} organization.".format(bcolors.OKBLUE,
                        ping_response["username"], bcolors.ENDC, bcolors.YELLOW, organization_name, bcolors.ENDC))
 
    def __str__(self) -> str:
        return "Client initialized for organization `{}`".format(self.organization.name)

    @exception_handler
    @beartype
    def get_organization(self,) -> Organization:
        """Retrieve organization information currently connected

        Examples:
            ```python
            organization = client.get_organization()
            ```

        Returns:
            The (Organization) of the client that you are using
        """
        return self.organization

    @exception_handler
    @beartype
    def get_datalake(self,) -> Datalake:
        """Retrieve datalake information of organization currently connected

        Examples:
            ```python
            datalake = client.get_datalake()
            ```

        Returns:
            The (Datalake) of the client that you are using
        """
        return self.datalake

    @exception_handler
    @beartype
    def _convert_response_to_dataset(self, response):
        dataset_id = response['dataset_id']
        dataset_name = response['dataset_name']
        dataset_version = response['version']
        return Dataset(self.connexion, dataset_id, dataset_name, dataset_version)
        
    @exception_handler
    @beartype
    def create_dataset(self, name: str, data: Union[Data, MultiData], version: str = 'first',
                       description: str = '', private: bool = True, nb_threads: int = 20) -> Dataset:
        """Create a (Dataset) in this organization.

        This methods allows user to create a dataset into the organization currently connected.
        A dataset takes (Data) coming from organization's (Datalake) and transform it as annotable (Picture).
        User can specify name of the first version, a description and if the dataset is private or not.

        Examples:
            Create a dataset named datatest with data from datalake
            ```
                data = datalake.fetch_data()
                ds = client.create_dataset('datatest', data)
            ```

        Arguments:
            name (str): Name of the dataset. It must be unique in the organization.
            data ((Data) or (MultiData)): A bunch of data to be added to the dataset
            version (str, optional): Name of the first version. Defaults to 'first'.
            description (str, optional): A description of the dataset. Defaults to ''.
            private (bool, optional): Specify if the dataset is private. Defaults to True.

        Returns:
            A (Dataset) that you can manipulate, connected to Picsellia
        """
        assert name != '', 'Dataset name can\'t be empty'

        if isinstance(data, Data):
            data_ids = [data.id]
        else:
            data_ids = [data.id for data in data]

        assert data_ids != [], 'Please specify the assets to add to dataset'

        first_page = data_ids[:20]
        payload = json.dumps({
            'name': name,
            'version': version,
            'data_ids': first_page,
            'description': description,
            'private': private,
        })
        r = self.connexion.post(
            '/organization/{}/dataset'.format(self.organization.id), data=payload).json()
        created_dataset = self._convert_response_to_dataset(r["dataset"])

        # Send other pictures
        if len(data_ids) > 20:
            other_ids = data_ids[20:]

            logger.info("🌐 Dataset is created with 20 pictures ..")
            logger.info("🌐 Adding other pictures to dataset ..")

            f = partial(mlt.mlt_add_data_to_dataset, self.connexion, created_dataset.id)
            mlt.do_multiprocess_things(f, other_ids, nb_threads)

        logger.info("📚 Dataset {} created\n📊 Size: {} pictures\n🌐 Platform url: {}"
                    .format(name, len(data_ids), created_dataset.get_resource_url_on_platform()))
        return created_dataset

    @exception_handler
    @beartype
    def get_dataset(self, name: str, version: str = "latest") -> Dataset:
        """Get a dataset by its name and version

        Examples:
            ```python
            dataset = client.get_dataset('datatest', 'first')
            ```

        Arguments:
            name (str): Name of the dataset
            version (str, optional): Version of the dataset. Defaults to "latest".

        Returns:
            A (Dataset) that you can use and manipulate
        """
        r = self.connexion.get('/organization/{}/dataset/{}/{}'.format(self.organization.id, name, version)).json()
        return self._convert_response_to_dataset(r["dataset"])

    @exception_handler
    @beartype
    def get_dataset_by_id(self, id: str) -> Dataset:
        """Get a dataset by its id

        Examples:
            ```python
            dataset = client.get_dataset('918351d2-3e96-4970-bb3b-420f33ded895')
            ```

        Arguments:
            id (str): id of the dataset to retrieve

        Returns:
            A (Dataset) that you can use and manipulate
        """
        r = self.connexion.get('/dataset/{}'.format(id)).json()
        return self._convert_response_to_dataset(r["dataset"])

    @exception_handler
    @beartype
    def list_datasets(self,) -> List[Dataset]:
        """Retrieve all dataset of current organization

        Examples:
            ```python
            datasets = client.list_datasets()
            ```

        Returns:
            A list of (Dataset) object that belongs to your organization
        """
        r = self.connexion.get(
            '/organization/{}/datasets'.format(self.organization.id)).json()
        return list(map(self._convert_response_to_dataset, r['datasets']))

    @exception_handler
    @beartype
    def search_datasets(self, name: str = None, version: str = None) -> List[Dataset]:
        """Retrieve all dataset of current organization.

        Specifying name and/or version allows user to filter results.

        Examples:
            ```python
            datasets = client.search_datasets()
            datasets = client.search_datasets(name="datatest")
            datasets = client.search_datasets(version="latest")
            datasets = client.search_datasets(name="datatest", version="latest")
            ```

        Returns:
            A list of (Dataset) objects that belongs to your organization, with given name and/or version
        """
        params = {}
        if name is not None:
            params["name"] = name
        if version is not None:
            params["version"] = version
        r = self.connexion.get(
            '/organization/{}/datasets'.format(self.organization.id), params=params).json()
        return list(map(self._convert_response_to_dataset, r['datasets']))

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
    def create_model(self, name: str, type: str) -> Model:
        """Creates a new model.

        Arguments:
            name (str): Model name to create.
            type (str): Model type (classification, detection, segmentation).

        Returns:
            A (Model) object that you can manipulate
        """
        data = json.dumps({
            "name": name,
            "type": type
        })
        r = self.connexion.post(
            '/organization/{}/model'.format(self.organization.id), data=data).json()
        created_model = self._convert_response_to_model(r["model"])
        logger.info("📚 Model {} created\n📊 Type: {}\n🌐 Platform url: {}".format(name, type, created_model.get_resource_url_on_platform()))
        return created_model

    @exception_handler
    @beartype
    def get_model(self, name: str) -> Model:
        """Retrieve a model by its name.

        Examples:
            ```python
                model = client.get_model("foo_model")
            ```
        Arguments:
            name (str): name of the model your are looking for

        Returns:
            A (Model) object that you can manipulate
        """
        params = {"name": name}
        r = self.connexion.get('/organization/{}/model/search'.format(self.organization.id), params=params).json()
        return self._convert_response_to_model(r["model"])

    @exception_handler
    @beartype
    def get_model_by_id(self, id: str) -> Model:
        """Retrieve a model by its id

        Examples:
            ```python
            model = client.get_model_by_id("d8fae655-5c34-4a0a-a59a-e49c89f20998")
            ```
        Arguments:
            id (str): id of the model that you are looking for

        Returns:
            A (Model) object that you can manipulate
        """
        r = self.connexion.get('/model/{}'.format(id)).json()
        return self._convert_response_to_model(r["model"])

    @exception_handler
    @beartype
    def list_models(self,) -> List[Model]:
        """List all models stored in this organization

        This will return all the models stored
        If no project is found, will throw a ResourceNotFoundError

        Examples:
            ```python
            models = client.list_models()
            ```

        Returns:
            A list of all (Model) that belong to this organization
        """
        r = self.connexion.get('/organization/{}/models'.format(self.organization.id)).json()
        return list(map(self._convert_response_to_model, r["models"]))

    @exception_handler
    @beartype
    def _convert_response_to_project(self, response: dict) -> Project:
        return Project(
            self.connexion,
            response["project_id"],
            response["project_name"]
        )

    @exception_handler
    @beartype
    def create_project(self, name: str, description: str = None, dataset: Dataset = None) -> Project:
        """Create a project with given name and parameters

        This project will be registered into used organization.
        You can specify this kwargs to build project :
            - description

        Examples:
            ```python
                foo_dataset = client.get_dataset("foo", "v1") 
                my_project = client.create_project("my_project", description="My first project!", foo_dataset)
            ```
        Arguments:
            name (str): name of the project
            description (str): description of the project
            dataset (Dataset): dataset attached to this project

        Returns:
            A (Project) that you can manipulate to run experiments, or attach dataset
        """
        data = {
            "name": name
        }
        if description != None:
            data["description"] = description

        if dataset != None:
            data["dataset_id"] = dataset.id

        r = self.connexion.post(
            '/organization/{}/project'.format(self.organization.id), data=json.dumps(data)).json()
        created_project = self._convert_response_to_project(r["project"])
        logger.info("📚 Project {} created\n📊 Description: {}\n🌐 Platform url: {}".format(name, description if description is not None else '', created_project.get_resource_url_on_platform()))
        return created_project

    @exception_handler
    @beartype
    def get_project(self, project_name: str) -> Project:
        """Get a project from its name

        Retrieve a project from its name.
        Project must belong to used organization.
        If no project is found, will throw a ResourceNotFoundError

        Examples:
            ```python
                my_project = client.get_project("my_project")
            ```
        Arguments:
            project_name (str): name of the project to retrieve

        Returns:
            A (Project) of your organization, you can manipulate to run experiments, or attach dataset
        """
        r = self.connexion.get('/organization/{}/project'.format(
            self.organization.id), params={"name": project_name}).json()
        return self._convert_response_to_project(r["project"])

    @exception_handler
    @beartype
    def get_project_by_id(self, project_id: str) -> Project:
        """Get a project from its id

        Retrieve a project from its id.
        Project must belong to used organization.
        If no project is found, will throw a ResourceNotFoundError

        Examples:
            ```python
                my_project = client.get_project("2214aacc-b884-41e1-b70f-420c0cd7eefb")
            ```
        Arguments:
            project_id (str): id of the project to retrieve

        Returns:
            A (Project) of your organization, you can manipulate to run experiments, or attach dataset
        """
        r = self.connexion.get('/project/{}'.format(project_id)).json()
        return self._convert_response_to_project(r["project"])

    @exception_handler
    @beartype
    def list_projects(self,) -> List[Project]:
        """List all projects of your organization.

        Retrieve all projects of your organization

        Examples:
            ```python
                projects = client.list_projects()
            ```

        Returns:
            A list of Project of your organization
        """
        r = self.connexion.get(
            '/organization/{}/projects'.format(self.organization.id)).json()
        return list(map(self._convert_response_to_project, r['projects']))


    @exception_handler
    @beartype
    def _convert_response_to_deployment(self, response: dict) -> Deployment:
        return Deployment(
            self.connexion,
            response["pk"],
            response["name"],
            response["oracle_url"] if "oracle_url" in response else None,
            response["serving_url"] if "serving_url" in response else None
        )

    @exception_handler
    @beartype
    def get_deployment(self, name: str) -> Deployment:
        """Get a (Deployment) from its name.

        Examples:
            ```python
                deployment = client.get_deployment(
                    name="awesome-deploy"
                )
            ```
        Arguments:
            name (str): auto-generated name of your deployment.

        Returns:
            A (Deployment) object connected and authenticated to all the services.
        """        
        r = self.connexion.get('/organization/{}/deployment_by_name/search?name={}'.format(
            self.organization.id, name)).json()
        return self._convert_response_to_deployment(r["deployment"])


    @exception_handler
    @beartype
    def get_deployment_by_id(self, id: str) -> Deployment:
        """Get a (Deployment) from its name.

        Examples:
            ```python
                deployment = client.get_deployment_id(
                    id="YOUR DEPLOYMENT ID"
                )
            ```
        Arguments:
            id (str): deployment id displayed in your deployment settings.

        Returns:
            A (Deployment) object connected and authenticated to all the services.
        """
        r = self.connexion.get("/deployment/{}".format(id)).json()
        return self._convert_response_to_deployment(r["deployment"])

    @exception_handler
    @beartype
    def list_deployments(self,) -> List[Deployment]:
        """List all (Deployment) of your organization

        Examples:
            ```python
                our_deployments = client.list_deployments()
            ```
        Arguments:
            id (str): deployment id displayed in your deployment settings.

        Returns:
            List of (Deployment): all deployments object connected and authenticated to all the services.
        """
        r = self.connexion.get("/organization/{}/deployments".format(self.organization.id)).json()
        return list(map(self._convert_response_to_deployment, r['deployments']))
