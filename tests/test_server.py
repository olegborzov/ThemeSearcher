#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import unittest
from urllib.parse import quote

from server import app


class TestServer(unittest.TestCase):
    def setUp(self):
        self.test_client = app.test_client

    def test_good_response(self):
        query = "тайская кухня"
        url = "/?query=" + quote(query)
        request, result = self.test_client.get(url)
        result_dict = json.loads(result.text)

        self.assertEqual(int(result.status), 200)
        self.assertEqual(result_dict["query"], query)
        self.assertCountEqual(result_dict["themes"], ['книги', 'товары'])

    def test_url_without_query_param(self):
        url = "/"
        request, result = self.test_client.get(url)
        result_dict = json.loads(result.text)
        good_dict = {'error_msg': 'Запрос не указан'}

        self.assertEqual(int(result.status), 400)
        self.assertDictEqual(result_dict, good_dict)

    def test_not_found_query(self):
        query = "абвг деж"
        url = "/?query=" + quote(query)
        request, result = self.test_client.get(url)
        result_dict = json.loads(result.text)

        self.assertEqual(int(result.status), 200)
        self.assertEqual(result_dict["query"], query)
        self.assertCountEqual(result_dict["themes"], [])


if __name__ == '__main__':
    unittest.main()
