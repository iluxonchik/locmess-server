import unittest

from pony.orm import *

from locmess.tables import db
from locmess.locmess import LocMess

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        db.drop_all_tables(with_all_data=True)  # in case a db already exists
        self._lm = LocMess()
        db.create_tables()

    def tearDown(self):
        db.drop_all_tables(with_all_data=True)
