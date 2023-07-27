from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)
from app.libs import hashPassword, timestamp
import datetime
import os
from werkzeug.datastructures import FileStorage
from app import *

parser = reqparse.RequestParser()
parser.add_argument('next', help='', required=False)

# to manage products based on the categories


class Products(Resource):
    # @jwt_required
    def __init__(self):
        parser.add_argument('productId', required=False)
        parser.add_argument('merchantId', required=False)
        parser.add_argument('categoryId', required=False)
        parser.add_argument('productName', required=False)
        parser.add_argument('subCategoryId', required=False)
        parser.add_argument('description',  required=False)
        parser.add_argument('productQuantity', required=False)
        # parser.add_argument('productUom', required=False)
        parser.add_argument('productSellingPrice',  required=False)
        parser.add_argument('productImage', required=False)
        parser.add_argument('bestSelling', required=False)
        parser.add_argument('productStatus', required=False)
        parser.add_argument('productMrp', required=False)
        parser.add_argument('productUomId', required=False)
        parser.add_argument('noOfItems', required=False)
        parser.add_argument("userId", required=False)

        self.uid = get_jwt_identity()
        self.user = get_jwt_claims()

    # to insert products

    def post(self):
        args = parser.parse_args()

        created_by = self.uid
        created_date = datetime.datetime.now()

        conn = mysql.connect()
        cursor = conn.cursor()
        print(f'args {args}')

        # cursor.execute("SELECT config_id FROM configuration_master WHERE config_value=%s",args.productUom)
        # uom = cursor.fetchone()[0]
        cursor.execute(" SELECT %s IN (SELECT product_name FROM paypre_ecom.products WHERE merchant_id=%s AND category_id=%s AND sub_category_id=%s) AS exist ",(args.productName, args.merchantId,args.categoryId,args.subCategoryId))
        print('cursor executed')
        exist = cursor.fetchone()[0]
        if exist >= 1:
            return {
                'message': 'Data already exist',
                'statusCode': 0
            }

        if not args.description:
             cursor.execute(
            "INSERT into products(merchant_id, category_id,product_name,product_qty,product_uom,mrp,"
            "selling_price,image_url,best_selling,product_status,sub_category_id,created_by,created_date, no_of_items) value (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%S)",
            (
                args.merchantId,
                args.categoryId,
                args.productName, 
                args.productQuantity,
                args.productUomId, 
                args.productMrp, 
                args.productSellingPrice, 
                args.productImage,
                args.bestSelling, 
                args.productStatus, 
                args.subCategoryId,
                created_by, 
                created_date,
                args.noOfItems
            ))
        else:
            cursor.execute(
                "INSERT into products(merchant_id, category_id,product_name,description,product_qty,product_uom,mrp,"
                "selling_price,image_url,best_selling,product_status,sub_category_id,created_by,created_date, no_of_items) value (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    args.merchantId,
                    args.categoryId,
                    args.productName, 
                    args.description, 
                    args.productQuantity,
                    args.productUomId, 
                    args.productMrp, 
                    args.productSellingPrice, 
                    args.productImage,
                    args.bestSelling, 
                    args.productStatus, 
                    args.subCategoryId,
                    created_by, 
                    created_date,
                    args.noOfItems
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

    # to view products

    def get(self):
        args = parser.parse_args()

        conn = mysql.connect()
        cursor = conn.cursor()

        products = []

        if args.merchantId and args.categoryId:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "FROM products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "INNER JOIN categories ON products.category_id = categories.category_id WHERE products.merchant_id=%s AND products.category_id=%s ",(args.userId, args.userId,args.merchantId, args.categoryId))
            product_details = cursor.fetchall()
            conn.commit()

        elif args.productId and args.merchantId:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "Inner join categories on products.category_id = categories.category_id where products.product_id=%s and products.merchant_id=%s",(args.userId,args.userId,args.productId, args.merchantId))
            product_details = cursor.fetchall()
            conn.commit() 
        
        elif args.bestSelling and args.merchantId:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "Inner join categories on products.category_id = categories.category_id where products.best_selling=%s and products.merchant_id=%s",(args.userId,args.userId,args.bestSelling, args.merchantId))
            product_details = cursor.fetchall()
            conn.commit()
        
        elif args.productStatus and args.merchantId:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "Inner join categories on products.category_id = categories.category_id where products.product_status=%s and products.merchant_id=%s",(args.userId,args.userId,args.productStatus, args.merchantId))
            product_details = cursor.fetchall()
            conn.commit()

        elif args.subCategoryId and args.merchantId:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "Inner join categories on products.category_id = categories.category_id where products.sub_category_id=%s and products.merchant_id=%s",(args.userId,args.userId,args.subCategoryId, args.merchantId))
            product_details = cursor.fetchall()
            conn.commit()
        
        elif args.categoryId and args.merchantId:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "Inner join categories on products.category_id = categories.category_id where products.category_id=%s and products.merchant_id=%s",(args.userId,args.userIdargs.categoryId, args.merchantId))
            product_details = cursor.fetchall()
            conn.commit()

        elif args.merchantId:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "Inner join categories on products.category_id = categories.category_id where products.merchant_id=%s ",(args.userId, args.userId, args.merchantId))
            product_details = cursor.fetchall()
            conn.commit()  

        elif args.productId:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "Inner join categories on products.category_id = categories.category_id where products.product_id=%s",(args.userId, args.userId, args.productId))
            product_details = cursor.fetchall()
            conn.commit() 
        
        elif args.bestSelling:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "Inner join categories on products.category_id = categories.category_id where products.best_selling=%s",(args.userId, args.userId, args.bestSelling))
            product_details = cursor.fetchall()
            conn.commit()
        
        elif args.productStatus:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "Inner join categories on products.category_id = categories.category_id where products.product_status=%s",(args.userId, args.userId, args.productStatus))
            product_details = cursor.fetchall()
            conn.commit()

        elif args.subCategoryId:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "Inner join categories on products.category_id = categories.category_id where products.sub_category_id=%s",(args.userId, args.userId,args.subCategoryId))
            product_details = cursor.fetchall()
            conn.commit()
        
        elif args.categoryId:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "Inner join categories on products.category_id = categories.category_id where products.category_id=%s",(args.userId, args.userId, args.categoryId))
            product_details = cursor.fetchall()
            conn.commit()

        else:
            cursor.execute("SELECT products. *, configuration_master.config_value, categories.category_name, " 
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "FROM products INNER JOIN configuration_master ON configuration_master.config_id = products.product_uom "
            "INNER JOIN categories ON products.category_id = categories.category_id ",(args.userId, args.userId))
            product_details = cursor.fetchall()          

        if product_details:
            for product in product_details:
                cursor.execute("SELECT config_value FROM configuration_master WHERE config_id=%s", product[7])
                uom_value = cursor.fetchone()[0]
                cursor.execute("SELECT sub_category_name FROM sub_categories WHERE sub_category_id=%s",(product[3]))
                subName = cursor.fetchone()
                products.append(
                    {"productId": product[0], 
                    "merchantId": product[1],
                    "categoryId": product[2],
                    "subCategoryId": product[3], 
                    "subCategoryName":(subName[0] if subName else subName),
                    "productName": product[4],
                    "description": product[5], 
                    "productQuantity": str(product[6]), 
                    "productUom": uom_value,
                    "productUomId":str(product[7]),
                    "productMrp": str(int(product[8])),
                    "productSellingPrice": str(int(product[9])), 
                    "productImage": product[10], 
                    "bestSelling": product[11],
                    "productStatus": product[12],
                    "noOfItems": product[17],                                  
                    "categoryName": product[19],
                    "cartExist":product[20],
                    "wishlistExist":product[21]
                    })
                
            return {
                    "data": products,
                    "statusCode": 1
                }

        else:
            return {
                    'message': 'data not found',
                    'statusCode': 0
                    }


    # to update products

    def put(self):

        args = parser.parse_args()
        # updated_by = self.uid
        updated_by = 1
        updated_date = datetime.datetime.now()
        conn = mysql.connect()
        cursor = conn.cursor()
        # print(f'con {conn}')
        # print(f'args {args}')
        # cursor.execute("SELECT config_id FROM configuration_master WHERE config_value=%s"% (args.productUom))
        # uom = cursor.fetchone()[0]
        # print(f'getting all values {uom}')
        # print(f'uom {uom}')
        # print(f'type of uom {type(uom)}')
        cursor.execute("select count(*) from products where merchant_id=%s and category_id=%s and sub_category_id=%s and product_id !=%s and product_name=%s",(args.merchantId,args.categoryId,args.subCategoryId,args.productId,args.productName))
        exist = cursor.fetchone()[0]
        print(f'exist {exist}')
        if exist >=1:
            return {
                'message': 'Data already exist',
                'statusCode': 0
            }
        if not args.description:
                cursor.execute("UPDATE products SET merchant_id=%s,category_id=%s,product_name=%s,product_qty=%s,product_uom=%s,mrp=%s,"
            "selling_price=%s,image_url=%s,best_selling=%s,product_status=%s,updated_by=%s,updated_date=%s,no_of_items=%s WHERE product_id=%s",(
                args.merchantId,
                args.categoryId,
                args.productName,
                args.productQuantity,
                args.productUomId,
                args.productMrp,
                args.productSellingPrice,
                args.productImage,
                args.bestSelling,
                args.productStatus,
                updated_by,
                updated_date,
                args.noOfItems,
                args.productId

            ))
        else:

            cursor.execute("UPDATE products SET merchant_id=%s,category_id=%s,product_name=%s,description=%s,product_qty=%s,product_uom=%s,mrp=%s,"
            "selling_price=%s,image_url=%s,best_selling=%s,product_status=%s,updated_by=%s,updated_date=%s,no_of_items=%s WHERE product_id=%s",(
                args.merchantId,
                args.categoryId,
                args.productName,
                args.description,
                args.productQuantity,
                args.productUomId,
                args.productMrp,
                args.productSellingPrice,
                args.productImage,
                args.bestSelling,
                args.productStatus,
                updated_by,
                updated_date,
                args.noOfItems,
                args.productId

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

        cursor.execute("UPDATE products SET product_status='D' WHERE product_id =%s", args.productId)
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


class ActiveProducts(Resource):
    def __init__(self) :
        super().__init__()
        parser.add_argument('productId', required=False)
        parser.add_argument('merchantId', required=False)
        parser.add_argument('categoryId', required=False)
        parser.add_argument('productName', required=False)
        parser.add_argument('subCategoryId', required=False)
        parser.add_argument('description',  required=False)
        parser.add_argument('productQuantity', required=False)
        # parser.add_argument('productUom', required=False)
        parser.add_argument('productSellingPrice',  required=False)
        parser.add_argument('productImage', required=False)
        parser.add_argument('bestSelling', required=False)
        parser.add_argument('productStatus', required=False)
        parser.add_argument('productMrp', required=False)
        parser.add_argument('productUomId', required=False)
        parser.add_argument('userId', required=False)

    def get(self):
        args = parser.parse_args()

        conn = mysql.connect()
        cursor = conn.cursor()

        products = []
        
        
        
        # args.userId = (args.userId if args.userId else None)

        if args.merchantId and args.categoryId:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "FROM products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "INNER JOIN categories ON products.category_id = categories.category_id WHERE products.merchant_id=%s AND products.category_id=%s and products.product_status='A'",(args.userId, args.userId,args.merchantId, args.categoryId))
            product_details = cursor.fetchall()
            conn.commit()

        elif args.productId and args.merchantId:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "Inner join categories on products.category_id = categories.category_id where products.product_id=%s and products.merchant_id=%s and products.product_status='A'",(args.userId,args.userId,args.productId, args.merchantId))
            product_details = cursor.fetchall()
            conn.commit() 
        
        elif args.bestSelling and args.merchantId:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "Inner join categories on products.category_id = categories.category_id where products.best_selling=%s and products.merchant_id=%s and products.product_status='A'",(args.userId,args.userId,args.bestSelling, args.merchantId))
            product_details = cursor.fetchall()
            conn.commit()
        
        # elif args.productStatus and args.merchantId:
        #     cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
        #     "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
        #     "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
        #     "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
        #     "Inner join categories on products.category_id = categories.category_id where products.product_status=%s and products.merchant_id=%s",(args.userId,args.userId,args.productStatus, args.merchantId))
        #     product_details = cursor.fetchall()
        #     conn.commit()

        elif args.subCategoryId and args.merchantId:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "Inner join categories on products.category_id = categories.category_id where products.sub_category_id=%s and products.merchant_id=%s and products.product_status='A'",(args.userId,args.userId,args.subCategoryId, args.merchantId))
            product_details = cursor.fetchall()
            conn.commit()
        
        elif args.categoryId and args.merchantId:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "Inner join categories on products.category_id = categories.category_id where products.category_id=%s and products.merchant_id=%s and products.product_status='A'",(args.userId,args.userIdargs.categoryId, args.merchantId))
            product_details = cursor.fetchall()
            conn.commit()

        elif args.merchantId:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "Inner join categories on products.category_id = categories.category_id where products.merchant_id=%s and products.product_status='A'",(args.userId, args.userId, args.merchantId))
            product_details = cursor.fetchall()
            conn.commit()  

        elif args.productId:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "Inner join categories on products.category_id = categories.category_id where products.product_id=%s and products.product_status='A'",(args.userId, args.userId, args.productId))
            product_details = cursor.fetchall()
            conn.commit() 
        
        elif args.bestSelling:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "Inner join categories on products.category_id = categories.category_id where products.best_selling=%s and products.product_status='A'",(args.userId, args.userId, args.bestSelling))
            product_details = cursor.fetchall()
            conn.commit()
        
        # elif args.productStatus:
        #     cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
        #     "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
        #     "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
        #     "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
        #     "Inner join categories on products.category_id = categories.category_id where products.product_status=%s",(args.userId, args.userId, args.productStatus))
        #     product_details = cursor.fetchall()
        #     conn.commit()

        elif args.subCategoryId:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "Inner join categories on products.category_id = categories.category_id where products.sub_category_id=%s and products.product_status='A'",(args.userId, args.userId,args.subCategoryId))
            product_details = cursor.fetchall()
            conn.commit()
        
        elif args.categoryId:
            cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
            "Inner join categories on products.category_id = categories.category_id where products.category_id=%s and products.product_status='A'",(args.userId, args.userId, args.categoryId))
            product_details = cursor.fetchall()
            conn.commit()

        else:
            cursor.execute("SELECT products. *, configuration_master.config_value, categories.category_name, " 
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
            "FROM products INNER JOIN configuration_master ON configuration_master.config_id = products.product_uom "
            "INNER JOIN categories ON products.category_id = categories.category_id and products.product_status='A'",(args.userId, args.userId))
            product_details = cursor.fetchall()             

        if product_details:
            for product in product_details:
                cursor.execute("SELECT config_value FROM configuration_master WHERE config_id=%s", product[7])
                uom_value = cursor.fetchone()[0]
                cursor.execute("SELECT sub_category_name FROM sub_categories WHERE sub_category_id=%s",(product[3]))
                subName = cursor.fetchone()
                products.append(
                    {"productId": product[0], 
                    "merchantId": product[1],
                    "categoryId": product[2],
                    "subCategoryId": product[3], 
                    "subCategoryName":(subName[0] if subName else subName),
                    "productName": product[4],
                    "description": product[5], 
                    "productQuantity": str(product[6]), 
                    "productUom": uom_value,
                    "productUomId":str(product[7]),
                    "productMrp": str(int(product[8])),
                    "productSellingPrice": str(int(product[9])), 
                    "productImage": product[10], 
                    "bestSelling": product[11],
                    "productStatus": product[12],
                    "noOfItems": product[17],                                  
                    "categoryName": product[19],
                    "cartExist":product[20],
                    "wishlistExist":product[21]
                    })
                
            return {
                    "data": products,
                    "statusCode": 1
                }

        else:
            return {
                    'message': 'data not found',
                    'statusCode': 0
                    }