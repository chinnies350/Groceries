from flask import jsonify
from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql

from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)

from random import randint
import json
import pprint
import requests as req
from bson.objectid import ObjectId

parser = reqparse.RequestParser()

# import MySQLdb
# to send otp for verification


class Otp(Resource):
    # @jwt_required
    def __init__(self):
        parser.add_argument(
            'mobileNo', help='mobile number is required', required=False)
        parser.add_argument(
            'type', help='type is required', required=False)
        parser.add_argument("merchantId",required=False)

        # self.uid = get_jwt_identity()
        # self.user = get_jwt_claims()

    def get(self):
        try:
            args = parser.parse_args()

            mobile = args.mobileNo
            range_start = 10 ** (4 - 1)
            range_end = (10 ** 4) - 1
            bb = randint(range_start, range_end)
            print(bb)
            p = "Your OTP is  " + str(bb) + "  Please Dont share with anyone" + "\n\n"
            print(bb)

            if args.type == "forgot":
                conn = mysql.connect()
                cursor = conn.cursor()

                cursor.execute("select * from users where primary_phone=%s", args.mobileNo)
                result = cursor.fetchall()

                print("result", result)

                if result:

                    conn = mysql.connect()
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT config_value FROM configuration_master where config_name='smsURL'")
                    sms_url = cursor.fetchone()

                    print(sms_url[0])

                    conn.commit()
                    print(p)
                    return_res = req.post(str(sms_url[0])+str(mobile)+'&msg='+str(p) +'')
                    print("-------", return_res)
                    print(return_res.text)
                    if "Success" in return_res.text:
                        return {"statusCode": 1, "message": str(bb)}
                    else:
                        return {"statusCode": 0, "message": "Failed"}
                else:
                    return {"statusCode": 0, "message": "Not Registered"}

            elif args.type == "COD":

                conn = mysql.connect()
                cursor = conn.cursor()

                cursor.execute(
                        "SELECT config_value FROM configuration_master where config_name='smsURL'")
                sms_url = cursor.fetchone()

                print(sms_url[0])

                conn.commit()

                return_res = req.post(str(sms_url[0]) + str(mobile) + '&msg=' + str(p) + '')
                print("-------", return_res)
                print(return_res.text)
                if "Success" in return_res.text:
                        return {"statusCode": 1, "message": str(bb)}
                else:
                        return {"statusCode": 0, "message": "Failed"}


            else:
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.execute("select * from users where primary_phone=%s and merchant_id=%s", (args.mobileNo, args.merchantId))
                result = cursor.fetchall()

                print("result", result)

                if result:
                    return {
                        "statusCode": 0, 
                        "message": "Already Exist"
                        }
                    
                else:
                    cursor.execute("SELECT config_value FROM configuration_master where config_name='smsURL'")
                    sms_url = cursor.fetchone()
                    conn.commit()

                    return_res = req.post(str(sms_url[0]) + str(mobile) + '&msg=' + str(p) + '')
                    
                    if "Success" in return_res.text:
                        return {
                            "statusCode": 1, 
                            "message": str(bb)
                            }
                    else:
                        return {
                            "statusCode": 0, 
                            "message": "Failed"
                            }

        except Exception as e:
            return {"message": e, "statusCode": 0}
        
                
