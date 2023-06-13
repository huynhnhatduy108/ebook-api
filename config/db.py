from pymongo import MongoClient
import certifi
from .constant import DATABASE_URL

cluster = DATABASE_URL
client = MongoClient(cluster, tlsCAFile=certifi.where())
client= client.ebook

