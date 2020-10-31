import json
from db import ensure_db_connection

@ensure_db_connection
def hello(event, context, db_connection):
    data = json.loads(event['body'])
    print(data)
    # 'pathParameters': {'post_id': '1'}

    cursor = db_connection.cursor()
    cursor.execute('''INSERT INTO public.comments_table 
    (post_id, commnet) 
    VALUES (%s, %s)''', (
        int(event['pathParameters']['post_id']), 
        data['commentTxt']
    ))
    db_connection.commit()

    responseObject = {}
    responseObject['statusCode'] = 200
    responseObject['headers'] = {}
    responseObject['headers']['Content-Type'] = 'application/json'
    responseObject['headers']['Access-Control-Allow-Origin'] = '*'
    responseObject['headers']['Allow'] = 'GET, OPTIONS, POST, PUT'
    responseObject['headers']['Access-Control-Allow-Methods'] = '*'
    responseObject['body'] = json.dumps(event)

    return responseObject