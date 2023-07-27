from flask import jsonify
from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql
import requests as req
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)

parser = reqparse.RequestParser()

class SMS(Resource):
    def __init__(self):
        parser.add_argument('mobileNo', help='mobile number is required', required=False)
        parser.add_argument('link',  required=False)
        parser.add_argument('amount', required=False)
        parser.add_argument('merchantName', required=False)

    def post(self):
        args = parser.parse_args()
        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute("select * from users where primary_phone=%s", args.mobileNo)
            result = cursor.fetchone()
            
            mobile = args.mobileNo
            link = args.link
            amount = args.amount
            merchant_name = args.merchantName
            user_name = result[2]

            message = "Hi "+user_name+"! \n Your payment Rs."+str(amount)+" is pending for your last order from "+merchant_name+"...\n Please complete it by using below link \n"+args.link

            if result:
                cursor.execute("SELECT config_value FROM configuration_master where config_name='smsURL'")
                sms_url = cursor.fetchone()

                return_res = req.post(str(sms_url[0])+str(mobile)+'&msg='+message +'')
                print(return_res.text)
                if "Success" in return_res.text:
                    return {
                        "statusCode": 1, 
                        "message": "Message sent!"}
                else:
                    return {
                        "statusCode": 0, 
                        "message": "Failed"
                        }

        except Exception as e:
            print(e)