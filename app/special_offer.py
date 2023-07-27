from flask_restful import Resource, reqparse
from app import mysql
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)
from app.libs import hashPassword, timestamp, myconverter
import datetime
from bson import ObjectId
from pprint import pprint
import json


parser = reqparse.RequestParser()

# to manage offers
class Special(Resource):
    # @jwt_required
    def __init__(self):
        parser.add_argument('offerId', help='offer id is required', required=False)
        parser.add_argument('productId', help='product id is required', required=False)
        parser.add_argument('merchantId', help='product id is required', required=False)
        parser.add_argument('categoryId', help='category id is required', required=False)
        parser.add_argument('productName', help='product name required', required=False)
        parser.add_argument('description', help='description is required', required=False)
        parser.add_argument('productQuantity', help='Product quantity is required', required=False)
        # parser.add_argument('productUom', help='Product UOM is required', required=False)
        parser.add_argument('productUomId', help='config ID is required', required=False)
        parser.add_argument('productMrp', help='mrp is required', required=False)
        parser.add_argument('productSellingPrice', help='selling price is required', required=False)
        parser.add_argument('productImage', help='image url is required', required=False)
        parser.add_argument('offerStartDate', help='offer start date is required', required=False)
        parser.add_argument('offerEndDate', help='offer end date is required', required=False)
        parser.add_argument('productStatus', help='Product status required', required=False)
        parser.add_argument('userId', help='userid for cart filtering', required=False)
        parser.add_argument('subCategoryId', help='userid for cart filtering', required=False)

        self.uid = get_jwt_identity()
        self.user = get_jwt_claims()

    # to add offers
    def post(self):

        args = parser.parse_args()
        # updatedBy = self.uid
        created_by = 1
        created_date = datetime.datetime.now()

        conn = mysql.connect()
        cursor = conn.cursor()

        # cursor.execute("SELECT config_id FROM configuration_master WHERE config_value=%s",args.productUom)
        # uom = cursor.fetchone()[0]
        if not args.description:
            cursor.execute("INSERT INTO special_offer(product_id,merchant_id,category_id,product_name,product_qty,"
            "product_uom,mrp,selling_price,image_url,offer_start_date,offer_end_date,product_status,created_by,created_date,sub_category_id) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(
                args.productId,
                args.merchantId, 
                args.categoryId, 
                args.productName,  
                args.productQuantity,
                args.productUomId,
                args.productMrp, 
                args.productSellingPrice,
                args.productImage, 
                args.offerStartDate,
                args.offerEndDate, 
                args.productStatus,
                created_by,
                created_date,
                args.subCategoryId
                ))
            pass
        else:
            cursor.execute("INSERT INTO special_offer(product_id,merchant_id,category_id,product_name,description,product_qty,"
            "product_uom,mrp,selling_price,image_url,offer_start_date,offer_end_date,product_status,created_by,created_date,sub_category_id) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(
                args.productId,
                args.merchantId, 
                args.categoryId, 
                args.productName, 
                args.description, 
                args.productQuantity,
                args.productUomId,
                args.productMrp, 
                args.productSellingPrice,
                args.productImage, 
                args.offerStartDate,
                args.offerEndDate, 
                args.productStatus,
                created_by,
                created_date,
                args.subCategoryId
                ))
            

        conn.commit()
        conn.close()

        return {
                'message': 'data inserted successfully',
                'statusCode': 1
                }

    # to get offers
    def get(self):
        args = parser.parse_args()
        conn = mysql.connect()
        cursor = conn.cursor()
        if args.merchantId:
            cursor.execute("select special_offer. *,configuration_master.config_value, "
            "IF( %s IN (SELECT UC.user_id FROM special_offer SP INNER JOIN user_cart UC ON UC.product_id = SP.product_id WHERE SP.product_id = special_offer.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM special_offer SP INNER JOIN user_wishlist WC ON WC.product_id = SP.product_id WHERE SP.product_id = special_offer.product_id ), 'Y','N') AS id1, "
            "categories.category_name, sub_categories.sub_category_name "
            "from special_offer INNER JOIN configuration_master ON special_offer.product_uom=configuration_master.config_id "
            "INNER JOIN categories ON categories.category_id = special_offer.category_id "
            "LEFT JOIN sub_categories ON sub_categories.sub_category_id = special_offer.sub_category_id "
            "where special_offer.merchant_id=%s", (args.userId, args.userId, args.merchantId))
            result = cursor.fetchall()
        else:
            cursor.execute("select special_offer. *,configuration_master.config_value, "
            "IF( %s IN (SELECT UC.user_id FROM special_offer SP INNER JOIN user_cart UC ON UC.product_id = SP.product_id WHERE SP.product_id = special_offer.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM special_offer SP INNER JOIN user_wishlist WC ON WC.product_id = SP.product_id WHERE SP.product_id = special_offer.product_id ), 'Y','N') AS id1, "
            "categories.category_name, sub_categories.sub_category_name "
            "from special_offer INNER JOIN configuration_master ON special_offer.product_uom=configuration_master.config_id "
            "LEFT JOIN sub_categories ON sub_categories.sub_category_id = special_offer.sub_category_id "
            "INNER JOIN categories ON categories.category_id = special_offer.category_id",(args.userId, args.userId)) 
            result = cursor.fetchall()
            conn.commit()

        if result:
            data = []
            for r in result:
                cursor.execute("SELECT config_value FROM configuration_master WHERE config_id=%s", r[7])
                uom_value = cursor.fetchone()[0]
                data.append({
                    "offerId": r[0], 
                    "productId": r[1], 
                    "merchantId": r[2],
                    "categoryId": r[3], 
                    "productName": r[4],
                    "description": r[5], 
                    "productQuantity": float(r[6]),
                    "productUom":uom_value, 
                    "productUomId":r[7],
                    "productMrp": float(r[8]),
                    "productSellingPrice": float(r[9]), 
                    "productImage": r[10], 
                    "offerStartDate": myconverter(r[11]),
                    "offerEndDate": myconverter(r[12]), 
                    "productStatus": r[13],
                    "sub_category_id":r[18],
                    "cartExist":r[20],
                    "wishlistExist":r[21],
                    "categoryName":r[22],
                    "subCategoryName":r[23]
                    }) 
            return {
            'data': data,
            'statusCode': 1
        }
        else:
            return {
            'message': 'no data found',
            'statusCode': 0
            }
        
    # to update offers

    def put(self):
        try:
            args = parser.parse_args()

            # updatedBy = self.uid
            updatedBy = 1
            updatedDate = timestamp()

            conn = mysql.connect()
            cursor = conn.cursor()

            # cursor.execute("SELECT config_id FROM configuration_master WHERE config_value=%s",args.productUom)
            # uom = cursor.fetchone()[0]
            if not args.description:
                cursor.execute("update special_offer set product_id=%s, merchant_id=%s, category_id=%s, product_name=%s,"
                " product_qty=%s,product_uom=%s,mrp=%s, selling_price=%s,image_url=%s,offer_start_date=%s,"
                "offer_end_date=%s,product_status=%s,updated_by=%s,updated_date=%s, sub_category_id=%s where offer_id=%s",(
                    args.productId,
                    args.merchantId, 
                    args.categoryId, 
                    args.productName,  
                    args.productQuantity,
                    args.productUomId,
                    args.productMrp, 
                    args.productSellingPrice,
                    args.productImage, 
                    args.offerStartDate,
                    args.offerEndDate, 
                    args.productStatus,
                    updatedBy,
                    updatedDate,
                    args.subCategoryId,
                    args.offerId
                ))
                
            else:
            
                cursor.execute("update special_offer set product_id=%s, merchant_id=%s, category_id=%s, product_name=%s,"
                "description=%s, product_qty=%s,product_uom=%s,mrp=%s, selling_price=%s,image_url=%s,offer_start_date=%s,"
                "offer_end_date=%s,product_status=%s,updated_by=%s,updated_date=%s,sub_category_id=%s where offer_id=%s",(
                    args.productId,
                    args.merchantId, 
                    args.categoryId, 
                    args.productName, 
                    args.description, 
                    args.productQuantity,
                    args.productUomId,
                    args.productMrp, 
                    args.productSellingPrice,
                    args.productImage, 
                    args.offerStartDate,
                    args.offerEndDate, 
                    args.productStatus,
                    updatedBy,
                    updatedDate,
                    args.subCategoryId,
                    args.offerId
                ))
            result = cursor.rowcount

            conn.commit()
            conn.close()

            if result>=1:
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

    # to delete offers

    def delete(self):
        args = parser.parse_args()
        
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("UPDATE special_offer SET product_status='D' where offer_id=%s", args.offerId)
        result = cursor.rowcount

        conn.commit()
        conn.close()
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

