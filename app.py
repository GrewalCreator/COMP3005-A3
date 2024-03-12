from flask import Flask, request
import configparser
import os
import psycopg2
from dotenv import load_dotenv


app = Flask(__name__)

# Ensure The Following Section is generated prior to load_dotenv()
config = configparser.ConfigParser()
config.read('config.ini')

PASSWORD = config['Password']['password']
os.environ['PASSWORD'] = PASSWORD

load_dotenv()

url = os.getenv("DATABASE_URL")
print(url)
if url:
    url = url.replace("$PASSWORD", PASSWORD)


connection = psycopg2.connect(url)

def setup_db():
    with connection:
        with connection.cursor() as cursor:
            with open("init.sql", "r") as init_file:
                sql_queries = init_file.read()
                cursor.execute(sql_queries)

@app.get("/")
def index():
    setup_db()  
    return {"message": "Initial Table & Values Generated Successfully"}, 201