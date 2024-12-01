from pymongo import MongoClient
import os
import psycopg2



def get_db():
    client = MongoClient('mongodb+srv://benjaminsilva:benjaminsilva@cluster0.uawrn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
    db = client['mi_ecommerce']
    return db

def get_db_postgres():
    conn = psycopg2.connect(
        host="postgres",
        database="mydb",
        user="postgres",
        password="password"
    )
    return conn
