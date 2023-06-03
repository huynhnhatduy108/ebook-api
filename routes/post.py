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

@post.get(
    path='/',
    name="List post",
    description="Get list post",
)
async def list_posts(param:PostQueryParams = Depends()):
    query = {}
    page = param.page
    page_size = param.page_size
    skip = page * page_size - page_size;

    if "keyword" in dict(param):
        if param.keyword:
            query["$or"] = [{"name":{"$regex" : param.keyword, '$options': 'i'}},
                            {"name_en":{"$regex" : param.keyword, '$options': 'i'}},
                            {"intro":{"$regex" : param.keyword, '$options': 'i'}},
                            {"intro_en":{"$regex" : param.keyword, '$options': 'i'}},
                            ]
    if "category" in dict(param):
        if param.category:
            query["categories"] = param.category

    post = client.post.find(query,{"deleted_flag":0})
    post = post.skip(skip).limit(page_size)
    total_record = client.post.count_documents(query)

    post = serializeList(post)
    data ={
        "items": post,
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
    post = client.post.find_one({"_id":ObjectId(id)},{"deleted_flag":0})

    if not post:
        raise HTTPException(404, detail="Post not found!")
    
    post = serializeDict(post)

    return post

@post.get(
    path='/slug/{slug}',
    name="Info post by slug",
    description="Info post by slug",
)
async def info_post_by_slug(slug):
    post = client.post.find_one({"slug":slug},{"deleted_flag":0})

    if not post:
        raise HTTPException(404, detail="Post not found!")
    
    # update view 
    post_view = client.post_view.find_one_and_update(
        {"post_id": str(post["_id"])},
        {"$inc": {"views": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    if post_view:
        post["views"] = post_view["views"]
    post = serializeDict(post)

    return post

 
@post.post(
    path='/',
    name="Create post",
    description="Create post",
)
async def create_post(post: Post):
    post = post.dict()
    # post_create = client.post.insert_one(post)

    print("post==/>", post)

    # category_ids = []
    # categories = []
    # if "categories" in post:
    #     if post["categories"]:
    #         category_ids = [ObjectId(category) for category in post["categories"]]
    #         categories = client.category.find({"_id": {"$in": category_ids}})
    #         categories = [{"_id":str(cate["_id"]), "name":cate["name"]} for cate in categories]
    #         post["categories"] = categories
    #     else:
    #         post["categories"]=[]

    # post_create = client.post.insert_one(post)
    # post["_id"] = str(post_create.inserted_id)

    # client.post_view.insert_one({"post_id":post["_id"], "views": 0 })

    # if categories:
    #     client.category.update_many({"_id": {"$in": category_ids}},{"$push": {"posts": post["_id"]}})
    
    return "post"



@post.put(
    path='/{id}',
    name="update post",
    description="update post",
) 
async def update_post(id, post: Post, auth: dict = Depends(validate_token)):

    post_exist = client.post.find_one({"_id":ObjectId(id)})
    if not post_exist:
        raise HTTPException(404, detail="post not found!")
    
    post= post.dict()
    if post_exist["name"]!= post["name"]:
        post["slug"] = gen_slug_radom_string(post["name"], 8)

    if "categories" in post:
        category_ids = [ObjectId(category) for category in post["categories"]]
        category_exist_ids = [ObjectId(category["_id"]) for category in post_exist["categories"]]
        list_add,list_delete = compare_old_to_new_list(category_ids, category_exist_ids)
        
        if len(list_add):
            list_add = [ObjectId(cate) for cate in list_add]
            client.category.update_many({"_id": {"$in": list_add}},{"$push": {"posts": id}})
        if len(list_delete):
            list_delete = [ObjectId(cate) for cate in list_delete]
           
            client.category.update_many({"_id": {"$in": list_delete}},{"$pull": {"posts": id}})

        categories = client.category.find({"_id": {"$in": category_ids}}, {"_id": 1, "name": 1})
        categories = [{"_id": str(cate["_id"]), "name": cate["name"]} for cate in categories]
        post["categories"] = categories

    post = client.post.find_one_and_update({"_id":ObjectId(id)},{
        "$set":post
    }, return_document = ReturnDocument.AFTER)


    post["_id"] = str(post["_id"])

    return post

@post.delete(  
    path='/{id}',
    name="Delete post",
    description="Delete post",
)
async def delete_post(id, auth: dict = Depends(validate_token)):
    post = client.post.find_one({"_id":ObjectId(id)})
    if not post:
        raise HTTPException(404, detail="post not found!")
    
    # if auth["role"] !=1:
    #     raise HTTPException(403, detail="No permission!")

    category_ids = [ObjectId(cate["_id"]) for cate in post["categories"]]
    if len(category_ids):
        client.category.update_many({"_id": {"$in": category_ids}},
                                    {"$pull": {"posts": id}})

    client.post.find_one_and_delete({"_id":ObjectId(id)})
    return JSONResponse(content={"message":"Delete success"}, status_code=200)
