import boto3
from db import ensure_db_connection

from comments_handler import CommentsHandler
from posts_handler import PostHandler

s3 = boto3.client('s3')


@ensure_db_connection
def get_n_posts(event, context, db_connection):
    if not event['queryStringParameters']['page']:
        return
        
    return PostHandler(db_connection).get_n_posts(
        event['queryStringParameters']['page'],
        event['queryStringParameters']['section'],
        event['queryStringParameters']['number_of_posts'])


@ensure_db_connection
def get_post(event, context, db_connection):
    if not event['pathParameters']['post_id']:
        return

    return PostHandler(db_connection).get_post_by_id(event['pathParameters']['post_id'])



@ensure_db_connection
def upload_post(event, context, db_connection):
    # if not event['body']['img_url']:
    #     return
    print(event)
    return PostHandler(db_connection, s3).upload_post(event)


@ensure_db_connection
def get_all_comments(event, context, db_connection):
    if not event['pathParameters']['post_id']:
        return
    
    return CommentsHandler(db_connection).get_comments(event['pathParameters']['post_id'])


@ensure_db_connection
def save_comment(event, context, db_connection):
    if not event['pathParameters']['post_id']:
        return
    
    return CommentsHandler(db_connection).save_comment(event)


@ensure_db_connection
def delete_comment(event, context, db_connection):


    return CommentsHandler(db_connection).delete_comment(event)

@ensure_db_connection
def upvote_post(event, context, db_connection):
    if not event['pathParameters']['post_id']:
        return
    print(event)
    return PostHandler(db_connection).upvote_post(event['pathParameters']['post_id'], event['queryStringParameters']['username'])

@ensure_db_connection
def downvote_post(event, context, db_connection):
    if not event['pathParameters']['post_id']:
        return

    return PostHandler(db_connection).downvote_post(event['pathParameters']['post_id'], event['queryStringParameters']['username'])

@ensure_db_connection
def search_post(event, context, db_connection):
    if not event['queryStringParameters']['letters']:
        return
    
    return PostHandler(db_connection).search_results(event['queryStringParameters']['letters'])

@ensure_db_connection
def move_new(event, context, db_connection):
    return PostHandler(db_connection).move_new_posts()

@ensure_db_connection
def move_trending(event, context, db_connection):
    return PostHandler(db_connection).move_trending_posts()

@ensure_db_connection
def get_liked_posts(event, context, db_connection):
    print(event)
    return PostHandler(db_connection).get_liked_posts_by_user(event['pathParameters']['username'])