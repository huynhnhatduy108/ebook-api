from fastapi import APIRouter, Depends, HTTPException
from functions.auth import generate_token, validate_token
from functions.function import compare_old_to_new_list, gen_slug_radom_string
from models.ebook import Ebook, EbookComment
from config.db import client
from schemas.ebook import EbookQueryParams, serializeDict, serializeList
from bson import ObjectId
from fastapi.responses import JSONResponse
from pymongo import ReturnDocument, UpdateOne

ebook = APIRouter() 

@ebook.get(
    path='/',
    name="List ebook",
    description="Get list ebook",
)
async def list_ebooks(param:EbookQueryParams = Depends()):
    match_condition = {"$and":[]}
    page = param.page
    page_size = param.page_size
    skip = page * page_size - page_size;

    if "keyword" in dict(param):
        if param.keyword:
            keyword_scope = {
                                "$or":[
                                        {"name":{"$regex" : param.keyword, '$options': 'i'}},
                                        {"content":{"$regex" : param.keyword, '$options': 'i'}},
                                        {"intro":{"$regex" : param.keyword, '$options': 'i'}},
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

    pipline=[
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
                        "from": "ebook_view",
                        "localField": "_id",
                        "foreignField": "ebook_id",
                        "as": "views"
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
                        "views": { "$arrayElemAt": ["$views.views", 0] },
                    }
                },
                {
                    "$project": {
                        "deleted_flag": 0,
                        "created_by":0,
                        "updated_by":0,
                    }
                },
                {
                    "$facet": {
                        "data": [{"$skip": skip},{"$limit": page_size}],
                        "count": [{"$count": "total_record"}]
                    }
                },
            ]

    result = client.ebook.aggregate(pipline)
    result = list(result)

    items = result[0]["data"]

    # print("items==>", items)
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


@ebook.get(
    path='/{id}',
    name="Info ebook by id",
    description="Info ebook by id",
)
async def info_ebook_by_id(id:str):
    
    ebooks = client.ebook.aggregate([
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
                        "from": "ebook_view",
                        "localField": "_id",
                        "foreignField": "ebook_id",
                        "as": "views"
                    }
                },
                 {
                    "$match": {
                        "_id": ObjectId(id)
                    }
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
                        "views": { "$arrayElemAt": ["$views.views", 0] },
                        "admin":{
                            "username": { "$arrayElemAt": ["$created_by.username", 0] },
                            "full_name": { "$arrayElemAt": ["$created_by.full_name", 0] },
                        }
                    }
                },
                {
                    "$project": {
                        "deleted_flag": 0,
                        "created_by":0,
                        "updated_by":0,
                    }
                }
            ])
    
    ebook = next(ebooks, None)
    # print("ebook===>", ebook)

    if not ebook:
        raise HTTPException(404, detail="Ebook not found!")
    
    ebook = serializeDict(ebook)

    return ebook

