from flask_restful import Resource, reqparse
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)
from app import mysql
import datetime

parser = reqparse.RequestParser()


class SubCategories(Resource):
    def __init__(self):
        super().__init__()
        parser.add_argument('categoryId',required=False)
        parser.add_argument('merchantId',required=False)
        parser.add_argument('subCategoryName',required=False)
        parser.add_argument('status',required=False)
        parser.add_argument('imageUrl',required=False)
        parser.add_argument('subCategoryId',required=False)
        parser.add_argument("userId", required=False)
        

        self.uid = get_jwt_identity()
        self.user = get_jwt_claims()

    def get(self):
        args = parser.parse_args()

        conn = mysql.connect()
        cursor = conn.cursor()
        if args.categoryId and args.merchantId:
            cursor.execute("SELECT sub_categories.*, categories.category_name FROM sub_categories LEFT JOIN categories ON categories.category_id = sub_categories.category_id "
            "WHERE sub_categories.category_id=%s AND sub_categories.merchant_id=%s ",(args.categoryId, args.merchantId))
        elif args.subCategoryName and args.merchantId:
            cursor.execute("SELECT sub_categories.*, categories.category_name FROM sub_categories LEFT JOIN categories ON categories.category_id = sub_categories.category_id " 
            "WHERE sub_categories.sub_category_name=%s AND sub_categories.merchant_id=%s ",(args.subCategoryName, args.merchantId))
        # elif args.status and args.merchantId:
        #     cursor.execute("SELECT * FROM sub_categories WHERE status=%s AND merchant_id=%s AND status='A'",(args.status, args.merchantId))
        elif args.subCategoryId and args.merchantId:
            cursor.execute("SELECT sub_categories.*, categories.category_name FROM sub_categories LEFT JOIN categories ON categories.category_id = sub_categories.category_id " 
            "WHERE sub_categories.sub_category_id=%s AND sub_categories.merchant_id=%s ",(args.subCategoryId, args.merchantId))
        elif args.merchantId:
            cursor.execute("SELECT sub_categories.*, categories.category_name FROM sub_categories LEFT JOIN categories ON categories.category_id = sub_categories.category_id "
            "WHERE sub_categories.merchant_id=%s ",(args.merchantId))
        else:
            cursor.execute("SELECT sub_categories.*, categories.category_name FROM sub_categories LEFT JOIN categories ON categories.category_id = sub_categories.category_id " )
        row = cursor.fetchall()
    
        data = []
        
        if row:
            for r in row:
                products = []
                cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
                "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
                "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
                "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
                "Inner join categories on products.category_id = categories.category_id where products.sub_category_id=%s and products.merchant_id=%s and products.product_status='A'",(args.userId, args.userId,r[0], r[2]))
                product_details = cursor.fetchall()
                if product_details:
                    for product in product_details:
                        cursor.execute("SELECT config_value FROM configuration_master WHERE config_id=%s", product[7])
                        uom_value = cursor.fetchone()[0]
                        products.append(
                            {"productId": product[0], 
                            "merchantId": product[1],
                            "categoryId": product[2],
                            "subCategoryId": product[3], 
                            "productName": product[4],
                            "description": product[5], 
                            "productQuantity": str(product[6]), 
                            "productUom": uom_value,
                            "productUomId":str(product[7]),
                            "productMrp": str(product[8]),
                            "productSellingPrice": str(product[9]), 
                            "productImage": product[10], 
                            "bestSelling": product[11],
                            "productStatus": product[12],                                         
                            "categoryName": product[19],
                            "cartExist":product[20],
                            "wishlistExist":product[21]
                            })
                data.append({
                    "subCategoryId":r[0],
                    "categoryId":r[1],
                    "merchantId":r[2],
                    "subCategoryName":r[3],
                    "status":r[4],
                    "imageUrl":r[5],
                    "categoryName":r[10],
                    "products":products
                })
            conn.commit()
            return {
                    "data": data,
                    "statusCode": 1
                }
       
        else: 
            conn.commit()
            return {
                    'message': 'data not found',
                    'statusCode': 0
                    }





    def post(self):
        args = parser.parse_args()
        print(f'args {args}')
        status = 'A'
        created_by = self.uid
        created_date = datetime.datetime.now()

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT %s IN (SELECT sub_category_name FROM paypre_ecom.sub_categories WHERE category_id=%s AND merchant_id=%s)",(args.subCategoryName,args.categoryId,args.merchantId))
        exist = cursor.fetchone()[0]
        if exist >=1:
            return {
                'message': 'Data already exist',
                'statusCode': 0
            }
        cursor.execute("INSERT INTO sub_categories(category_id,merchant_id, sub_category_name, status, image_url, created_by, created_date)"
        "VALUES(%s,%s,%s,%s,%s,%s,%s)",(
            args.categoryId,
            args.merchantId,
            args.subCategoryName,
            status,
            args.imageUrl,
            created_by,
            created_date
        ))

        result  = cursor.rowcount
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


    def put(self):
        args = parser.parse_args()
        status="A"
        updated_by = self.uid
        updated_date = datetime.datetime.now()
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("select count(*) from sub_categories where merchant_id=%s and category_id=%s and sub_category_id!=%s and sub_category_name=%s",(args.merchantId,args.categoryId,args.subCategoryId,args.subCategoryName))
        exist = cursor.fetchone()
        if exist:
            return {
                'message': 'Data already exist',
                'statusCode': 0
            }

        cursor.execute("UPDATE sub_categories SET category_id=%s,merchant_id=%s, sub_category_name=%s, status=%s,"
        " image_url=%s, created_by=%s, created_date=%s WHERE sub_category_id=%s",(
            args.categoryId,
            args.merchantId,
            args.subCategoryName,
            status,
            args.imageUrl,
            updated_by,
            updated_date,
            args.subCategoryId
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

    #     to delete products

    def delete(self):

        args = parser.parse_args()

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("UPDATE sub_categories SET status='D' WHERE sub_category_id =%s", args.subCategoryId)
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

class ActiveSubCategory(Resource):
    def __init__(self):
        super().__init__()
        parser.add_argument('categoryId',required=False)
        parser.add_argument('merchantId',required=False)
        parser.add_argument('subCategoryName',required=False)
        parser.add_argument('status',required=False)
        parser.add_argument('imageUrl',required=False)
        parser.add_argument('subCategoryId',required=False)
        parser.add_argument("userId", required=False)

    # 
    def get(self):
        args = parser.parse_args()

        conn = mysql.connect()
        cursor = conn.cursor()
        if args.categoryId and args.merchantId:
            cursor.execute("SELECT sub_categories.*, categories.category_name FROM sub_categories LEFT JOIN categories ON categories.category_id = sub_categories.category_id "
            "WHERE sub_categories.category_id=%s AND sub_categories.merchant_id=%s AND sub_categories.status='A'",(args.categoryId, args.merchantId))
        elif args.subCategoryName and args.merchantId:
            cursor.execute("SELECT sub_categories.*, categories.category_name FROM sub_categories LEFT JOIN categories ON categories.category_id = sub_categories.category_id " 
            "WHERE sub_categories.sub_category_name=%s AND sub_categories.merchant_id=%s AND sub_categories.status='A'",(args.subCategoryName, args.merchantId))
        # elif args.status and args.merchantId:
        #     cursor.execute("SELECT * FROM sub_categories WHERE status=%s AND merchant_id=%s AND status='A'",(args.status, args.merchantId))
        elif args.subCategoryId and args.merchantId:
            cursor.execute("SELECT sub_categories.*, categories.category_name FROM sub_categories LEFT JOIN categories ON categories.category_id = sub_categories.category_id " 
            "WHERE sub_categories.sub_category_id=%s AND sub_categories.merchant_id=%s AND sub_categories.status='A'",(args.subCategoryId, args.merchantId))
        elif args.merchantId:
            cursor.execute("SELECT sub_categories.*, categories.category_name FROM sub_categories LEFT JOIN categories ON categories.category_id = sub_categories.category_id "
            "WHERE sub_categories.merchant_id=%s AND sub_categories.status='A'",(args.merchantId))
        else:
            cursor.execute("SELECT sub_categories.*, categories.category_name FROM sub_categories LEFT JOIN categories ON categories.category_id = sub_categories.category_id " 
            "WHERE sub_categories.status='A'")
        row = cursor.fetchall()
    
        data = []
        
        if row:
            for r in row:
                products = []
                cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
                "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
                "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
                "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
                "Inner join categories on products.category_id = categories.category_id where products.sub_category_id=%s and products.merchant_id=%s and products.product_status='A'",(args.userId, args.userId, r[0], r[2]))
                product_details = cursor.fetchall()
                if product_details:
                    for product in product_details:
                        cursor.execute("SELECT config_value FROM configuration_master WHERE config_id=%s", product[7])
                        uom_value = cursor.fetchone()[0]
                        products.append(
                            {"productId": product[0], 
                            "merchantId": product[1],
                            "categoryId": product[2],
                            "subCategoryId": product[3], 
                            "productName": product[4],
                            "description": product[5], 
                            "productQuantity": str(product[6]), 
                            "productUom": uom_value,
                            "productUomId":str(product[7]),
                            "productMrp": str(product[8]),
                            "productSellingPrice": str(product[9]), 
                            "productImage": product[10], 
                            "bestSelling": product[11],
                            "productStatus": product[12],                                         
                            "categoryName": product[19],
                            "cartExist":product[20],
                            "wishlistExist":product[21]
                            })
                data.append({
                    "subCategoryId":r[0],
                    "categoryId":r[1],
                    "merchantId":r[2],
                    "subCategoryName":r[3],
                    "status":r[4],
                    "imageUrl":r[5],
                    "categoryName":r[10],
                    "products":products
                })
            conn.commit()
            return {
                    "data": data,
                    "statusCode": 1
                }
       
        else: 
            conn.commit()
            return {
                    'message': 'data not found',
                    'statusCode': 0
                    }
        
        



