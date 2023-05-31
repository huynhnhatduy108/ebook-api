from pymongo import MongoClient
import certifi

cluster = "mongodb+srv://nest:nest@nest-cluster.gapiqqm.mongodb.net/ebook?retryWrites=true&w=majority"
client = MongoClient(cluster, tlsCAFile=certifi.where())
client= client.ebook

