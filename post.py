import json
from db import ensure_db_connection
import common as CONFIG

@ensure_db_connection
def hello(db_connection):
    # pathParameters key hold post_id value
    post_id = 34
    cursor = db_connection.cursor()
    cursor.execute("""
    select post_id, post_title from public.posts where post_title like '%UI%'
    """.format(post_id))

    result = [row._asdict() for row in cursor]
    print(result)

    responseObject = {}
    responseObject['statusCode'] = 200
    responseObject['headers'] = {}
    responseObject['headers']['Content-Type'] = 'application/json'
    responseObject['headers']['Access-Control-Allow-Origin'] = '*'
    responseObject['headers']['Allow'] = 'GET, OPTIONS, POST'
    responseObject['headers']['Access-Control-Allow-Methods'] = '*'
    responseObject['body'] = json.dumps(result, default=str)
    return responseObject

hello()

