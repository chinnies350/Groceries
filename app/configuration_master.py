from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)
from app.libs import hashPassword, timestamp, myconverter

from bson import ObjectId
import datetime
import json

conn = mysql.connect()
cursor = conn.cursor()

parser = reqparse.RequestParser()

# to manage all the payments
class ConfigurationMaster(Resource):
    def __init__(self):
        parser.add_argument('configId', required=False)
        parser.add_argument('configName', required=False)
        parser.add_argument('configValue', required=False)
        parser.add_argument('configStatus', required=False)
        parser.add_argument('configType', required=False)


        self.uid = get_jwt_identity()
        self.user = get_jwt_claims()
    
    def get(self):
        data = []
        args = parser.parse_args()

        conn = mysql.connect()
        cursor = conn.cursor()

        if args.configType:
            cursor.execute("SELECT * FROM configuration_master WHERE config_Type=%s",args.configType)
            result = cursor.fetchall()
        elif args.configName:
            cursor.execute("SELECT * FROM configuration_master WHERE config_name=%s",args.configName)
            result = cursor.fetchall()
        else:
            cursor.execute("SELECT * FROM configuration_master")
            result = cursor.fetchall()

        if result:
            for i in result:
                data.append({
                    "configId":i[0],
                    "configName":i[1],
                    "configValue":i[2],
                    "configStatus":i[3],
                    "configType":i[4]
                })

            return{
                "data":data,
                "statusCode":1
            }
        
        else:
            return{
                "message":"No data found!",
                "statusCode":0
            }