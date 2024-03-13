from flask import Flask, request, render_template, jsonify
import configparser
import os
import psycopg2
from dotenv import load_dotenv
from yaml import safe_load as yload

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






@app.route("/")
def index():
    return "Welome To PostConnect API!"

@app.route("/api/setup", methods=['POST'])
def setup_db():
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            with open("init.sql", "r") as init_file:
                sql_queries = init_file.read()
                cursor.execute(sql_queries)
    return {"message": "Initial Table & Values Generated Successfully"}, 201


@app.route("/api/getAllStudents", methods=['GET'])
def getAllStudents():
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            with open("queries.yaml") as file_object:
                parsed_yaml = yload(file_object)
                cursor.execute(parsed_yaml["sql"]["getAllStudents"])
                data = cursor.fetchall()
                return jsonify(data);


@app.route("/api/addStudent", methods=['POST'])
def addStudent():
    studentFields = ['first_name', 'last_name', 'email', 'enrollment_date']
    try:
        data = request.json
        if any(field not in data for field in studentFields):
            return jsonify({"error": f"One or more required fields are missing"}), 400

        with open("queries.yaml") as file_object:
            parsed_yaml = yload(file_object)
            sql_insert = parsed_yaml["sql"]["addStudent"]

        with psycopg2.connect(url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_insert, (data['first_name'], data['last_name'], data['email'], data['enrollment_date']))
                connection.commit()
                if cursor.rowcount > 0:
                    return jsonify({"message": "Student added successfully"}), 201
                else:
                    connection.rollback()
                    return jsonify({"error": "Email already exists"}), 400  


        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@app.route("/api/updateStudentEmail", methods=['PUT'])
def updateStudentEmail():
    updateFields = ['student_id', 'new_email']
    try:
        data = request.json
        if any(field not in data for field in updateFields):
            return jsonify({"error": f"One or more required fields are missing"}), 400
        

        with open("queries.yaml") as file_object:
            parsed_yaml = yload(file_object)
            sql_update = parsed_yaml["sql"]["updateStudentEmail"]


        with psycopg2.connect(url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_update, (data['new_email'],data['student_id']))
                connection.commit()
                if cursor.rowcount > 0:
                    return jsonify({"message": "Student added successfully"}), 201
                else:
                    connection.rollback()
                    return jsonify({"error": "Student ID not found"}), 404  
                
    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": "Email already exists elsewhere"}), 409

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@app.route("/api/deleteStudent", methods=['DELETE'])
def deleteStudent():
    deleteFields = ['student_id']
    try:
        data = request.json
        if any(field not in data for field in deleteFields):
            return jsonify({"error": f"One or more required fields are missing"}), 400
        
        with open("queries.yaml") as file_object:
            parsed_yaml = yload(file_object)
            sql_delete = parsed_yaml["sql"]["deleteStudent"]
        
        with psycopg2.connect(url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_delete, (data['student_id'],))
                connection.commit()
                if cursor.rowcount > 0:
                    return jsonify({"message": "Student removed successfully"}), 201
                else:
                    connection.rollback()
                    return jsonify({"error": "Student ID not found"}), 404  
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500