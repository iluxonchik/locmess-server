from locmess import settings
from locmess.settings import logging
from locmess.exceptions import AuthorizationError

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

    @db_session
    def test_get_messages_in_essid_region(self):
        username = 'Dr.Dre'
        self._lm.add_user(username=username, password='TheDocumentary')
        token = self._lm.login(username=username, password='TheDocumentary')


        location = {'ssids': ['MEO-WiFi', 'eduroam']}
        loc1 = self._lm.add_location(username, token, name='Dres House', is_gps=False,
            location_json=json.dumps(location))

        location = {'ssids': ['NOS-WiFi']}
        loc2 = self._lm.add_location(username, token, name='Game\'s House', is_gps=False,
            location_json=json.dumps(location))

        location = {'ssids': ['eduroam', 'Kitty Cent']}
        loc3 = self._lm.add_location(username, token, name='Other House', is_gps=False,
            location_json=json.dumps(location))

        location = {'ssids': ['Kitty Cent', 'MEO-WiFi']}
        loc4 = self._lm.add_location(username, token, name='Catspotting Spot',
        is_gps=False, location_json=json.dumps(location))

        location = {'ssids': ['ElGato', 'Doctor\'s advocate']}
        loc5 = self._lm.add_location(username, token, name='Kittens Library',
        is_gps=False, location_json=json.dumps(location))

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

        msg_4 = self._lm.add_message(username, token, title='How bout another one?',
                             location=loc4,
                             text='Would you do it if my name was Dre?',
                             is_centralized=True,
                             is_black_list=False,
                             properties=json.dumps({}))

        msg_5 = self._lm.add_message(username, token, title='And one more time',
                             location=loc5,
                             text='Would you do it if my name was Dre?',
                             is_centralized=True,
                             is_black_list=False,
                             properties=json.dumps({}))

        my_location = ('eduroam',)  # msg_1, msg_3
        messages = self._lm.get_available_messages_by_ssid(username,
                token, my_ssids=my_location)

        self.assertEqual(len(messages), 2, 'Unexpected number of matching messages')
        self.assertCountEqual([msg_1, msg_3], messages, 'Unexpected matching messages')

        my_location = ('eduroam', 'Kitty Cent')  # msg_1, msg_3, msg_4
        messages = self._lm.get_available_messages_by_ssid(username,
                token, my_ssids=my_location)

        expected_msg_list = [msg_1, msg_3, msg_4]
        self.assertEqual(len(messages), 3, 'Unexpected number of matching messages')
        self.assertCountEqual(expected_msg_list, messages, 'Unexpected matching messages\n'
        '\t Expected: {}\n\tActual:{}'.format(expected_msg_list, messages))

        my_location = ('funny', 'Kitty Cent')  # msg_1, msg_3, msg_4
        messages = self._lm.get_available_messages_by_ssid(username,
                token, my_ssids=my_location)

        self.assertEqual(len(messages), 2, 'Unexpected number of matching messages')
        self.assertCountEqual([msg_3, msg_4], messages, 'Unexpected matching messages')

        my_location = ()
        messages = self._lm.get_available_messages_by_ssid(username,
                token, my_ssids=my_location)

        self.assertEqual(len(messages), 0, 'Unexpected number of matching messages')

        my_location = ('the protege', 'of the D.R.E.')
        messages = self._lm.get_available_messages_by_ssid(username,
                token, my_ssids=my_location)

        self.assertEqual(len(messages), 0, 'Unexpected number of matching messages')


    def test_location_created(self):
        """
        Just making sure that location creation is working.
        """
        self._lm.add_user(username='TheGame', password='TheDocumentary')
        token = self._lm.login(username='TheGame', password='TheDocumentary')

        location = {'latitude': 19, 'longitude': 92, 'radius': 1992}
        self._lm.add_location('TheGame', token, name='Dres House', is_gps=True,
            location_json=json.dumps(location))

        loc = self._lm.get_location_by_name('TheGame', token, name='Dres House')
        self.assertIsNotNone(loc)
        self.assertTrue(loc.is_gps)

        raw_json = loc.location
        parsed_json = json.loads(raw_json)

        self.assertEqual(parsed_json['latitude'], 19)
        self.assertEqual(parsed_json['longitude'], 92)
        self.assertEqual(parsed_json['radius'], 1992)


    def test_user_profile_keys(self):
        """
        Test user profile keys.

        All of the tests are in the same method: yes, bad test design, but
        we're in a hurry, and hey, the tests are stil here.
        """
        username = 'KittyCent'
        self._lm.add_user(username=username, password='PowerOfTheKitten')
        token = self._lm.login(username=username, password='PowerOfTheKitten')

        expected_value = 'value1'
        self._lm.update_key(username, token, 'key1', expected_value)
        value_of_key1 = self._lm.get_value(username, token, 'key1')
        self.assertEqual(value_of_key1, expected_value, 'Key-Value mismatch')

        # let's get a value of a non-existing key
        value_of_key2 = self._lm.get_value(username, token, 'key2')
        self.assertIsNone(value_of_key2, 'Non-existing key value is not None')

        # Let's delete an existing key
        self._lm.delete_key(username, token, 'key1')
        value_of_key1 = self._lm.get_value(username, token, 'key1')
        self.assertIsNone(value_of_key1, 'Key not deleted')

        # Let's delete an non-existing key (make sure it's ignored)
        self._lm.delete_key(username, token, 'key2')
        value_of_key2 = self._lm.get_value(username, token, 'key2')
        self.assertIsNone(value_of_key2, 'Non-existing key not deleted')

        # Let's add a key ...
        expected_value = 'value1'
        self._lm.update_key(username, token, 'key1', expected_value)
        value_of_key1 = self._lm.get_value(username, token, 'key1')
        self.assertEqual(value_of_key1, expected_value, 'Key-Value mismatch')

        # ... amd then update the existing key's value
        expected_value = 'new value'
        self._lm.update_key(username, token, 'key1', expected_value)
        value_of_key1 = self._lm.get_value(username, token, 'key1')
        self.assertEqual(value_of_key1, expected_value, 'Key-Value mismatch')

        # Let's add many key-values
        expected_key1 = 'key1'
        expected_value1 = 'value1'

        expected_key2 = 'key2'
        expected_value2 = 'value2'

        expected_key3 = 'key3'
        expected_value3 = 'value3'

        self._lm.update_key(username, token, expected_key1, expected_value1)
        self._lm.update_key(username, token, expected_key2, expected_value2)
        self._lm.update_key(username, token, expected_key3, expected_value3)

        expected_prfile_key_value_dict = {
                                            expected_key1 : expected_value1,
                                            expected_key2 : expected_value2,
                                            expected_key3 : expected_value3,
                                         }
        actual_profile_key_value_dict = self._lm.get_key_value_bin(username, token)

        self.assertCountEqual(actual_profile_key_value_dict,
                                                expected_prfile_key_value_dict)

    @db_session
    def test_blacklist_and_whitelist_messages(self):
        # BLACKLIST: profiles that match DON'T receive messages
        # WHITELIST: ONLY profiles that MATCH receive the messages
        username = 'Dr.Dre'
        self._lm.add_user(username=username, password='TheDocumentary')
        token = self._lm.login(username=username, password='TheDocumentary')

        key1 = 'Favorite Album'
        value1 = '2001'
        self._lm.update_key(username, token, key1, value1)

        key2 = 'Favourite Album Contender'
        value2 = 'The Chronic'
        self._lm.update_key(username, token, key2, value2)


        location = {'latitude': 1.0001, 'longitude': 1.0001, 'radius': 200}
        loc1 = self._lm.add_location(username, token, name='Dres House', is_gps=True,
            location_json=json.dumps(location))

        # msg1 will NOT be received by the user
        msg1_props = {
                            key1: value1,
                            key2: value2,
                     }
        msg_1 = self._lm.add_message(username, token, title='Question',
                             location=loc1,
                             text='Would you do it if my name was Dre?',
                             is_centralized=True,
                             is_black_list=True,
                             properties=json.dumps(msg1_props))

        # msg2 WILL be be received by the user
        msg2_props = {
                            key1: value1,
                            key2: value2,
                     }
        msg_2 = self._lm.add_message(username, token, title='Another Question',
                             location=loc1,
                             text='Would you do it if my name was Dre?',
                             is_centralized=True,
                             is_black_list=False,
                             properties=json.dumps(msg2_props))

        # msg3 WILL be be received by the user (null policy)
        msg_3 = self._lm.add_message(username, token, title='One More Question',
                             location=loc1,
                             text='Would you do it if my name was Dre?',
                             is_centralized=True,
                             is_black_list=False,
                             properties=json.dumps({}))

        # msg4 WILL be be received by the user (null policy)
        msg_4 = self._lm.add_message(username, token, title='And Once Again',
                             location=loc1,
                             text='Would you do it if my name was Dre?',
                             is_centralized=True,
                             is_black_list=False,
                             properties=json.dumps({}))

        my_location = (1, 1)

        messages = self._lm.get_available_messages_by_gps(username,
                token, curr_coord=my_location)

        self.assertEqual(len(messages), 3, 'Unexpected number of matching messages')
        self.assertCountEqual([msg_2, msg_3, msg_4], messages, 'Unexpected matching messages')


    @db_session
    def test_delete_message(self):
        username = 'Dr.Dre'
        self._lm.add_user(username=username, password='TheDocumentary')
        token = self._lm.login(username=username, password='TheDocumentary')


        location = {'ssids': ['MEO-WiFi', 'eduroam']}
        loc1 = self._lm.add_location(username, token, name='Dres House', is_gps=False,
            location_json=json.dumps(location))

        location = {'ssids': ['NOS-WiFi']}
        loc2 = self._lm.add_location(username, token, name='Game\'s House', is_gps=False,
            location_json=json.dumps(location))

        location = {'ssids': ['eduroam', 'Kitty Cent']}
        loc3 = self._lm.add_location(username, token, name='Other House', is_gps=False,
            location_json=json.dumps(location))

        location = {'ssids': ['Kitty Cent', 'MEO-WiFi']}
        loc4 = self._lm.add_location(username, token, name='Catspotting Spot',
        is_gps=False, location_json=json.dumps(location))

        location = {'ssids': ['ElGato', 'Doctor\'s advocate']}
        loc5 = self._lm.add_location(username, token, name='Kittens Library',
        is_gps=False, location_json=json.dumps(location))

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

        msg_4 = self._lm.add_message(username, token, title='How bout another one?',
                             location=loc4,
                             text='Would you do it if my name was Dre?',
                             is_centralized=True,
                             is_black_list=False,
                             properties=json.dumps({}))

        msg_5 = self._lm.add_message(username, token, title='And one more time',
                             location=loc5,
                             text='Would you do it if my name was Dre?',
                             is_centralized=True,
                             is_black_list=False,
                             properties=json.dumps({}))

        expected_messages = [msg_1, msg_2, msg_3, msg_4, msg_5]
        all_msgs = [msg for msg in Message.select()]
        self.assertCountEqual(expected_messages, all_msgs,
                                                    'Unexpected message colleciton.')

        # Let's try to delete a message
        self._lm.delete_message(username, token, msg_3.id)
        expected_messages = [msg_1, msg_2, msg_4, msg_5]
        all_msgs = [msg for msg in Message.select()]
        self.assertCountEqual(expected_messages, all_msgs, 'Message deletion error.')

        # Let's try to delete the same message twice (make sure it's ignored)
        self._lm.delete_message(username, token, msg_3.id)
        expected_messages = [msg_1, msg_2, msg_4, msg_5]
        all_msgs = [msg for msg in Message.select()]
        self.assertCountEqual(expected_messages, all_msgs, 'Message deletion error.')

        # Now let's try to delete a message with the user who did not create it
        username = 'If_You_Ever_Knew_Dre_You_Would_Say_I_Was_The_New_Dre'
        self._lm.add_user(username=username, password='TheDocumentary')
        token = self._lm.login(username=username, password='TheDocumentary')

        with self.assertRaises(AuthorizationError):
            self._lm.delete_message(username, token, msg_1.id)

        # Make sure that the state was not changed
        expected_messages = [msg_1, msg_2, msg_4, msg_5]
        all_msgs = [msg for msg in Message.select()]
        self.assertCountEqual(expected_messages, all_msgs,
                                                    'Database state not preserved.')

    @db_session
    def test_get_my_messages(self):
        username1 = 'Dr.Dre'
        self._lm.add_user(username=username1, password='TheDocumentary')
        token1 = self._lm.login(username=username1, password='TheDocumentary')

        username2 = 'Kitty_Cent'
        self._lm.add_user(username=username2, password='TheDocumentary')
        token2 = self._lm.login(username=username2, password='TheDocumentary')

        location = {'ssids': ['MEO-WiFi', 'eduroam']}
        loc1 = self._lm.add_location(username1, token1, name='Dres House', is_gps=False,
            location_json=json.dumps(location))

        location = {'ssids': ['NOS-WiFi']}
        loc2 = self._lm.add_location(username1, token1, name='Game\'s House', is_gps=False,
            location_json=json.dumps(location))

        location = {'ssids': ['eduroam', 'Kitty Cent']}
        loc3 = self._lm.add_location(username2, token2, name='Other House', is_gps=False,
            location_json=json.dumps(location))

        location = {'ssids': ['Kitty Cent', 'MEO-WiFi']}
        loc4 = self._lm.add_location(username2, token2, name='Catspotting Spot',
        is_gps=False, location_json=json.dumps(location))

        location = {'ssids': ['ElGato', 'Doctor\'s advocate']}
        loc5 = self._lm.add_location(username2, token2, name='Kittens Library',
        is_gps=False, location_json=json.dumps(location))

        msg_1 = self._lm.add_message(username1, token1, title='Question',
                             location=loc1,
                             text='Would you do it if my name was Dre?',
                             is_centralized=True,
                             is_black_list=False,
                             properties=json.dumps({}))

        msg_2 = self._lm.add_message(username1, token1, title='Another Question',
                             location=loc2,
                             text='Would you do it if my name was Dre?',
                             is_centralized=True,
                             is_black_list=False,
                             properties=json.dumps({}))


        msg_3 = self._lm.add_message(username2, token2, title='One More Question',
                             location=loc3,
                             text='Would you do it if my name was Dre?',
                             is_centralized=True,
                             is_black_list=False,
                             properties=json.dumps({}))

        msg_4 = self._lm.add_message(username2, token2, title='How bout another one?',
                             location=loc4,
                             text='Would you do it if my name was Dre?',
                             is_centralized=True,
                             is_black_list=False,
                             properties=json.dumps({}))

        msg_5 = self._lm.add_message(username2, token2, title='And one more time',
                             location=loc5,
                             text='Would you do it if my name was Dre?',
                             is_centralized=True,
                             is_black_list=False,
                             properties=json.dumps({}))

        expected_user1_msgs = [msg_1, msg_2]
        expected_user2_msgs = [msg_3, msg_4, msg_5]

        usr1_res = self._lm.get_my_messages(username1, token1)
        self.assertCountEqual(expected_user1_msgs, usr1_res, 'Unexpected messages for user')

        usr2_res = self._lm.get_my_messages(username2, token2)
        self.assertCountEqual(expected_user2_msgs, usr2_res, 'Unexpected messages for user')
