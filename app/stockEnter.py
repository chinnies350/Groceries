from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql
import datetime
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)

parser = reqparse.RequestParser()

class StockEntry(Resource):
    def __init__(self) :
        super().__init__()
        parser.add_argument("stockId", required=False)
        parser.add_argument("qty", required=False)
        parser.add_argument("rate", required=False)
        parser.add_argument("reference", required=False)
        parser.add_argument("merchantId", required=False)
        parser.add_argument("categoryId", required=False)
        parser.add_argument("productId", required=False)
        parser.add_argument("subCategoryId", required=False)
        

        self.uid = get_jwt_identity()
        self.user = get_jwt_claims()

    def get(self):
        args = parser.parse_args()
        conn = mysql.connect()
        cursor = conn.cursor()

        if args.qty:
             cursor.execute("SELECT SEM.*, category_name, sub_category_name,product_name  FROM stock_entry_master SEM "
                "INNER JOIN categories C ON C.category_id = SEM.category_id "
                "INNER JOIN products P ON P.product_id = SEM.product_id "
                "INNER JOIN sub_categories SC ON SC.sub_category_id = SEM.sub_category_id WHERE SEM.qty=%s and SEM.merchant_id=%s",(args.qty, args.merchantId))
        elif args.stockId:
             cursor.execute("SELECT SEM.*, category_name, sub_category_name,product_name  FROM stock_entry_master SEM "
                "INNER JOIN categories C ON C.category_id = SEM.category_id "
                "INNER JOIN products P ON P.product_id = SEM.product_id "
                "INNER JOIN sub_categories SC ON SC.sub_category_id = SEM.sub_category_id WHERE SEM.stock_id=%s and SEM.merchant_id=%s",(args.stockId, args.merchantId))
        elif args.rate:
            cursor.execute("SELECT SEM.*, category_name, sub_category_name,product_name  FROM stock_entry_master SEM "
                "INNER JOIN categories C ON C.category_id = SEM.category_id "
                "INNER JOIN products P ON P.product_id = SEM.product_id "
                "INNER JOIN sub_categories SC ON SC.sub_category_id = SEM.sub_category_id WHERE SEM.rate=%s and SEM.merchant_id=%s",(args.rate, args.merchantId))
        elif args.reference:
            cursor.execute("SELECT SEM.*, category_name, sub_category_name,product_name  FROM stock_entry_master SEM "
                "INNER JOIN categories C ON C.category_id = SEM.category_id "
                "INNER JOIN products P ON P.product_id = SEM.product_id "
                "INNER JOIN sub_categories SC ON SC.sub_category_id = SEM.sub_category_id WHERE SEM.reference=%s and SEM.merchant_id=%s",(args.reference, args.merchantId))
        else:
            cursor.execute("SELECT SEM.*, category_name, sub_category_name,product_name  FROM stock_entry_master SEM "
                "INNER JOIN categories C ON C.category_id = SEM.category_id "
                "INNER JOIN products P ON P.product_id = SEM.product_id "
                "INNER JOIN sub_categories SC ON SC.sub_category_id = SEM.sub_category_id where SEM.merchant_id=%s",(args.merchantId))
        row = cursor.fetchall()
        data = []
        if row:
            for r in row:
                data.append({
                    "stockId":r[0],
                    "qty":r[1],
                    "rate":str(r[2]),
                    "reference":r[3],
                    "merchantId":r[8],
                    "categoryId":r[9],
                    "subCategoryId":r[10],
                    "productId":r[11],
                    "categoryName":r[12],
                    "subCategoryName":r[13],
                    "productName":r[14]
                })

            return {
                    "data": data,
                    "statusCode": 1
                }

        else:
            return {
                    'message': 'data not found',
                    'statusCode': 0
                    }



    def post(self):
        args = parser.parse_args()
        conn = mysql.connect()
        cursor = conn.cursor()

        createdBy = self.uid
        createdDate = datetime.datetime.now()

        cursor.execute("INSERT INTO stock_entry_master(qty, rate, reference, created_by, created_date,merchant_id,category_id,sub_category_id,product_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(
            args.qty,
            args.rate,
            args.reference,
            createdBy,
            createdDate,
            args.merchantId,
            args.categoryId,
            args.subCategoryId,
            args.productId
        ))

        result = cursor.rowcount
        if result >=1:
            cursor.execute("UPDATE products SET no_of_items=%s WHERE product_id =%s",(args.qty, args.productId))
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
                'message': 'Data is not Inserted1',
                'statusCode': 0
            }

        else:
            return {
                'message': 'Data is not Inserted0',
                'statusCode': 0
            }

    def put(self):

        args = parser.parse_args()
        conn = mysql.connect()
        cursor = conn.cursor()

        updatedBy = self.uid
        updatedDate = datetime.datetime.now()

        cursor.execute("UPDATE stock_entry_master SET qty=%s, rate=%s, reference=%s, updated_by=%s, updated_date=%s, merchant_id=%s, category_id=%s, sub_category_id=%s, product_id=%s WHERE stock_id=%s",(
            args.qty,
            args.rate,
            args.reference,
            updatedBy,
            updatedDate,
            args.merchantId,
            args.categoryId,
            args.subCategoryId,
            args.productId,
            args.stockId
        ))

        result = cursor.rowcount
        conn.commit()
        conn.close()

        if result >=1:
            return {
                'message': 'Updated successfully',
                'statusCode': 1
            }

        else:
            return {
                'message': 'Data is not updated',
                'statusCode': 0
            }
