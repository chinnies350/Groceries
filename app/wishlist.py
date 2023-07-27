from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)
from app.libs import hashPassword, timestamp, dateconvertor
import datetime
parser = reqparse.RequestParser()
parser.add_argument('next', help='', required=False)

# to manage wishlist operations

class Wishlist(Resource):
    # @jwt_required
    def __init__(self):

        parser.add_argument('userId', required=False)
        parser.add_argument('productId', required=False)
        parser.add_argument('wishlistId', required=False)
        parser.add_argument('productQuantity', required=False)
        # parser.add_argument('productUom', required=False) 
        parser.add_argument('productUomId', required=False)        
        parser.add_argument('merchantId', required=False)
        parser.add_argument('categoryId', required=False)
        parser.add_argument("specialOfferStatus", required=False)

        self.uid = get_jwt_identity()
        self.user = get_jwt_claims()     


    def post(self):
        args = parser.parse_args()
        # created_by = self.uid
        # userId= self.uid
        created_by = 1
        created_date = datetime.datetime.now()

        conn = mysql.connect()
        cursor = conn.cursor()

        # cursor.execute("SELECT config_id FROM configuration_master WHERE config_value=%s",args.productUom)
        # uom = cursor.fetchone()[0]

        cursor.execute("insert into user_wishlist(user_id, merchant_id, product_id, category_id, quantity,product_uom,"
        "created_by,created_date,special_offer_status) value (%s,%s,%s,%s,%s,%s,%s,%s,%s)",(
            args.userId,
            args.merchantId,
            args.productId,
            args.categoryId,
            args.productQuantity,
            args.productUomId,
            created_by,
            created_date,
            args.specialOfferStatus
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


    def get(self):
        try:

            args = parser.parse_args()

            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute("SELECT user_wishlist.*, products.product_name,products.description,products.mrp,products.selling_price,"
            "products.image_url,configuration_master.config_value,products.category_id FROM user_wishlist "
            "INNER JOIN products ON user_wishlist.product_id=products.product_id INNER JOIN configuration_master ON "
            "user_wishlist.product_uom = configuration_master.config_id where user_id=%s AND user_wishlist.merchant_id=%s ORDER BY user_wishlist.wishlist_id desc", (args.userId, args.merchantId))
            result = cursor.fetchall()

            print(result)

            conn.commit()
            wishlist = []

            if result:
                for row in result:
                    cursor.execute("SELECT config_value FROM configuration_master WHERE config_id=%s", row[6])
                    uom_value = cursor.fetchone()[0]
                    data = {
                        "wishlistId":row[0],                    
                        "userId":row[1],
                        "merchantId":row[2],    
                        "productId":row[3],
                        "categoryId":row[4],
                        "productQuantity":row[5],
                        "productUom":uom_value,
                        "productUomId":row[6],
                        "specialOfferStatus":row[11],
                        "productName":row[12],      
                        "description":row[13],
                        "productMrp":str(row[14]),
                        "productSellingPrice":str(row[15]),
                        "productImage":row[16],
                        }

                    wishlist.append(data)
                    
                return {
                    "data":wishlist,
                    "statusCode":1

                }

            else:
                return {
                    'message': "No data found!",
                    'statusCode':0

                }
        except Exception as e:
            print(e)


    def delete(self):

        args = parser.parse_args()
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM user_wishlist WHERE wishlist_id =%s",args.wishlistId)
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
