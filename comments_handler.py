import json
import psycopg2
from datetime import datetime

from db import ensure_db_connection


class CommentsHandler:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    
    def get_comments(self, post_id):
        responseObject = self.__generate_response_dict()
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
            SELECT * FROM public.comments_table WHERE post_id = {}
            """.format(post_id))

            result = [row._asdict() for row in cursor]
            responseObject['body'] = json.dumps(result, default=str)

        except (Exception, psycopg2.DatabaseError) as error:
            responseObject['statusCode'] = 400
            responseObject['body'] = json.dumps(error)

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
    

    def delete_comment(self, comment_id):
        responseObject = self.__generate_response_dict()
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''DELETE FROM public.comments_table
            WHERE comment_id = {}'''.format(comment_id['pathParameters']['comment_id']))

            self.db_connection.commit()
            responseObject['body'] = 'Success'
            
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            responseObject['statusCode'] = 400
            responseObject['body'] = json.dumps(error)

        return responseObject

    def save_comment(self, event):
        data = json.loads(event['body'])
        responseObject = self.__generate_response_dict()

        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''INSERT INTO public.comments_table 
            (post_id, commnet, created_on) 
            VALUES (%s, %s, %s)''', (
                int(event['pathParameters']['post_id']), 
                data['commentTxt'],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            self.db_connection.commit()

            responseObject['body'] = json.dumps(event)

        except (Exception, psycopg2.DatabaseError) as error:
            responseObject['statusCode'] = 400
            responseObject['body'] = json.dumps(error)

        return responseObject