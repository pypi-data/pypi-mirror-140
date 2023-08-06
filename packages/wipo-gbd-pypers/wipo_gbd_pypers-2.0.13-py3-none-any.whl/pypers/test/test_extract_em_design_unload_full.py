import unittest
from pypers.steps.fetch.extract.em.designs_full_unload import FullUnload
from pypers.utils.utils import dict_update
import os
import shutil
from pypers.test import mock_db, mockde_db, mock_logger
from mock import patch, MagicMock
import copy


class MockMongoDatabase():

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __init__(self, create_client=False, mode=None):
        self.mode = mode
        if create_client:
            self.client = MockMongoDatabase()

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def close(self, *args, **kwargs):
        pass

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def find(self, *args, **kwargs):
        flatten = ["%s_%s" % (k, v) for k, v in args[0].items()]
        flatten.sort()
        mode = "%s_%s_%s" % (self.mode, ''.join(flatten), '%s')
        if len(args) == 2:
            flatten = ["%s_%s" % (k, v) for k, v in args[1].items()]
            flatten.sort()
        mode = mode % ''.join(flatten)
        print(mode)
        return MockMogoDbDocument(mode)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def find_one(self, *args, **kwargs):
        flatten = ["%s_%s" % (k, v) for k, v in args[0].items()]
        flatten.sort()
        mode = "%s_%s_%s" % (self.mode, ''.join(flatten), '%s')
        flatten = ["%s_%s" % (k, v) for k, v in args[1].items()]
        flatten.sort()
        mode = mode % ''.join(flatten)
        if mode == 'emap-map_applicant_F001_designs_1':
            return {
                'designs': ['F003']
            }
        if mode == 'emrp-map_representative_F002_designs_1':
            return {
                'designs': ['F002']
            }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def get_collection(self, *args, **kwargs):
        return MockMongoDatabase(mode=args[0])

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def insert_one(self, *args, **kwargs):
        pass

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def count(self):
        return 1001


class MockMogoDbDocument:

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __init__(self, mode):
        self.mode = mode
        self.data = {}
        if mode in ['emid___id_0',
                    ]:
            code = 'Delete'
            if mode == 'test_load_uid_F002__id_0':
                code = 'Update'
            self.data = {
                'uid': 'F001',
                'run_id': '1',
                'archive': 'toto',
                'Design': {
                    '@operationCode': code,
                    'ApplicantDetails': {
                        'Applicant': {
                            'ApplicantIdentifier': 'F001'
                        },
                        'ApplicantKey': {
                            'Identifier': 'F001'
                        }
                    },
                    'RepresentativeDetails': {
                        'Representative': {
                            'RepresentativeIdentifier': 'F002'
                        },
                        'RepresentativeKey': {
                            'Identifier': 'F002'
                        }
                    }

                }
            }
            if mode in ['test_load_uid_F002__id_0',
                        'test_load_uid_F003__id_0']:
                self.data.update({
                    'run_id': '1',
                    'archive': 'toto',
                })
        if mode in ['emap_uid_F001__id_0archive_0run_id_0uid_0',
                    'emap_run_id_1__id_0archive_0run_id_0',]:
            self.data = {
                'Applicant': {
                    'ApplicantIdentifier': 'F001'
                }
            }
        if mode in ['emrp_uid_F002__id_0archive_0run_id_0uid_0',
                    'emrp_run_id_1__id_0archive_0run_id_0']:
            self.data = {
                'Representative': {
                    'RepresentativeIdentifier': 'F002'
                }
            }
        self.data = [copy.deepcopy(self.data), self.data]

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def sort(self, *args, **kwargs):
        return self

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def skip(self, *args, **kwargs):
        return self

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def limit(self, *args, **kwargs):
        return self.data

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __iter__(self):
        return MockMongoDbDocumentIterator(self)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def count(self):
        return len(self.data)


class MockMongoDbDocumentIterator:
    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __init__(self, db):
        self.db = db
        self.index = 0

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def __next__(self):
        if self.index == 0:
            self.index += 1
            return self.db.data[0]
        raise StopIteration


class TestLoad(unittest.TestCase):

    path_test = os.path.join(os.path.dirname(__file__), 'foo')
    cfg = {
        'step_class':
            'pypers.steps.fetch.extract.em.designs_full_unload.FullUnload',
        'sys_path': None,
        'name': 'FullUnload',
        'meta': {
            'job': {},
            'pipeline': {
                'input': {

                },
                'collection': 'test_load',
                'run_id': 1,
                'log_dir': path_test
            },
            'step': {}
        },
    }

    extended_cfg = {
        'output_dir': path_test,
        'archive_name': 'toto',
        'remove_orig': 1,
        'dburl': 'mongodb://localhost:27017/',
        'dbname': 'toto',
        'ns_ignore': ['languageCode']
    }

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        if os.path.exists('toto'):
            shutil.rmtree('toto')
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
        step = FullUnload.load_step("test", "test", "step")
        step.process()


if __name__ == "__main__":
    unittest.main()
