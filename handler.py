import json
import psycopg2
from psycopg2.extras import NamedTupleCursor
import common as CONFIG

def hello():

    db_connection = psycopg2.connect(user=CONFIG.DB['user'],
                            password=CONFIG.DB['password'],
                            host=CONFIG.DB['host'],
                            port=CONFIG.DB['portnumber'],
                            database=CONFIG.DB['dbname'],
                            cursor_factory=NamedTupleCursor)
                            
    start = 0
    end = 10

    cursor = db_connection.cursor()
    cursor.execute("""
    select p.* , count(ct.commnet) as number_of_comments from public.posts p 
    left join public.comments_table ct on p.post_id = ct.post_id 
    group by p.post_id 
    offset {}
    limit {}
    """.format(start, end))

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

hello()