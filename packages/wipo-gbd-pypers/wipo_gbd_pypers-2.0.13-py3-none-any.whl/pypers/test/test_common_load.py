import unittest
from pypers.steps.fetch.common.load import Load
from pypers.utils.utils import dict_update
import os
import shutil
from pypers.test import mock_db, mockde_db, mock_logger

from mock import patch, MagicMock


class MockMongoDatabase():

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __init__(self, create_client=False):
        if create_client:
            self.client = MockMongoDatabase()

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def close(self, *args, **kwargs):
        pass

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def get_collection(self, *args, **kwargs):
        return MockMongoDatabase()

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def insert_one(self, *args, **kwargs):
        pass


class TestLoad(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class': 'pypers.steps.fetch.common.load.Load',
        'sys_path': None,
        'name': 'load',
        'meta': {
            'job': {},
            'pipeline': {
                'input': {

                },
                'output_dir': path_test,
                'collection': 'test_load',
                'run_id': 1,
                'log_dir': path_test
            },
            'step': {}
        },
    }

    extended_cfg = {
        'manifest':{
                    'data_files': {}
        },
        'input_dir': path_test,
        'archive_name': 'vi12345.zip',
        'remove_orig': 1,
        'ns_ignore': ['languageCode']
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        self.cfg = dict_update(self.cfg, self.extended_cfg)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def tearDown(self):
        try:
            shutil.rmtree(self.path_test)
            pass
        except Exception as e:
            pass

    @patch('pymongo.database.Database',
           MagicMock(return_value=MockMongoDatabase(create_client=True)))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def test_process(self):
        mockde_db.update(self.cfg)
        step = Load.load_step("test", "test", "step")
        step.process()
        for el in self.extended_cfg['manifest']['data_files'].keys():
            p_xml = el.get('xml', None)
            if p_xml:
                dest_path = os.path.join(self.path_test, p_xml)
                self.assertFalse(os.path.exists(dest_path))
        self.assertEqual(step.archive_name, self.cfg['archive_name'])


if __name__ == "__main__":
    unittest.main()