class ActiveSpecialOffers(Resource):
    def __init__(self):
        super().__init__()
        parser.add_argument('merchantId', help='product id is required', required=False)
        parser.add_argument('userId', help='userId for the cart and wishlist filtering', required=False)

    def get(self):
        
        args = parser.parse_args()
        conn = mysql.connect()
        cursor = conn.cursor()
        if args.merchantId:
            cursor.execute("select special_offer. *,configuration_master.config_value, "
            "IF( %s IN (SELECT UC.user_id FROM special_offer SP INNER JOIN user_cart UC ON UC.product_id = SP.product_id WHERE SP.product_id = special_offer.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM special_offer SP INNER JOIN user_wishlist WC ON WC.product_id = SP.product_id WHERE SP.product_id = special_offer.product_id ), 'Y','N') AS id1, "
            "categories.category_name, sub_categories.sub_category_name "  
            "from special_offer INNER JOIN configuration_master ON special_offer.product_uom=configuration_master.config_id "
            "INNER JOIN categories ON categories.category_id = special_offer.category_id "
            "LEFT JOIN sub_categories ON sub_categories.sub_category_id = special_offer.sub_category_id "
            "where special_offer.merchant_id=%s AND special_offer.product_status='A'", (args.userId, args.userId, args.merchantId))
            result = cursor.fetchall()
        else:
            cursor.execute("select special_offer. *,configuration_master.config_value, "
            "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = special_offer.product_id ) , 'Y','N') AS id, "
            "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = special_offer.product_id ), 'Y','N') AS id1 "
            "categories.category_name, sub_categories.sub_category_name "
            "from special_offer INNER JOIN configuration_master ON special_offer.product_uom=configuration_master.config_id "
            "INNER JOIN categories ON categories.category_id = special_offer.category_id "
            "LEFT JOIN sub_categories ON sub_categories.sub_category_id = special_offer.sub_category_id "
            "WHERE special_offer.product_status='A'",(args.userId, args.userId)) 
            result = cursor.fetchall()
            conn.commit()

        if result:
            data = []
            for r in result:
                sampleDic = {}
                for i, j in enumerate(r):
                    sampleDic[i] = j
                pprint(sampleDic)
                cursor.execute("SELECT config_value FROM configuration_master WHERE config_id=%s", r[7])
                uom_value = cursor.fetchone()[0]
                data.append({
                    "offerId": r[0], 
                    "productId": r[1], 
                    "merchantId": r[2],
                    "categoryId": r[3], 
                    "productName": r[4],
                    "description": r[5], 
                    "productQuantity": float(r[6]),
                    "productUom":uom_value, 
                    "productUomId":r[7],
                    "productMrp": float(r[8]),
                    "productSellingPrice": float(r[9]), 
                    "productImage": r[10], 
                    "offerStartDate": myconverter(r[11]),
                    "offerEndDate": myconverter(r[12]), 
                    "productStatus": r[13],
                    "subCategoryId":r[18],
                    "cartExist":r[20],
                    "wishlistExist":r[21],
                    "categoryName":r[22],
                    "subCategoryName":r[23]
                    }) 
            return {
            'data': data,
            'statusCode': 1
        }
        else:
            return {
            'message': 'no data found',
            'statusCode': 0
            }