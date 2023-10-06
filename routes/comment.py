from fastapi import APIRouter, Depends, HTTPException
from functions.auth import generate_token, validate_token
from models.comment import EbookComment, PostComment
from config.db import client
from bson import ObjectId
from fastapi.responses import JSONResponse
from schemas.comment import CommentQueryParams
import math


comment = APIRouter() 

@comment.get(  
    path='/ebook',
    name="Get list comment ebook",
    description="Get list comment ebook",
)
async def list_comment_ebook(param:CommentQueryParams = Depends()):

    match_condition = {"$and":[]}
    sort_condition ={}
    page = param.page
    page_size = param.page_size
    skip = page * page_size - page_size;

    if "keyword" in dict(param):
        if param.keyword:
            keyword_scope = {
                                "$or":[
                                        {"ebook_name":{"$regex" : param.keyword, '$options': 'i'}},
                                      ]       
                            }
            
            match_condition["$and"].append(keyword_scope)


    if "ordering" in dict(param):
        sort_condition=param.ordering

    
    pipeline = [
            {
                "$group": {
                    "_id": "$ebook_id",
                    "count":{"$sum":1}
                }    
            },
            {
                "$lookup": {
                        "from": "ebook",
                        "localField": "_id",
                        "foreignField": "_id",
                        "as": "ebook_docs"
                    }
            },
            {   "$addFields": {
                    "ebook_name":{ "$arrayElemAt": ["$ebook_docs.name", 0] }
                }
            },
             {
                    "$match": match_condition if match_condition["$and"] else {}
            },
           {
                "$project": {
                        "_id": 0,
                        "ebook_id": { "$toString": "$_id" },
                        "count": 1,
                        "ebook_name":1
                    }
            },
            {
                    "$sort":sort_condition
            },
            {
                "$facet": {
                        "data": [{"$skip": skip},{"$limit": page_size}],
                        "count": [{"$count": "total_record"}]
                    }
            }
        ]

    result = client.ebook_comment.aggregate(pipeline)
    result = list(result)
    items = result[0]["data"]
    total_record = 0
    if result[0]["data"]:
        total_record = result[0]["count"][0]["total_record"]
    
    data ={
        "items": items,
        "page":page,
        "page_size":page_size,
        "total_record":total_record,
        "total_page":math.ceil(total_record / page_size)
    }
    return data


@comment.get(  
    path='/ebook/{ebook_id}',
    name="Get list comment by ebook id",
    description="Get list comment by ebook id",
)
async def comment_ebook(ebook_id):
    
    pipeline = [
            {
                "$match": {"ebook_id": ObjectId(ebook_id)}
            },
            {
                "$lookup": {
                    "from": "user",
                    "localField": "user_id",
                    "foreignField": "_id",
                    "as": "user"
                }
            },
            {
                "$addFields": {
                    "_id": {"$toString": "$_id"},
                    "parent_id": {"$toString": "$parent_id"},
                    "user_comment": {
                        "username": {"$arrayElemAt": ["$user.username", 0]},
                        "full_name": {"$arrayElemAt": ["$user.full_name", 0]},
                        "avatar_url": {"$arrayElemAt": ["$user.avatar_url", 0]},
                    },
                }
            },
            {
                "$project": {
                    "deleted_flag": 0,
                    "ebook_id": 0,
                    "user_id": 0,
                    "user": 0,
                }
            },
            {
                "$facet": {
                    "comments": [{"$match": {"parent_id": ""}},{"$sort": {"created_at": -1}}],
                    "sub_comments": [{"$match": {"parent_id": {"$ne": ""}}},{"$sort": {"created_at": -1}}]
                }
            }
        ]

    results = list(client.ebook_comment.aggregate(pipeline)) 
    comments = list(results[0]["comments"])
    sub_comments = list(results[0]["sub_comments"])

    for comment in comments:
        comment["sub_comments"] = []
        for sub_cmt in sub_comments:
            if comment["_id"] == sub_cmt["parent_id"]:
                comment["sub_comments"].append(sub_cmt)

    return comments


@comment.post(  
    path='/ebook',
    name="Comment ebook",
    description="Comment ebook",
)
async def comment_ebook(comment: EbookComment, auth: dict = Depends(validate_token)):

    comment= comment.dict()
    comment["user_id"] = ObjectId(auth)  
    ebook = client.ebook.find_one({"_id":comment["ebook_id"]})

    if not ebook:
        raise HTTPException(404, detail="Ebook not found!")
    
    ebook_comment_create = client.ebook_comment.insert_one(comment)

    comment["_id"] = str(ebook_comment_create.inserted_id)
    comment["ebook_id"] = str(comment["ebook_id"])
    comment["parent_id"] = str(comment["parent_id"])

    del comment["user_id"]

    return comment


@comment.delete(  
    path='/ebook/{comment_id}',
    name="delete comment ebook",
    description="delete comment ebook",
)
async def detele_comment_ebook(comment_id, auth: dict = Depends(validate_token)):
    ebook_comment = client.ebook_comment.find_one({"_id":ObjectId(comment_id)})

    if not ebook_comment:
        raise HTTPException(404, detail="Comment not found!")
    
    client.ebook_comment.find_one_and_delete({"parent_id":ObjectId(comment_id)})
    client.ebook_comment.find_one_and_delete({"_id":ObjectId(comment_id)})

    return JSONResponse(content={"message":"Delete comment success"}, status_code=200)

