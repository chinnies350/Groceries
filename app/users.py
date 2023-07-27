from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)
from app.libs import hashPassword, timestamp, myconverter

from bson import ObjectId
import datetime
import json
from pprint import pprint


parser = reqparse.RequestParser()
parser.add_argument('next', help='', required=False)



# to manage all the users

class Users(Resource):

    def __init__(self):
        parser.add_argument('userId', required=False)
        parser.add_argument('merchantId', required=False)
        parser.add_argument('userName', required=False)
        parser.add_argument('email', required=False)
        parser.add_argument('primaryPhone', required=False)
        parser.add_argument('password', required=False)
        parser.add_argument('delAddress1', required=False)
        parser.add_argument('delCity1', required=False)
        parser.add_argument('delPincode1', required=False)        
        parser.add_argument('delState1', required=False)
        parser.add_argument('addType1', required=False)
        parser.add_argument('delAddress2', required=False)
        parser.add_argument('delCity2', required=False)
        parser.add_argument('delPincode2', required=False)        
        parser.add_argument('delState2', required=False)
        parser.add_argument('addType1', required=False)        
        parser.add_argument('addType2', required=False)
        parser.add_argument('defaultAddress', required=False)
        parser.add_argument('secondaryPhone', required=False)
        parser.add_argument('userRole', required=False)
        parser.add_argument('userStatus', required=False)       


        # self.uid = get_jwt_identity()
        # self.user = get_jwt_claims()

    def post(self):
        args = parser.parse_args()

        createdBy = 1
        createdDate = datetime.datetime.now()

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users (merchant_id, user_name, email, primary_phone, password,"
        "del_address_1,del_city_1,del_pincode_1,del_state_1, add_type_1,del_address_2,del_city_2,"
        " del_pincode_2,del_state_2,add_type_2, default_address,secondary_phone,user_role, user_status, created_by, created_date)"
        " Values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(
            args.merchantId,
            args.userName,
            args.email,
            args.primaryPhone,
            hashPassword(args.password),
            args.delAddress1,
            args.delCity1,
            args.delPincode1,
            args.delState1,
            args.addType1,
            args.delAddress2,
            args.delCity2,
            args.delPincode2,
            args.delState2,
            args.addType2,
            args.defaultAddress,
            args.secondaryPhone,           
            args.userRole,
            args.userStatus,
            createdBy,
            createdDate

        ))
        result = cursor.rowcount
        conn.commit()
        conn.close()

        if result >=1:
            return {
                'message': 'inserted successfully',
                'statusCode': 1
            }

        else:
            return {
                'message': 'Data is not updated',
                'statusCode': 0
            }

    def put(self):
        args = parser.parse_args()

        updatedBy = 1
        updatedDate = datetime.datetime.now()

        conn = mysql.connect()
        cursor = conn.cursor()
        # print(f'args {args}')
        cursor.execute("Update users set merchant_id=%s, user_name=%s, primary_phone=%s,"
        "del_address_1=%s,del_city_1=%s,del_pincode_1=%s,del_state_1=%s, add_type_1=%s,del_address_2=%s,del_city_2=%s,"
        " del_pincode_2=%s,del_state_2=%s,add_type_2=%s, default_address=%s,secondary_phone=%s,user_role=%s, user_status=%s, updated_by=%s, updated_date=%s"
        " where email=%s and user_id=%s",(
            args.merchantId,
            args.userName,
            args.primaryPhone,
            args.delAddress1,
            args.delCity1,
            args.delPincode1,
            args.delState1,
            args.addType1,
            args.delAddress2,
            args.delCity2,
            args.delPincode2,
            args.delState2,
            args.addType2,
            args.defaultAddress,
            args.secondaryPhone,           
            args.userRole,
            args.userStatus,
            updatedBy,
            updatedDate,
            args.email,
            args.userId

        ))
        result = cursor.rowcount
        conn.commit()
        conn.close()

        if result >=1:
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
        
        args = parser.parse_args()
        conn = mysql.connect()
        cursor = conn.cursor()

        if args.userId:
            cursor.execute("Select * from users where user_id=%s ", (args.userId))
            result = cursor.fetchall()
        elif args.userRole and args.merchantId:
            cursor.execute("Select * from users where user_role=%s and merchant_id=%s and user_status='A'", (args.userRole, args.merchantId))
            result = cursor.fetchall()
        elif args.merchantId:
            print('merchant if ')
            cursor.execute("Select * from users where merchant_id=%s AND (user_role='U' OR user_role='D')", (args.merchantId))
            result = cursor.fetchall()
        else:
            cursor.execute("select * from users WHERE user_role='U' OR user_role='D' ")
            result = cursor.fetchall()
        data=[]

        for r in result:
            data_dt ={
                "userId":r[0],
                "merchantId":r[1],
                "userName":r[2],
                "email":r[3],
                "primaryPhone":r[4],
                "password":r[5],
                "delAddress1":r[6],
                "delCity1":r[7],
                "delPincode1":r[8],
                "delState1":r[9],
                "addType1":r[10],
                "delAddress2":r[11],
                "delCity2":r[12],
                "delPincode2":r[13],
                "delState2":r[14],
                "addType2":r[15],
                "defaultAddress":r[16],
                "secondaryPhone":r[17], 
                "userRole":r[18],
                "userStatus":r[19]
                }
            data.append(data_dt)
        return {
            'data': data,
            'statusCode':1

        }


    def delete(self):
        args = parser.parse_args()

        conn = mysql.connect()
        cursor = conn.cursor()
        
        cursor.execute("update users set user_status='D' where user_id=%s",args.userId)      
        conn.commit()
        conn.close()
        result = cursor.rowcount
        if result >=1:
            return {
                'message': 'deleted successfully',
                'statusCode': 1
            }

        else:
            return {
                'message': 'Data is not deleted',
                'statusCode': 0
            }

            
