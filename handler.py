import json
from db import ensure_db_connection
import common as CONFIG

@ensure_db_connection
def hello(event, context, db_connection):

    start = event['queryStringParameters']['start']
    end = event['queryStringParameters']['end']

    cursor = db_connection.cursor()
    cursor.execute("""
    select * from public.posts_table offset {} fetch first {} rows only
    """.format(start, end))

    result = [row._asdict() for row in cursor]

    responseObject = {}
    responseObject['statusCode'] = 200
    responseObject['headers'] = {}
    responseObject['headers']['Content-Type'] = 'application/json'
    responseObject['headers']['Access-Control-Allow-Origin'] = '*'
    responseObject['headers']['Allow'] = 'GET, OPTIONS, POST'
    responseObject['headers']['Access-Control-Allow-Methods'] = '*'
    responseObject['body'] = json.dumps(result)

    return responseObject    
