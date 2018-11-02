#!/usr/bin/env/ python3

"""Unittests for streamtape.py."""

import configparser
import datetime as dt
from datetime import timedelta
import json
from json import JSONDecodeError
import unittest
from unittest.mock import patch, mock_open

import streamtape


@patch('builtins.print')
@patch('streamtape.read_quickstreams')
class TestListQuickstreams(unittest.TestCase):

    def test_error_printed_if_quickstreams_empty(self, mock_read, mock_print):
        mock_read.return_value = {}
        streamtape.list_quickstreams()
        mock_print.assert_called_with("No Quickstream bookmarks found.")

    def test_json_printed_if_quickstreams_exist(self, mock_read, mock_print):
        mock_read.return_value = {'print_this': {'print': 'this'}}
        streamtape.list_quickstreams()
        expected = json.dumps({'print_this': {'print': 'this'}}, indent=4)
        mock_print.assert_called_with(expected)


@patch('streamtape.read_quickstreams')
class TestDeleteQuickstream(unittest.TestCase):

    @patch('streamtape.save_quickstreams')
    def test_bookmarked_name_deletes_correctly(self, mock_save, mock_read):
        mock_read.return_value = {'to_del': {'to': 'delete'},
                                  'to_keep': {'to': 'keep'}}
        streamtape.delete_quickstream('to_del')
        mock_save.assert_called_with({'to_keep': {'to': 'keep'}})

    @patch('builtins.print')
    def test_wrong_name_prints_help_message(self, mock_print, mock_read):
        mock_read.return_value = {'name_key': {'key': 'value'}}
        streamtape.delete_quickstream('wrong')
        mock_print.assert_called_with(
            "No Quickstream under that name (-ls to list them, -h for help)"
        )

    @patch('streamtape.save_quickstreams')
    def test_wrong_name_does_not_call_save(self, mock_save, mock_read):
        mock_read.return_value = {'name_key': {'key': 'value'}}
        streamtape.delete_quickstream('wrong')
        assert not mock_save.called


@patch('streamtape.read_quickstreams')
class TestLoadQuickstream(unittest.TestCase):

    def test_bookmarked_name_returns_correctly(self, mock_read):
        mock_read.return_value = {'name_key': {'key': 'value'}}
        loaded_quickstream = streamtape.load_quickstream('name_key')
        self.assertEqual({'key': 'value'}, loaded_quickstream)

    def test_wrong_name_calls_sys_exit(self, mock_read):
        mock_read.return_value = {'name_key': {'key': 'value'}}
        self.assertRaises(SystemExit, streamtape.load_quickstream, 'wrong')


@patch('builtins.open')
class TestReadQuickstreams(unittest.TestCase):

    def test_returns_right_data_if_quickstreams_present(self, mock_in_open):
        mock_written = json.dumps({'read_this': {'read': 'this'}}, indent=4)
        mock_loaded = json.loads(mock_written)
        with mock_open(mock_in_open, read_data=mock_written) as __:
            result = streamtape.read_quickstreams()
        self.assertEqual(result, mock_loaded)

    def test_returns_blank_dict_if_no_quickstreams_saved(self, mock_in_open):
        with mock_open(mock_in_open, read_data='') as __:
            result = streamtape.read_quickstreams()
        self.assertEqual(result, {})

    def test_raises_decode_exception_if_no_quickstreams_(self, mock_in_open):
        with mock_open(mock_in_open, read_data='') as __:
            streamtape.read_quickstreams()
        self.assertRaises(JSONDecodeError)

    def test_returns_blank_dictionary_if_no_file_found(self, mock_in_open):
        mock_in_open.side_effect = FileNotFoundError
        result = streamtape.read_quickstreams()
        self.assertEqual(result, {})


