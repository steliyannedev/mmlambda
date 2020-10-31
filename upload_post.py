import json
from db import ensure_db_connection
import common as CONFIG
import base64
import boto3
from datetime import date

@ensure_db_connection
def hello(event, context, db_connection):
    data = json.loads(event['body'])
    s3_url = save_image_to_s3(data['img_url'])

    cursor = db_connection.cursor()
    cursor.execute('''INSERT INTO public.posts 
    (author_id, author_name, post_title, post_likes, post_dislikes, img_url, sections, created_on) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', (        
        data['author_id'], 
        data['author_name'], 
        data['post_title'],
        data['post_likes'],
        data['post_dislikes'],
        s3_url,
        data['sections'],
        data['created_on']
    ))
    db_connection.commit()

    responseObject = {}
    responseObject['statusCode'] = 200
    responseObject['headers'] = {}
    responseObject['headers']['Content-Type'] = 'application/xml'
    responseObject['headers']['Access-Control-Allow-Origin'] = '*'
    responseObject['headers']['Allow'] = 'GET, OPTIONS, POST, PUT'
    responseObject['headers']['Access-Control-Allow-Methods'] = '*'
    responseObject['body'] = json.dumps(event)

    return responseObject

def save_image_to_s3(image):
    s3 = boto3.client('s3')
    filename = 'an_image.png'
    s3_url = 'https://s3-image-storing-bucket.s3.eu-central-1.amazonaws.com/{}'.format(filename)
    s3.put_object(Body=base64.b64decode(image.split(',')[1]), Bucket='s3-image-storing-bucket', Key=filename)
    return s3_url
    

    
# INSERT INTO public.posts
# (author_id, author_name, post_title, post_likes, post_dislikes, img_url, sections, created_on)
# VALUES('', '', '', 0, 0, '', '', '');
