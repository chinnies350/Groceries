from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)
from app.libs import timestamp

import os
from werkzeug.datastructures import FileStorage
from app import *
import datetime
parser = reqparse.RequestParser()


# to manage category details
class Categories(Resource):
    # @jwt_required
    def __init__(self):
        parser.add_argument('categoryName', help='categoryName is required', required=False)
        parser.add_argument('categoryStatus', help='categoryStatus', required=False)
        parser.add_argument('categoryId', help='categoryId is required', required=False)
        parser.add_argument('imageUrl', help='categoryId is required', required=False)
        parser.add_argument('merchantId', help='categoryId is required', required=False)

        # self.uid = get_jwt_identity()
        # self.user = get_jwt_claims()

    # to insert categories

    def post(self):
        try:

            args = parser.parse_args()
            conn = mysql.connect()
            cursor = conn.cursor()

            print(args)
            # created_by = self.uid
            created_by = 1
            created_date = datetime.datetime.now()
                 
            cursor.execute("SELECT '%s' IN (SELECT category_name FROM categories WHERE merchant_id=%s)",(args.categoryName,args.merchantId))
            exist = cursor.fetchone()
            if exist >= 1:
                return {
                'message': 'Data already exist',
                'statusCode': 0
            }
            cursor.execute("insert into categories(merchant_id,category_name,image_url,created_by, created_date)"
            " value (%s,%s,%s,%s,%s)",(
                args.merchantId, 
                args.categoryName,
                args.imageUrl,
                created_by, 
                created_date
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
                    'message': 'Data is not Inserted',
                    'statusCode': 0

                }
        except Exception as e:
            print(e)
            return {"message": e, "statusCode": 0}

    # to view categories

    def get(self):
        data = []

        conn = mysql.connect()
        cursor = conn.cursor()


        args = parser.parse_args()
        if args.merchantId and args.categoryId:
            cursor.execute("select * from categories where merchant_id=%s and category_id=%s", (args.merchantId, args.categoryId))
            result = cursor.fetchall()
        elif args.merchantId:
            cursor.execute("select * from categories where merchant_id=%s", args.merchantId)            
            result = cursor.fetchall()
        elif args.categoryId:
            cursor.execute("select * from categories where category_id=%s", args.categoryId)            
            result = cursor.fetchall()
        else:
            cursor.execute("select * from categories")            
            result = cursor.fetchall()
        if result:
            for row in result:
                data.append({
                    "categoryId":row[0],
                    "merchantId":row[1],
                    "categoryName":row[2],
                    "categoryStatus":row[4],
                    "imageUrl":row[3]
                })
            if data:
                return {
                    "data": data,
                    "statusCode": 1
                }
            else:
                return {
                    "message": "No data found",
                    "statusCode": 0
                }
            
        else:
            return {
                "message": "No data found",
                "statusCode": 0
            }

      

    # edit or update categories details
    def put(self):
        try:

            args = parser.parse_args()
            conn = mysql.connect()
            cursor = conn.cursor()


            # updated_by = self.uid
            updated_by = 1
            updated_date = datetime.datetime.now()
            cursor.execute("select count(*) from categories where merchant_id=%s and category_id!=%s and category_name=%s",(args.merchantId,args.categoryId,args.categoryName))
            exist = cursor.fetchone()[0]
            print(f'exist {exist}')
            if exist >= 1:
                return {
                    'message': 'Data already exist',
                    'statusCode': 0
                }

            cursor.execute("UPDATE categories SET merchant_id=%s,category_name=%s,category_status=%s,image_url=%s, "
            "updated_by=%s,updated_date=%s WHERE category_id =%s",(
                args.merchantId,
                args.categoryName,
                args.categoryStatus,
                args.imageUrl,
                updated_by,
                updated_date,
                args.categoryId
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
        except Exception as e:
            print(e)
            return {"message": e, "statusCode": 0}

    # to delete category details
    def delete(self):
        try:

            args = parser.parse_args()
            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute("UPDATE categories SET category_status='D' WHERE category_id =%s", args.categoryId)
            result = cursor.rowcount
            conn.commit()

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
        except Exception as e:
            return {"message": e, "statusCode": 0}

class Subcategory(Resource):
    # @jwt_required
    def __init__(self):
        parser.add_argument('categoryName', help='categoryName is required', required=False)
        parser.add_argument('categoryStatus', help='categoryStatus', required=False)
        parser.add_argument('categoryId', help='categoryId is required', required=False)
        parser.add_argument('imageUrl', help='categoryId is required', required=False)
        parser.add_argument('merchantId', help='categoryId is required', required=False)

        self.uid = get_jwt_identity()
        self.user = get_jwt_claims()

    # to list sub categories
    def get(self):

        categoryStatus = 'A'

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("select * from configuration_master where config_status='A' and config_name='sub category'")
        result = cursor.fetchall()

        conn.commit()

        datalist = []

        if result:
            for row in result:
                datalist.append({
                    "subcategoryId": row[0],
                    "subcategoryName": row[2]
                    })
            return {
                "data": datalist,
                "statusCode": 1
            }

        else:
            return {
                "data": "No data found",
                "statusCode": 0
            }

# to view particular category
class Listcategories(Resource):
    # @jwt_required
    def __init__(self):
        parser.add_argument('categoryId', required=False)
        parser.add_argument('merchantId', required=False)
        parser.add_argument('categoryStatus', required=False)

    def get(self):

        args = parser.parse_args()

        categoryStatus = 'A'

        if args.categoryId:

            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute("select * from categories where category_id=%s", args.categoryId)
            result = cursor.fetchall()
            print(result)
            conn.commit()
        
        elif args.merchantId:
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("select * from categories where merchant_id=%s", args.merchantId)
            result = cursor.fetchall()
            conn.commit()

        elif args.categoryStatus:
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("select * from categories where category_status=%s", args.categoryStatus)
            result = cursor.fetchall()
            conn.commit()
        
        else:

            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute("select * from categories")
            result = cursor.fetchall()

            cursor.execute("SELECT categories.category_id, COUNT(*) AS product_count, categories.category_name, "
            "categories.image_url, categories.category_status FROM categories JOIN products ON "
            "products.category_id = categories.category_id GROUP BY categories.category_id;")
            product_details = cursor.fetchall()

            conn.commit()

        productlist=[]

        if result:
            for row in result:
                productlist.append({
                    "categoryId": row[0],
                    "productCount":row[1], 
                    "categoryName": row[2], 
                    "categoryStatus": row[4],
                    "imageUrl": row[3]
                    })

            return {
                "data": productlist,
                "statusCode": 1,
                "productCount": len(result)
            }

        else:
            return {
                    "data": "No data found",
                    "statusCode": 0

                }


class ActiveCategories(Resource):
    def __init__(self) :
        super().__init__()
        parser.add_argument('categoryName', help='categoryName is required', required=False)
        parser.add_argument('categoryStatus', help='categoryStatus', required=False)
        parser.add_argument('categoryId', help='categoryId is required', required=False)
        parser.add_argument('imageUrl', help='categoryId is required', required=False)
        parser.add_argument('merchantId', help='categoryId is required', required=False)
    def get(self):
        try:
            data = []

            conn = mysql.connect()
            cursor = conn.cursor()


            args = parser.parse_args()

            if args.merchantId and args.categoryId:
                cursor.execute("select * from categories where merchant_id=%s and category_id=%s and category_status='A'", (args.merchantId, args.categoryId))
                result = cursor.fetchall()
            elif args.merchantId:
                cursor.execute("select * from categories where merchant_id=%s and category_status='A'", args.merchantId)            
                result = cursor.fetchall()
            elif args.categoryId:
                cursor.execute("select * from categories where category_id=%s and category_status='A'", args.categoryId)            
                result = cursor.fetchall()
            else:
                cursor.execute("select * from categories WHERE category_status='A'")            
                result = cursor.fetchall()
            if result:
                for row in result:
                    data.append({
                        "categoryId":row[0],
                        "merchantId":row[1],
                        "categoryName":row[2],
                        "categoryStatus":row[4],
                        "imageUrl":row[3]
                    })
                if data:
                    return {
                        "data": data,
                        "statusCode": 1
                    }
                else:
                    return {
                        "message": "No data found",
                        "statusCode": 0
                    }
                
            else:
                return {
                    "message": "No data found",
                    "statusCode": 0
                }
        except Exception as e:
            print(e)
            return {"message": e, "statusCode": 0}
    
        