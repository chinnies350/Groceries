from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)
from app.libs import hashPassword, timestamp, myconverter

from bson import ObjectId

import json


parser = reqparse.RequestParser()
parser.add_argument('next', help='', required=False)


# gets the order delivered count

class Deliverycount(Resource):
    # @jwt_required
    def __init__(self):
        parser.add_argument(
            'merchantId', required=False)


    def get(self):
        args=parser.parse_args()

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            if args.merchantId:
                cursor.execute(
                "SELECT (SELECT COUNT(*) FROM paypre_ecom.orders where delivery_status='O' AND merchant_id=%s) AS ordered, "
                "(SELECT COUNT(*) FROM paypre_ecom.orders where delivery_status='D' AND merchant_id=%s) AS delivered, "
                "(SELECT COUNT(*) FROM paypre_ecom.orders where delivery_status='P' AND merchant_id=%s) AS progress, "
                "(SELECT COUNT(*) FROM paypre_ecom.orders where delivery_status='A' AND merchant_id=%s) AS accepted ",(args.merchantId,args.merchantId,args.merchantId,args.merchantId))

                result = cursor.fetchall()

                conn.commit()

                data = {}

                for i in result:
                    data = {
                    'orderedCount':i[0],
                    'deliveredCount':i[1],
                    'progressCount':i[2],
                    'accepted':i[3],
                    'statusCode':1
                }

                if data:

                    return data
                else:
                    return {
                        "message": "data not found",
                        "statusCode":0
                    }
            
            else:

                cursor.execute(
                "SELECT (SELECT COUNT(*) FROM paypre_ecom.orders where delivery_status='O') AS ordered, "
                "(SELECT COUNT(*) FROM paypre_ecom.orders where delivery_status='D') AS delivered, "
                "(SELECT COUNT(*) FROM paypre_ecom.orders where delivery_status='P') AS progress, "
                "(SELECT COUNT(*) FROM paypre_ecom.orders where delivery_status='A') AS accepted ")

                result = cursor.fetchall()

                conn.commit()

                data = {}

                for i in result:
                    data = {
                    'orderedCount':i[0],
                    'deliveredCount':i[1],
                    'progressCount':i[2],
                    'acceptedCount':i[3],
                    'statusCode':1
                }

                if data:

                    return data
                else:
                    return {
                        "message": "data not found",
                        "statusCode":0
                    }
        except Exception as e:
                return {"message": e, "statusCode": 0}


# to view top 10 selling products

