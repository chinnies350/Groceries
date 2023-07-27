from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)
from app.libs import hashPassword, timestamp, myconverter

from bson import ObjectId

import json


parser = reqparse.RequestParser()

class Info(Resource):
    @jwt_required
    def __init__(self):
        parser.add_argument(
            'sellerId', help='clientId is required', required=False)



        self.uid = get_jwt_identity()

        self.user = get_jwt_claims()
    
    def get(self):
    
        data = parser.parse_args()

        conn = mysql.connect()
        cursor = conn.cursor()

           

                # cur.execute("SELECT product_name FROM products WHERE product_name LIKE 'jui%';")

        cursor.execute("select sellers.* , products.product_name, products.category_id from sellers INNER JOIN products ON products.seller_id = sellers.seller_id where sellers.seller_id='"+data['sellerId']+"' ")

        result = cursor.fetchall()
        conn.commit()

        
        products=[]

        if result!=():

            for product in result:
                data = {"sellerId":product[0],"sellerName":product[1] ,"email":product[2], "contact":product[3],"password":product[4],"pincode":product[5],"Address":product[6],"panCardName":product[7],"panCardNumber":product[8],"accountName":product[9],"accountNumber":product[10],"ifscNumber":product[11],"storeName":product[12],"storeAddress":product[13],"productName":product[21],"categoryId":product[22]}

                products.append(data)


                conn.commit()

            


            return {

                            'data': products,
                            'statusCode': 1
                        }
        else:
            return {

                    'data': 'no data',
                    'statusCode': 1
                }
            

        

class SellerTransactions(Resource):
    @jwt_required
    def __init__(self):
        parser.add_argument(
            'from', help='clientId is required', required=False)
        parser.add_argument(
            'to', help='clientId is required', required=False)
        parser.add_argument(
            'sellerId', help='clientId is required', required=False)



        self.uid = get_jwt_identity()

        self.user = get_jwt_claims()

    def post(self):
        
        data = parser.parse_args()

        conn = mysql.connect()
        cursor = conn.cursor()
        print(data['from'])
        print(data['to'])
        print(data['sellerId'])
            

        cursor.execute("SELECT * FROM orders WHERE delivered_time BETWEEN '"+data['from']+"'  AND '"+data['to']+"' and seller_id='"+data['sellerId']+"'")

        result = cursor.fetchall()
        print(result)
        products=[]

        for product in result:
            data = {"orderId":product[0],"sellingPrice":float(product[5]) ,"quantity":product[3],"numberofOrders":product[6], "netAmount":float(product[10]), "transactionStatus":product[17],"sellerId":product[34]}

            products.append(data)


        conn.commit()

        if data!=[]:


            return {

                'data': products,
                'statusCode': 1
                    }
        else:
            return {

                'data': 'no data',
                'statusCode': 1
            }


    def get(self):
        data = parser.parse_args()
        conn = mysql.connect()
        cursor = conn.cursor()

            

        cursor.execute("SELECT sellers.seller_id,sellers.seller_name, COUNT(*) as 'total_transactions',sum(total_amount) as total_amount FROM orders inner join sellers on sellers.seller_id=orders.seller_id GROUP BY seller_id HAVING COUNT(*) > 1 order by seller_id")
    
        result = cursor.fetchall()
        print(result)
        products=[]

        for product in result:
            data = {"sellerId":product[0],"sellerName":product[1],"totalTransactions":product[2],"totalAmount":float(product[3])}

            products.append(data)


        conn.commit()

        if data!=[]:


            return {

                'data': products,
                'statusCode': 1
                    }
        else:
            return {

                'data': 'no data',
                'statusCode': 1
            }
            

       
