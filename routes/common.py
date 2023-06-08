from fastapi import APIRouter, Depends, HTTPException
from config.constant import DASHBOARD
from functions.auth import generate_token, validate_token
from config.db import client
from bson import ObjectId
from fastapi.responses import JSONResponse


common = APIRouter() 

@common.get(  
    path='/dashboard/',
    name="Get info dashboard",
    description="Get info dashboard",
)
async def get_info_dashboard():

    # count category
    categories = client.category.count_documents({})

    # count ebook commment
    pipeline_ebook_comments = [
            {
                "$facet": {
                    "parent": [{"$match": {"parent_id": ""}},{"$count": "total_record"}],
                    "sub": [{"$match": {"parent_id": {"$ne": ""}}},{"$count": "total_record"}]
                }
            }
        ]
    ebook_comments = list(client.ebook_comment.aggregate(pipeline_ebook_comments))

    count_ebook_cmts_parent, count_ebook_cmts_sub = 0, 0
    if ebook_comments[0]["parent"]:
        count_ebook_cmts_parent = ebook_comments[0]["parent"][0]["total_record"]
    if ebook_comments[0]["sub"]:
        count_ebook_cmts_sub = ebook_comments[0]["sub"][0]["total_record"]

    pipeline_post_comments = [
            {
                "$facet": {
                    "parent": [{"$match": {"parent_id": ""}},{"$count": "total_record"}],
                    "sub": [{"$match": {"parent_id": {"$ne": ""}}},{"$count": "total_record"}]
                }
            }
        ]
    post_comments = list(client.post_comment.aggregate(pipeline_post_comments)) 

    count_post_cmts_parent, count_post_cmts_sub = 0, 0
    if post_comments[0]["parent"]:
        count_post_cmts_parent = post_comments[0]["parent"][0]["total_record"]
    if post_comments[0]["sub"]:
        count_post_cmts_sub = post_comments[0]["sub"][0]["total_record"]

    # post
    posts = client.post.count_documents({})
    post_views = list(client.post_view.aggregate([
                {
                    "$group": {
                        "_id": 1,
                        "total_views": { "$sum": "$views" }
                    }
                }
        ]))
    p_views =0
    if len(post_views) > 0:
         p_views = post_views[0]["total_views"]

    # users
    users = client.user.count_documents({})

    # Ebook
    ebooks = client.ebook.count_documents({})
    ebook_views = list(client.ebook_view.aggregate([
                {
                    "$group": {
                        "_id": 1,
                        "total_views": { "$sum": "$views" }
                    }
                }
        ]))
    e_views =0
    if len(ebook_views) > 0:
         e_views = ebook_views[0]["total_views"]

    ebook_downloads = list(client.ebook_download.aggregate([
                {
                    "$group": {
                        "_id": 1,
                        "total_downloads": { "$sum": "$downloads" }
                    }
                }
        ]))
    e_downloads =0
    if len(ebook_downloads) > 0:
         e_downloads = ebook_downloads[0]["total_downloads"]


    dashboard = client.dashboard.find_one({"key":DASHBOARD})

    data ={
        "user_count": users,
        "ebook_count": {
            "count":ebooks,
            "views":e_views,
            "downloads":e_downloads,
             "comment": {
                "parent":count_ebook_cmts_parent,
                "sub":count_ebook_cmts_sub,
            },
        },
         "post_count": {
            "count":posts,
            "views":p_views,
             "comment": {
                "parent":count_post_cmts_parent,
                "sub":count_post_cmts_sub,
            },
        },
        "category_count": categories,
        "views":dashboard["views"],
        "downloads":dashboard["downloads"],
        "online_reads":dashboard["online_reads"],

    }
   

    return data


@common.post(  
    path='/create/',
    name="create dashboard",
    description="create dashboard",
)
async def create_dashboard():
    dashboard = client.dashboard.find({"key":DASHBOARD})

    if dashboard:
        raise HTTPException(400, detail="Dashboard was existed!")
     
    data ={
            "key":DASHBOARD,
            "views":0,
            "dowloads":0,
            "online_reads":0,
        }
    client.dashboard.insert_one(data)

    return {"message":"Dashboard create success"}

@common.get(  
    path='/travel/',
    name="Travell to website",
    description="Travell to website",
)
async def travel_to_dashboard():
    client.dashboard.find_one_and_update({"key":DASHBOARD},{"$inc": {"views": 1}},upsert=True,)
    return {"message":"Well common to Ebook Free"}

