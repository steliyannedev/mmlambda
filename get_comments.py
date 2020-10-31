import json
from db import ensure_db_connection

@ensure_db_connection
def get_comments(event, context, db_connection):
    post_id = event['pathParameters']['post_id']
    cursor = db_connection.cursor()
    cursor.execute("""
    select * from public.comments_table where post_id = {}
    """.format(post_id))

    result = [row._asdict() for row in cursor]

    responseObject = {}
    responseObject['statusCode'] = 200
    responseObject['body'] = json.dumps(result)

    return responseObject