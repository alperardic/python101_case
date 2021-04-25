from flask import Flask, request, jsonify
from mysql.connector import errorcode
import requests
import mysql.connector
import configparser
import logging
import os

app = Flask(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read(f'{dir_path}/casestudy.cfg')
logging.basicConfig(filename=config['LOGGING']['log_file'], level=config['LOGGING']['log_level'])

def connect():
    return mysql.connector.connect(
        user=config['DEFAULT']['mysql_user'],
        password=config['DEFAULT']['mysql_password'],
        host=config['DEFAULT']['mysql_host'],
        database=config['DEFAULT']['mysql_database'],
        auth_plugin='mysql_native_password')

@app.route('/selection', methods=['GET'])
def select():
    try:
        mysqldb = connect()
        cursor =  mysqldb.cursor(buffered=True)
        query = f"SELECT * FROM {config['DEFAULT']['mysql_database']}.{config['DEFAULT']['mysql_table']};"
        cursor.execute(query)
        response = jsonify(cursor.fetchall())
        mysqldb.close()
    except mysql.connector.Error as e:
        if(e.errno == errorcode.ER_ACCESS_DENIED_ERROR):
            logging.error(str(e))
            return("AUTH ERROR!")
            
        elif(e.errno == errorcode.ER_BAD_DB_ERROR):
            logging.error(str(e))
            return("DB NOT EXIST!")
            
    return(response)

@app.route('/insertion', methods=['POST','PUT'])
def insert():
    insertion = request.get_json()
    name = insertion["name"]
    lastname = insertion["lastname"]
    location = insertion["location"]
    age = insertion["age"]
    try:
        mysqldb = connect()
        cursor =  mysqldb.cursor(buffered=True)
        query = f"""INSERT INTO 
        alper.alper (name, lastname, location, age) VALUES
        ('{name}', '{lastname}', '{location}','{age}');"""
        cursor.execute(query)
        mysqldb.commit()
        mysqldb.close()
    except mysql.connector.Error as e:
        if(e.errno == errorcode.ER_ACCESS_DENIED_ERROR):
            logging.error(str(e))
            return("AUTH ERROR!")
            
        elif(e.errno == errorcode.ER_BAD_DB_ERROR):
            logging.error(str(e))
            return("DB NOT EXIST!")
            
    return jsonify(correct=insertion)

@app.route('/deleting', methods=['DELETE'])
def delete():
    number_id= request.get_json()
    number=number_id["number_id"]   
    try:
        mysqldb = connect()
        cursor =  mysqldb.cursor(buffered=True)
        query = f""" DELETE FROM {config['DEFAULT']['mysql_database']}.{config['DEFAULT']['mysql_table']} WHERE ID = {number}; """
        cursor.execute(query)
        mysqldb.commit()
        mysqldb.close()
    except mysql.connector.Error as e:
        if(e.errno == errorcode.ER_ACCESS_DENIED_ERROR):
            logging.error(str(e))
            return("AUTH ERROR!")
            
        elif(e.errno == errorcode.ER_BAD_DB_ERROR):
            logging.error(str(e))
            return("DB NOT EXIST!")
            
    return jsonify(correct=number)


if __name__ == "__main__":
    app.run(host=config['APISERVER']['api_host'], port=config['APISERVER']['api_port'])
    