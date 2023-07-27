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
class Payment(Resource):
    def __init__(self):
        parser.add_argument('paymentId', required=False)
        parser.add_argument('merchantId', required=False)
        parser.add_argument('paymentType', required=False)
        parser.add_argument('accessCode', required=False)
        parser.add_argument('workingKey', required=False)
        parser.add_argument('redirectUrl', required=False)
        parser.add_argument('cancelUrl', required=False)
        parser.add_argument('secureUrl', required=False)
        parser.add_argument('upiId', required=False)
        parser.add_argument('status', required=False)   


        self.uid = get_jwt_identity()
        self.user = get_jwt_claims()
    
    def post(self):

        args = parser.parse_args()
        print(f'args {args}')
        conn = mysql.connect()
        cursor = conn.cursor()

        created_by = 1
        created_date = datetime.datetime.now()
        # cursor.execute("INSERT INTO payment_details(merchant_id, payment_type,access_code,working_key, redirect_url, cancel_url, secure_url, upi_id,status,created_by,created_date) VALUES({},{},{},{},{},{},{},{},{},{},{})".format(
        #     args.merchantId,
        #     args.paymentType,
        #     args.accessCode,
        #     args.workingKey,
        #     args.redirectUrl,
        #     args.cancelUrl,
        #     args.secureUrl,
        #     args.upiId,
        #     args.status,
        #     created_by,
        #     created_date
        # )
        # )
        cursor.execute("SELECT %s IN (SELECT upi_id FROM payment_details WHERE merchant_id=%s)",(args.upiId,args.merchantId))
        exist = cursor.fetchone()
        if exist >= 1:
            return {
                'message': 'Data already exist',
                'statusCode': 0
            }

        cursor.execute("INSERT INTO payment_details(merchant_id,payment_type,access_code,working_key,redirect_url,cancel_url,"
        "secure_url,upi_id,status,created_by,created_date)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(
            args.merchantId,
            args.paymentType,
            args.accessCode,
            args.workingKey,
            args.redirectUrl,
            args.cancelUrl,
            args.secureUrl,
            args.upiId,
            args.status,
            created_by,
            created_date
        ))

        result = cursor.rowcount
        

        if result >= 1:
            
            cursor.execute("SELECT * FROM payment_details WHERE merchant_id=1 AND status='A' ORDER BY payment_id DESC;")
            result = cursor.fetchall()
            if result:
                for i, id in enumerate(result):
                    if i != 0:
                        cursor.execute("UPDATE payment_details SET status='D' WHERE payment_id=%s",(id))
            conn.commit()
            conn.close()
            return {
                'message': 'inserted successfully',
                'statusCode': 1
            }

        else:
            return {
                'message': 'Data is not inserted',
                'statusCode': 0
            }

    def put(self):

        args = parser.parse_args()

        conn = mysql.connect()
        cursor = conn.cursor()

        updatedBy = self.uid
        updatedDate = datetime.datetime.now()

        cursor.execute("UPDATE payment_details SET payment_type=%s,access_code=%s,working_key=%s,redirect_url=%s,cancel_url=%s,"
        "secure_url=%s,upi_id=%s,status=%s, updated_by=%s, updated_date=%s WHERE merchant_id=%s and payment_id=%s", (            
            args.paymentType,
            args.accessCode,
            args.workingKey,
            args.redirectUrl,
            args.cancelUrl,
            args.secureUrl,
            args.upiId,
            args.status,
            updatedBy,
            updatedDate,
            args.merchantId,
            args.paymentId
        ))
        print('cursor executed1')

        if cursor.rowcount>=1:
            cursor.execute("SELECT payment_id FROM payment_details WHERE merchant_id=%s AND status='A' AND payment_id != %s ORDER BY payment_id DESC;",(args.merchantId,args.paymentId))
            print('cursor executed 2')
            result = cursor.fetchall()
            print('ftech 1')
            if result:
                for id in result:
                    print(f'id {id}')
                    cursor.execute("UPDATE payment_details SET status='D' WHERE payment_id=%s",(id))
                    print('cursor executed 3')
            conn.commit()
            conn.close()
            return {
                'message': 'updated successfully',
                'statusCode': 1
            }

        else:
            return {
                'message': 'Data is not updated',
                'statusCode': 0
            }

    def get(self):
        data=[]
        args = parser.parse_args()

        conn = mysql.connect()
        cursor = conn.cursor()
        
        if args.merchantId:
            cursor.execute("select * from payment_details WHERE merchant_id=%s",args.merchantId)
            result = cursor.fetchall()
        else:
            cursor.execute("select * from payment_details")
            result = cursor.fetchall()
            conn.commit()       

        for r in result:
            data.append(
                {   "paymentId":r[0],
                    "merchantId":r[1],
                    "paymentType":r[2],
                    "accessCode":r[3],
                    "workingKey":r[4],
                    "redirectUrl":r[5],
                    "cancelUrl":r[6],
                    "secureUrl":r[7],
                    "upiId":r[8],
                    "status":r[9]
                }
            )
        if data:  
            return {
                'data': data,
                'statusCode':1
            }
        else:
            return {
                'message':"No data found",
                "statusCode":0
            }

    def delete(self):

        args = parser.parse_args()

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("update payment_details set status='D' where payment_id=%s and merchant_id=%s",(
            args.paymentId, 
            args.merchantId
        ))
        conn.commit()
        conn.close()

        if cursor.rowcount>=1:
            return {
                'message': 'deleted successfully',
                'statusCode': 1
            }

        else:
            return {
                'message': 'Data is not deleted',
                'statusCode': 0
            }


class ActivePayment(Resource):
    def __init__(self):
        super().__init__()
        parser.add_argument('merchantId',required=False)
        pass

    def get(self):
        args = parser.parse_args()
        conn = mysql.connect()
        cursor = conn.cursor()

        if args.merchantId:
            cursor.execute("SELECT * FROM paypre_ecom.payment_details where merchant_id=%s and status='A'",(args.merchantId))

        else:
            cursor.execute("SELECT * FROM paypre_ecom.payment_details where status='A'")

        result = cursor.fetchall()
        data = []
        if result:
            for r in result:
                data.append(
                    {   "paymentId":r[0],
                        "merchantId":r[1],
                        "paymentType":r[2],
                        "accessCode":r[3],
                        "workingKey":r[4],
                        "redirectUrl":r[5],
                        "cancelUrl":r[6],
                        "secureUrl":r[7],
                        "upiId":r[8],
                        "status":r[9]
                    }
                )
        if data:  
            return {
                'data': data,
                'statusCode':1
            }
        else:
            return {
                'message':"No data found",
                "statusCode":0
            }
        

