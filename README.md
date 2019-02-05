# ThemeSearcher - тестовое задание
Асинхронный HTTP-сервер, обрабатывающий поисковые запросы пользователей.

- Сервис принимает текстовый запрос пользователя.
Пример URL (при условии, что сервер запущен на локальной машине на порту 9090):
```
http://localhost:9090/?query=купить%20слона
```
- Определяет, к какой теме или темам может принадлежать запрос (подробности см. ниже).
- Выдает результат в формате json, в котором указан список соответствующих запросу тем.<br>
Пример результата: 
```
>>> http "http://localhost:9090/?query=тайская кухня"
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 96
Content-Type: application/json
Keep-Alive: 5

{
    "query": "тайская кухня",
    "themes": [
        "товары",
        "книги"
    ]
}
```
- Если передан пустой запрос, либо query-параметр "query" отсутствует в запросе, 
возвращается ответ с 400 кодом и описанием ошибки:
```
>>> http "http://localhost:9090/?query="             
HTTP/1.1 400 Bad Request
Connection: keep-alive
Content-Length: 50
Content-Type: application/json
Keep-Alive: 5

{
    "error_msg": "Запрос не указан"
}
```

Каждая тема определяется набором фраз, например:
- новости: "деревья на Садовом кольце", "добрый автобус", "выставка IT-технологий";
- кухня: "рецепт борща", "яблочный пирог", "тайская кухня";
- товары: "Дети капитана Гранта", "зимние шины", "Тайская кухня";
или любые другие, на ваше усмотрение. Важно, чтобы какая-то из фраз встретилась в нескольких наборах индексов, как "тайская кухня" в примере.

Правило принадлежности запроса теме:
1. Если набор слов из запроса содержит в себе все слова какой-либо из фраз, то запрос считается соответствующим теме. Иначе - не соответствующим.
2. Порядок слов в запросе и во фразах не учитывается.

## Установка
Чтобы установить пакет, нужно выполнить следующие команды в папке проекта:
```
virtualenv venv
source venv/bin/activate
python3 setup.py install
```

В папке проекта должна лежать папка **data** с файлами: 
 - **phrases.json** - темы с фразами
 - **stopwords.txt** - стоп-слова, которые не учитываются при построении индекса и поиске тем

Примеры файлов в нужном формате уже есть в папке data.<br>
Также можно указать другой путь к папке data с помощью переменной окружения *THEMESEARCHER_DATA_DIR*.

## Запуск сервера
```
python3 server.py
```
По умолчанию сервер запускается на порту: 9090

## Запуск тестов
Тесты запускаются следующей командой (внутри виртуального окружения):
```
python3 setup.py test
```

## Сравнение производительности с реализацией на SQlite3
Сравним производительность реализованного алгоритма с реализацией на основе БД SQLite3.

#### Производительность реализации на SQlite3
Реализуем простую таблицу в SQlite3 c помощью ORM Peewee и расширением FTS4. 
И заполним ее данными из примера - поисковыми фразами (без учета тем).
```
from playhouse.sqlite_ext import (CSqliteExtDatabase, FTSModel, DocIDField, SearchField)
import read_data, index

# Считываем входные данные
path = read_data.get_data_path()
themes_phrases = read_data.read_themes_phrases(path)


# Создаем In_memory базу данных с полнотекстовым поиском
db = CSqliteExtDatabase(':memory:')


class PhraseIndex(FTSModel):
    docid = DocIDField()
    content = SearchField()
    class Meta:
        database = db
        
db.create_tables([PhraseIndex])


# Заливаем фразы в БД
with db.atomic():
    db_phrases = []
    counter = 1
    for theme, theme_phrases in themes_phrases.items():
        for phrase in theme_phrases:
            pi = PhraseIndex.create(docid=counter, content=phrase)
            db_phrases.append(pi)
            counter += 1
```

Измерим производительность полученного решения (пренебрежем влиянием функции list на производительность):
```
>>> %%timeit
... results = list(PhraseIndex.select(PhraseIndex).where(PhraseIndex.content.match("тайская кухня")))
704 µs ± 10.9 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)
```

#### Производительность нашей реализации
Считаем данные и построим индекс:
```
import index, read_data

# Строим индекс
path = read_data.get_data_path()
themes_phrases = read_data.read_themes_phrases(path)
stop_words = read_data.read_stop_words(path)
myindex = index.InvertedIndex(themes_phrases, stop_words)
```

Измерим производительность нашего решения:
```
>>> %%timeit
... results = myindex.get_themes("тайская кухня")
16.6 µs ± 2.06 µs per loop (mean ± std. dev. of 7 runs, 100000 loops each)
```

Как видим, производительность нашего "велосипедного" решения более чем на порядок
превосходит реализацию с помощью БД.
