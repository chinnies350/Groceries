from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)

from pprint import pprint

parser = reqparse.RequestParser()
# parser.add_argument('next', help='', required=False)

# to manage cart details
class Cart(Resource):
    # @jwt_required
    def __init__(self):
        parser.add_argument('cartId', required=False)
        parser.add_argument('userId', required=False)
        parser.add_argument('productId', required=False)
        parser.add_argument('categoryId', required=False)
        parser.add_argument('productQuantity', required=False)
        # parser.add_argument('productUom', required=False)
        parser.add_argument('productUomId', required=False)
        parser.add_argument('noOfOrders', required=False)
        parser.add_argument('updatedDate', required=False)
        parser.add_argument('merchantId', required=False)
        parser.add_argument("specialOfferStatus", required=False)

        # self.uid = get_jwt_identity()
        # self.user = get_jwt_claims()

    # insert cart details
    def post(self):
        try:
            args = parser.parse_args()
            # print(f'args {args}')
            conn = mysql.connect()
            cursor = conn.cursor()

            # check the cart limit

            cursor.execute("SELECT count(*) from user_cart where user_id={}".format(args.userId))

            cart_count = cursor.fetchone()

            conn.commit()

            for cartcount in cart_count:
                if cartcount <= 50:
                    conn = mysql.connect()
                    cursor = conn.cursor()

                    try:
                        cursor.execute("SELECT cart_id from user_cart where user_id=? AND product_id=? AND "
                                       "category_id=?", (args.userId, args.productId, args.categoryId))
                        dat = cursor.fetchone()[0]
                    except:
                        dat = None

                    if dat:
                        cursor.execute("UPDATE user_cart SET no_of_order=no_of_order+1 WHERE cart_id=%s", dat)
                        result = cursor.rowcount
                        conn.commit()
                    else:
                        # try:
                        # cursor.execute("SELECT config_id FROM configuration_master WHERE config_value= ?",(args.productUom))
                        # print('cursor 0 executed')
                        # uom = cursor.fetchone()[0]
                        # print(f'uom {uom}')
                        # print(f'uom type {type(uom)}')
                        # print(f'uom type str{type(str(uom))}')
                        cursor.execute("INSERT INTO user_cart(user_id,merchant_id,product_id,category_id,quantity,product_uom,"
                                    "no_of_order, special_offer_status) VALUES (%s,%s,%s,%s,%s,%s,%s,'%s')" % (
                                            args.userId,
                                            args.merchantId,
                                            args.productId,
                                            args.categoryId,
                                            args.productQuantity,
                                            args.productUomId,
                                            args.noOfOrders,
                                            args.specialOfferStatus
                                            
                        ))
                        print('cursur executed')

                        result = cursor.rowcount

                        conn.commit()
                        conn.close()

                        # except Exception as e:
                        #     return {
                        #     'message': 'Enter valid data',
                        #     'statusCode': 0
                        # }


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
                else:
                    return {
                        'message': 'You have crossed your cart limit',
                        'statusCode': 0

                    }

        except Exception as e:
            print(e)
            return {"message": e, "statusCode": 0}

    # view cart details

    def get(self):

        args = parser.parse_args()
        print(f'args {args}')
        # data = {
        #     'userId': 101,
        #     'productId': 11,
        #     'categoryId': 10
        # }
        result = []

        conn = mysql.connect()
        cursor = conn.cursor()

        # cursor.execute("SELECT cart_id from user_cart where user_id=%s AND product_id=%s AND "
        #                "category_id=%s", (args.userId, args.productId, args.categoryId))
        # dat = cursor.fetchone()        
        # conn.commit()              

        cursor.execute("SELECT  user_cart.*, categories.category_name,products.product_name,products.product_qty, products.product_uom, "
        "IF (UPPER(special_offer_status)='Y',(SELECT mrp FROM special_offer WHERE special_offer.product_id = products.product_id limit 1),(SELECT mrp FROM products P WHERE P.product_id = products.product_id limit 1)) AS mrp, "
        "IF (UPPER(special_offer_status)='Y',(SELECT selling_price FROM special_offer WHERE special_offer.product_id = products.product_id limit 1),(SELECT selling_price FROM products P WHERE P.product_id = products.product_id limit 1)) AS selling_price, "
        "products.image_url,configuration_master.config_value, products.no_of_items "
        "as val, merchant_details.merchant_name, configuration_master.config_id FROM user_cart INNER JOIN categories ON user_cart.category_id=categories.category_id  "
        "INNER JOIN products ON user_cart.product_id=products.product_id INNER JOIN configuration_master ON "
        "user_cart.product_uom = configuration_master.config_id INNER JOIN merchant_details ON merchant_details.merchant_id=user_cart.merchant_id "
        "where user_id=%s AND user_cart.merchant_id=%s", (args.userId, args.merchantId))
        # "where user_id=%s union SELECT user_cart.*, categories.category_name,products.product_name, "
        # "products.product_qty,products.product_uom,products.mrp,products.selling_price,products.image_url, "
        # "configuration_master.config_value,'N' as val, merchant_details.merchant_name FROM user_cart INNER JOIN categories "
        # "ON user_cart.category_id=categories.category_id  INNER JOIN products ON user_cart.product_id=products.product_id "
        # "INNER JOIN configuration_master ON user_cart.product_uom = configuration_master.config_id INNER JOIN merchant_details "
        # "ON merchant_details.merchant_id=user_cart.merchant_id WHERE user_id=%s", (args.userId, args.userId))

        # cart_details = cursor.fetchone()
        # print(f'fetch one {cart_details}')

        cart_details = cursor.fetchall()

        conn.commit()

        for row in cart_details:
            sampleDic = {}

            for i, j in enumerate(row):
                sampleDic[i] = j  
            # print(f'sampleDic {sampleDic}')
            pprint(sampleDic)

            data = {
                "cartId":row[0],
                "userId": row[1],
                "merchantId":row[2],
                "productId": row[3],
                "categoryId": row[4],
                "productQuantity": row[5],
                "noOfOrders": str(row[7]),
                "productMrp": str(row[14]), 
                "productSellingPrice": str(row[15]),
                "productImage": row[16],
                "categoryName": row[10],
                "productName": row[11],
                "productUom": row[17],
                "productUomId": row[13],
                "specialOfferStatus":row[9],
                "noOfItems":row[18]
                
            }

            result.append(data)

        if result != []:
            return {

                "data": result,
                "statusCode": 1

            }
        else:
            return {
                "message": "No data found!",
                "statusCode": 0
            }

    # delete cart details
    def delete(self):
        try:

            args = parser.parse_args()          

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_cart WHERE cart_id =%s", args.cartId)

            result = cursor.rowcount

            conn.commit()
            conn.close()


            if result != 0:

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


# to view the cart count of particular users
class CartCount(Resource):
    # @jwt_required
    def __init__(self):

        parser.add_argument('userId', help='categoryId is required', required=False)

    def get(self):

        args = parser.parse_args()

        result = []

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT  COUNT(*) FROM user_cart where user_id=%s",args.userId)
        cart_details = cursor.fetchall()

        conn.commit()

        for row in cart_details:

            data = {"count": row[0]}
            result.append(data)

        if result:
            return {
                "data": result,
                "statusCode": 1

            }
        else:
            return {
                "message": "No data found",
                "statusCode": 0
            }
