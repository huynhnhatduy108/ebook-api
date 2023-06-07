from fastapi import APIRouter, Depends, HTTPException
from functions.auth import generate_token, validate_token
from models.comment import EbookComment, PostComment
from config.db import client
from bson import ObjectId
from fastapi.responses import JSONResponse


comment = APIRouter() 

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
    path='/ebook/',
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