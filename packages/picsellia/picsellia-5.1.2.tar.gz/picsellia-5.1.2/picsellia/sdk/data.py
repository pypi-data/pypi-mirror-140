from functools import partial
import json
import logging
import os
import sys
from time import sleep
from typing import List, Union
from beartype import beartype
from picsellia.utils import bcolors, print_next_bar
from picsellia.decorators import exception_handler
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao
from picsellia import exceptions as exceptions
from picsellia import pxl_multithreading as mlt

logger = logging.getLogger('picsellia')


class Data(Dao):

    def __init__(self, connexion: Connexion, datalake_id: str, id: str, external_url: str, internal_key: str):
        super().__init__(connexion)
        self.datalake_id = datalake_id
        self.id = id
        self.external_url = external_url
        self.internal_key = internal_key

    def __str__(self,): return "{}Data{} object with id: {}".format(bcolors.GREEN, bcolors.ENDC, self.id)

    @exception_handler
    @beartype
    def add_tags(self, tags: Union[str, List[str]]) -> None:
        """Add some tags to data

        You can give a string, a list of string.

        Examples:
            ```python
                data.add_tags("bicyle")
                data.add_tags(["car", "truck", "plane"])
            ```
        """
        if isinstance(tags, str):
            tags = [tags]

        assert tags != [], "Given tags are empty. They can't be empty"
        data = {
            'tags': tags,
            'data_ids': [self.id]
        }
        self.connexion.post('/datalake/{}/data/tags'.format(self.datalake_id), data=json.dumps(data))
        logger.info("{} tags added to data (id: {}) in datalake {}.".format(len(tags), self.id, self.datalake_id))

    @exception_handler
    @beartype
    def remove_tags(self, tags: Union[str, List[str]]) -> None:
        """Remove some tags of a data

        You can give a string or a list of string.

        Examples:
            ```python
                data.remove_tags("plane")
                data.remove_tags(["truck", "car"])
            ```
        """
        if isinstance(tags, str):
            tags = [tags]

        assert tags != [], "Given tags are empty. They can't be empty"
        data = {
            'tags': tags,
            'data_ids': [self.id]
        }
        self.connexion.delete('/datalake/{}/data/tags'.format(self.datalake_id), data=json.dumps(data))
        logger.info("{} tags removed from data (id: {}) in datalake {}.".format(len(tags), self.id, self.datalake_id))

    @exception_handler
    @beartype
    def get_tags(self,) -> List[str]:
        """Retrieve the tags of your data.

        Examples:
            ```python
                tags = data.get_tags()
                assert tags == ["bicyle"]
            ```

        Returns:
            List of tags as strings
        """
        r = self.connexion.get('/datalake/{}/data/{}/tags'.format(self.datalake_id, self.id)).json()
        return r["tags"]

    @exception_handler
    @beartype
    def delete(self,) -> None:
        """Delete data and remove it from datalake.

        :warning: **DANGER ZONE**: Be very careful here!

        Remove this data from datalake, and all of the picture linked to this data.

        Examples:
            ```python
                data.delete()
            ```
        """
        data = {
            'data_ids': [self.id]
        }
        self.connexion.delete('/datalake/{}/data/delete'.format(self.datalake_id), data=json.dumps(data))
        logger.info("1 asset (id: {}) deleted from datalake {}.".format(self.id, self.datalake_id))


    @exception_handler
    @beartype
    def download(self, target_path : str = './') -> None:
        """Download

        Examples:
            ```python
                data = clt.get_datalake().fetch_data(1)
                data.download('./pictures/')
            ```

        Arguments:
            target_path (str, optional): Target path where data will be downloaded. Defaults to './'.
        """
        path = os.path.join(target_path, self.external_url)
        if self.connexion.download_some_file(False, self.internal_key, path, False):
            logger.info('{} downloaded successfully'.format(self.external_url))
        else:
            logger.error("Could not download {} file".format(self.internal_key))

