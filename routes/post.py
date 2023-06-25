from fastapi import APIRouter, Depends, HTTPException
from functions.auth import generate_token, validate_token
from functions.function import compare_old_to_new_list, gen_slug_radom_string
from models.post import Post
from config.db import client
from schemas.post import PostQueryParams, serializeDict, serializeList
from bson import ObjectId
from fastapi.responses import JSONResponse
from pymongo import ReturnDocument

post = APIRouter() 

def get_info_by_slug_or_id(match={}):

    posts = client.post.aggregate([
                {
                    "$lookup": {
                        "from": "category",
                        "localField": "categories",
                        "foreignField": "_id",
                        "as": "categories"
                    }
                },
                {
                    "$lookup": {
                        "from": "user",
                        "localField": "created_by",
                        "foreignField": "_id",
                        "as": "created_by"
                    }
                },
                 {
                    "$lookup": {
                        "from": "ebook",
                        "localField": "ebook_id",
                        "foreignField": "_id",
                        "as": "ebook_docs"
                    }
                },
                 {
                    "$match": match
                },
                {
                    "$addFields": {
                        "_id": { "$toString": "$_id" },
                        "categories": {
                            "$map": {
                                "input": "$categories",
                                "as": "category",
                                "in": {
                                    "_id": { "$toString": "$$category._id" },
                                    "name": "$$category.name",
                                    "name_en": "$$category.name_en",
                                    "description": "$$category.description"
                                }
                            }
                        },
                        "ebook":{
                            "_id": { "$toString": "$ebook_id" },
                            "name":{ "$arrayElemAt": ["$ebook_docs.name", 0] },
                            "pdf_url": { "$arrayElemAt": ["$ebook_docs.pdf_url", 0] },
                        },
                      
                        "author":{
                            "username": { "$arrayElemAt": ["$created_by.username", 0] },
                            "full_name": { "$arrayElemAt": ["$created_by.full_name", 0] },
                        }
                    }
                },
                {
                    "$project": {
                        "deleted_flag": 0,
                        "ebook_id":0,
                        "created_by":0,
                        "updated_by":0,
                        "ebook_docs":0
                    }
                }
            ])
    
    post = next(posts, None)

    if not post:
        raise HTTPException(404, detail="Post not found!")

    comments = client.post_comment.aggregate([
                {
                    "$lookup": {
                        "from": "user",
                        "localField": "user_id",
                        "foreignField": "_id",
                        "as": "user"
                    }
                },
                 {
                    "$match": match
                },
                {
                    "$addFields": {
                        "_id": { "$toString": "$_id" },
                        "user_comment":{
                            "username": { "$arrayElemAt": ["$user.username", 0] },
                            "full_name": { "$arrayElemAt": ["$user.full_name", 0] },
                        }
                    }
                },
                {
                    "$project": {
                        "deleted_flag": 0,
                        "post_id":0,
                        "user_id":0,
                        "user":0,
                    }
                }
            ])
    post["comments"]= list(comments)

    return post

