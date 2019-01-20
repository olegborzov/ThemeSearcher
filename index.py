#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, Optional, Set

from pymorphy2 import MorphAnalyzer


__all__ = ("InvertedIndex",)


@dataclass(frozen=True)
class Phrase:
    theme_ids: Set[int]
    words_count: int


class InvertedIndex:
    """
    Инвертированный индекс
    Содержит методы для построения индекса и получения результатов (тем)
    по запросу.
    """

    _themes: List[str]  # Список фраз
    _phrases: List[Phrase]  # Список ID тем для фраз
    _phrases_ids: Dict[str, int]  # Словарь {фраза: ID фразы в _phrases_themes}
    _words_phrases: Dict[str, Set[int]]  # Словарь {слово: множество ID фраз}

    _stop_words: Set[str]
    _morph: MorphAnalyzer

    def __init__(self,
                 themes_phrases: Dict[str, List[str]],
                 stop_words: Set[str]):
        """
        Создание морфологического словаря для лемматизации и построение индекса

        :param themes_phrases: словарь тем с фразами
        :param stop_words:
        """
        self._themes = []
        self._phrases = []
        self._phrases_ids = {}
        self._words_phrases = {}

        self._stop_words = stop_words
        self._morph = MorphAnalyzer()

        self._build(themes_phrases)

    # API
    def get_themes(self, query: str) -> Set[str]:
        """
        Получение списка тем по запросу.

        :param query: запрос
        :return: список названий тем
        """

        query_words = self._phrase_to_words(query)
        query_phrases = self._get_query_phrases(query_words)

        query_themes = set()
        for phrase in query_phrases:
            for theme_id in phrase.theme_ids:
                query_themes.add(self._themes[theme_id])

        return query_themes

    def _get_query_phrases(self, query_words: Set[str]) -> List[Phrase]:
        """
        Ищет все фразы, где встречаются слова запроса и возвращает те фразы,
        все слова которых полностью содержатся в запросе
        (за исключением стоп-слов).

        :param query_words: список нормализованных слов запроса
        :return: Список фраз по запросу
        """
        query_phrases = {}

        for norm_word in query_words:
            word_phrases = self._words_phrases.get(norm_word)
            if word_phrases is None:
                continue

            for phrase_id in word_phrases:
                try:
                    query_phrases[phrase_id]["words_count"] += 1
                except KeyError:
                    query_phrases[phrase_id] = {
                        "phrase": self._phrases[phrase_id],
                        "words_count": 1
                    }

        query_phrases = [
            phrase_info["phrase"]
            for phrase_info in query_phrases.values()
            if phrase_info["words_count"] == phrase_info["phrase"].words_count
        ]

        return query_phrases

    # Построение индекса
    def _build(self, themes_phrases: Dict[str, List[str]]):
        """
        Построение индекса
        """
        for theme_name, phrases in themes_phrases.items():
            self._add_theme(theme_name, phrases)

    # Методы для работы с темами
    def _add_theme(self, theme_name: str, phrases: List[str]):
        """
        Добавляет тему и фразы темы в индекс

        :param theme_name: фраза
        :return: индекс фразы в списке
        """
        self._themes.append(theme_name)
        theme_id = len(self._themes) - 1

        for phrase in phrases:
            self._add_phrase(phrase, theme_id)

    def _get_theme_name(self, theme_id: int) -> str:
        """
        Возвращает название темы по ее ID.

        :param theme_id: id темы
        :return: название темы
        """
        return self._themes[theme_id]

    # Методы для работы с фразами
    def _add_phrase(self, phrase_value: str, theme_id: int):
        """
        Индексирует фразу (если она еще не проиндексирована).
        Добавляет id темы во множество id тем для этой фразы.

        :param phrase_value: значение фразы
        :return: индекс фразы в списке
        """
        try:
            phrase_id = self._phrases_ids[phrase_value]
            phrase = self._phrases[phrase_id]
            phrase.theme_ids.add(theme_id)
        except KeyError:
            phrase_words = self._phrase_to_words(phrase_value)

            phrase = Phrase({theme_id}, len(phrase_words))
            self._phrases.append(phrase)
            phrase_id = len(self._phrases) - 1
            self._phrases_ids[phrase_value] = phrase_id

            for word in phrase_words:
                self._add_word(word, phrase_id)

    # Методы для работы со словами
    def _add_word(self, norm_word: str, phrase_id: int):
        """
        Добавление слова в словарь, если его там нет.
        В список id фраз слова добавляется id текущей фразы.

        :param norm_word: слово
        :param phrase_id: id фразы
        """
        word_phrases = self._words_phrases.setdefault(norm_word, set())
        word_phrases.add(phrase_id)

    def _phrase_to_words(self, phrase: str) -> Set[str]:
        """
        Возвращает множество лемматизированных слов, из которых состоит фраза
        (за исключением стоп-слов).
        Алгоритм:
            1. Фраза разбивается на слова
            По каждому слову:
            2. Если слова нет в списке стоп-слов - слово лемматизируется и
            добавляется с множество слов

        :param phrase: фраза
        :return: множество слов
        """
        phrase_words = set(word for word in phrase.split(" ") if word)
        result_words = set()

        for word in phrase_words:
            norm_word = self._normalize_word(word)
            if norm_word is not None:
                result_words.add(norm_word)

        return result_words

    @lru_cache(maxsize=500)
    def _normalize_word(self, word: str) -> Optional[str]:
        """
        Нормализация слова: приведение к нижнему регистру и лемматизация.

        :param word: слово
        :return: нормализованное слово или None, если это стоп-слово
        """

        norm_word = word.lower()
        if norm_word in self._stop_words:
            return None

        return self._morph.parse(norm_word)[0].normal_form