class MultiData(Dao):

    def __init__(self, connexion: Connexion, datalake_id: str, data_list: List[Data]):
        super().__init__(connexion)
        self.datalake_id = datalake_id

        if data_list == []:
            raise exceptions.NoDataError("A MultiData can't be empty")

        for data in data_list:
            self.check(data)

        self.data_list = data_list
    
    def __str__(self,): return "{}MultiData{} object, size: {}".format(bcolors.GREEN, bcolors.ENDC,len(self))

    def check(self, v):
        if not isinstance(v, Data):
            raise TypeError(v)

    def __getitem__(self, key) -> Union[Data, 'MultiData']:
        if isinstance(key, slice):
            indices = range(*key.indices(len(self.data_list)))
            data = [self.data_list[i] for i in indices]
            return MultiData(self.connexion, self.datalake_id, data)
        return self.data_list[key]

    def __len__(self): return len(self.data_list)

    def __delitem__(self, i):
        if len(self.data_list) < 2:
            raise exceptions.NoDataError("You can't remove from this list the last data. A MultiData can't be empty")

        del self.data_list[i]

    def __setitem__(self, i, v):
        self.check(v)
        self.data_list[i] = v

    @exception_handler
    @beartype
    def add_tags(self, tags: Union[str, List[str]]) -> None:
        """Add some tags to a bunch of data

        You can give a string, a list of string.

        Examples:
            ```python
                whole_data = datalake.fecth_data()
                whole_data.add_tags("never")
                whole_data.add_tags(["gonna", "give", "you", "up"])
            ```
        """
        if isinstance(tags, str):
            tags = [tags]
        assert tags != [], "Given tags are empty. They can't be empty"
        payload = {
            'tags': tags,
            'data_ids': [data.id for data in self.data_list]
        }
        self.connexion.post('/datalake/{}/data/tags'.format(self.datalake_id), data=json.dumps(payload))
        logger.info("{} tags added to {} data in datalake {}."
                    .format(len(tags), len(self.data_list), self.datalake_id))

    @exception_handler
    @beartype
    def remove_tags(self, tags: Union[str, List[str]]) -> None:
        """Remove some tags on a list of data

        You can give a string, a list of string.

        Examples:
            ```python
                whole_data = datalake.fecth_data()
                whole_data.remove_tags("gonna")
                whole_data.remove_tags(["you"])
            ```
        """
        if isinstance(tags, str):
            tags = [tags]

        assert tags != [], "Given tags are empty. They can't be empty"
        data = {
            'tags': tags,
            'data_ids': [data.id for data in self.data_list]
        }
        self.connexion.delete('/datalake/{}/data/tags'.format(self.datalake_id), data=json.dumps(data))
        logger.info("{} tags removed from {} data in datalake {}."
                    .format(len(tags), len(self.data_list), self.datalake_id))

    @exception_handler
    @beartype
    def delete(self,) -> None:
        """Delete a bunch of data and remove them from datalake.

        :warning: **DANGER ZONE**: Be very careful here!

        Remove a bunch of data from datalake, and all of the picture linked to all data.

        Examples:
            ```python
                whole_data = datalake.fetch_data(quantity=3)
                whole_data.delete()
            ```
        """
        data = {
            'data_ids': [data.id for data in self.data_list]
        }
        self.connexion.delete('/datalake/{}/data/delete'.format(self.datalake_id), data=json.dumps(data))
        logger.info("{} data deleted from datalake {}.".format(len(self.data_list), self.datalake_id))

    @exception_handler
    @beartype
    def download(self, target_path: str = './', nb_threads: int = 20) -> None:
        """Download this multi data in given target path


        Examples:
            ```python
                bunch_of_data = client.get_datalake().fetch_data(25)
                bunch_of_data.download('./downloads/')
            ```
        Arguments:
            target_path (str, optional): Target path where to download. Defaults to './'.
            nb_threads (int, optional): Number of threads used to download. Defaults to 20.
        """
        f = partial(mlt.mlt_download_list_data_or_pics, self.connexion, self.datalake_id, target_path)
        mlt.do_multiprocess_things(f, self.data_list, nb_threads)
        logger.info("{} downloaded in {}".format(len(self.data_list), target_path))
