#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sanic import Sanic
from sanic.request import Request
from sanic.response import json

from index import InvertedIndex
from read_data import get_data_path, read_stop_words, read_themes_phrases


app = Sanic(configure_logging=False)


@app.listener('before_server_start')
async def setup_index(app, loop):
    data_path = get_data_path()
    stop_words = read_stop_words(data_path)
    themes_phrases = read_themes_phrases(data_path)

    app.index = InvertedIndex(themes_phrases, stop_words)


@app.route('/')
async def index(request: Request):
    query = request.raw_args.get("query")
    if not query:
        return json(
            {"error_msg": "Запрос не указан"},
            status=400,
            ensure_ascii=False,
            indent=2
        )

    query_themes = app.index.get_themes(query)
    response_dict = {"themes": query_themes, "query": query}
    return json(response_dict, ensure_ascii=False, indent=2)


def run_server(to_debug=False):
    app.run(host="0.0.0.0", port=9090, debug=to_debug)


if __name__ == "__main__":
    run_server()
