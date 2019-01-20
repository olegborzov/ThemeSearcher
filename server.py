#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sanic import Sanic
from sanic.request import Request
from sanic.response import json

from index import InvertedIndex
from read_data import get_data_path, read_stop_words, read_themes_phrases


app = Sanic()


@app.listener('before_server_start')
async def setup_db(app, loop):
    data_path = get_data_path()
    stop_words = read_stop_words(data_path)
    themes_phrases = read_themes_phrases(data_path)

    app.index = InvertedIndex(themes_phrases, stop_words)


@app.route('/')
async def index(request: Request):
    query = request.raw_args.get("query")
    if query is None:
        return json({"error_msg": "Запрос не указан"}, status=400)

    query_themes = app.index.get_themes(query)
    return json({"themes": query_themes}, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
