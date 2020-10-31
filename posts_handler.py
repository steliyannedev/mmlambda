import json
import os
import string
import random
import base64
import psycopg2
from datetime import date, datetime, timedelta
from pytz import timezone

ALLOWED_IMAGE_EXTENSTIONS = ['jpeg', 'png']

class PostHandler:
    def __init__(self, db_connection, s3=None):
        self.db_connection = db_connection
        self.s3 = s3
        self.bucket_location = 's3-image-storing-bucket'
    
    def get_n_posts(self, start, end):
        responseObject = self.__generate_response_dict()

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                select p.* , count(ct.commnet) as number_of_comments from public.posts p 
                left join public.comments_table ct on p.post_id = ct.post_id 
                group by p.post_id 
                offset {}
                limit {}
            """.format(start, end))

            result = [row._asdict() for row in cursor]
            responseObject['body'] = json.dumps(result, default=str)

        except (Exception, psycopg2.DatabaseError) as error:
            self.__handle_errors(400, error)

        return responseObject


    def get_post_by_id(self, post_id):
        responseObject = self.__generate_response_dict()

        try:
            cursor =self.db_connection.cursor()
            cursor.execute("""
            select * from public.posts where post_id = {}
            """.format(post_id))

            self.db_connection.commit()

            result = [row._asdict() for row in cursor]
            responseObject['body'] = json.dumps(result, default=str)

        except (Exception, psycopg2.DatabaseError) as error:
            self.__handle_errors(400, error)

        return responseObject


    def __generate_response_dict(self):
        responseObject = {}
        responseObject['statusCode'] = 200
        responseObject['headers'] = {}
        responseObject['headers']['Content-Type'] = 'application/json'
        responseObject['headers']['Access-Control-Allow-Origin'] = '*'
        responseObject['headers']['Allow'] = 'GET, OPTIONS, POST'
        responseObject['headers']['Access-Control-Allow-Methods'] = '*'

        return responseObject


    def upload_post(self, event):
        data = json.loads(event['body'])
        responseObject = self.__generate_response_dict()
        image_s3_url = self.__save_image_to_s3(data['img_url'])

        if image_s3_url is None:

            responseObject['statusCode'] = 400
            responseObject['body'] = 'Not allowed file extension'

            return responseObject

        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''INSERT INTO public.posts 
            (author_id, author_name, post_title, post_likes, post_dislikes, img_url, sections, created_on) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', (        
                data['author_id'], 
                data['author_name'], 
                data['post_title'],
                0,
                0,
                image_s3_url,
                'new',
                datetime.now(tz=timezone('Europe/Sofia')).strftime("%Y-%m-%d %H:%M:%S")
            ))
            self.db_connection.commit()

            responseObject['headers']['Content-Type'] = 'application/xml'
            responseObject['body'] = json.dumps(data)

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            self.__handle_errors(400, error)
        
        return responseObject


    
    def __save_image_to_s3(self, base64_image):
        image_metadata, base64_encoded_image = base64_image.split(',')
        decoded_base64_image = base64.b64decode(base64_encoded_image)
        content_type = image_metadata.split(';')[0].split(':')[1]
        image_extenstion = content_type.split('/')[1]
        letters = string.ascii_letters
        filename = ''.join(random.choice(letters) for i in range(15))

        if image_extenstion not in ALLOWED_IMAGE_EXTENSTIONS:
            return None
        
        s3_url = 'https://s3-image-storing-bucket.s3.eu-central-1.amazonaws.com/{}.{}'.format(filename, image_extenstion)
        self.s3.put_object(Body=decoded_base64_image, Bucket=self.bucket_location, Key=filename + '.' + image_extenstion, ContentType=content_type) # check for error handling

        return s3_url
    
    
    def __handle_errors(self, code, error):
        responseObject = {}
        responseObject['statusCode'] = code
        responseObject['body'] = error

        return responseObject
    
    def upvotePost(self, post_id):
        responseObject = self.__generate_response_dict()

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
            update public.posts 
            set post_likes = post_likes + 1
            where post_id = {}
            """.format(post_id))

            self.db_connection.commit()

            responseObject['body'] = json.dumps('Success')

        except (Exception, psycopg2.DatabaseError) as error:
            self.__handle_errors(400, error)

        return responseObject
    

    def downvoarPost(self, post_id):
        responseObject = self.__generate_response_dict()

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
            update public.posts 
            set post_likes = post_likes - 1
            where post_id = {}
            """.format(post_id))

            self.db_connection.commit()

            responseObject['body'] = json.dumps('Success')

        except (Exception, psycopg2.DatabaseError) as error:
            self.__handle_errors(400, error)

        return responseObject
    
    def searchResults(self, letters):
        responseObject = self.__generate_response_dict()

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
            select post_id, post_title from public.posts where post_title like '%{}%'
            """.format(letters))

            self.db_connection.commit()

            result = [row._asdict() for row in cursor]
            responseObject['body'] = json.dumps(result, default=str)
        except (Exception, psycopg2.DatabaseError) as error:
            return self.__handle_errors(400, error)

        return responseObject

    def moveNewPosts(self):
        currentDate = datetime.now()
        d = currentDate - timedelta(hours=1)
        cursor = self.db_connection.cursor()
        cursor.execute("""
            update public.posts set sections = 'trending' where created_on < '{}' and created_on > '{}' and post_likes > 10
            """.format(currentDate, d))
        
        self.db_connection.commit()

    def moveTrendingPosts(self):
        currentDate = datetime.now()
        d = currentDate - timedelta(hours=2)
        cursor = self.db_connection.cursor()
        cursor.execute("""
            update public.posts set sections = 'hot' where created_on < '{}' and created_on > '{}' and post_likes > 100
            """.format(currentDate, d))
        
        self.db_connection.commit()
