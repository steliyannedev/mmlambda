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
    
    def get_n_posts(self, page, section, number_of_posts):
        responseObject = self.__generate_response_dict()
        print('page: ', page)

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                select p.* , count(ct.commnet) as number_of_comments from public.posts p 
                left join public.comments_table ct on p.post_id = ct.post_id 
                where sections = '{}'
                group by p.post_id 
                order by created_on desc
                offset {}
                limit {}
            """.format(section, page, number_of_posts))

            result = [row._asdict() for row in cursor]
            print('result: ', result)
            responseObject['body'] = json.dumps(result, default=str)

        except (Exception, psycopg2.DatabaseError) as error:
            print('error: ', error)
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
    
    def upvote_post(self, post_id, username):
        responseObject = self.__generate_response_dict()
        try:
            self.save_like_record(post_id, username)
            responseObject['body'] = json.dumps('Success')
        except (Exception, psycopg2.DatabaseError) as error:
            print('upvote_post', error)
            self.__handle_errors(400, error)


    def save_like_record(self, post_id, username):
        post_from_db = self.get_post_likes_by_id(post_id, username)
        print('post_from_db', post_from_db)
        print('post_id', post_id)
        print('username', username)
        if post_from_db is None or post_from_db.likes_dislikes in (-1, 0):
            try:
                print('goes inside try')
                cursor = self.db_connection.cursor()
                cursor.execute("""
                INSERT INTO post_likes (username , post_id , likes_dislikes) 
                VALUES ('{}', {}, 1)
                ON CONFLICT (username, post_id) DO UPDATE 
                SET likes_dislikes = post_likes.likes_dislikes + 1;
                """.format(username, post_id))

                self.db_connection.commit()
                self.increment_post(post_id)
        
            except (Exception, psycopg2.DatabaseError) as error:
                print('save_like_record error: ', error)
                self.__handle_errors(400, error)

        elif post_from_db.likes_dislikes == 1:
            return


    def save_dislike_record(self, post_id, username):
        post_from_db = self.get_post_likes_by_id(post_id, username)
        if post_from_db is None or post_from_db.likes_dislikes in (1, 0):
            try:
                print('save_dislike method')
                cursor = self.db_connection.cursor()
                cursor.execute("""
                INSERT INTO post_likes (username , post_id , likes_dislikes) 
                VALUES ('{}', {}, -1)
                ON CONFLICT (username, post_id) DO UPDATE 
                SET likes_dislikes = post_likes.likes_dislikes - 1;
                """.format(username, post_id))

                self.db_connection.commit()
                self.decrement_post(post_id)
        
            except (Exception, psycopg2.DatabaseError) as error:
                print('save_dislike_record error: ', error)
                self.__handle_errors(400, error)

        elif post_from_db.likes_dislikes == 1:
            return

    
    def increment_post(self, post_id):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
            update public.posts 
            set post_likes = post_likes + 1
            where post_id = {}
            """.format(post_id))

            self.db_connection.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print('increment_post error: ', error)
            self.__handle_errors(400, error)


    def get_liked_posts_by_user(self, username):
        responseObject = self.__generate_response_dict()

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
            select * from public.post_likes where username = '{}'
            """.format(username))

            self.db_connection.commit()

            result = [row._asdict() for row in cursor]
            print('result: ', result)
            responseObject['body'] = json.dumps(result, default=str)

        except (Exception, psycopg2.DatabaseError) as error:
            print('liked posts', error)
            self.__handle_errors(400, error)

        return responseObject

    
    def get_post_likes_by_id(self, post_id, username):
        cursor = self.db_connection.cursor()
        cursor.execute("""
        select likes_dislikes from public.post_likes
        where post_id = {} and username = '{}'
        """.format(post_id, username))

        self.db_connection.commit()

        return cursor.fetchone()
            

    def decrement_post(self, post_id):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
            update public.posts 
            set post_likes = post_likes - 1
            where post_id = {}
            """.format(post_id))

            self.db_connection.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print('increment_post error: ', error)
            self.__handle_errors(400, error)

    def downvote_post(self, post_id, username):
        responseObject = self.__generate_response_dict()
        try:
            self.save_dislike_record(post_id, username)
            responseObject['body'] = json.dumps('Success')

        except (Exception, psycopg2.DatabaseError) as error:
            print('downvote_post error: ', error)
            self.__handle_errors(400, error)

        return responseObject
    
    def search_results(self, letters):
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

    def move_new_posts(self):
        # currentDate = datetime.now()
        # d = currentDate - timedelta(hours=1)
        cursor = self.db_connection.cursor()
        cursor.execute("""
            update public.posts set sections = 'trending' where post_likes > 0
            """)
        
        self.db_connection.commit()

    def move_trending_posts(self):
        # currentDate = datetime.now()
        # d = currentDate - timedelta(hours=2)
        cursor = self.db_connection.cursor()
        cursor.execute("""
            update public.posts set sections = 'hot' where post_likes > 1
            """)
        
        self.db_connection.commit()
