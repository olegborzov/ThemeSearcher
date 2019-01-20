#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from typing import Dict, List, Set

__all__ = ("get_data_path", "read_themes_phrases", "read_stop_words")


def get_data_path() -> str:
    """
    Получение пути к папке с входными данными (темы и стоп-слова).

    :return: путь к папке с входными данными
    """
    dir_path = os.getenv("THEMESEARCHER_DATA_DIR")

    if dir_path is None:
        dir_path = os.getcwd()
        dir_path = os.path.join(dir_path, "data")

    return dir_path


def read_themes_phrases(data_path: str) -> Dict[str, List[str]]:
    """
    Парсинг json-файла тем с фразами для построения индекса

    :return: словарь тем с фразами
    """
    phrases_path = os.path.join(data_path, "phrases.json")
    with open(phrases_path, "r", encoding="UTF-8") as f:
        phrases = json.load(f)

    return phrases


def read_stop_words(data_path: str) -> Set[str]:
    """
    Парсинг файла со стоп-словами

    :return: множество стоп-слов
    """
    stop_words_path = os.path.join(data_path, "stop_words.txt")
    with open(stop_words_path, "r", encoding="UTF-8") as f:
        stop_words = set(line.strip() for line in f)

    return stop_words