@comment.delete(  
    path='/delete_all_comment_ebook/{ebook_id}',
    name="delete all comment ebook",
    description="delete all comment ebook",
)
async def detele_all_comment_ebook(ebook_id, auth: dict = Depends(validate_token)):

    client.ebook_comment.delete_many({"ebook_id":ObjectId(ebook_id)})
    
    return JSONResponse(content={"message":"Delete all comment success"}, status_code=200)


# Post comment 
@comment.get(  
    path='/post',
    name="Get list comment post",
    description="Get list comment post",
)
async def list_comment_ebook(param:CommentQueryParams = Depends()):

    match_condition = {"$and":[]}
    sort_condition ={}
    page = param.page
    page_size = param.page_size
    skip = page * page_size - page_size;

    if "keyword" in dict(param):
        if param.keyword:
            keyword_scope = {
                                "$or":[
                                        {"post_name":{"$regex" : param.keyword, '$options': 'i'}},
                                      ]       
                            }
            
            match_condition["$and"].append(keyword_scope)


    if "ordering" in dict(param):
        sort_condition=param.ordering

    
    pipeline = [
            {
                "$group": {
                    "_id": "$post_id",
                    "count":{"$sum":1}
                }    
            },
            {
                "$lookup": {
                        "from": "post",
                        "localField": "_id",
                        "foreignField": "_id",
                        "as": "post_docs"
                    }
            },
            {   "$addFields": {
                    "post_name":{ "$arrayElemAt": ["$post_docs.name", 0] }
                }
            },
             {
                    "$match": match_condition if match_condition["$and"] else {}
            },
           {
                "$project": {
                        "_id": 0,
                        "post_id": { "$toString": "$_id" },
                        "count": 1,
                        "post_name":1
                    }
            },
            {
                    "$sort":sort_condition
            },
            {
                "$facet": {
                        "data": [{"$skip": skip},{"$limit": page_size}],
                        "count": [{"$count": "total_record"}]
                    }
            }
        ]

    result = client.post_comment.aggregate(pipeline)
    result = list(result)
    items = result[0]["data"]
    total_record = 0
    if result[0]["data"]:
        total_record = result[0]["count"][0]["total_record"]
    
    data ={
        "items": items,
        "page":page,
        "page_size":page_size,
        "total_record":total_record,
        "total_page":math.ceil(total_record / page_size)
    }
    return data


@comment.get(  
    path='/post/{post_id}',
    name="Get list comment by post id",
    description="Get list comment by post id",
)
async def comment_post(post_id):
    
    pipeline = [
            {
                "$match": {"post_id": ObjectId(post_id)}
            },
            {
                "$lookup": {
                    "from": "user",
                    "localField": "user_id",
                    "foreignField": "_id",
                    "as": "user"
                }
            },
            {
                "$addFields": {
                    "_id": {"$toString": "$_id"},
                    "parent_id": {"$toString": "$parent_id"},
                    "user_comment": {
                        "username": {"$arrayElemAt": ["$user.username", 0]},
                        "full_name": {"$arrayElemAt": ["$user.full_name", 0]},
                        "avatar_url": {"$arrayElemAt": ["$user.avatar_url", 0]},
                    },
                }
            },
            {
                "$project": {
                    "deleted_flag": 0,
                    "post_id": 0,
                    "user_id": 0,
                    "user": 0,
                }
            },
            {
                "$facet": {
                    "comments": [{"$match": {"parent_id": ""}},{"$sort": {"created_at": -1}}],
                    "sub_comments": [{"$match": {"parent_id": {"$ne": ""}}},{"$sort": {"created_at": -1}}]
                }
            }
        ]

    results = list(client.post_comment.aggregate(pipeline)) 
    comments = list(results[0]["comments"])
    sub_comments = list(results[0]["sub_comments"])

    for comment in comments:
        comment["sub_comments"] = []
        for sub_cmt in sub_comments:
            if comment["_id"] == sub_cmt["parent_id"]:
                comment["sub_comments"].append(sub_cmt)

    return comments


@comment.post(  
    path='/post',
    name="Comment post",
    description="Comment post",
)
async def comment_post(comment: PostComment, auth: dict = Depends(validate_token)):

    comment= comment.dict()
    comment["user_id"] = ObjectId(auth)  
    post = client.post.find_one({"_id":comment["post_id"]})

    if not post:
        raise HTTPException(404, detail="Post not found!")
    
    post_comment_create = client.post_comment.insert_one(comment)

    comment["_id"] = str(post_comment_create.inserted_id)
    comment["post_id"] = str(comment["post_id"])
    comment["parent_id"] = str(comment["parent_id"])

    del comment["user_id"]

    return comment


@comment.delete(  
    path='/post/{comment_id}',
    name="delete comment post",
    description="delete comment post",
)
async def detele_comment_post(comment_id, auth: dict = Depends(validate_token)):
    post_comment = client.post_comment.find_one({"_id":ObjectId(comment_id)})

    if not post_comment:
        raise HTTPException(404, detail="Comment not found!")
    
    client.post_comment.find_one_and_delete({"parent_id":ObjectId(comment_id)})
    client.post_comment.find_one_and_delete({"_id":ObjectId(comment_id)})

    return JSONResponse(content={"message":"Delete comment success"}, status_code=200)

@comment.delete(  
    path='/delete_all_comment_post/{post_id}',
    name="delete all comment post",
    description="delete all comment post",
)
async def detele_all_comment_post(post_id, auth: dict = Depends(validate_token)):

    client.post_comment.delete_many({"post_id":ObjectId(post_id)})
    
    return JSONResponse(content={"message":"Delete all comment success"}, status_code=200)