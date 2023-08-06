from datetime import date
from functools import partial
import json
import logging
import os
from typing import Dict, List, Union
from beartype import beartype
from picsellia.decorators import exception_handler
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao
import picsellia.exceptions as exceptions
from picsellia.utils import bcolors
from picsellia import pxl_multithreading as mlt
logger = logging.getLogger('picsellia')


class Picture(Dao):

    def __init__(self, connexion: Connexion, id: str, external_url: str, internal_key: str):
        super().__init__(connexion)
        self.id = id
        self.external_url = external_url
        self.internal_key = internal_key

    @exception_handler
    @beartype
    def add_annotation(self, data: List[dict], creation_date: date = None, duration: float = None,
                       reviewed: bool = None, is_accepted: bool = None, is_skipped: bool = None,
                       nb_instances: int = None) -> None:
        """Add annotation to this picture.

        Data of annotation is mandatory and its type will be checked here before sending it to platform.
        Other information will be stored in Picsellia database.

        Examples:
            ```
                data = [{
                    "type":"rectangle",
                    "label":"car",
                    "rectangle":{
                        "top":45,
                        "left":120,
                        "width":50,
                        "height":50
                    }
                }]
                pic.add_annotation(data)
            ```
        Arguments:
            data (List[dict]): List of annotations.
            creation_date (date, optional): Creation date; Shall be a 'date' type. Defaults to None.
            duration (float, optional): Duration. Defaults to None.
            reviewed (bool, optional): Reviewed. Defaults to None.
            is_accepted (bool, optional): Is accepted. Defaults to None.
            is_skipped (bool, optional): Is skipped. Defaults to None.
            nb_instances (int, optional): Number of instances. Defaults to None.

        Raises:
            exceptions.TyperError: When annotation is not parsable
        """
        if data == []:
            raise exceptions.TyperError("Data shall not be empty")

        for annot in data:
            if annot == {}:
                raise exceptions.TyperError("An annotation shall not be empty")
            annot_keys = annot.keys()
            if "type" not in annot_keys:
                raise exceptions.TyperError(
                    "'type' key missing from object {}".format(annot))
            supported_types = ["classification", "rectangle", "polygon"]
            if annot["type"] not in supported_types:
                raise exceptions.TyperError(
                    "type must be of {}, found '{}'".format(supported_types, annot["type"]))
            if "label" not in annot_keys:
                raise exceptions.TyperError(
                    "'label' key missing from object {}".format(annot))
            if annot["type"] == "classification":
                pass
            elif annot["type"] == "rectangle":
                if "rectangle" not in annot_keys:
                    raise exceptions.TyperError(
                        "missing 'rectangle' key for object {}".format(annot))
                rect = annot["rectangle"]
                if "top" not in rect.keys():
                    raise exceptions.TyperError(
                        "missing 'top' key in rectangle for object {}".format(annot))
                if "left" not in rect.keys():
                    raise exceptions.TyperError(
                        "missing 'left' key in rectangle for object {}".format(annot))
                if "width" not in rect.keys():
                    raise exceptions.TyperError(
                        "missing 'width' key in rectangle for object {}".format(annot))
                if "height" not in rect.keys():
                    raise exceptions.TyperError(
                        "missing 'height' key in rectangle for object {}".format(annot))
            elif annot["type"] == "polygon":
                if "polygon" not in annot_keys:
                    raise exceptions.TyperError(
                        "missing 'polygon' key for object {}".format(annot))
                poly = annot["polygon"]
                if type(poly) != dict:
                    raise exceptions.TyperError(
                        "'polygon' must be a dict, not {}".format(type(poly)))
                if "geometry" not in poly.keys():
                    raise exceptions.TyperError(
                        "missing 'geometry' key in 'polygon' for object {}".format(annot))
                geometry = poly["geometry"]
                if type(geometry) != list:
                    raise exceptions.TyperError(
                        "'geometry' must be a list, not {}".format(type(geometry)))
                if len(geometry) < 3:
                    raise exceptions.TyperError(
                        "polygons can't have less than 3 points")
                for coords in geometry:
                    if type(coords) != dict:
                        raise exceptions.TyperError(
                            "coordinates in 'geometry' must be a dict, not {}".format(type(coords)))
                    if 'x' not in coords.keys():
                        raise exceptions.TyperError(
                            "missing 'x' coordinate in 'geometry' for object {}".format(annot))
                    if 'y' not in coords.keys():
                        raise exceptions.TyperError(
                            "missing 'y' coordinate in 'geometry' for object {}".format(annot))

        payload = {"data": data}
        if creation_date is not None:
            payload["creation_date"] = creation_date.isoformat()
        if duration is not None:
            payload["duration"] = duration
        if reviewed is not None:
            payload["reviewed"] = reviewed
        if is_accepted is not None:
            payload["is_accepted"] = is_accepted
        if is_skipped is not None:
            payload["is_skipped"] = is_skipped
        if nb_instances is not None:
            payload["nb_instances"] = nb_instances
        self.connexion.put('/picture/{}/annotations'.format(self.id), data=json.dumps(payload)).json()

    @exception_handler
    @beartype
    def delete_annotations(self,) -> None:
        """Delete all annotations of a picture.

        :warning: **DANGER ZONE**: Be careful here !

        Examples:
            ```python
                pic.delete_annotations()
            ```
        """
        self.connexion.delete('/picture/{}/annotations'.format(self.id))

    @exception_handler
    @beartype
    def list_annotations(self,) -> List[Dict]:
        """List all annotation of a picture

        Examples:
            ```python
                annotations = pic.list_annotations()
            ```

        Returns:
            A list of dict representing annotations
        """
        r = self.connexion.get('/picture/{}/annotations'.format(self.id)).json()
        return r["annotations"]

    @exception_handler
    @beartype
    def delete(self,) -> None:
        """Delete picture from its dataset

        :warning: **DANGER ZONE**: Be very careful here!

        Remove this picture and its annotation from the dataset it belongs

        Examples:
            ```python
                pic.delete()
            ```
        """
        self.connexion.delete('/picture/{}'.format(self.id))
        logger.info("Picture {} removed from dataset".format(self.id))

    @exception_handler
    @beartype
    def download(self, target_path : str = './') -> None:
        """Download this picture into given target path

        Examples:
            ```python
                pic = foo_dataset.get_picture('bar.png')
                pic.download('./pictures/')
            ```

        Arguments:
            target_path (str, optional): Target path where picture will be downloaded. Defaults to './'.
        """
        path = os.path.join(target_path, self.external_url)
        if self.connexion.download_some_file(False, self.internal_key, path, False):
            logger.info('{} downloaded successfully'.format(self.external_url))
        else:
            logger.error("Could not download {} file".format(self.internal_key))


