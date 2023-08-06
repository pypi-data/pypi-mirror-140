from datetime import date
import json
import logging
import os
import shutil
import sys
import unittest
import uuid

from picsellia import Client, exceptions
from picsellia.sdk.data import Data, MultiData
from picsellia.sdk.picture import MultiPicture, Picture

unittest.defaultTestLoader.sortTestMethodsUsing = lambda *args: -1

try:
    TOKEN = os.environ["PXL_TEST_TOKEN"]
    HOST = os.environ["PXL_HOST"]
except KeyError:
    print('FATAL ERROR, you need to define env var PXL_TEST_TOKEN with api token and PXL_HOST with platform host')
    sys.exit(1)

logging.getLogger('picsellia')


class TestSDK(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.host = HOST
        cls.token = TOKEN
        return super().setUpClass()


class TestClient(TestSDK):

    def test_init_client(self):
        clt = Client(api_token=self.token, host=self.host)
        self.assertIsNotNone(clt.connexion)
        self.assertEqual(clt.connexion.host, self.host)
        self.assertEqual(clt.connexion.headers["Authorization"],"Token " + self.token)
        self.assertEqual(clt.connexion.headers["Content-type"], "application/json")
        self.assertIsNotNone(clt.organization)
        self.assertIsNotNone(clt.organization.id)
        self.assertIsNotNone(clt.organization.name)

    def test_init_environ_token(self):
        os.environ["PICSELLIA_TOKEN"] = self.token
        clt = Client(host=self.host)
        self.assertEqual(clt.connexion.headers["Authorization"],"Token " + self.token)
        self.assertEqual(clt.connexion.headers["Content-type"], "application/json")

        self.assertEqual('Client initialized for organization `{}`'.format(
            clt.organization.name), str(clt))

    def test_init_no_environ_token(self):
        os.environ["PICSELLIA_TOKEN"] = self.token
        del os.environ["PICSELLIA_TOKEN"]
        with self.assertRaises(Exception):
            Client(host=self.host)


class TestInitializedClientSDK(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.host = HOST
        cls.token = TOKEN
        cls.clt = Client(cls.token, host=cls.host)
        return super().setUpClass()


class TestOrganization(TestInitializedClientSDK):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_organization(self):
        organization = self.clt.get_organization()

        org = organization.get_infos()
        self.assertEqual(org["id"], organization.id)
        self.assertEqual(org["name"], organization.name)

    def test_get_resource_url(self):
        organization = self.clt.get_organization()
        self.assertEqual("{}/organization/{}".format(self.clt.connexion.base_url, organization.id),
                         organization.get_resource_url_on_platform())

        self.clt.connexion.base_url = None
        with self.assertRaises(exceptions.PicselliaError):
            organization.get_resource_url_on_platform()


class TestProject(TestInitializedClientSDK):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        project_list = cls.clt.list_projects()

        for project in project_list:
            project.delete()

    def test_create_project(self):
        project = self.clt.create_project("test_project_1")

        self.assertEqual(project.name, "test_project_1")

        project.delete()

    def test_get_datalake_platform_url(self,):
        project = self.clt.create_project("test_project_2")

        base_url = self.clt.connexion.base_url
        self.assertEqual("{}/project/{}".format(base_url, project.id),
                         project.get_resource_url_on_platform())

        self.clt.connexion.base_url = None
        with self.assertRaises(exceptions.PicselliaError):
            project.get_resource_url_on_platform()
        self.clt.connexion.base_url = base_url

    def test_list_project(self):
        project = self.clt.create_project("test_project_3")

        project_list = self.clt.list_projects()

        self.assertEqual(len(project_list), 1)
        self.assertEqual(project_list[0].name, "test_project_3")

        project.delete()

    def test_update_project(self):
        project = self.clt.create_project("test_project_4")

        project.update(description="test project description")

        project.delete()

    def test_get_project_by_name(self):
        project = self.clt.create_project("test_project_5")

        project_retr = self.clt.get_project("test_project_5")
        self.assertEqual(project.name, project_retr.name)

        project.delete()

    def test_get_project_by_id(self):
        project = self.clt.create_project("test_project_6")

        project_retr = self.clt.get_project_by_id(project.id)
        self.assertEqual(project.id, project_retr.id)
        self.assertEqual(project.name, project_retr.name)

        project.delete()

    def test_list_workers(self):
        project = self.clt.create_project("test_project_7")

        workers = project.list_workers()
        self.assertTrue(len(workers) > 0)
        self.assertIsNotNone(workers[0].get_infos()["username"])

        project.delete()


class TestDatalake(TestInitializedClientSDK):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        datalake = cls.clt.get_datalake()
        try:
            datalist = datalake.list_data()
            for one_data in datalist:
                one_data.delete()
        except exceptions.NoDataError:
            datalist = []

    def test_get_datalake(self,):
        datalake = self.clt.get_datalake()
        self.assertIsNotNone(datalake)

    def test_get_datalake_platform_url(self,):
        datalake = self.clt.get_datalake()
        base_url = self.clt.connexion.base_url
        self.assertEqual("{}/datalake/{}".format(base_url, datalake.id),
                         datalake.get_resource_url_on_platform())

        self.clt.connexion.base_url = None
        with self.assertRaises(exceptions.PicselliaError):
            datalake.get_resource_url_on_platform()
        self.clt.connexion.base_url = base_url

    def test_upload_one_data(self,):
        self.clear_data()

        datalake = self.clt.get_datalake()
        data_list_input = datalake.upload_data(
            'tests/files/test.png', ["tag1"])
        data_list = datalake.fetch_data(tags=["tag1"])
        self.assertIsNotNone(data_list)
        self.assertEqual(len(data_list.data_list), 1)
        self.assertEqual(data_list[0].id, data_list_input.id)

    def test_upload_zero_data(self,):
        self.clear_data()

        datalake = self.clt.get_datalake()
        with self.assertRaises(exceptions.PicselliaError):
            datalake.upload_data('tests/files/unknown.png', ["tag1"])

    def test_upload_one_unknown_data_but_other_good(self,):
        self.clear_data()

        datalake = self.clt.get_datalake()
        data_list_input = datalake.upload_data(
            ['tests/files/test.png', 'unknown'], ["tag2"])

        data_list = datalake.list_data()
        self.assertIsNotNone(data_list)
        self.assertEqual(len(data_list.data_list), 1)
        self.assertEqual(data_list[0].id, data_list_input.id)

    def test_upload_multiple_data(self,):
        self.clear_data()

        datalake = self.clt.get_datalake()
        files = os.listdir('tests/files/test_image_dir')
        files = ['tests/files/test_image_dir/' + fle for fle in files]
        datalake.upload_data(files, ["tag2"])

        data_list = datalake.fetch_data(tags=["tag2"])
        self.assertEqual(len(data_list.data_list), len(files))

    def clear_data(self):
        datalake = self.clt.get_datalake()
        try:
            datalist = datalake.list_data()
            for one_data in datalist:
                one_data.delete()
        except exceptions.NoDataError:
            datalist = []


class TestData(TestInitializedClientSDK):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        datalake = cls.clt.get_datalake()
        try:
            datalist = datalake.list_data()
        except exceptions.NoDataError:
            datalist = []
        for one_data in datalist:
            one_data.delete()

        files = os.listdir('tests/files/test_image_dir')
        cls.files = ['tests/files/test_image_dir/' + fle for fle in files]
        cls.datalake = cls.clt.get_datalake()
        cls.datalake.upload_data(cls.files, ["tag3"])

    def test_fetch_data(self):
        data_list = self.datalake.fetch_data()
        self.assertEqual(len(data_list.data_list), 6)

        with self.assertRaises(exceptions.NoDataError):
            self.datalake.fetch_data(tags=["tag1"])

        data_list = self.datalake.fetch_data(tags=["tag3"], quantity=100)
        self.assertEqual(len(data_list.data_list), len(self.files))

        data_list = self.datalake.fetch_data(tags=["tag3"], quantity=2)
        self.assertEqual(len(data_list.data_list), 2)

        data_list = self.datalake.fetch_data(tags="tag3", quantity=2)
        self.assertEqual(len(data_list.data_list), 2)

    def test_one_data_tags(self):
        one_data = self.datalake.fetch_data(quantity=1, tags=["tag3"])[0]

        one_data.add_tags("a")
        one_data.add_tags(["b", "c"])

        with self.assertRaises(AssertionError):
            one_data.add_tags([])

        tags = one_data.get_tags()
        self.assertIn("a", tags)
        self.assertIn("b", tags)
        self.assertIn("c", tags)

        one_data.remove_tags("a")
        one_data.remove_tags(["b", "c"])

        with self.assertRaises(AssertionError):
            one_data.remove_tags([])

        tags = one_data.get_tags()
        self.assertEqual(tags, ["tag3"])

    def test_add_tags_on_multiple(self):
        multidata = self.datalake.fetch_data(quantity=2)

        multidata.add_tags("a")
        multidata.add_tags(["b", "c"])

        with self.assertRaises(AssertionError):
            multidata.add_tags([])

        tags = multidata[0].get_tags()
        self.assertIn("a", tags)
        self.assertIn("b", tags)
        self.assertIn("c", tags)

        tags = multidata[1].get_tags()
        self.assertIn("a", tags)
        self.assertIn("b", tags)
        self.assertIn("c", tags)

        multidata.remove_tags("a")
        multidata.remove_tags(["b", "c"])

        with self.assertRaises(AssertionError):
            multidata.remove_tags([])

        tags = multidata[0].get_tags()
        self.assertEqual(tags, ["tag3"])

        tags = multidata[1].get_tags()
        self.assertEqual(tags, ["tag3"])

    def test_delete_data(self):
        one_data = self.datalake.fetch_data(quantity=1)[0]
        one_data.add_tags('T1')
        one_data.delete()

        with self.assertRaises(exceptions.NoDataError):
            self.datalake.fetch_data(tags=['T1'])

    def test_delete_multidata(self):
        multidata = self.datalake.fetch_data(quantity=2)
        multidata.add_tags('T1')
        multidata.delete()

        with self.assertRaises(exceptions.NoDataError):
            self.datalake.fetch_data(tags=['T1'])

    def test_checks_on_multidata(self):
        with self.assertRaises(exceptions.NoDataError):
            MultiData(self.datalake.connexion, self.datalake.id, [])

        with self.assertRaises(TypeError):
            MultiData(self.datalake.connexion, self.datalake.id, [
                      Picture(self.datalake.connexion, "1", "2", "3")])

        one_data = self.datalake.fetch_data(quantity=1)[0]
        multidata = self.datalake.fetch_data(quantity=2)
        multidata[1] = one_data

        with self.assertRaises(IndexError):
            multidata[2] = one_data

        self.assertEqual(len(multidata), 2)
        del multidata[0]
        self.assertEqual(len(multidata), 1)
        with self.assertRaises(exceptions.NoDataError):
            del multidata[1]

        multidata = self.datalake.fetch_data(quantity=3)[:2]
        self.assertEqual(len(multidata), 2)


    def test_download_data(self):
        multidata = self.datalake.fetch_data(quantity=3)

        data = multidata[0]
        data.download()
        path = "./{}".format(data.external_url)
        self.assertTrue(os.path.exists(path))
        os.remove(path)
        
        data.download('../downloads')
        path = "../downloads/{}".format(data.external_url)
        self.assertTrue(os.path.exists(path))
        os.remove(path)

        multidata.download()
        for d in multidata:
            path = "./{}".format(d.external_url)
            self.assertTrue(os.path.exists(path))
            os.remove(path)

        multidata.download('../downloads')
        for d in multidata:
            path = "../downloads/{}".format(d.external_url)
            self.assertTrue(os.path.exists(path))
            os.remove(path)

        data = multidata[0]
        data.download()
        path = "./{}".format(data.external_url)
        self.assertTrue(os.path.exists(path))
        data.download() # Override file
        self.assertTrue(os.path.exists(path))
        os.remove(path)

class TestDataset(TestInitializedClientSDK):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        try:
            datasets = cls.clt.list_datasets()
        except exceptions.ResourceNotFoundError:
            datasets = []

        for dataset in datasets:
            dataset.delete()

        datalake = cls.clt.get_datalake()

        files = os.listdir('tests/files/test_image_dir')
        files = ['tests/files/test_image_dir/' + fle for fle in files]
        datalake = cls.clt.get_datalake()
        datalake.upload_data(files, ["tag3"])
        data_list = datalake.fetch_data(quantity=2)

        cls.dataset = cls.clt.create_dataset("datatest", data_list)
        cls.dataset.update('detection')

    def test_create_dataset_with_only_one_image(self,):
        datalake = self.clt.get_datalake()

        data_list = datalake.fetch_data(quantity=1)[0]

        dataset = self.clt.create_dataset("datatest_create", data_list)
        self.assertIsNotNone(dataset)
        self.assertEqual(dataset.name, "datatest_create")
        self.assertEqual(dataset.version, "first")
        dataset.delete()

    def test_get_dataset_platform_url(self,):
        datalake = self.clt.get_datalake()

        data_list = datalake.fetch_data(quantity=1)[0]

        dataset = self.clt.create_dataset("datatest_get_url", data_list)
        base_url = self.clt.connexion.base_url
        self.assertEqual("{}/dataset/{}".format(base_url, dataset.id),
                         dataset.get_resource_url_on_platform())

        self.clt.connexion.base_url = None
        with self.assertRaises(exceptions.PicselliaError):
            dataset.get_resource_url_on_platform()
        self.clt.connexion.base_url = base_url

    def test_create_dataset(self,):
        datalake = self.clt.get_datalake()

        data_list = datalake.fetch_data(quantity=1)

        dataset = self.clt.create_dataset("datatest_create", data_list)
        self.assertIsNotNone(dataset)
        self.assertEqual(dataset.name, "datatest_create")
        self.assertEqual(dataset.version, "first")
        dataset.delete()

    def test_get_dataset_by_name(self,):
        dataset = self.clt.get_dataset("datatest", "first")

        self.assertIsNotNone(dataset)
        self.assertEqual(dataset.name, self.dataset.name)
        self.assertEqual(dataset.version, self.dataset.version)
        self.assertEqual(dataset.id, self.dataset.id)

    def test_get_dataset_by_id(self,):
        dataset = self.clt.get_dataset("datatest", "first")
        dataset_from_id = self.clt.get_dataset_by_id(dataset.id)

        self.assertIsNotNone(dataset)
        self.assertEqual(dataset_from_id.name, self.dataset.name)
        self.assertEqual(dataset_from_id.version, self.dataset.version)
        self.assertEqual(dataset_from_id.id, self.dataset.id)

    def test_search_dataset(self,):
        data_list = self.clt.datalake.fetch_data(quantity=1)
        dataset1 = self.clt.create_dataset("d1", data_list, 'v1')
        dataset2 = self.clt.create_dataset("d2", data_list, 'v1')

        pics = dataset1.list_pictures()[:1]
        dataset3 = dataset1.fork("v2", pics)

        self.assertIsNotNone(dataset1)
        self.assertIsNotNone(dataset2)
        self.assertIsNotNone(dataset3)

        ids_1 = [d.id for d in self.clt.search_datasets(name="d1")]
        self.assertIn(dataset1.id, ids_1)
        self.assertIn(dataset3.id, ids_1)
        self.assertNotIn(dataset2.id, ids_1)

        ids_2 = [d.id for d in self.clt.search_datasets(version="v1")]
        self.assertIn(dataset1.id, ids_2)
        self.assertIn(dataset2.id, ids_2)
        self.assertNotIn(dataset3.id, ids_2)

        ids_3 = [d.id for d in self.clt.search_datasets(
            name="d2", version="v1")]
        self.assertIn(dataset2.id, ids_3)
        self.assertNotIn(dataset1.id, ids_3)
        self.assertNotIn(dataset3.id, ids_3)

    def test_list_pictures_without_data(self,):
        data_list = self.clt.datalake.fetch_data(quantity=1)
        dataset1 = self.clt.create_dataset("test_dataset_without_pic", data_list)

        pics = dataset1.list_pictures()
        pics.delete()

        self.assertIsNotNone(dataset1)

        with self.assertRaises(exceptions.NoDataError):
            dataset1.list_pictures()

    def test_fork_dataset_with_one_pic(self,):
        pics = self.dataset.list_pictures()[0]

        new_dataset = self.dataset.fork("second", pics)
        self.assertIsNotNone(new_dataset)
        self.assertEqual(new_dataset.name, self.dataset.name)
        self.assertEqual(new_dataset.version, "second")
        self.assertNotEqual(new_dataset.id, self.dataset.id)

        new_dataset.delete()

    def test_fork_dataset(self,):
        pics = self.dataset.list_pictures()[:1]

        new_dataset = self.dataset.fork("second", pics)
        self.assertIsNotNone(new_dataset)
        self.assertEqual(new_dataset.name, self.dataset.name)
        self.assertEqual(new_dataset.version, "second")
        self.assertNotEqual(new_dataset.id, self.dataset.id)

        new_dataset.delete()

    def test_add_data_to_dataset(self,):
        datalake = self.clt.get_datalake()
        data_list = datalake.fetch_data(quantity=6)
        dataset2 = self.clt.create_dataset("datatest2", data_list[2:4])

        dataset2.add_data(data_list[0])
        dataset2.add_data([data_list[0], data_list[1]])
        dataset2.add_data(data_list[0:2])
        dataset2.add_data(data_list)
        dataset2.delete()

    def test_add_labels(self,):
        self.dataset.add_labels("car")

        labels = self.dataset.get_labels()
        self.assertEqual(labels[0]["name"], "car")

        self.dataset.delete_labels("car")

        labels = self.dataset.get_labels()
        self.assertEqual(len(labels), 0)

    def test_download_dataset(self):
        self.dataset.download()
        self.assertTrue(os.path.exists("datatest"))
        shutil.rmtree("datatest")

        self.dataset.download("tests/files/test_dl_dataset")
        self.assertTrue(os.path.exists("tests/files/test_dl_dataset"))
        shutil.rmtree("tests/files/test_dl_dataset")

    def test_upload_annotations_from_file_with_unknown_file(self,):
        with self.assertRaises(exceptions.InvalidQueryError):
            self.dataset.upload_annotations_from_file(
                ann_path="tests/files/not_a_file.json", ann_format="PICSELLIA")

    def test_upload_annotations_from_file_unknown_without_images(self,):
        with self.assertRaises(exceptions.InvalidQueryError):
            self.dataset.upload_annotations_from_file(
                ann_path="tests/files/not_a_file.json", tags=["test_push"], ann_format="PICSELLIA")

    def test_upload_annotations_from_file_unparsable_without_images(self,):
        # missing images 'key' in json
        with self.assertRaises(exceptions.ResourceNotFoundError):
            self.dataset.upload_annotations_from_file(
                ann_path="tests/files/test_annotations_wrong.json", tags=["test_push"], ann_format="PICSELLIA")

    def test_upload_annotations_from_file_list_delete(self,):
        datalake = self.clt.get_datalake()
        file_list = os.listdir("tests/files/test_push_dataset_dir")
        filepaths = [os.path.join("tests/files/test_push_dataset_dir", f)
                     for f in file_list]
        data_list = datalake.upload_data(filepaths)

        dataset = self.clt.create_dataset("test_push_dataset", data_list)
        dataset.update('detection')
        dataset.upload_annotations_from_file(
            ann_path="tests/files/test_annotations_rectangle.json", ann_format="PICSELLIA")
        annotations = dataset.list_annotations()  # test list all annotations
        self.assertGreater(len(annotations), 0)
        annotations = dataset.list_annotations(1, 0)  # test list with offset and limit

        # TODO annotations = dataset.list_annotations(1, 0, from_snapshot=True)

        dataset.delete_all_annotations()

    def test_create_dataset(self,):
        files = os.listdir('tests/files/test_a_lot')
        files = ['tests/files/test_a_lot/' + fle for fle in files]
        datalake = self.clt.get_datalake()
        datalake.upload_data(files, ["tag_a_lot"])
        data_list = datalake.fetch_data(quantity=25)

        dataset = self.clt.create_dataset("datatest_a_lot_1", data_list[0:10])
        self.assertEqual(10, len(dataset.list_pictures()))
        dataset.delete()
        dataset = self.clt.create_dataset("datatest_a_lot_2", data_list[0:20])
        self.assertEqual(20, len(dataset.list_pictures()))
        dataset.delete()
        dataset = self.clt.create_dataset("datatest_a_lot_3", data_list[0:25])
        self.assertEqual(25, len(dataset.list_pictures()))
        dataset.delete()


class TestPicture(TestInitializedClientSDK):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        datalake = cls.clt.get_datalake()
        files = os.listdir('tests/files/test_push_dataset_dir')
        files = ['tests/files/test_push_dataset_dir/' + fle for fle in files]
        datalake = cls.clt.get_datalake()
        datalake.upload_data(files, ["test_pics"])
        data_list = datalake.fetch_data(tags="test_pics")
        cls.dataset = cls.clt.create_dataset("datatest_picture", data_list)
        cls.dataset.update('detection')

    def test_checks_on_multidata(self):
        with self.assertRaises(exceptions.NoDataError):
            MultiPicture(self.dataset.connexion, self.dataset.id, [])

        with self.assertRaises(TypeError):
            MultiPicture(self.dataset.connexion, self.dataset.id, [
                         Data(self.dataset.connexion, "1", "2", "3", "4")])

        one_pic = self.dataset.list_pictures()[0]
        multipic = self.dataset.list_pictures()[:2]
        self.assertTrue(isinstance(one_pic, Picture))
        self.assertTrue(len(multipic), 2)

        multipic[1] = one_pic

        with self.assertRaises(IndexError):
            multipic[2] = one_pic

        self.assertEqual(len(multipic), 2)
        del multipic[0]
        self.assertEqual(len(multipic), 1)
        with self.assertRaises(exceptions.NoDataError):
            del multipic[1]

        pics = self.dataset.list_pictures()
        for pic in pics:
            pic.delete()



    def test_download_pictures(self):
        multipics = self.dataset.list_pictures()

        pic = multipics[0]
        pic.download()
        path = "./{}".format(pic.external_url)
        self.assertTrue(os.path.exists(path))
        os.remove(path)
        
        pic.download('../downloads')
        path = "../downloads/{}".format(pic.external_url)
        self.assertTrue(os.path.exists(path))
        os.remove(path)

        multipics.download()
        for d in multipics:
            path = "./{}".format(d.external_url)
            self.assertTrue(os.path.exists(path))
            os.remove(path)

        multipics.download('../downloads')
        for d in multipics:
            path = "../downloads/{}".format(d.external_url)
            self.assertTrue(os.path.exists(path))
            os.remove(path)

        pic = multipics[0]
        pic.download()
        path = "./{}".format(pic.external_url)
        self.assertTrue(os.path.exists(path))
        pic.download() # Override file
        self.assertTrue(os.path.exists(path))
        os.remove(path)


    def test_syncronize(self):
        multipics = self.dataset.list_pictures()
        self.assertTrue(len(multipics) > 0)

        target_path = "./test_sync/"
        os.mkdir(target_path)
        diff = self.dataset.synchronize(target_path)

        # Empty dir
        self.assertEqual(len(diff), len(multipics))

        # No download by default
        self.assertEqual(len(os.listdir(target_path)), 0)
        
        self.dataset.synchronize(target_path, do_download=True)
        files = os.listdir(target_path)
        self.assertEqual(len(files), len(multipics))

        diff = self.dataset.synchronize(target_path)
        self.assertIsNone(diff)

        os.remove(target_path + "/" + files[0])
        diff = self.dataset.synchronize(target_path)
        self.assertEqual(len(diff), 1)

        diff = self.dataset.synchronize(target_path, do_download=True)
        files = os.listdir(target_path)
        self.assertEqual(len(files), len(multipics))

        shutil.rmtree(target_path)


class TestPictureAnnotation(TestInitializedClientSDK):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        datalake = cls.clt.get_datalake()
        files = os.listdir('tests/files/test_push_dataset_dir')
        files = ['tests/files/test_push_dataset_dir/' + fle for fle in files]
        datalake = cls.clt.get_datalake()
        datalake.upload_data(files, ["test_pics"])
        data_list = datalake.fetch_data(tags="test_pics")
        cls.dataset = cls.clt.create_dataset(
            "datatest_picture_annotations", data_list)
        cls.dataset.update('detection')

    def test_add_list_delete_annotation(self):
        filename = "image_11.jpg"
        self.dataset.list_pictures()
        picture = self.dataset.get_picture(filename)
        with open("tests/files/test_annotations_rectangle.json", 'r') as f:
            annot_dict = json.load(f)
            annotation_data = annot_dict["annotations"][1]["annotations"]
            picture.add_annotation(data=annotation_data, creation_date=date.today(),
                                   duration=10.0, reviewed=False, is_accepted=True, is_skipped=True, nb_instances=10)
        annots = picture.list_annotations()
        self.assertEqual(len(annots), 1)
        picture.delete_annotations()
        annots = picture.list_annotations()
        self.assertEqual(len(annots), 0)

        with open("tests/files/test_annotations_classif.json", 'r') as f:
            annot_dict = json.load(f)
            annotation_data = annot_dict["annotations"][1]["annotations"]
            picture.add_annotation(data=annotation_data)
        annots = picture.list_annotations()
        self.assertEqual(len(annots), 1)
        picture.delete_annotations()
        annots = picture.list_annotations()
        self.assertEqual(len(annots), 0)

        with open("tests/files/test_annotations_polygon.json", 'r') as f:
            annot_dict = json.load(f)
            annotation_data = annot_dict["annotations"][0]["annotations"]
            picture.add_annotation(data=annotation_data)
        annots = picture.list_annotations()
        self.assertEqual(len(annots), 1)
        picture.delete_annotations()
        annots = picture.list_annotations()
        self.assertEqual(len(annots), 0)

        picture = self.dataset.get_picture("image_11.jpg")

        with self.assertRaises(TypeError):
            picture.add_annotation(data={})

        with self.assertRaises(exceptions.TyperError):
            picture.add_annotation(data=[])

        with self.assertRaises(TypeError):
            picture.add_annotation(data=[[]])

        with self.assertRaises(exceptions.TyperError):
            # Dict empty in 2
            picture.add_annotation(data=[{}])

        with self.assertRaises(exceptions.TyperError):
            # Type not present
            picture.add_annotation(data=[{"label": "car"}])

        with self.assertRaises(exceptions.TyperError):
            # Type unknown
            picture.add_annotation(data=[{"type": "unknown"}])

        with self.assertRaises(exceptions.TyperError):
            # Label not present
            picture.add_annotation(data=[{"type": "classification"}])

        with self.assertRaises(exceptions.TyperError):
            # no rectangle
            data = [{"type": "rectangle", "label": "car"}]
            picture.add_annotation(data=data)

        with self.assertRaises(exceptions.TyperError):
            # no height
            data = [{"type": "rectangle", "label": "car",
                     "rectangle": {"top": 1, "left": 1, "width": 1}}]
            picture.add_annotation(data=data)

        with self.assertRaises(exceptions.TyperError):
            # no top
            data = [{"type": "rectangle", "label": "car",
                     "rectangle": {"height": 1, "left": 1, "width": 1}}]
            picture.add_annotation(data=data)

        with self.assertRaises(exceptions.TyperError):
            # no width
            data = [{"type": "rectangle", "label": "car",
                     "rectangle": {"left": 1, "top": 1, "height": 1}}]
            picture.add_annotation(data=data)

        with self.assertRaises(exceptions.TyperError):
            # no left
            data = [{"type": "rectangle", "label": "car",
                     "rectangle": {"width": 1, "top": 1, "height": 1}}]
            picture.add_annotation(data=data)

        with self.assertRaises(exceptions.TyperError):
            # no polygon
            data = [{"type": "polygon", "label": "car"}]
            picture.add_annotation(data=data)

        with self.assertRaises(exceptions.TyperError):
            # polygon bad type
            data = [{"type": "polygon", "label": "car", "polygon":  "HEY"}]
            picture.add_annotation(data=data)

        with self.assertRaises(exceptions.TyperError):
            # no geometry
            data = [{"type": "polygon", "label": "car", "polygon": {}}]
            picture.add_annotation(data=data)

        with self.assertRaises(exceptions.TyperError):
            # bad geo
            data = [{"type": "polygon", "label": "car",
                     "polygon":  {"geometry": "YAA"}}]
            picture.add_annotation(data=data)

        with self.assertRaises(exceptions.TyperError):
            # empty geo
            data = [{"type": "polygon", "label": "car",
                     "polygon":  {"geometry": []}}]
            picture.add_annotation(data=data)

        with self.assertRaises(exceptions.TyperError):
            # tiny geo
            data = [{"type": "polygon", "label": "car", "polygon":  {
                "geometry": [{"x": 1, "y": 2}, {"x": 3, "y": 4}]}}]
            picture.add_annotation(data=data)

        with self.assertRaises(exceptions.TyperError):
            # bad coord
            data = [{"type": "polygon", "label": "car", "polygon":  {
                "geometry": [{"x": 1, "y": 2}, {"x": 3, "y": 4}, "HEYO"]}}]
            picture.add_annotation(data=data)

        with self.assertRaises(exceptions.TyperError):
            # no x
            data = [{"type": "polygon", "label": "car", "polygon":  {
                "geometry": [{"x": 1, "y": 2}, {"x": 3, "y": 4}, {"y": 4}]}}]
            picture.add_annotation(data=data)

        with self.assertRaises(exceptions.TyperError):
            # no y
            data = [{"type": "polygon", "label": "car", "polygon":  {
                "geometry": [{"x": 1, "y": 2}, {"x": 3, "y": 4}, {"x": 4}]}}]
            picture.add_annotation(data=data)

        pics = self.dataset.list_pictures()
        pics.delete()


class TestModel(TestInitializedClientSDK):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        datalake = cls.clt.get_datalake()
        models = cls.clt.list_models()
        for model in models:
            model.delete()
        try:
            datalist = datalake.list_data()
        except exceptions.NoDataError:
            datalist = []
        for one_data in datalist:
            one_data.delete()
        project_list = cls.clt.list_projects()
        for project in project_list:
            project.delete()

        files = os.listdir('tests/files/test_image_dir')
        cls.files = ['tests/files/test_image_dir/' + fle for fle in files]
        cls.datalake = cls.clt.get_datalake()
        cls.datalake.upload_data(cls.files, ["tag3"])
        data_list = datalake.fetch_data(quantity=2)
        cls.dataset = cls.clt.create_dataset("datatest", data_list)
        cls.dataset.update('detection')
        cls.project = cls.clt.create_project("test_project_1")
        cls.experiment = cls.project.create_experiment(
            name="test_experiment_1")
        cls.parameters = {
            "param1": 1
        }
        cls.experiment.log('parameters', data=cls.parameters, type="table")
        cls.model = cls.clt.create_model("test_model", "detection")
        cls.model_with_sources = cls.clt.create_model("test_model_with_source", "detection")
        cls.model_with_sources.update(
            source_dataset=cls.dataset,
        )
        cls.model_with_sources.update(
            source_experiment=cls.experiment
        )

    def test_get_model_platform_url(self,):
        base_url = self.clt.connexion.base_url
        self.assertEqual("{}/model/{}".format(base_url, self.model.id),
                         self.model.get_resource_url_on_platform())

        self.clt.connexion.base_url = None
        with self.assertRaises(exceptions.PicselliaError):
            self.model.get_resource_url_on_platform()
        self.clt.connexion.base_url = base_url

    def test_create_model(self):
        model = self.clt.create_model("model_1", "classification")

        self.assertEqual(model.name, "model_1")
        self.assertEqual(model.type, "classification")

        model.delete()

    def test_create_model_same_name_error(self):
        with self.assertRaises(exceptions.ResourceConflictError):
            self.clt.create_model(self.model.name, "classification")

    def test_get_model_by_id(self):
        model = self.clt.create_model("model_1", "classification")

        model_retr = self.clt.get_model_by_id(model.id)
        self.assertEqual(model.id, model_retr.id)
        self.assertEqual(model.name, model_retr.name)
        self.assertEqual(model.type, model_retr.type)

        model.delete()

    def test_get_model_by_id_not_found(self):
        with self.assertRaises(exceptions.ResourceNotFoundError):
            self.clt.get_model_by_id(
                "014630b4-691a-41f0-a48d-cf2e1f9487f0")

    def test_get_model_by_name(self):
        model_retr = self.clt.get_model("test_model")

        self.assertEqual(self.model.id, model_retr.id)
        self.assertEqual(self.model.name, model_retr.name)
        self.assertEqual(self.model.type, model_retr.type)

    def test_get_model_by_name_not_found(self):
        with self.assertRaises(exceptions.ResourceNotFoundError):
            self.clt.get_model("unknown")

    def test_list_models(self):
        model2 = self.clt.create_model("model_2", "classification")
        model3 = self.clt.get_model("test_model_with_source")
        models = self.clt.list_models()

        self.assertIsNotNone(models)
        self.assertEqual(len(models), 3)

        # sort to ensure order
        names = sorted([self.model.name, model2.name, model3.name])
        names_retr = sorted([model.name for model in models])

        ids = sorted([self.model.id, model2.id, model3.id])
        ids_retr = sorted([model.id for model in models])

        self.assertListEqual(names, names_retr)
        self.assertListEqual(ids, ids_retr)

        model2.delete()

    def test_update_model(self):
        self.model.update(labels={'0': 'car', '1': 'bird'})
        self.model.update(description="Yes yes yes", tag=["test_tag"])

    def test_model_store(self,):
        with self.assertRaises(FileNotFoundError):
            self.model.store('config', 'unknown')

        self.model.store('config', 'tests/files/sm_test_file.config')
        # test file already stored
        self.model.store('config', 'tests/files/sm_test_file.config')
        self.model.store('model-latest', 'tests/files/test_dir', True)
        path_dwl = './tests/files/test_dir.zip'
        self.assertTrue(os.path.exists(path_dwl))
        os.remove(path_dwl)

        self.model.store('large_file', 'tests/files/lg_test_file.pb')

        with self.assertRaises(FileNotFoundError):
            self.model.store('unknown', 'unknown')

        self.assertIsNotNone(self.model.id)
        self.model.download('config')
        path_dwl = './{}'.format(self.model.id)
        self.assertTrue(os.path.exists(path_dwl))
        shutil.rmtree(path_dwl)

        self.model.download('model-latest', './tests/files/')
        path_dwl = './tests/files/{}'.format(self.model.id)
        self.assertTrue(os.path.exists(path_dwl))
        shutil.rmtree(path_dwl)

        with self.assertRaises(FileNotFoundError):
            self.model.download('unknown')

    def test_update_thumb(self,):
        self.model.update_thumbnail("tests/files/test.png")

        with self.assertRaises(FileNotFoundError):
            self.model.update_thumbnail("unknown")

        with self.assertRaises(exceptions.InvalidQueryError):
            self.model.update_thumbnail("tests/files/lg_test_file.pb")

    def test_deploy(self,):
        config = {
            "min_det_threshold": 0.2
        }
        deployment = self.model.deploy(
            config=config
        )
        fetched_deployment = self.clt.get_deployment(deployment.name)
        self.assertEqual(deployment.name, fetched_deployment.name)

    def test_deploy_wrong_config_key(self,):
        config = {
            "min_det_threshold_error": 0.2
        }
        with self.assertRaises(exceptions.InvalidQueryError):
            deployment = self.model.deploy(
                config=config
            )

    def test_deploy_wrong_config_type(self,):
        config = {
            "min_det_threshold": "0.2"
        }
        with self.assertRaises(exceptions.InvalidQueryError):
            deployment = self.model.deploy(
                config=config
            )

    def test_deploy_wrong_config_interval(self,):
        config = {
            "min_det_threshold": 20.0
        }
        with self.assertRaises(exceptions.InvalidQueryError):
            deployment = self.model.deploy(
                config=config
            )

    def test_get_source_dataset(self,):
        source_dataset = self.model_with_sources.get_source_dataset()
        self.assertEqual(source_dataset.name, self.dataset.name)
        self.assertEqual(source_dataset.version, self.dataset.version)
        self.assertEqual(source_dataset.id, self.dataset.id)

    def test_get_source_dataset_no_dataset(self,):
        with self.assertRaises(exceptions.ResourceNotFoundError):
            self.model.get_source_dataset()

    def test_get_source_experiment(self,):
        source_experiment = self.model_with_sources.get_source_experiment(
            False, False, False
        )
        self.assertEqual(source_experiment.name, self.experiment.name)
        self.assertEqual(source_experiment.id, self.experiment.id)
    
    def test_get_source_experiment_no_experiment(self,):
        with self.assertRaises(exceptions.ResourceNotFoundError):
            self.model.get_source_experiment()
    

        
        

class TestExperimentCRUD(TestInitializedClientSDK):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.project = cls.clt.create_project("test_project_experiment_crud")
        cls.experiment = cls.project.create_experiment(
            name="test_experiment_1")
        cls.exp_id = cls.experiment.id

    def test_get_experiment_by_name(self):
        experiment = self.project.get_experiment(name="test_experiment_1")
        self.assertEqual(self.exp_id, experiment.id)

    def test_get_experiment_by_id(self):
        experiment = self.project.get_experiment(id=self.exp_id)
        self.assertEqual(self.exp_id, experiment.id)

    def test_get_experiment_without_identifier_error(self):
        with self.assertRaises(exceptions.PicselliaError):
            self.project.get_experiment()

    def test_list_experiments(self):
        experiments = self.project.list_experiments()
        self.assertEqual(len(experiments), 1)
        self.assertEqual(self.exp_id, experiments[0].id)

    def test_update_experiment(self):
        self.experiment.update(description="test")

    def test_delete_experiment(self):
        experiment = self.project.create_experiment(
            name="test_experiment_delete")

        experiment.delete()
        with self.assertRaises(exceptions.ResourceNotFoundError):
            experiment = self.project.get_experiment(
                name="test_experiment_delete")

    def test_create_experiment_from_another(self):
        exp1 = self.project.create_experiment(name="test_experiment_3")
        exp2 = self.project.create_experiment(name="test_experiment_4", previous=exp1)

        exp_retr = self.project.get_experiment("test_experiment_4")
        self.assertEqual(exp2.id, exp_retr.id)

        exp2.delete()
        exp1.delete()

    def test_create_experiment_from_model_source(self):
        model = self.clt.create_model("model2", "classification")
        exp = self.project.create_experiment(name="test_experiment_5", source=model)

        exp_retr = self.project.get_experiment("test_experiment_5")
        self.assertEqual(exp.id, exp_retr.id)

        exp.delete()
        model.delete()

    def test_delete_all_experiments(self):
        self.project.create_experiment(name="test_experiment_2")

        self.project.delete_all_experiments()
        with self.assertRaises(exceptions.ResourceNotFoundError):
            self.project.get_experiment(name="test_experiment_1")
        with self.assertRaises(exceptions.ResourceNotFoundError):
            self.project.get_experiment(name="test_experiment_2")


class TestExperiment(TestInitializedClientSDK):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.project = cls.clt.create_project("test_project_experiment")
        cls.experiment = cls.project.create_experiment(
            name="test_experiment_1")
        cls.exp_id = cls.experiment.id
        files = os.listdir('tests/files/test_push_dataset_dir')
        files = ['tests/files/test_push_dataset_dir/' + fle for fle in files]
        datalake = cls.clt.get_datalake()
        data_list = datalake.upload_data(files, ["tag_exp"])
        dataset = cls.clt.create_dataset("test_push_dataset_test", data_list)
        dataset.update(type="detection")
        dataset1 = cls.clt.create_dataset("test_push_dataset_test1", data_list)
        dataset1.update(type="detection")
        dataset2 = cls.clt.create_dataset("test_push_dataset_test2", data_list)
        dataset2.update(type="detection")
        cls.project.attach_dataset(dataset)

    def test_get_experiment_platform_url(self,):
        base_url = self.clt.connexion.base_url
        self.assertEqual("{}/experiment/{}".format(base_url, self.experiment.id),
                         self.experiment.get_resource_url_on_platform())

        self.clt.connexion.base_url = None
        with self.assertRaises(exceptions.PicselliaError):
            self.experiment.get_resource_url_on_platform()
        self.clt.connexion.base_url = base_url

    def test_logging(self,):
        self.experiment.start_logging_chapter("chapter 1")
        self.experiment.start_logging_buffer(5)
        self.experiment.end_logging_buffer()
        self.experiment.send_experiment_logging("chapter 1", "chapter 1")

    def test_update_job_status(self,):
        self.experiment.update_job_status("success")

    def test_launch(self,):
        self.experiment.launch()

    def test_publish(self,):
        self.experiment.publish("test_model_1")
        model = self.clt.get_model("test_model_1")
        model.delete()

    def test_store_with_path_and_download(self,):
        self.experiment.store("small_file", "tests/files/test_dir", True)
        self.experiment.store("large_file", "tests/files/lg_test_file.pb")
        os.remove("tests/files/test_dir.zip")
        self.experiment.download("small_file", "tests/files/dl_test_dir")
        self.assertTrue(os.path.isfile("tests/files/dl_test_dir/test_dir.zip"))
        os.remove("tests/files/dl_test_dir/test_dir.zip")
        self.experiment.download("large_file", "tests/files/dl_test_dir")
        self.assertTrue(os.path.isfile(
            "tests/files/dl_test_dir/lg_test_file.pb"))
        os.remove("tests/files/dl_test_dir/lg_test_file.pb")
        self.experiment.store(
            "small_file", "tests/files/sm_test_file.config")  # test update file
        with self.assertRaises(exceptions.ResourceNotFoundError):
            self.experiment.download("not_a_file")
        files = self.experiment.list_artifacts()
        files = [fle["name"] for fle in files]
        self.assertIn("small_file", files)
        self.assertIn("large_file", files)
        self.project.get_experiment("test_experiment_1", with_artifacts=True)
        shutil.rmtree("test_experiment_1")
        self.project.get_experiment(
            "test_experiment_1", with_artifacts=True, tree=True)
        shutil.rmtree("test_experiment_1")
        self.experiment.delete_artifact("small_file")
        self.experiment.delete_all_artifacts()

    def test_log(self,):
        self.experiment.log("value", 25, 'value')  # test log single value
        self.experiment.log("image", 'tests/files/test.png',
                            'image')  # test log image
        self.experiment.log("line", [1, 2, 3, 4], "line")  # test log line
        # test log replace value
        self.experiment.log("value", 26, "value", True)
        # test log update no replace value
        self.experiment.log("value", 26, "value")
        self.experiment.log("line", [5, 6, 7], "line")  # test log append lines
        log_list = self.experiment.list_logs()
        log_list = [dt["name"] for dt in log_list]
        self.assertIn("value", log_list)
        self.assertIn("line", log_list)
        self.assertIn("image", log_list)
        self.experiment.delete_log("value")
        self.experiment.delete_all_logs()

    def test_download_annotations_pic_train_test_split(self,):
        dataset = self.clt.get_dataset("test_push_dataset_test", "first")
        dataset.upload_annotations_from_file(
            ann_path="tests/files/test_annotations_rectangle.json", ann_format="PICSELLIA")
        experiment = self.project.create_experiment(
            name="test_experiment_2", dataset=dataset)
        experiment.download_annotations()
        experiment.png_dir = "tests/files/png_dir"
        experiment.download_pictures()
        experiment.generate_labelmap()
        experiment.train_test_split()
        experiment = self.project.get_experiment("test_experiment_1")
        experiment.dict_annotations = {}
        experiment.base_dir = ""
        with self.assertRaises(exceptions.ResourceNotFoundError):
            experiment.generate_labelmap()  # test no 'images' key in dict annotations
        with self.assertRaises(exceptions.ResourceNotFoundError):
            experiment.download_pictures()  # test no 'images' key in dict annotations
        with self.assertRaises(exceptions.ResourceNotFoundError):
            experiment.train_test_split()  # test no 'images' key in dict annotations
        shutil.rmtree("tests/files/png_dir")
        os.remove("label_map.pbtxt")

    def test_create_scan(self,):
        config = {
            'script': 'tests/__init__.py',
            'execution': {
                'type': 'agents'
            },
            'strategy': 'grid',
            'metric': {
                'name': 'Loss-total_loss',
                'goal': 'minimize'
            },
            'parameters': {
                'batch_size': {
                    'values': [2, 4, 8],
                },
            },
            'data': ['tests/files/test.png'],
            'requirements': [
                {
                    'package': 'numpy',
                    'version': '0.0.1'
                }
            ]
        }
        self.project.create_scan("test_scan", config)

        config["script"] = "tests/files/not_a_file.txt"
        with self.assertRaises(FileNotFoundError):
            self.project.create_scan("test_scan_no_file", config)

    def test_create_scan_large_script(self,):
        config = {
            'script': 'tests/files/lg_test_file.pb',
            'execution': {
                'type': 'agents'
            },
            'strategy': 'grid',
            'metric': {
                'name': 'Loss-total_loss',
                'goal': 'minimize'
            },
            'parameters': {
                'batch_size': {
                    'values': [2, 4, 8],
                },
            },
        }
        self.project.create_scan("test_scan_large", config)

    def test_create_scan_2(self,):
        config = {
            'image': 'picsellpn/simple-run:1.0',
            'execution': {
                'type': 'agents'
            },
            'strategy': 'grid',
            'metric': {
                'name': 'Loss-total_loss',
                'goal': 'minimize'
            },
            'parameters': {
                'batch_size': {
                    'values': [2, 4, 8],
                },
            },
            'requirements': 'tests/files/test_req.txt'
        }
        self.project.create_scan("test_scan_2", config)

    def test_create_scan_error(self,):
        config = {
            'image': 'picsellpn/simple-run:1.0',
            'execution': {
                'type': 'agents'
            },
            'strategy': 'grid',
            'metric': {
                'name': 'Loss-total_loss',
                'goal': 'minimize'
            },
            'parameters': {
                'batch_size': {
                    'values': [2, 4, 8],
                },
            },
            'requirements': {
                'package': 'numpy',
                'version': '0.0.1'
            }
        }
        with self.assertRaises(exceptions.InvalidQueryError):
            self.project.create_scan("test_scan_3", config)

    def test_create_scan_and_test_runs(self,):
        config = {
            'image': 'picsellpn/simple-run:1.0',
            'execution': {
                'type': 'agents'
            },
            'strategy': 'grid',
            'metric': {
                'name': 'Loss-total_loss',
                'goal': 'minimize'
            },
            'parameters': {
                'batch_size': {
                    'values': [2, 4, 8],
                },
            },
        }
        scan = self.project.create_scan("test_scan_run_1", config)
        run = scan.get_next_run()
        experiment = run.get_experiment()
        self.assertEqual(experiment.name, "test_scan_run_1-0")
        run = scan.get_run_by_id(run.id)
        run.update(status="success")
        run.end()

    def test_run_download_data_script_and_req(self,):
        config = {
            'script': 'tests/__init__.py',
            'execution': {
                'type': 'agents'
            },
            'strategy': 'grid',
            'metric': {
                'name': 'Loss-total_loss',
                'goal': 'minimize'
            },
            'parameters': {
                'batch_size': {
                    'values': [2, 4, 8],
                },
            },
            'data': ['tests/files/test.png'],
            'requirements': [
                {
                    'package': 'requests',
                    'version': '2.23.0'
                }
            ]
        }
        scan = self.project.create_scan("test_scan_run_2", config)
        run = scan.get_next_run()
        run.download_script()
        run.download_data()
        run.install_requirements()

    def test_generate_requirements(self,):
        config = {
            'script': 'tests/__init__.py',
            'execution': {
                'type': 'agents'
            },
            'strategy': 'grid',
            'metric': {
                'name': 'Loss-total_loss',
                'goal': 'minimize'
            },
            'parameters': {
                'batch_size': {
                    'values': [2, 4, 8],
                },
            },
            'requirements': "tests/files/wrong_test_req.txt"
        }
        with self.assertRaises(exceptions.ResourceNotFoundError):
            # wrong requirements path
            self.project.create_scan("test_scan_run_3", config)
        config["requirements"] = "tests/files/bad_test_req.txt"
        config["requirements"] = "tests/files/test_req.txt"
        self.project.create_scan("test_scan_run_3", config)

    def test_create_scan_and_launch(self,):
        config = {
            'image': 'picsellpn/simple-run:1.0',
            'execution': {
                'type': 'agents'
            },
            'strategy': 'grid',
            'metric': {
                'name': 'Loss-total_loss',
                'goal': 'minimize'
            },
            'parameters': {
                'batch_size': {
                    'values': [2, 4, 8],
                },
            },
        }
        scan = self.project.create_scan("test_scan_run_4", config)
        with self.assertRaises(exceptions.InvalidQueryError):
            scan.launch()


class TestClearAssets(TestInitializedClientSDK):

    def test_clear_datasets(self):
        try:
            datasets = self.clt.list_datasets()
        except exceptions.ResourceNotFoundError:
            datasets = []
        for dataset in datasets:
            dataset.delete()

    def test_clear_data(self):
        datalake = self.clt.get_datalake()
        try:
            datas = datalake.list_data()
            for data in datas:
                data.delete()
        except exceptions.NoDataError:
            datas = []

    def test_clear_models(self):
        models = self.clt.list_models()
        for model in models:
            model.delete()

    def test_clear_projects(self):
        projects = self.clt.list_projects()
        for project in projects:
            project.delete()

    def test_clear_deployments(self):
        deployments = self.clt.list_deployments()
        for deployment in deployments:
            deployment.delete()


class TestDeployment(TestInitializedClientSDK):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        datalake = cls.clt.get_datalake()
        models = cls.clt.list_models()
        for model in models:
            model.delete()
        try:
            datalist = datalake.list_data()
        except exceptions.NoDataError:
            datalist = []
        for one_data in datalist:
            one_data.delete()
        try:
            deployments = cls.clt.list_deployments()
        except exceptions.ResourceNotFoundError:
            deployments = []
        for deployment in deployments:
            deployment.delete()

        project_list = cls.clt.list_projects()
        for project in project_list:
            project.delete()

        files = os.listdir('tests/files/test_image_dir')
        cls.files = ['tests/files/test_image_dir/' + fle for fle in files]
        cls.datalake = cls.clt.get_datalake()
        cls.datalake.upload_data(cls.files, ["tag3"])
        data_list = datalake.fetch_data(quantity=2)
        cls.dataset = cls.clt.create_dataset("datatest", data_list)
        cls.dataset.update('detection')
        cls.dataset2 = cls.clt.create_dataset("datatest2", data_list)
        cls.dataset2.update('detection')
        cls.dataset_no_type = cls.clt.create_dataset("dataset_no_type", data_list)
        cls.dataset_wrong_type = cls.clt.create_dataset("dataset_wrong_type", data_list)
        cls.dataset_wrong_type.update('detectionKOK')
        cls.project = cls.clt.create_project("test_project_1")
        cls.experiment = cls.project.create_experiment(
            name="test_experiment_1")
        cls.parameters = {
            "param1": 1
        }
        cls.experiment.log('parameters', data=cls.parameters, type="table")
        cls.model = cls.clt.create_model("test_model", "detection")
        cls.model_with_sources = cls.clt.create_model("test_model_with_source", "detection")
        cls.model_with_sources.update(
            source_dataset=cls.dataset,
        )
        cls.model_with_sources.update(
            source_experiment=cls.experiment
        )
        cls.deployment = cls.model_with_sources.deploy(
            config={
                "min_det_threshold": 0.2
            }
        )
        cls.deployment2 = cls.model.deploy(
            config={
                "min_det_threshold": 0.2
            }
        )

    def test_get_deployment_by_name(self):
        fetched_deployment = self.clt.get_deployment(
            name=self.deployment.name
        )
        self.assertEqual(self.deployment.id, fetched_deployment.id)
        self.assertEqual(self.deployment.name, fetched_deployment.name)

    def test_get_deployment_by_id(self):
        fetched_deployment = self.clt.get_deployment_by_id(
            id=str(self.deployment.id)
        )
        self.assertEqual(self.deployment.id, fetched_deployment.id)
        self.assertEqual(self.deployment.name, fetched_deployment.name)

    def test_get_deployment_by_name_not_exists(self):
        with self.assertRaises(exceptions.ResourceNotFoundError): 
            name = "stupid-name"
            fetched_deployment = self.clt.get_deployment(
                name=name
            )

    def test_get_deployment_by_id_not_exists(self):
        with self.assertRaises(exceptions.ResourceNotFoundError): 
            stupid_id = str(uuid.uuid4())
            fetched_deployment = self.clt.get_deployment_by_id(
                id=stupid_id
            )

    def test_list_deployments(self):
        deployments = self.clt.list_deployments()
        self.assertEqual(len(deployments), 2)
        deployment = deployments[0]
        self.assertEqual(self.deployment.id, deployment.id)
        self.assertEqual(self.deployment.name, deployment.name)

    def test_init_feedback_loop_wrong_dataset_type(self):
        with self.assertRaises(exceptions.InvalidQueryError):
            self.deployment.init_feedback_loop(
                dataset=self.dataset_wrong_type
            )

    def test_init_feedback_loop_no_dataset_type(self):
        with self.assertRaises(exceptions.InvalidQueryError):
            self.deployment.init_feedback_loop(
                dataset=self.dataset_no_type
            )

    def test_init_feedback_loop(self):
        self.deployment.init_feedback_loop(
            dataset=self.dataset
        )

    def test_update_feedback_loop(self):
        self.deployment2.init_feedback_loop(
            dataset=self.dataset
        )
        self.deployment2.update_feedback_loop(
            dataset=self.dataset2
        )
        
    def test_init_continous_training(self):
        self.deployment.init_continuous_training(
            project=self.project,
            dataset=self.dataset,
            model=self.model_with_sources,
            parameters=self.parameters,
            training_type="experiment",
            feedback_loop_trigger=100
        )
    
    def test_activate_continuous_training(self):
        self.deployment.activate_continuous_training()

    def detest_activate_continuous_training(self):
        self.deployment.deactivate_continuous_training()

    def test_activate_continuous_training_not_set(self):
        with self.assertRaises(exceptions.ResourceNotFoundError):
            self.deployment2.activate_continuous_training()

    def test_deactivate_continuous_training_not_set(self):
        with self.assertRaises(exceptions.ResourceNotFoundError):
            self.deployment2.deactivate_continuous_training()
