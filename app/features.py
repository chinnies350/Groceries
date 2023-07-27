from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt,
    get_jwt_claims,
    get_current_user
)
from app.libs import hashdePassword, timestamp, myconverter
import socket
import os
from werkzeug.datastructures import FileStorage
from app import *
import datetime

parser = reqparse.RequestParser()
parser.add_argument('next', help='', required=False)

class Features(Resource):
    # @jwt_required
    def __init__(self):
        parser.add_argument('heading', required=False)
        parser.add_argument('merchantId',  required=False)
        parser.add_argument('imageUrl',  required=False)
        parser.add_argument('description',  required=False)
        parser.add_argument('status',  required=False)
        parser.add_argument('featureId', required=False)

        # self.uid = get_jwt_identity()
        # self.user = get_jwt_claims()

    def post(self):
        args = parser.parse_args()

        conn = mysql.connect()
        cur = conn.cursor()

        created_by = 1
        created_date = datetime.datetime.now()

        try:
            cur.execute("insert into features (merchant_id, heading, image, description, status, created_by, created_date) "
                        "values (%s, %s, %s, %s, %s, %s, %s)", (
                            args.merchantId,
                            args.heading,
                            args.imageUrl,                            
                            args.description,
                            args.status,
                            created_by,
                            created_date
                            
                        ))
            conn.commit()
            conn.close()

            
            if cur.rowcount >= 1:
                return{
                    'message': 'inserted successfully!',
                    'statusCode': 1
                }
            else:
                return {
                    'message': 'Sorry Try again',
                    'statusCode': 0
                }

        except Exception as e:
            print(e)          
            return {
                'message': 'Sorry Try again',
                'statusCode': 0
            }

    def get(self):
        args = parser.parse_args()
        conn = mysql.connect()
        cur = conn.cursor()

        if args.merchantId:
            cur.execute("select * from features WHERE status='A' and merchant_id=%s", args.merchantId)
            info = cur.fetchall()
        else:
            cur.execute("select * from features WHERE status='A'")
            info = cur.fetchall()

        response = []
        if info:
            for i in info:
                response.append({
                    "featureId": i[0],
                    "merchantId":i[1],
                    "heading":i[2],
                    "imageUrl": i[3],
                    "description":i[4],
                    "status": i[5]
                })

        if response:
            return {
                'data': response,
                'statusCode': 1
            }
        else:
            return {
                'data': 'No records found',
                'statusCode': 0
            }

    def put(self):
        args = parser.parse_args()
        conn = mysql.connect()
        cur = conn.cursor()

        updated_by = 1
        updated_date = datetime.datetime.now()

        try:
            cur.execute("UPDATE features SET merchant_id=%s, heading=%s, image=%s, description=%s, status=%s, updated_by=%s, updated_date=%s"
                        "where feature_id=%s", (
                            args.merchantId,
                            args.heading,
                            args.imageUrl,                            
                            args.description,
                            args.status,
                            updated_by,
                            updated_date,
                            args.featureId
                        ))
            conn.commit()
            conn.close()

            if cur.rowcount >= 1:
                return{
                    'message': 'updated successfully!',
                    'statusCode': 1
                }
            else:
                return {
                    'message': 'Sorry Try again',
                    'statusCode': 0
                }

        except Exception as e:
            print(e)          
            return {
                'message': 'Sorry Try again',
                'statusCode': 0
            }

    def delete(self):
        args = parser.parse_args()

        try:
            conn = mysql.connect()
            cur = conn.cursor()
            cur.execute("UPDATE features SET status='D' WHERE feature_id=%s", args.featureId)
            conn.commit()
            conn.close()

            if cur.rowcount >= 1:
                return{
                    'message': 'deleted successfully!',
                    'statusCode': 1
                }
            else:
                return {
                    'message': 'Sorry Try again',
                    'statusCode': 0
                }

        except Exception as e:
            print(e)          
            return {
                'message': 'Sorry Try again',
                'statusCode': 0
            }