@post.get(
    path='/',
    name="List post",
    description="Get list post",
)
async def list_posts(param:PostQueryParams = Depends()):
    match_condition = {"$and":[{"is_public":True}]}
    sort_condition = {}
    page = param.page
    page_size = param.page_size
    skip = page * page_size - page_size;

    if "keyword" in dict(param):
        if param.keyword:
            keyword_scope = {
                                "$or":[
                                        {"name":{"$regex" : param.keyword, '$options': 'i'}},
                                        {"slug":{"$regex" : gen_slug_radom_string(param.keyword,0), '$options': 'i'}},
                                      ]       
                            }
            
            match_condition["$and"].append(keyword_scope)

    if "categories" in dict(param):
        if param.categories:
            cates_scope = {"categories._id":{"$in":param.categories} }
            match_condition["$and"].append(cates_scope)

    if "tags" in dict(param):
        if param.tags:
            cates_scope = {"tags":{"$in":param.tags} }
            match_condition["$and"].append(cates_scope)
    
    if "ordering" in dict(param):
        sort_condition=param.ordering

    pipline= [
                {
                    "$lookup": {
                        "from": "category",
                        "localField": "categories",
                        "foreignField": "_id",
                        "as": "categories"
                    }
                },
                {
                    "$match": match_condition if match_condition["$and"] else {}
                },
                {
                    "$addFields": {
                        "_id": { "$toString": "$_id" },
                        "categories": {
                            "$map": {
                                "input": "$categories",
                                "as": "category",
                                "in": {
                                    "_id": { "$toString": "$$category._id" },
                                    "name": "$$category.name",
                                    "name_en": "$$category.name_en",
                                    "description": "$$category.description"
                                }
                            }
                        },
                    }
                },
                {
                    "$project": {
                        "deleted_flag": 0,
                        "created_by":0,
                        "updated_by":0,
                        "ebook_id":0,
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
                },
            ]

    result = client.post.aggregate(pipline)
    result = list(result)
    items = result[0]["data"]
    total_record = 0
    if result[0]["data"]:
        total_record = result[0]["count"][0]["total_record"]

    data ={
        "items": items,
        "page":page,
        "page_size":page_size,
        "total_record":total_record
    }
    return data

@post.get(
    path='/admin',
    name="List post admin",
    description="Get list post admin",
)
async def list_posts_admin(param:PostQueryParams = Depends(), auth = Depends(validate_token)):
    match_condition = {"$and":[]}
    sort_condition = {}
    page = param.page
    page_size = param.page_size
    skip = page * page_size - page_size;

    if "keyword" in dict(param):
        if param.keyword:
            keyword_scope = {
                                "$or":[
                                        {"name":{"$regex" : param.keyword, '$options': 'i'}},
                                        {"slug":{"$regex" : gen_slug_radom_string(param.keyword,0), '$options': 'i'}},
                                      ]       
                            }
            
            match_condition["$and"].append(keyword_scope)

    if "categories" in dict(param):
        if param.categories:
            cates_scope = {"categories._id":{"$in":param.categories} }
            match_condition["$and"].append(cates_scope)

    if "tags" in dict(param):
        if param.tags:
            cates_scope = {"tags":{"$in":param.tags} }
            match_condition["$and"].append(cates_scope)
    
    if "ordering" in dict(param):
        sort_condition=param.ordering

    pipline= [
                # {
                #     "$lookup": {
                #         "from": "category",
                #         "localField": "categories",
                #         "foreignField": "_id",
                #         "as": "categories"
                #     }
                # },
                {
                    "$match": match_condition if match_condition["$and"] else {}
                },
                # {
                #     "$addFields": {
                #         "_id": { "$toString": "$_id" },
                #         "categories": {
                #             "$map": {
                #                 "input": "$categories",
                #                 "as": "category",
                #                 "in": {
                #                     "_id": { "$toString": "$$category._id" },
                #                     "name": "$$category.name",
                #                     "name_en": "$$category.name_en",
                #                     "description": "$$category.description"
                #                 }
                #             }
                #         },
                #     }
                # },
                {
                    "$project": {
                        "deleted_flag": 0,
                        "created_by":0,
                        "updated_by":0,
                        "ebook_id":0,
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
                },
            ]

    result = client.post.aggregate(pipline)
    result = list(result)
    items = result[0]["data"]
    total_record = 0
    if result[0]["data"]:
        total_record = result[0]["count"][0]["total_record"]

    data ={
        "items": items,
        "page":page,
        "page_size":page_size,
        "total_record":total_record
    }
    return data


@post.get(
    path='/{id}',
    name="Info post by id",
    description="Info post by id",
)
async def info_post_by_id(id:str):
    
    match = {"_id":ObjectId(id)}
    post = get_info_by_slug_or_id(match)
    
    return post

@post.get(
    path='/slug/{slug}',
    name="Info post by slug",
    description="Info post by slug",
)
async def info_post_by_slug(slug):

    match = {"slug":slug}
    post = get_info_by_slug_or_id(match)
    
    # update view 
    post_view = client.post.find_one_and_update(
        {"_id": ObjectId(post["_id"])},
        {"$inc": {"views": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    if post_view:
        post["views"] = post_view["views"]
    
    return post

 
@post.post(
    path='/',
    name="Create post",
    description="Create post",
)
async def create_post(post: Post, auth = Depends(validate_token)):
    post = post.dict()
    post['slug'] = gen_slug_radom_string(post["name"],5)
    post['created_by'] = ObjectId(auth)
    post['updated_by'] = ObjectId(auth)

    post_create = client.post.insert_one(post)

    if post["categories"]:
        client.category.update_many({"_id": {"$in": post["categories"]}},{"$push": {"posts": post_create.inserted_id}})

    categories = list(client.category.find({"_id": {"$in": post["categories"]}}, {"_id": { "$toString": "$_id" }, "name": 1, "name_en":1, "description":1}))

    post["_id"] = str(post_create.inserted_id)
    post["categories"] = categories
    post["ebook_id"] = str(post["ebook_id"])
    del post['created_by'], post['updated_by']

    return post



@post.put(
    path='/{id}',
    name="update post",
    description="update post",
) 
async def update_post(id, post: Post, auth: dict = Depends(validate_token)):

    post_exist = client.post.find_one({"_id": ObjectId(id)}) 

    if not post_exist:
        raise HTTPException(404, detail="Post not found!")
    
    post = post.dict()
    post['updated_by'] = ObjectId(auth)

        
    if "name" in post and post_exist["name"]!= post["name"]:
        post["slug"] = gen_slug_radom_string(post["name"], 5)

    if "categories" in post:
        category_ids = post["categories"]
        category_exist_ids = post_exist["categories"]
        is_equal,list_add,list_delete = compare_old_to_new_list(category_ids, category_exist_ids) 
        if not is_equal:
            if len(list_add):
                list_add = [ObjectId(cate) for cate in list_add]
                client.category.update_many({"_id": {"$in": list_add}},{"$push": {"posts": ObjectId(id)}})
            if len(list_delete):
                list_delete = [ObjectId(cate) for cate in list_delete]
                client.category.update_many({"_id": {"$in": list_delete}},{"$pull": {"posts": ObjectId(id)}})

    categories = list(client.category.find({"_id": {"$in": category_ids}}, {"_id": { "$toString": "$_id" }, "name": 1, "name_en":1, "description":1}))

    post = client.post.find_one_and_update({"_id":ObjectId(id)},{
        "$set":post
    }, return_document = ReturnDocument.AFTER)

    post["_id"] = str(post["_id"])
    post["categories"]=categories
    del post['created_by'], post['updated_by']

    return post

@post.delete(  
    path='/{id}',
    name="Delete post",
    description="Delete post",
)
async def delete_post(id, auth: dict = Depends(validate_token)):

    # if auth["role"] !=1:
    #     raise HTTPException(403, detail="No permission!")

    post = client.post.find_one({"_id":ObjectId(id)})
    if not post:
        raise HTTPException(404, detail="post not found!")

    category_ids = post["categories"]
    if len(category_ids):
        client.category.update_many({"_id": {"$in": category_ids}},
                                    {"$pull": {"posts": ObjectId(id)}})

    client.post.find_one_and_delete({"_id":ObjectId(id)})
    return JSONResponse(content={"message":"Delete success"}, status_code=200)