class MultiPicture(Dao):

    def __init__(self, connexion: Connexion, dataset_id: str, picture_list: List[Picture]):
        super().__init__(connexion)
        self.dataset_id = dataset_id

        if picture_list == []:
            raise exceptions.NoDataError("A MultiPicture can't be empty")

        for pic in picture_list:
            self.check(pic)

        self.picture_list = picture_list
    
    def __str__(self,): return "{}MultiPictures{} object, size: {}".format(bcolors.GREEN, bcolors.ENDC,len(self))

    def check(self, v):
        if v is None or not isinstance(v, Picture):
            raise TypeError(v)

    def __getitem__(self, key) -> Union[Picture, 'MultiPicture']:
        if isinstance(key, slice):
            indices = range(*key.indices(len(self.picture_list)))
            pictures = [self.picture_list[i] for i in indices]
            return MultiPicture(self.connexion, self.dataset_id, pictures)
        return self.picture_list[key]

    def __len__(self): return len(self.picture_list)

    def __delitem__(self, i):
        if len(self.picture_list) < 2:
            raise exceptions.NoDataError("You can't remove the last picture. A MultiPicture can't be empty")

        del self.picture_list[i]

    def __setitem__(self, i, v):
        self.check(v)
        self.picture_list[i] = v

    @exception_handler
    @beartype
    def delete(self,) -> None:
        """Delete pictures from their dataset

        :warning: **DANGER ZONE**: Be very careful here!

        Remove this picture and its annotation from the dataset it belongs

        Examples:
            ```python
                pics = dataset.list_pictures()
                pics.delete()
            ```
        """
        payload = {'to_delete': [pic.id for pic in self.picture_list]}
        self.connexion.delete('/dataset/{}/pictures'.format(self.dataset_id), data=json.dumps(payload))
        logger.info("{} pictures removed from dataset {}".format(len(self.picture_list), self.dataset_id))

    @exception_handler
    @beartype
    def download(self, target_path: str = './', nb_threads: int = 20) -> None:
        """Download this multi picture in given target path


        Examples:
            ```python
                bunch_of_pics = client.get_dataset("foo_dataset").list_pictures()
                bunch_of_pics.download('./downloads/')
            ```
        Arguments:
            target_path (str, optional): Target path where to download. Defaults to './'.
            nb_threads (int, optional): Number of threads used to download. Defaults to 20.
        """
        f = partial(mlt.mlt_download_list_data_or_pics, self.connexion, self.dataset_id, target_path)
        mlt.do_multiprocess_things(f, self.picture_list, nb_threads)
        logger.info("{} downloaded in {}".format(len(self.picture_list), target_path))
