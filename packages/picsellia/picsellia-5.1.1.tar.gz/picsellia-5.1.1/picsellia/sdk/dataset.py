import json
import logging
import os
from typing import List, Optional, Union
from beartype import beartype
from picsellia import exceptions
from picsellia.decorators import exception_handler
from picsellia.exceptions import NoDataError, InvalidQueryError
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao
from picsellia.sdk.data import Data
from picsellia.sdk.data import MultiData
from picsellia.sdk.picture import Picture, MultiPicture
from pathlib import Path
import picsellia.pxl_multithreading as mlt
from multiprocessing import Pool, Value
import requests
import multiprocessing
from itertools import chain
from functools import partial
import tqdm
import collections

from picsellia.utils import print_line_return

logger = logging.getLogger('picsellia')


class Dataset(Dao):

    def __init__(self, connexion: Connexion, id: str, name: str, version: str):
        super().__init__(connexion)
        self.id = id
        self.name = name
        self.version = version

    @exception_handler
    @beartype
    def get_resource_url_on_platform(self,) -> str:
        """Get platform url of this resource.

        Examples:
            ```python
                print(foo_dataset.get_resource_url_on_platform())
                >>> https://app.picsellia.com/dataset/62cffb84-b92c-450c-bc37-8c4dd4d0f590
            ```

        Returns:
            Url on Platform for this resource
        """
        if self.connexion.base_url is None:
            raise exceptions.PicselliaError('Could not parse platform url. You cannot get platform link')

        return "{}/dataset/{}".format(self.connexion.base_url, self.id)

    @exception_handler
    @beartype
    def fork(self, version: str, pictures: Union[MultiPicture, Picture]) -> 'Dataset':
        """Fork current dataset with a new version name.

        Will create a new dataset, with same name of current object and a new version name.
        Pictures used shall be given after being retrieved.

        Examples:
            ```python
                foo_dataset = client.fetch_dataset('datatest', 'first')
                pics = foo_dataset.list_pictures()
                bar_dataset = foo_dataset.fork('second', pics)
            ```

        Arguments:
            version (str): new version name
            pictures ((MultiPicture) or (Picture)): pictures used for the new dataset

        Returns:
            A (Dataset) with given pictures
        """
        assert version != '', 'Version name can\'t be empty'

        if isinstance(pictures, Picture):
            pictures = [pictures]

        data = json.dumps({
            'version': version,
            'picture_ids': [pic.id for pic in pictures]
        })
        r = self.connexion.post('/dataset/{}/fork'.format(self.id), data=data)
        logger.info("Version {} for dataset {} created with {} assets in it".format(version, self.name, len(pictures)))
        dataset_id = r.json()["dataset"]['dataset_id']
        return Dataset(self.connexion, dataset_id, self.name, version)

    @exception_handler
    @beartype
    def _convert_response_to_picture(self, response: dict) -> Picture:
        return Picture(
            self.connexion,
            response["picture_id"],
            response["external_url"],
            response["internal_key"]
        )

    @exception_handler
    @beartype
    def list_pictures(self,) -> MultiPicture:
        """List all pictures of this dataset

        It will retrieve all pictures object of this dataset.
        You will then be able to manipulate them or add them to another dataset.

        Examples:
            ```python
                pictures = foo_dataset.list_pictures()
            ```

        Returns:
            A (MultiPicture) object that wraps some (Picture) that you can manipulate.
        """
        r = self.connexion.get('/dataset/{}/pictures'.format(self.id)).json()
        pictures = list(map(self._convert_response_to_picture, r["pictures"]))

        if len(pictures) == 0:
            raise NoDataError("This dataset has no pictures")

        return MultiPicture(
            self.connexion,
            self.id,
            pictures
        )

    @exception_handler
    @beartype
    def get_picture(self, filename: str) -> Picture:
        """Get one picture from its filename

        Examples:
            ```python
                pic = foo_dataset.get_picture('image_1.png')
            ```
        Arguments:
            filename (str): Filename of the image in the dataset

        Returns:
            A (Picture) object that you can manipulate or download
        """
        r = self.connexion.get('/dataset/{}/picture?filename={}'.format(self.id, filename)).json()
        picture = self._convert_response_to_picture(r["picture"])
        return picture

    @exception_handler
    @beartype
    def add_data(self, data: Union[Data, List[Data], MultiData]) -> None:
        """Add retrieved data from datalake to this dataset

        It will add given data into this dataset object.

        Examples:
            ```python
                data = datalake.fetch_data()[:10]
                bar_dataset.add_pictures(data)
            ```
        Arguments:
            data ((Data), List[(Data)] or (MultiData)): data to add to dataset
        """
        if isinstance(data, Data):
            data = [data]

        assert data != [], 'Please specify assets to add to dataset'

        payload = json.dumps({
            'picture_ids': [pic.id for pic in data]
        })
        self.connexion.post('/dataset/{}/pictures'.format(self.id), data=payload)
        logger.info("{} assets added to Dataset {}/{}".format(len(data), self.name, self.version))

    @exception_handler
    @beartype
    def delete(self,) -> None:
        """Delete a dataset.

        :warning: **DANGER ZONE**: Be very careful here!

        It will remove this dataset from our database, all of its picture and annotation will be removed.

        Examples:
            ```python
                foo_dataset.delete()
            ```
        """
        self.connexion.delete('/dataset/{}'.format(self.id))
        logger.info("Dataset {} deleted".format(self.name))

    @exception_handler
    @beartype
    def update(self, type: str) -> None:
        """Update properties of a Dataset.

        Examples:
            ```python
                dataset.update(type='detection')
            ```
        """
        data = {
            "type": type
        }
        self.connexion.patch('/dataset/{}'.format(self.id), json.dumps(data))
        logger.info("Dataset {} deleted".format(self.name))

    @exception_handler
    @beartype
    def download(self, target_path: str = None, nb_threads: int = 20) -> None:
        """Downloads images of a dataset.

        It will download all images from a dataset into specified folder.
        If target_path is None, it will download into ./<dataset_name>/<dataset_version>
        You can precise a number of threads to use while downloading.

        Examples:
            ```python
                foo_dataset.download('~/Downloads/dataset_pics')
            ```
        Arguments:
            target_path (str, optional): Target folder. Defaults to None.
            nb_threads (int, optional): Number of threads to use. Defaults to 20.
        """
        if target_path is not None:
            path = target_path
        else:
            path = os.path.join(self.name, self.version)

        Path(path).mkdir(parents=True, exist_ok=True)

        r = self.connexion.get('/dataset/{}/download'.format(self.id)).json()
        images = r["images"]

        f = partial(mlt.mlt_download_list_external_picture, path)
        mlt.do_multiprocess_things(f, images, nb_threads)
    
        print_line_return()
        logger.info("{} images of dataset downloaded into {}".format(len(images), target_path))

    @exception_handler
    @beartype
    def get_labels(self) -> List[dict]:
        """Get all labels of a dataset

        It will retrieve a list of dictionnary representing labels.

        Examples:
            ```python
                foo_dataset.add_labels("today")
                labels = foo_dataset.get_labels()
                assert labels == [ { "name":"today", "type":"detection" }]
            ```

        Returns:
            List of label as dictionnaries
        """
        r = self.connexion.get('/dataset/{}/labels'.format(self.id)).json()
        return r["labels"]

    @exception_handler
    @beartype
    def add_labels(self, labels: Union[str, List[str]]) -> None:
        """Add labels to dataset.

        Add some labels to this dataset.
        You can specify a simple label or a list of label.

        Dataset needs a type before doing this action.

        Examples:
            ```python
                foo_dataset.add_labels("today")
                foo_dataset.add_labels(["is", "a", "good", "day"])
            ```
        Arguments:
            labels (str or List[str]): label names to add
        """
        if isinstance(labels, str):
            labels = [labels]
        assert labels != [], "You shall specify some labels to add"

        data = {
            "names": labels
        }
        self.connexion.post('/dataset/{}/labels'.format(self.id), data=json.dumps(data))
        logger.info("Labels {} has been added to dataset {} / {}".format(labels, self.name, self.version))

    @exception_handler
    @beartype
    def delete_labels(self, labels: Union[str, List[str]]) -> None:
        """Delete labels of a dataset.

        Remove some labels from this dataset.
        You can specify a simple label or a list of label.

        Dataset needs a type before doing this action.

        Examples:
            ```python
                foo_dataset.add_labels(["good", "day"])
                foo_dataset.remove_labels("day")
                labels = foo_dataset.get_labels()
                assert labels == [ { "name":"good", "type":"detection" }]
            ```
        Arguments:
            labels (str or List[str]): labels to remove
        """
        if isinstance(labels, str):
            labels = [labels]
        assert labels != [], "You shall specify some labels to add"

        data = {
            "names": labels
        }
        self.connexion.delete('/dataset/{}/labels'.format(self.id), data=json.dumps(data))
        logger.info("Labels {} has been removed from dataset {} / {}".format(labels, self.name, self.version))

    @exception_handler
    @beartype
    def _get_annotation_page(self, limit=1, offset=0, snapshot=False):
        r = self.connexion.get(
            '/dataset/{}/annotations?limit={}&offset={}&snapshot={}'.format(self.id, limit, offset, snapshot),
        ).json()
        return r

    @exception_handler
    @beartype
    def list_annotations(self, limit: int = None, offset: int = None, from_snapshot: bool = False) -> list:
        if from_snapshot:  # pragma: no cover
            annots = self._get_annotation_page(snapshot=True)
            url = annots["url"]
            object_name = annots["object_name"]
            with open(object_name, 'wb') as handler:
                response = requests.get(url, stream=True)
                total_length = response.headers.get('content-length')
                if total_length is None:
                    logger.error("Could not download {} file".format(object_name))
                else:
                    logger.debug("Downloading {}".format(object_name))
                    for data in response.iter_content(chunk_size=1024):
                        handler.write(data)
            with open(object_name, 'r') as f:
                annot_file = json.load(f)
                annotations = annot_file["annotations"]
            return annotations
        else:
            if limit is not None and offset is not None:
                annot_page = self._get_annotation_page(limit, offset)
                annotations = annot_page["annotations"]
            else:
                annotations = []
                page_size = 200
                annot_page = self._get_annotation_page(page_size, 0)
                annotations += annot_page["annotations"]
                nb_pages = annot_page["nb_pages"]
                list_pages = [i for i in range(1, nb_pages)]
                if nb_pages < 12:
                    nb_threads = nb_pages
                else:
                    try:
                        nb_threads = multiprocessing.cpu_count()
                    except Exception:
                        nb_threads = 12
                chunk_size = max(1, int(nb_pages/nb_threads))
                infos_split = list(mlt.chunks(list_pages, chunk_size))
                counter = Value('i', 0)
                result = []
                with Pool(nb_threads, initializer=mlt.init_pool_annotations,
                          initargs=(counter, nb_pages, self.connexion, self.id, page_size,)) as pool:
                    result = pool.map(mlt.dl_annotations, infos_split)
                annotations += list(chain.from_iterable(result))
            return annotations

    @exception_handler
    @beartype
    def delete_all_annotations(self) -> None:
        """Delete all annotations of this dataset

        :warning: **DANGER ZONE**: Be very careful here!

        It will remove all annotation of every pictures of this dataset

        Examples:
            ```python
                foo_dataset.delete_all_annotations()
            ```
        """
        self.connexion.delete('/dataset/{}/annotations'.format(self.id)).json()

    @exception_handler
    @beartype
    def _update_stats(self, repartition: dict = None, nb_annotations: int = None, nb_objects: int = None) -> None:
        data = {
            'repartition': repartition,
            'nb_annotations': nb_annotations,
            'nb_objects': nb_objects
        }
        self.connexion.post("/dataset/{}/update_stats".format(self.id), data=json.dumps(data))

    # Can't be beartyped as its used in mlt
    def _add_annotation_for_picture(self, annotation_yield,):  # pragma: no cover
        for annotations in annotation_yield:
            picture_name = annotations["external_picture_url"]
            picture = self.get_picture(picture_name)
            if "duration" in annotations.keys():
                duration = float(annotations["duration"])
            elif "time_spent" in annotations.keys():
                duration = float(annotations["time_spent"])
            nb_instances = int(annotations["nb_labels"])
            picture.add_annotation(
                data=annotations["annotations"],
                nb_instances=nb_instances,
                duration=duration)

    @exception_handler
    @beartype
    def upload_annotations_from_file(self, ann_path: str, ann_format: str,
                                     tags: Optional[list] = [], nb_jobs: Optional[int] = 5,
                                     rectangle: Optional[bool] = False):
        """Upload annotations from file
        """

        if not (os.path.isdir(ann_path) or os.path.isfile(ann_path)):
            raise InvalidQueryError('Please provide a valid directory for ann_path')

        logger.debug("Scanning categories ...")
        if ann_path is not None:
            # if ann_format == "COCO":
            #     parser = COCOParser(path=ann_path)
            #     dataset_type = parser.find_dataset_type() if not rectangle else "detection"
            #     ann_type = "rectangle" if dataset_type == "detection" else "polygon"
            #     label_names = [l["name"] for l in parser.categories]
            #     self.add_labels(label_names)

            #     logger.debug("Uploading annotations ...\n")

            #     annotations_list, repartition, nb_annotations, nb_objects = \
            #                                                     parser.generate_annotations(rectangle=rectangle)
            #     nb_threads = 20 if nb_jobs == -1 else nb_jobs
            #     pool = Pool(nb_threads)

            #     f = partial(self._upload_annotation, True, self.id)

            #     for _ in tqdm.tqdm(pool.imap_unordered(f, annotations_list), total=len(annotations_list)):
            #         pass
            #     self._update_stats(repartition=repartition, nb_annotations=nb_annotations, nb_objects=nb_objects)
            #     logger.info("Dataset Uploaded to Picsellia, you can check it on the platform.")

            # if ann_format == "PASCAL-VOC":
            #     parser = PVOCParser(path=ann_path)
            #     # TODO -> Handle segmentation cases.
            #     classes, image_infos, ann_data, repartition, nb_annotations, nb_objects = \
            #                                                   parser._generate_images_labels_annotations(tags=tags)
            #     classes = list(set(classes))
            #     label_names = [l["name"] for l in classes]
            #     self.add_labels(label_names)
            #     nb_threads = 20 if nb_jobs == -1 else nb_jobs
            #     pool = Pool(nb_threads)

            #     f = partial(self._upload_annotation, True, self.id)

            #     for _ in tqdm.tqdm(pool.imap_unordered(f, ann_data), total=len(ann_data)):
            #         pass

            #     self._update_stats(repartition=repartition, nb_annotations=nb_annotations, nb_objects=nb_objects)
            #     logger.info("Dataset Uploaded to Picsellia, you can check it on the platform.")
            if ann_format == "PICSELLIA":
                with open(ann_path, 'rb') as f:
                    dict_annotations = json.load(f)
                label_to_create = []

                repartition = collections.Counter()
                nb_annotations = 0
                nb_objects = 0

                for annotations in dict_annotations["annotations"]:
                    nb_annotations += 1
                    tmpp = []
                    for ann in annotations["annotations"]:
                        tmpp.append(ann["label"])
                        nb_objects += 1
                        tmp = [ann["type"], ann["label"]]
                        if tmp not in label_to_create:
                            label_to_create.append(tmp)
                    repartition.update(tmpp)
                label_names = [lab[1] for lab in label_to_create]
                self.add_labels(label_names)

                upload = partial(self._add_annotation_for_picture)
                nb_threads = 20 if nb_jobs == -1 else nb_jobs
                
                with Pool(nb_threads) as pool:
                    nb_threads = 20 if nb_jobs == -1 else nb_jobs
                    list_annotations = list(mlt.chunks(dict_annotations["annotations"], nb_threads))
                    for _ in tqdm.tqdm(pool.imap_unordered(upload, list_annotations), total=len(list_annotations)):
                        pass
                self._update_stats(repartition=repartition, nb_annotations=nb_annotations, nb_objects=nb_objects)
                logger.info("Dataset Uploaded to Picsellia, you can check it on the platform.")
        pass

    @exception_handler
    @beartype
    def synchronize(self, target_dir: str, do_download: bool = False) -> Union[MultiPicture, None]:
        """Synchronize this dataset with target dir by comparing pictures in target dir with pictures uploaded in dataset.

        CARE ! IT WILL JUST PRINT DIFFERENCES, AUTO DOWNLOAD/UPLOAD NOT IMPLEMENTED YET 

        Examples:
            ```python
                foo_dataset.synchronize('./foo_dataset/first')
            ```
        Arguments:
            target_dir (str): directory to synchronize against
        """
        assert os.path.isdir(target_dir), "Please select a valid directory path"
        logger.info("⌛️ Scanning Dataset Pictures ..")
        pictures = self.list_pictures()
        external_urls = set(map(lambda picture: picture.external_url, pictures))
        logger.info("🔍 Scanning Local Dataset Folder ..")
        local_filenames = set([e for e in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, e))])


        not_uploaded = local_filenames - external_urls
        if len(not_uploaded) > 0:
            logger.info("📚 {} pictures not uploaded. You need to add data to the datalake first with :".format(len(not_uploaded)))
            logger.info("filepaths = {}".format(list(map(lambda filename: target_dir + "/" + filename, not_uploaded))))
            logger.info("list_data = client.get_datalake().upload_data(filepaths)")
            logger.info("client.get_dataset(\"{}\", \"{}\").add_data(list_data)".format(self.name, self.version))

        not_downloaded = external_urls - local_filenames 
        if len(not_downloaded) > 0:
            pictures = list(filter(lambda picture: picture.external_url in not_downloaded, pictures.picture_list))
            pics = MultiPicture(self.connexion, self.id, pictures)
            logger.info("📚 {} pictures not downloaded".format(len(not_downloaded)))
            if do_download:
                logger.info("📚 Downloading {} pictures".format(len(not_downloaded)))
                pics.download(target_dir)
            else:
                logger.info("📚 Call this method again with do_download=True if you want to download these pictures")
            return pics
        else:
            logger.info("✅ Dataset is up-to-date.")
            return None
        
        