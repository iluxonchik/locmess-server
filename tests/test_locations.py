from locmess import settings
from locmess.settings import logging

import os
import unittest
from pony.orm import *
from locmess.tables import Location
import json
from tests.base import BaseTestCase


class LocationTestCase(BaseTestCase):

    @db_session
    def test_get_all_locations(self):
        """
        Different users creating different locations, make sure a user
        can access all of them.
        """
        username1 = 'Dr.Dre'
        self._lm.add_user(username=username1, password='TheDocumentary')
        token_u1 = self._lm.login(username=username1, password='TheDocumentary')

        username2 = 'The Game'
        self._lm.add_user(username=username2, password='TheDocumentary')
        token_u2 = self._lm.login(username=username2, password='TheDocumentary')

        # this user won't have any locations added
        username3 = 'iluxonchik.meow'
        self._lm.add_user(username=username3, password='TheDocumentary')
        token_u3 = self._lm.login(username=username3, password='TheDocumentary')


        location = {'latitude': 1.0001, 'longitude': 1.0001, 'radius': 200}
        loc1 = self._lm.add_location(username1, token_u1, name='Dres House', is_gps=True,
            location_json=json.dumps(location))

        location = {'latitude': 1.0001, 'longitude': 1.0002, 'radius': 200}
        loc2 = self._lm.add_location(username2, token_u2, name='Games House', is_gps=True,
            location_json=json.dumps(location))

        location = {'latitude': 1.0001, 'longitude': 1.0003, 'radius': 200}
        loc3 = self._lm.add_location(username2, token_u2, name='Other House', is_gps=True,
            location_json=json.dumps(location))

        location = {'latitude': 100.0001, 'longitude': 100.0003, 'radius': 200}
        loc4 = self._lm.add_location(username2, token_u2, name='Not In Range 1',
        is_gps=True, location_json=json.dumps(location))

        location = {'latitude': 110.0001, 'longitude': 105.0003, 'radius': 200}
        loc5 = self._lm.add_location(username1, token_u1, name='Not In Range 2',
        is_gps=True, location_json=json.dumps(location))

        location = {'ssids': ['MEO-WiFi', 'eduroam']}
        loc6 = self._lm.add_location(username1, token_u1, name='Compton', is_gps=False,
            location_json=json.dumps(location))

        location = {'ssids': ['NOS-WiFi']}
        loc7 = self._lm.add_location(username2, token_u2,
                                name='Carvoeiro, Faro, Portugal', is_gps=False,
                                location_json=json.dumps(location))

        expected_locations = (loc1, loc2, loc3, loc4, loc5, loc6, loc7)

        # let's try with User #1
        res_locations = self._lm.get_all_locations(username1, token_u1)
        self.assertEqual(len(res_locations), 7, 'Unexpected location count')
        self.assertCountEqual(res_locations, expected_locations,
                                         'Unexpected location list returned')

        # let's try with User #2
        res_locations = self._lm.get_all_locations(username2, token_u2)
        self.assertEqual(len(res_locations), 7, 'Unexpected location count')
        self.assertCountEqual(res_locations, expected_locations,
                                         'Unexpected location list returned')

        # let's try with User #3
        res_locations = self._lm.get_all_locations(username3, token_u3)
        self.assertEqual(len(res_locations), 7, 'Unexpected location count')
        self.assertCountEqual(res_locations, expected_locations,
                                         'Unexpected location list returned')