class Topten(Resource):
    # @jwt_required
    def __init__(self):
        parser.add_argument('merchantId',  required=False)
        parser.add_argument("fromDate", required=False)
        parser.add_argument("toDate",required=False)

    def get(self):
        args = parser.parse_args()
        conn = mysql.connect()
        cursor = conn.cursor()
        
        if args.merchantId and args.merchantId == "0" and args.fromDate and args.toDate:
            cursor.execute("select distinct order_details.merchant_id, merchant_name from order_details LEFT JOIN merchant_details ON merchant_details.merchant_id = order_details.merchant_id")
            ids = cursor.fetchall()
            if ids:
                totalData = []
                for id in ids:
                    cursor.execute("select order_details.merchant_id, category_id,(select category_name from categories where categories.category_id=order_details.category_id) AS category_name, SUM(order_details.total_amount) " 
                        "from order_details "
                        "left join orders ON orders.order_id = order_details.order_id "
                        "where order_details.merchant_id=%s and delivered_time between %s and %s group by category_id ",(id[0], args.fromDate, args.toDate))
                    eachMerchant = cursor.fetchall()
                    if eachMerchant:
                        # eachMerchantDic = {}
                        eachMerchantList = []
                        for eachCategory in eachMerchant:
                            eachMerchantList.append({
                                "categoryId":eachCategory[1],
                                "categoryName":eachCategory[2],
                                "totalAmount":str(eachCategory[3])
                            })
                        totalData.append({
                            "merchantId":(id[0] if id else id),
                            "merchantName":(id[1] if id else id),
                            "categoryDetails": eachMerchantList
                        })
                    
                    else:
                        return {"message": "data not found", 
                        "statusCode": 0}
                return {
                    "data":totalData,
                    "statusCode":1
                }
            else:
                return {"message": "data not found", 
                        "statusCode": 0}
        elif args.merchantId and args.merchantId == "0" and not args.fromDate and not args.toDate:
            cursor.execute("select distinct order_details.merchant_id, merchant_name from order_details LEFT JOIN merchant_details ON merchant_details.merchant_id = order_details.merchant_id")
            ids = cursor.fetchall()
            if ids:
                totalData = []
                for id in ids:
                    cursor.execute("select merchant_id, category_id,(select category_name from categories where categories.category_id=order_details.category_id) AS category_name, SUM(total_amount) "
                                    "from order_details where merchant_id=%s group by category_id ",(id[0]))
                    eachMerchant = cursor.fetchall()
                    if eachMerchant:
                        # eachMerchantDic = {}
                        eachMerchantList = []
                        for eachCategory in eachMerchant:
                            eachMerchantList.append({
                                "categoryId":eachCategory[1],
                                "categoryName":eachCategory[2],
                                "totalAmount":str(eachCategory[3])
                            })
                        totalData.append({
                            "merchantId":(id[0] if id else id),
                            "merchantName":(id[1] if id else id),
                            "categoryDetails": eachMerchantList
                        })
                    
                    else:
                        return {"message": "data not found", 
                        "statusCode": 0}
                return {
                    "data":totalData,
                    "statusCode":1
                }
            else:
                return {"message": "data not found", 
                        "statusCode": 0}

            pass
        elif args.merchantId and args.fromDate and args.toDate:
             cursor.execute("select order_details.merchant_id, category_id,(select category_name from categories where categories.category_id=order_details.category_id) AS category_name, SUM(order_details.total_amount) " 
                        "from order_details "
                        "left join orders ON orders.order_id = order_details.order_id "
                        "where order_details.merchant_id=%s and delivered_time between %s and %s group by category_id ",(args.merchantId, args.fromDate, args.toDate))
        elif args.merchantId:
            cursor.execute("select merchant_id, category_id,(select category_name from categories where categories.category_id=order_details.category_id) AS category_name, SUM(total_amount) "
                                    "from order_details where merchant_id=%s group by category_id ",(args.merchantId))
        else:
            cursor.execute("select merchant_id, category_id,(select category_name from categories where categories.category_id=order_details.category_id) AS category_name, SUM(total_amount) "
                                    "from order_details group by category_id ")

        
        eachCategorys = cursor.fetchall()
        if eachCategorys:
            eachMerchantList = []
            for eachCategory in eachCategorys:
                eachMerchantList.append({
                    "merchantId":eachCategory[0],
                    "categoryId":eachCategory[1],
                    "categoryName":eachCategory[2],
                    "totalAmount":str(eachCategory[3])
                        })
            return {
                "data": eachMerchantList,
                "statusCode":1
            }
        else:
            return {"message": "data not found", 
                        "statusCode": 0}
    #         return {
    #             "data": data,
    #             "status code": 1
    #         }

    #     else :
    #         return {
    #             "message": "bulk order not found",
    #             "status code": 0
    #         }


class ToptenSellers(Resource):
    @jwt_required

    def get(self):

        try:

            conn = mysql.connect()
            cursor = conn.cursor()

            products=[]

            cursor.execute(
                    "SELECT orders.category_id, COUNT(orders.category_id), orders.seller_id, COUNT(orders.seller_id),orders.quantity,sellers.store_name FROM orders LEFT JOIN  sellers ON orders.seller_id = sellers.seller_id GROUP BY orders.category_id, orders.seller_id HAVING COUNT(orders.category_id) > 1 and COUNT(orders.seller_id) LIMIT 10")
            product_result = cursor.fetchall()

            conn.commit()

            for product in product_result:

                data = {"sellerId": product[2], "categoryId": product[0], "sellerName": product[5],
                             "Quantity": product[4] 
                            }

                products.append(data)


            return {
                'data':products,
                'statusCode':1
            }
        except Exception as e:
                return {"message": e, "statusCode": 0}

class ToptenSellersAmount(Resource):
    @jwt_required

    def get(self):

        try:

            conn = mysql.connect()
            cursor = conn.cursor()

            products=[]

            cursor.execute(
                    "SELECT orders.seller_id,  COUNT(orders.seller_id),orders.selling_price,orders.quantity, sellers.seller_name from orders left join sellers on sellers.seller_id=orders.seller_id group by orders.selling_price,orders.seller_id having max(orders.selling_price)>100 order by selling_price desc")
            product_result = cursor.fetchall()

            conn.commit()

            for product in product_result:

                data = {"sellerId": product[0], "sellingPrice": float(product[2]), "sellerName": product[4],"Quantity": product[3] }
                            

                products.append(data)


            return {
                'data':products,
                'statusCode':1
            }
        except Exception as e:
                return {"message": e, "statusCode": 0}
