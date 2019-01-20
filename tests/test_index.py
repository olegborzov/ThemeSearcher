#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from index import InvertedIndex


class TestIndex(unittest.TestCase):
    def setUp(self):
        stop_words = {"для", "у", "а", "на", "как", "где"}
        theme_phrases = {
            "товары": [
                "тайская кухня",
                "зимние шины"
            ],
            "книги": [
                "дети капитана гранта",
                "тайская кухня",
                "граф монте-кристо"
            ],
            "фильмы": [
                "дети капитана гранта",
                "китайская кухня",
                "граф монте-кристо"
            ],
            "кухня": [
                "рецепт борща",
                "как готовить плов",
                "рецепты тайской кухни"
            ]
        }
        self.index = InvertedIndex(theme_phrases, stop_words)

    def test_not_found(self):
        query = "несуществующее словище"
        themes = self.index.get_themes(query)

        self.assertFalse(themes)

    def test_query_contain_only_one_phrase_word(self):
        query = "кухня"
        themes = self.index.get_themes(query)

        self.assertFalse(themes)

    def test_multiple_themes(self):
        query = "дети капитана гранта"
        themes = self.index.get_themes(query)

        self.assertCountEqual(themes, {'книги', 'фильмы'})

    def test_query_has_more_words_than_phrase(self):
        query = "купить книгу дети капитана гранта"
        themes = self.index.get_themes(query)

        self.assertCountEqual(themes, {'книги', 'фильмы'})

    def test_query_has_other_words_order_than_phrase(self):
        query = "шины зимние"
        themes = self.index.get_themes(query)

        self.assertCountEqual(themes, {'товары'})

    def test_stop_words_not_affect_on_result(self):
        query = "готовить плов"
        themes = self.index.get_themes(query)

        self.assertCountEqual(themes, {'кухня'})

    def test_words_in_other_form(self):
        query = "рецепты борщ"
        themes = self.index.get_themes(query)

        self.assertCountEqual(themes, {'кухня'})


if __name__ == '__main__':
    unittest.main()