@ebook.get(
    path='/slug/{slug}',
    name="Info ebook by slug",
    description="Info ebook by slug",
)
async def info_ebook_by_slug(slug):

    ebooks = client.ebook.aggregate([
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
                        "from": "ebook_view",
                        "localField": "_id",
                        "foreignField": "ebook_id",
                        "as": "views"
                    }
                },
                 {
                    "$match": {
                        "slug": slug
                    }
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
                        "views": { "$arrayElemAt": ["$views.views", 0] },
                        "admin":{
                            "username": { "$arrayElemAt": ["$created_by.username", 0] },
                            "full_name": { "$arrayElemAt": ["$created_by.full_name", 0] },
                        }
                    }
                },
                {
                    "$project": {
                        "deleted_flag": 0,
                        "created_by":0,
                        "updated_by":0,
                    }
                }
            ])
    
    ebook = next(ebooks, None)
    # print("ebook===>", ebook)

    if not ebook:
        raise HTTPException(404, detail="Ebook not found!")
    
    # update view 
    ebook_view = client.ebook_view.find_one_and_update(
        {"ebook_id":ObjectId(ebook["_id"])},
        {"$inc": {"views": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    if ebook_view:
        ebook["views"] = ebook_view["views"]

    return ebook

 
@ebook.post(
    path='/',
    name="Create ebook",
    description="Create ebook",
)
async def create_ebook(ebook: Ebook, auth: dict = Depends(validate_token)):

    ebook = ebook.dict()
    ebook["slug"] = gen_slug_radom_string(ebook["name"], 8)
    ebook['created_by'] = ObjectId(auth)
    ebook['updated_by'] = ObjectId(auth)

    ebook_create = client.ebook.insert_one(ebook)

    client.ebook_view.insert_one({"ebook_id":ebook_create.inserted_id, "views": 0 })
    client.ebook_download.insert_one({"ebook_id":ebook_create.inserted_id, "downloads": 0 })

    if ebook["categories"]:
        client.category.update_many({"_id": {"$in": ebook["categories"]}},{"$push": {"ebooks": ebook["_id"]}})
    
    categories = list(client.category.find({"_id": {"$in": ebook["categories"]}}, {"_id": { "$toString": "$_id" }, "name": 1, "name_en":1, "description":1}))
    ebook["_id"] = str(ebook_create.inserted_id)
    ebook["categories"] = categories
    del ebook['created_by'], ebook['updated_by']

    return ebook


@ebook.put(
    path='/{id}',
    name="update ebook",
    description="update ebook",
) 
async def update_ebook(id, ebook: Ebook, auth: dict = Depends(validate_token)):

    ebook_exist = client.ebook.find_one({"_id":ObjectId(id)})
    if not ebook_exist:
        raise HTTPException(404, detail="Ebook not found!")
    
    ebook= ebook.dict()
    ebook['updated_by'] = ObjectId(auth)

    if ebook_exist["name"]!= ebook["name"]:
        ebook["slug"] = gen_slug_radom_string(ebook["name"], 8)

    if "categories" in ebook:
        category_ids = ebook["categories"]
        category_exist_ids = ebook_exist["categories"]
        is_equal,list_add,list_delete = compare_old_to_new_list(category_ids, category_exist_ids)
        if not is_equal:
            if len(list_add):
                list_add = [ObjectId(cate) for cate in list_add]
                client.category.update_many({"_id": {"$in": list_add}},{"$push": {"ebooks": id}})
            if len(list_delete):
                list_delete = [ObjectId(cate) for cate in list_delete]
                client.category.update_many({"_id": {"$in": list_delete}},{"$pull": {"ebooks": id}})

    categories = list(client.category.find({"_id": {"$in": category_ids}}, {"_id": { "$toString": "$_id" }, "name": 1, "name_en":1, "description":1}))

    ebook = client.ebook.find_one_and_update({"_id":ObjectId(id)},{
        "$set":ebook
    }, return_document = ReturnDocument.AFTER)

    ebook["_id"] = str(ebook["_id"])
    ebook["categories"] = categories
    del ebook['created_by'], ebook['updated_by']

    return ebook

@ebook.delete(  
    path='/{id}',
    name="Delete ebook",
    description="Delete ebook",
)
async def delete_ebook(id, auth: dict = Depends(validate_token)):
    ebook = client.ebook.find_one({"_id":ObjectId(id)})
    if not ebook:
        raise HTTPException(404, detail="Ebook not found!")
    
    # if auth["role"] !=1:
    #     raise HTTPException(403, detail="No permission!")


    if len(ebook["categories"]):
        client.category.update_many({"_id": {"$in": ebook["categories"]}},
                                    {"$pull": {"ebooks": ObjectId(id)}})
        
    client.ebook_view.find_one_and_delete({"ebook_id":ObjectId(id) })
    client.ebook_download.find_one_and_delete({"ebook_id":ObjectId(id)})
    client.ebook_comment.delete_many({"ebook_id":ObjectId(id)})
    client.ebook_rate.delete_many({"ebook_id":ObjectId(id)})

    client.ebook.find_one_and_delete({"_id":ObjectId(id)})
    
    return JSONResponse(content={"message":"Delete success"}, status_code=200)


@ebook.post(  
    path='/comment/',
    name="Comment ebook",
    description="Comment ebook",
)
async def comment_ebook(comment: EbookComment, auth: dict = Depends(validate_token)):

    comment= comment.dict()
    comment["user_id"] = ObjectId(auth)  

    ebook_comment_create = client.ebook_comment.insert_one(comment)

    comment["_id"] = str(ebook_comment_create.inserted_id)
    comment["ebook_id"] = str(comment["ebook_id"])
    del comment["user_id"]

    return comment


@ebook.delete(  
    path='/comment/{comment_id}',
    name="delete comment ebook",
    description="delete comment ebook",
)
async def detele_comment_ebook(comment_id, auth: dict = Depends(validate_token)):
    ebook_comment = client.ebook_comment.find_one({"_id":ObjectId(comment_id)})

    if not ebook_comment:
        raise HTTPException(404, detail="Commnet not found!")
    
    client.ebook_comment.find_one_and_delete({"_id":ObjectId(comment_id)})
    return JSONResponse(content={"message":"Delete comment success"}, status_code=200)

@ebook.delete(  
    path='/delete_all_comment/{ebook_id}',
    name="delete all comment ebook",
    description="delete all comment ebook",
)
async def detele_all_comment_ebook(ebook_id, auth: dict = Depends(validate_token)):

    client.ebook_comment.delete_many({"ebook_id":ObjectId(ebook_id)})
    
    return JSONResponse(content={"message":"Delete all comment success"}, status_code=200)
