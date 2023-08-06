from itertools import chain
import json
import logging
from multiprocessing import Pool, Value
from typing import Callable, List, Union
from uuid import uuid4
import requests
import os
from picsellia.exceptions import ResourceNotFoundError
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.data import Data, MultiData
from picsellia.sdk.picture import MultiPicture, Picture
from picsellia.utils import print_next_bar
from PIL import Image

logger = logging.getLogger('picsellia')


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# Multiprocessed init
def pool_init(length, counter):
    global mlt_counter
    global mlt_total_length
    global mlt_data_list

    mlt_counter = counter
    mlt_total_length = length
    mlt_data_list = []


def do_multiprocess_things(f : Callable, data_list : list, nb_threads : int = 20) -> list:
    nb_threads = min(len(data_list), nb_threads)
    chunk_size = (len(data_list) // nb_threads) + 1
    infos_split = list(chunks(data_list, chunk_size))
    counter = Value('i', 0)
    print_next_bar(0, len(data_list))
    with Pool(nb_threads, initializer=pool_init, initargs=(len(data_list), counter,)) as p:
        result = p.map(f, infos_split)

    return list(chain.from_iterable(result))

def mlt_download_list_external_picture(png_dir : str, infos : list) -> list:
    global mlt_counter
    global mlt_total_length

    downloaded = []
    for info in infos:
        pic_name = os.path.join(png_dir, os.path.split(info['external_picture_url'])[-1])
        if not os.path.isfile(pic_name) and _download_external_picture(info=info, pic_name=pic_name):
            downloaded.append(pic_name)

    with mlt_counter.get_lock():
        mlt_counter.value += len(infos)
        print_next_bar(mlt_counter.value, mlt_total_length)

    return downloaded

def _download_external_picture(info, pic_name):
    global mlt_counter
    global mlt_total_length
    try:
        response = requests.get(info["signed_url"], stream=True)
        if response.status_code == "404":
            raise ResourceNotFoundError('Picture does not exist on our server.')
        with open(pic_name, 'wb') as handler:
            for data in response.iter_content(chunk_size=1024):
                handler.write(data)
    except Exception:
        logger.error(f"Image {pic_name} can't be downloaded")
        return False
    return True

def mlt_download_list_data_or_pics(connexion : Connexion, lake_or_set_id : str, target_path: str, some_data_or_pics : Union[Picture, MultiPicture, Data, MultiData]) -> Union[MultiPicture, MultiData]:
    global mlt_counter
    global mlt_total_length

    if isinstance(some_data_or_pics, Data):
        some_data_or_pics = MultiData(connexion, lake_or_set_id, [some_data_or_pics])
    if isinstance(some_data_or_pics, Picture):
        some_data_or_pics = MultiPicture(connexion, lake_or_set_id, [some_data_or_pics])

    for pic in some_data_or_pics:
        path = os.path.join(target_path, pic.external_url)
        connexion.download_some_file(False, pic.internal_key, path, False)

    with mlt_counter.get_lock():
        mlt_counter.value += len(some_data_or_pics)
        print_next_bar(mlt_counter.value, mlt_total_length)

    return some_data_or_pics

def mlt_add_data_to_dataset(connexion : Connexion, dataset_id : str, data_ids: List[str]) -> list:
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
    global mlt_counter
    global mlt_total_length

    payload = json.dumps({
        'picture_ids': data_ids
    })
    connexion.post('/dataset/{}/pictures'.format(dataset_id), data=payload)
    with mlt_counter.get_lock():
        mlt_counter.value += len(data_ids)
        print_next_bar(mlt_counter.value, mlt_total_length)

    return data_ids

def mlt_upload_data(connexion : Connexion, datalake_id : str, tags: List[str], source: str, paths: List[str]):
    global mlt_data_list
    global mlt_total_length
    global mlt_counter

    data_list = []
    for path in paths:
        try:
            external_url = os.path.split(path)[-1]
            internal_key = os.path.join(str(uuid4())) + '.' + external_url.split('.')[-1]
            with Image.open(path) as image:
                width, height = image.size
            connexion.push_to_s3(path, internal_key)
            data = json.dumps({
                'internal_key': internal_key,
                'external_url': external_url,
                'height': height,
                'width': width,
                'tags': tags,
                'source': source
            })
            r = connexion.post('/datalake/{}/data/add'.format(datalake_id), data=data).json()
            data_list.append(Data(connexion, datalake_id, r["data"]["picture_id"], r["data"]["external_url"], r["data"]["internal_key"]))
        except Exception as e:
            logger.error('\nCould not upload {} because {}'.format(path, str(e)))
            continue
    with mlt_counter.get_lock():
        mlt_counter.value += len(paths)
        print_next_bar(mlt_counter.value, mlt_total_length)
    mlt_data_list += data_list
    return mlt_data_list
        

def init_pool_annotations(p, nb, req, ds_id, p_size):
    global page_done
    global nb_pages
    global connexion
    global annotation_list
    global dataset_id
    global page_size
    page_done = p
    nb_pages = nb - 1
    connexion = req
    dataset_id = ds_id
    annotation_list = []
    page_size = p_size


def dl_annotations(page_list):
    global page_done
    global nb_pages
    global connexion
    global annotation_list
    global dataset_id
    global page_size

    annotation_list = []
    for page in page_list:
        params = {
            'limit': page_size,
            'offset': page_size*page,
            'snapshot': False
        }
        r = connexion.get(
            'dataset/{}/annotations'.format(dataset_id), params=params)
        annotation_list += r.json()["annotations"]
        with page_done.get_lock():
            page_done.value += 1
        print_next_bar(page_done.value, nb_pages)
    return annotation_list