@patch('builtins.input')
@patch('streamtape.save_quickstreams')
@patch('streamtape.read_quickstreams')
class TestCreateBookmark(unittest.TestCase):

    def test_unused_name_calls_save_with_right_arg(self, mock_read,
                                                   mock_save, mock_input):
        test_record_settings = {'bookmark': 'unused'}
        mock_read.return_value = {'saved': {'already': 'saved'}}
        streamtape.create_bookmark(test_record_settings)
        mock_save.assert_called_once_with(
            {'saved': {'already': 'saved'}, 'unused': {'bookmark': None}}
        )

    def test_used_name_prompts_for_new_name(self, mock_read,
                                            mock_save, mock_input):
        test_record_settings = {'bookmark': 'used'}
        mock_read.return_value = {'used': {'already': 'used'}}
        streamtape.create_bookmark(test_record_settings)

        mock_input.assert_called()

    def test_used_name_saves_if_input_given_unused_name(self, mock_read,
                                                        mock_save, mock_input):
        test_record_settings = {'bookmark': 'used'}
        mock_read.return_value = {'used': {'already': 'used'}}
        mock_input.return_value = 'not_used'
        streamtape.create_bookmark(test_record_settings)

        mock_save.assert_called_with({'used': {'already': 'used'},
                                      'not_used': {'bookmark': None}})

    def test_used_name_prompts_until_unused_name_given(self, mock_read,
                                                       mock_save, mock_input):
        test_record_settings = {'bookmark': 'used'}
        mock_read.return_value = {'used': {'already': 'used'}}
        mock_input.side_effect = ['used', 'used', 'end_loop']
        streamtape.create_bookmark(test_record_settings)
        self.assertEqual(mock_input.call_count, 3)


class TestTimeToDatetime(unittest.TestCase):

    def test_later_time_yields_same_day_datetime_object(self):
        now = dt.datetime.now()
        later_time = now + dt.timedelta(minutes=5)
        start = streamtape.time_to_datetime('{}:{}'.format(later_time.hour,
                                                           later_time.minute))
        self.assertEqual(now.day, start.day)

    def test_earlier_time_yields_next_day_datetime_object(self):
        now = dt.datetime.now()
        later_time = now - dt.timedelta(minutes=5)
        start = streamtape.time_to_datetime('{}:{}'.format(later_time.hour,
                                                           later_time.minute))
        self.assertEqual(now.day + 1, start.day)

    def test_start_time_same_as_current_time_yields_next_day(self):
        now = dt.datetime.now()
        start = streamtape.time_to_datetime('{}:{}'.format(now.hour,
                                                           now.minute))
        self.assertEqual(now.day + 1, start.day)


@patch('subprocess.call')
@patch('streamtape.os')
class TestRecordStream(unittest.TestCase):

    def test_quality_arg_used_if_given(self, mock_os, mock_sub):
        streamtape.record_stream('channel', 'arg_quality', None)
        sub_call = str(mock_sub.call_args)
        self.assertTrue('arg_quality' in sub_call)

    @patch('streamtape.get_setting')
    def test_if_quality_none_default_used(self, mock_get, mock_os, mock_sub):
        mock_get.side_effect = ['def_quality', 'path', 'wait',
                                'attempts', 'rec_attempts']
        streamtape.record_stream('channel', None, None)
        sub_call = str(mock_sub.call_args)
        self.assertTrue('def_quality' in sub_call)

    def test_if_filename_is_not_none_it_is_used(self, mock_os, mock_sub):
        streamtape.record_stream('channel', None, 'given_filename')
        sub_call = str(mock_sub.call_args)
        self.assertTrue('given_filename.ts' in sub_call)

    def test_if_filename_is_none_timestamped_is_used(self, mock_os, mock_sub):
        streamtape.record_stream('channel', None, None)
        test_file_time = dt.datetime.now().strftime('%m-%d(%H-%M)')
        sub_call = str(mock_sub.call_args)
        self.assertTrue('{}.ts'.format(test_file_time) in sub_call)


if __name__ == '__main__':
    unittest.main(buffer=True)
