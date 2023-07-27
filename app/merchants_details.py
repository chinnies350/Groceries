from flask_restful import Resource, reqparse
from pymysql.cursors import Cursor
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

# to manage all the merchants
class Merchant(Resource):
    def __init__(self):
        parser.add_argument('merchantId', required=False)
        parser.add_argument('merchantName', required=False)
        parser.add_argument('merchantLogo', required=False)
        parser.add_argument('colorCode', required=False)
        parser.add_argument('terms', required=False)
        parser.add_argument('aboutUs', required=False)
        parser.add_argument('facebook', required=False)
        parser.add_argument('instagram', required=False)
        parser.add_argument('twitter', required=False)
        parser.add_argument('contactNumber', required=False)
        parser.add_argument('addressLine1', required=False)
        parser.add_argument('addressLine2', required=False)
        parser.add_argument('policy', required=False)
        parser.add_argument('email', required=False)
        parser.add_argument('minDeliveryChargeLimit', required=False)
        parser.add_argument('deliveryCharges', required=False)
        parser.add_argument('gstPercentage', required=False)
        parser.add_argument('gstNumber',  required=False)            
        parser.add_argument('status',  required=False)            
        parser.add_argument('mapUrl',  required=False)   
        parser.add_argument('password',  required=False)
        parser.add_argument('stockMaintenance',  required=False)
        parser.add_argument('cancellationAllowed',  required=False)
        parser.add_argument('cancellationBeforeHrs',  required=False)
        parser.add_argument('userId',  required=False)



        self.uid = get_jwt_identity()
        self.user = get_jwt_claims()
    
    def post(self):

        args = parser.parse_args()
        conn = mysql.connect()
        cursor = conn.cursor()       


        created_by = 1
        created_date = datetime.datetime.now()
        cursor.execute("select count(*) from users where email=%s",(args.email))
        isEXt = cursor.fetchone()[0]
        if isEXt >= 1:
            return {

                        'message': 'Email is already registered',
                        'statusCode': 0
                    }


        if args.cancellationBeforeHrs:
            print('first query if')
            cursor.execute("INSERT INTO merchant_details(merchant_name,merchant_logo,color_code,terms,about_us,facebook,"
            "instagram,twitter,contact_no,address_line1,address_line2,policy,email,min_del_charge_limit,delivery_charges,"
            "gst_percentage,gst_number,created_by,created_date,map_url,password,stock_maintenance,cancellation_allowed,cancellation_beforehrs)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(
                args.merchantName,
                args.merchantLogo,
                args.colorCode,
                args.terms,
                args.aboutUs,
                args.facebook,
                args.instagram,
                args.twitter,
                args.contactNumber,
                args.addressLine1,
                args.addressLine2,
                args.policy,
                args.email,
                args.minDeliveryChargeLimit,
                args.deliveryCharges,
                args.gstPercentage,
                args.gstNumber,
                created_by,
                created_date,
                args.mapUrl,
                hashPassword(args.password),
                args.stockMaintenance,
                args.cancellationAllowed,
                args.cancellationBeforeHrs
            ))
        else:
            print('first query else')
            cursor.execute("INSERT INTO merchant_details(merchant_name,merchant_logo,color_code,terms,about_us,facebook,"
            "instagram,twitter,contact_no,address_line1,address_line2,policy,email,min_del_charge_limit,delivery_charges,"
            "gst_percentage,gst_number,created_by,created_date,map_url,password,stock_maintenance,cancellation_allowed)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(
                args.merchantName,
                args.merchantLogo,
                args.colorCode,
                args.terms,
                args.aboutUs,
                args.facebook,
                args.instagram,
                args.twitter,
                args.contactNumber,
                args.addressLine1,
                args.addressLine2,
                args.policy,
                args.email,
                args.minDeliveryChargeLimit,
                args.deliveryCharges,
                args.gstPercentage,
                args.gstNumber,
                created_by,
                created_date,
                args.mapUrl,
                hashPassword(args.password),
                args.stockMaintenance,
                args.cancellationAllowed
            ))
        result = cursor.rowcount
        conn.commit()
        cursor.execute("SELECT merchant_id FROM merchant_details ORDER BY merchant_id DESC")
        a = cursor.fetchone()
        if result >= 1:
            userRole= 'A'
            userStatus = 'A'
             # merchant id
            cursor.execute("INSERT INTO users (merchant_id, user_name, email, primary_phone, password,"
            "del_address_1,del_address_2,user_role, user_status, created_by, created_date)"
            " Values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(
                a,
                args.merchantName,
                args.email,
                args.contactNumber,
                hashPassword(args.password),
                args.addressLine1,
                args.addressLine2,          
                userRole,
                userStatus,
                created_by,
                created_date

            ))
            result = cursor.rowcount

            if result >= 1:
                print("came to if condition")
                conn.commit()
                conn.close()
                return {
                'message': 'merchant inserted successfully',
                'statusCode': 1
            }
            else:
                conn.commit()
                conn.close()
                print('came to delete ')
                cursor.execute("DELETE FROM merchant_details WHERE merchant_id=%s",(a))
                dele = cursor.rowcount
                return {
                    'message': 'merchant is not inserted',
                    'statusCode': 0

                }

        conn.commit()
        conn.close()
        if result >= 1:
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

        print("args", args)
        updatedBy = self.uid
        cursor.execute("select count(*) from users where email=%s and merchant_id!=%s and user_role!='A'",(args.email,args.merchantId))
        isEXt = cursor.fetchone()[0]
        if isEXt >= 1:
            return {

                        'message': 'Email is already registered',
                        'statusCode': 0
                    }

        updatedDate = datetime.datetime.now()
        if args.cancellationBeforeHrs:
            cursor.execute("UPDATE merchant_details SET merchant_name=%s, merchant_logo=%s,color_code=%s,terms=%s,about_us=%s,"
            "facebook=%s,instagram=%s,twitter=%s,contact_no=%s,address_line1=%s,address_line2=%s,policy=%s,email=%s,"
            "min_del_charge_limit=%s,delivery_charges=%s,gst_percentage=%s,gst_number=%s,status=%s,updated_by=%s,updated_date=%s, map_url=%s, stock_maintenance=%s, cancellation_allowed=%s,cancellation_beforehrs=%s WHERE merchant_id=%s", (
                args.merchantName,
                args.merchantLogo,
                args.colorCode,
                args.terms,
                args.aboutUs,
                args.facebook,
                args.instagram,
                args.twitter,
                args.contactNumber,
                args.addressLine1,
                args.addressLine2,
                args.policy,
                args.email,
                args.minDeliveryChargeLimit,
                args.deliveryCharges,
                args.gstPercentage,
                args.gstNumber,
                args.status,
                updatedBy,
                updatedDate,
                args.mapUrl,
                args.stockMaintenance,
                args.cancellationAllowed,
                args.cancellationBeforeHrs,
                args.merchantId
            ))
        else:
            cursor.execute("UPDATE merchant_details SET merchant_name=%s, merchant_logo=%s,color_code=%s,terms=%s,about_us=%s,"
            "facebook=%s,instagram=%s,twitter=%s,contact_no=%s,address_line1=%s,address_line2=%s,policy=%s,email=%s,"
            "min_del_charge_limit=%s,delivery_charges=%s,gst_percentage=%s,gst_number=%s,status=%s,updated_by=%s,updated_date=%s, map_url=%s, stock_maintenance=%s, cancellation_allowed=%s WHERE merchant_id=%s", (
                args.merchantName,
                args.merchantLogo,
                args.colorCode,
                args.terms,
                args.aboutUs,
                args.facebook,
                args.instagram,
                args.twitter,
                args.contactNumber,
                args.addressLine1,
                args.addressLine2,
                args.policy,
                args.email,
                args.minDeliveryChargeLimit,
                args.deliveryCharges,
                args.gstPercentage,
                args.gstNumber,
                args.status,
                updatedBy,
                updatedDate,
                args.mapUrl,
                args.stockMaintenance,
                args.cancellationAllowed,
                args.merchantId
            ))
        print('first cursor completed')

        result = cursor.rowcount
        print(f'result 1 {result}')
        if  result:
            print('second cursor came')
            cursor.execute("UPDATE users SET user_name=%s, email=%s, primary_phone=%s, "
            "del_address_1=%s,del_address_2=%s, updated_by=%s, updated_date=%s WHERE merchant_id=%s and user_role='A' and user_id=%s",(
               args.merchantName,
                args.email,
                args.contactNumber,
                args.addressLine1,
                args.addressLine2, 
                updatedBy, 
                updatedDate,
                args.merchantId,
                args.userId

            ))
            print('second cursor completed')
            result = cursor.rowcount
            if  result:
                conn.commit()
                conn.close()
                return {
                'message': 'updated successfully',
                'statusCode': 1
                }
            else:
                conn.commit()
                conn.close()
                return {
                'message': 'Data is not updated',
                'statusCode': 0
            }
           
        else:
            conn.commit()
            conn.close()
            return {
                'message': 'Data is not updated',
                'statusCode': 0
            }

    def get(self):
        data=[]
        args = parser.parse_args()

        conn = mysql.connect()
        cursor = conn.cursor()

        print(args)
        if args.merchantId:
            cursor.execute("select merchant_details.*,users.user_id from merchant_details LEFT join users ON  users.merchant_id = merchant_details.merchant_id WHERE merchant_details.merchant_id=%s and user_role='A'",args.merchantId)
            result = cursor.fetchall()
        elif args.status:
            cursor.execute("select merchant_details.*,users.user_id from merchant_details LEFT join users ON  users.merchant_id = merchant_details.merchant_id WHERE merchant_details.status=%s and user_role='A'",args.status)
            result = cursor.fetchall()
        else:
            cursor.execute("select merchant_details.*,users.user_id from merchant_details LEFT join users ON  users.merchant_id = merchant_details.merchant_id where user_role='A'")
            result = cursor.fetchall()             

        for r in result:
            data.append(
                {
                    "merchantId":r[0],
                    "merchantName":r[1],
                    "merchantLogo":r[2],
                    "colorCode":r[3],
                    "terms":r[4],
                    "aboutUs":r[5],
                    "facebook":r[6],
                    "instagram":r[7],
                    "twitter":r[8],
                    "contactNumber":r[9],
                    "addressLine1":r[10],
                    "addressLine2":r[11],
                    "policy":r[12],
                    "email":r[13],
                    "minDeliveryChargeLimit":str(r[14]),
                    "deliveryCharges":str(r[15]),
                    "gstPercentage":str(r[16]),
                    "gstNumber":r[17],
                    "status":r[18],
                    "mapUrl":r[23],
                    "stockMaintenance":str(r[25]), 
                    "cancellationAllowed":str(r[26]),
                    "cancellationBeforeHrs":str(r[27]),
                    "userId":r[28]
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
        cursor.execute("update merchant_details set status=%s where merchant_id=%s",(args.status,args.merchantId))
        # cursor.execute("update merchant_details set status='D' where merchant_id='" + (args['merchantId']) + "'")
        result = cursor.rowcount
        conn.commit()
        conn.close()

        if result>=1:
            return {
                'message': 'deleted successfully',
                'statusCode': 1
            }

        else:
            return {
                'message': 'Data is not deleted',
                'statusCode': 0
            }



