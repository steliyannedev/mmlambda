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

    return PostHandler(db_connection).upvotePost(event['pathParameters']['post_id'])

@ensure_db_connection
def downvote_post(event, context, db_connection):
    if not event['pathParameters']['post_id']:
        return

    return PostHandler(db_connection).downvoarPost(event['pathParameters']['post_id'])

@ensure_db_connection
def search_post(event, context, db_connection):
    if not event['queryStringParameters']['letters']:
        return
    
    return PostHandler(db_connection).searchResults(event['queryStringParameters']['letters'])

@ensure_db_connection
def move_new(db_connection):
    return PostHandler(db_connection).moveNewPosts()

@ensure_db_connection
def move_trending(db_connection):
    return PostHandler(db_connection).moveTrendingPosts()