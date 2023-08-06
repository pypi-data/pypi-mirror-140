import logging
from functools import partial
from typing import List, Union
import picsellia.pxl_multithreading as mlt
from beartype import beartype
from picsellia import exceptions
from picsellia.decorators import exception_handler
from picsellia.exceptions import InvalidQueryError, NoDataError, PicselliaError
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao
from picsellia.sdk.data import Data, MultiData

from picsellia.utils import print_next_bar

logger = logging.getLogger('picsellia')


class Datalake(Dao):

    def __init__(self, connexion: Connexion, id: str):
        super().__init__(connexion)
        self.id = id

    @exception_handler
    @beartype
    def get_resource_url_on_platform(self,) -> str:
        """Get platform url of this resource.

        Examples:
            ```python
                print(foo_dataset.get_resource_url_on_platform())
                >>> https://app.picsellia.com/datalake/62cffb84-b92c-450c-bc37-8c4dd4d0f590
            ```

        Returns:
            Url on Platform for this resource
        """
        if self.connexion.base_url is None:
            raise exceptions.PicselliaError('Could not parse platform url. You cannot get platform link')

        return "{}/datalake/{}".format(self.connexion.base_url, self.id)

    @exception_handler
    @beartype
    def _convert_response_to_data(self, response):
        return Data(
            self.connexion,
            self.id,
            response["picture_id"],
            response["external_url"],
            response["internal_key"]
        )

    @exception_handler
    @beartype
    def upload_data(self, filepaths: Union[str, List[str]],
                    tags: List[str] = [], source: str = 'sdk', nb_threads: int = 20) -> Union[Data, MultiData]:
        """Upload data into this datalake.

        Upload files of pictures, representing data, into a datalake.
        You can give some tags as a list.
        You can give a source for your data.

        Examples:
            ```python
                lake = client.get_datalake()
                lake.upload_data(filepaths=["pics/twingo.png", "pics/ferrari.png"], tags=["car"], source='camera_one')
                lake.upload_data(filepaths="pics/truck.png", tags=["megacar"], source='camera_two')
            ```
        Arguments:
            filepaths (str or List[str]): Filepath of your data
            tags (List[str], optional): Tags that must be given to data. Defaults to [].
            source (str, optional): Source of your data. Defaults to 'sdk'.

        Returns:
            A (Data) object or a (MultiData) object that wraps a list of Data.
            You can manipulate this object returned and add some tags or feeding a Dataset.
        """
        if isinstance(filepaths, str):
            filepaths = [filepaths]

        logger.info("🌎 Starting upload ..") 

        f = partial(mlt.mlt_upload_data, self.connexion, self.id, tags, source)
        shared_data_list = mlt.do_multiprocess_things(f, filepaths, nb_threads)


        if len(shared_data_list) != len(filepaths):
            logger.error("❌ {} data not uploaded. Check readability / check paths".format(len(filepaths) - len(shared_data_list)))

        if len(shared_data_list) == 0:
            raise PicselliaError("Nothing has been uploaded. The image may not have been readable \
                                  or something went wrong while contacting picsellia.")
        elif len(shared_data_list) == 1:
            logger.info("✅ {} data uploaded.".format(shared_data_list[0].external_url))
            return shared_data_list[0]
        else:
            logger.info("✅ {} data uploaded.".format(len(shared_data_list)))
            return MultiData(self.connexion, self.id, shared_data_list)

    @exception_handler
    @beartype
    def list_data(self) -> MultiData:
        """List all pictures of your organization.

        List all pictures in this datalake.
        If there is no data, raise a NoDataError exception.

        Returned object is a MultiData. An object that allows manipulation of a bunch of data.
        You can add tags on them or feed a dataset with them.

        Examples:
            ```python
                lake = client.get_datalake()
                data = lake.list_data()
            ```

        Raises:
            NoDataError: When datalake has no data, raise this exception.

        Returns:
            A (MultiData) object that wraps a list of (Data).
            You can manipulate this object returned and add some tags or feeding a dataset.
        """
        r = self.connexion.get('/datalake/{}/data'.format(self.id)).json()
        list_data = list(map(self._convert_response_to_data, r["data"]))

        if len(list_data) == 0:
            raise NoDataError("No assets found in this datalake")

        return MultiData(self.connexion, self.id, list_data)

    @exception_handler
    @beartype
    def fetch_data(self, quantity: int = -1, tags: Union[str, List[str]] = [], no_tags: bool=False) -> MultiData:
        """Fetch data of datalake

        Use this method if you want a certain amount of data.
        You can precise `quantity` : it will limit the number of data retrieved.
        You can precise some `tags` : retrieved data SHALL HAVE all these tags.

        Examples:
            ```python
                lake = client.get_datalake()
                data = lake.fetch_data(quantity=10, tags="car")
                assert len(data) == 2
            ```
            Notes
            - We uploaded 2 pictures with tag "car" previously
            - Return type is MultiData but behaves like a list: you can slice it (-> MultiData) or get an item (-> Data)

        Arguments:
            quantity (int, optional): Number of data max to retrieve. Defaults to 1.
            tags (str or List[str], optional): List of tags that data shall have. Defaults to [].

        Raises:
            NoDataError: When there is no data to retrieve, raise this exception.

        Returns:
            A (MultiData) object that wraps a list of Data.
            You can manipulate this object returned and add some tags or feeding a dataset.
        """
        if no_tags and tags != []:
            raise InvalidQueryError("Please set no_tags to False if you want to use tags.")
        if isinstance(tags, str):
            tags = [tags]

        params = {
            'quantity': quantity,
            'no_tags': no_tags
        }
        if tags != []:
            params["tags"] = ",".join(tags)
        r = self.connexion.get('/datalake/{}/data'.format(self.id), params=params).json()
        list_data = list(map(self._convert_response_to_data, r["data"]))

        if len(list_data) == 0:
            raise NoDataError("No assets found with tags {}".format(tags))

        return MultiData(self.connexion, self.id, list_data)
