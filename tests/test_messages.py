from locmess import settings
from locmess.settings import logging

import os
import requests
import unittest
from pony.orm import *
from locmess.tables import Message, Location
import json
from tests.base import BaseTestCase
from datetime import datetime


class MessageTestCase(BaseTestCase):

    @db_session
    def test_message_created(self):
        self._lm.add_user(username='TheGame', password='TheDocumentary')
        token = self._lm.login(username='TheGame', password='TheDocumentary')

        location = {'latitude': 19, 'longitude': 92, 'radius': 1992}
        location = self._lm.add_location('TheGame', token, name='Dres House', is_gps=True,
            location_json=json.dumps(location))

        self._lm.add_message('TheGame', token, title='Question',
                             location=location,
                             text='Would you do it if my name was Dre?',
                             is_centralized=True,
                             is_black_list=False,
                             properties=json.dumps({}))


    @db_session
    def test_get_messages_in_gps_radius(self):
        username = 'Dr.Dre'
        self._lm.add_user(username=username, password='TheDocumentary')
        token = self._lm.login(username=username, password='TheDocumentary')

        location = {'latitude': 1.0001, 'longitude': 1.0001, 'radius': 200}
        loc1 = self._lm.add_location(username, token, name='Dres House', is_gps=True,
            location_json=json.dumps(location))

        location = {'latitude': 1.0001, 'longitude': 1.0002, 'radius': 200}
        loc2 = self._lm.add_location(username, token, name='Games House', is_gps=True,
            location_json=json.dumps(location))

        location = {'latitude': 1.0001, 'longitude': 1.0003, 'radius': 200}
        loc3 = self._lm.add_location(username, token, name='Other House', is_gps=True,
            location_json=json.dumps(location))

        location = {'latitude': 100.0001, 'longitude': 100.0003, 'radius': 200}
        loc4 = self._lm.add_location(username, token, name='Not In Range 1',
        is_gps=True, location_json=json.dumps(location))

        location = {'latitude': 110.0001, 'longitude': 105.0003, 'radius': 200}
        loc5 = self._lm.add_location(username, token, name='Not In Range 2',
        is_gps=True, location_json=json.dumps(location))


        msg_1 = self._lm.add_message(username, token, title='Question',
                             location=loc1,
                             text='Would you do it if my name was Dre?',
                             is_centralized=True,
                             is_black_list=False,
                             properties=json.dumps({}))

        msg_2 = self._lm.add_message(username, token, title='Another Question',
                             location=loc2,
                             text='Would you do it if my name was Dre?',
                             is_centralized=True,
                             is_black_list=False,
                             properties=json.dumps({}))

        msg_3 = self._lm.add_message(username, token, title='One More Question',
                             location=loc3,
                             text='Would you do it if my name was Dre?',
                             is_centralized=True,
                             is_black_list=False,
                             properties=json.dumps({}))

        self._lm.add_message(username, token, title='Not In Range 1',
                             location=loc4,
                             text='Would you do it if my name was Dre?',
                             is_centralized=True,
                             is_black_list=False,
                             properties=json.dumps({}))

        self._lm.add_message(username, token, title='Not In Range',
                             location=loc5,
                             text='Would you do it if my name was Dre?',
                             is_centralized=True,
                             is_black_list=False,
                             properties=json.dumps({}))

        my_location = (1, 1)

        messages = self._lm.get_available_messages_by_gps(username,
                token, curr_coord=my_location)

        self.assertEqual(len(messages), 3, 'Unexpected number of matching messages')
        self.assertCountEqual([msg_1, msg_2, msg_3], messages, 'Unexpected matching messages')


    def test_get_messages_in_essid_region(self):
        pass

    def test_location_created(self):
        """
        Just making sure that location creation is working.
        """
        self._lm.add_user(username='TheGame', password='TheDocumentary')
        token = self._lm.login(username='TheGame', password='TheDocumentary')

        location = {'latitude': 19, 'longitude': 92, 'radius': 1992}
        self._lm.add_location('TheGame', token, name='Dres House', is_gps=True,
            location_json=json.dumps(location))

        loc = self._lm.get_location_by_name(name='Dres House')
        self.assertIsNotNone(loc)
        self.assertTrue(loc.is_gps)

        raw_json = loc.location
        parsed_json = json.loads(raw_json)

        self.assertEqual(parsed_json['latitude'], 19)
        self.assertEqual(parsed_json['longitude'], 92)
        self.assertEqual(parsed_json['radius'], 1992)