class Particularuser(Resource):
    
    def __init__(self):
        parser.add_argument(
            'userId', help='userId is required', required=False)

        self.uid = get_jwt_identity()

        self.user = get_jwt_claims()

    def get(self):
        data = parser.parse_args()

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("select * from users where user_id='"+data['userId']+"'")


        result = cursor.fetchall()

        conn.commit()

        data = []

        for r in result:
            sampleDic = {}
            for i,j in enumerate(r):
                sampleDic[i]=j
            pprint(sampleDic)

            data_dt = {"userId":r[0],"userName":r[2],"email":r[3],"phone":r[4],"password":r[5],"address1":r[6],"city1":r[7],"pincode1":r[8],"address2":r[11],"city2":r[12],"pincode2":r[13],"secondaryContactNo":r[17],"userRole":r[18],"state1":r[9],"state2":r[14],"status":r[19]}
            data.append(data_dt)

        return {

            'data': data,
            'statusCode': 1

        }

class TotalUsers(Resource):
    def get(self):
        data = parser.parse_args()

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("select count(user_id) as total_user from users")
        result = cursor.fetchall()

        conn.commit()

        data = []

        for r in result:

            data_dt = {"totalUsers":r[0]}
            data.append(data_dt)

        return {

            'data': data,
            'statusCode': 1

        }




class Defaultaddress(Resource):
    
    def __init__(self):
        parser.add_argument(
            'userId', help='pincode is required', required=False)
        parser.add_argument(
            'defaultAddress', help='pincode is required', required=False)
        self.uid = get_jwt_identity()

        self.user = get_jwt_claims()

    def put(self):
        data = parser.parse_args()

        updatedBy = self.uid

        updatedDate = timestamp()

        conn = mysql.connect()
        cursor = conn.cursor()



        cursor.execute("update users set default_address='"+data['defaultAddress']+"' where user_id='"+(data['userId'])+"'")



        result = cursor.rowcount

        conn.commit()


        if result != 0:

            return {

                'message': 'updated successfully',
                'statusCode': 1

            }

        else:

            return {

                'message': 'Data is not updated',
                'statusCode': 0

            }


