from pymongo import MongoClient

def get_db():
    client = MongoClient('mongodb+srv://benjaminsilva:benjaminsilva@cluster0.uawrn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
    db = client['mi_ecommerce']
    return db
