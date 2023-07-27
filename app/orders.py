import datetime
from flask import jsonify
from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)
from app.libs import hashPassword, timestamp, timeconverter, myconverter
from bson import ObjectId
import json
import requests
from flask import Flask
from flask_mail import Mail, Message
from pprint import pprint

parser = reqparse.RequestParser()
parser.add_argument('next', help='', required=False)

# mail configuration :::::::::::::::::::;

app = Flask(__name__)

MUSERNAME = 'apps@prematix.com'
MPASSWORD = 'Preapps123'

app.config.update(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=MUSERNAME,
    MAIL_DEFAULT_SENDER=MUSERNAME,
    MAIL_PASSWORD=MPASSWORD
)
mail = Mail(app)

# :::::::::::::::::::::::::::::


def date_convertor(date):
    year = date[:4]
    month = date[5:7]
    day = date[8:10]
    time = date[11:]
    time = datetime.datetime.strptime(time, "%H:%M:%S").strftime("%I:%M %p")
    date = day + '/' + month + '/' + year + " " + time
    return date


def sms_notification(mobile, username, delivery_time, orderid, ordertype, deliver_loc=None):
    
    if ordertype == 'OP':
        
        message = "Dear " + username + ", Your Order (Id: " + \
                  str(orderid)[1:-1] + ") has been placed Successfully " \
                                       "and will be Delivered to " \
                                       "you on or before " + date_convertor(delivery_time) + ". Thank you. "
        admin_message = username + ", placed an order at " + date_convertor(delivery_time) + " and " \
                                                                                             "the delivery address " \
                                                                                             "is " + deliver_loc
    else:
        message = "Dear " + username + ", Your Order (Id: " + \
                  str(orderid)[1:-1] + ") has been Delivered Successfully. " \
                    "to enter the valuable Feedback Plaese Enter this link " \
                                       "Thank you for Choosing our Service. " \
                                       "Have a Good Day. "
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT config_value from configuration_master where config_name='smsURL'")
    smsURL = cursor.fetchone()
    conn.commit()
    sms = requests.post(smsURL[0]+str(mobile)+'&msg='+message+'')

    if deliver_loc:
        cursor.execute("SELECT primary_phone from users where user_role='A'")
        mobile_num = cursor.fetchone()[0]
        admin_sms = requests.post(smsURL[0] + str(mobile_num) + '&msg=' + admin_message + '')

    return 'ok'


def mail_notification(userid, username, delivery_time, orderid, ordertype):
    if ordertype == 'OP':
        message = "Dear " + username + ", \n" + "\t Your Order (Id: " + \
                  str(orderid)[1:-1] + ") has been placed Successfully " \
                                       "and will be Delivered to " \
                                       "you on or before " + date_convertor(delivery_time) + ". Thank you. "

        heading = "Order Placement Confirmation Notification"
    else:
        message = "Dear " + username + ", \n" + "\t Your Order (Id: " + \
                  str(orderid)[1:-1] + ") has been Delivered Successfully. " \
                                       "Thank you for Choosing our Service. Have a Good Day. "

        heading = "Order Delivery Confirmation Notification"

    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT email from users where user_id=%s", str(userid))
    email_id = cursor.fetchone()[0]

    try:
        with app.app_context():
            msg = Message(
                heading,
                recipients=[email_id]
            )
            msg.body = message
            mail.send(msg)
    except:
        pass

    return 'ok'


class Orders(Resource):
    # @jwt_required
    def __init__(self):

        parser.add_argument('orderId',  required=False)
        parser.add_argument('merchantId',  required=False)
        parser.add_argument('categoryId',  required=False)
        parser.add_argument('productId',  required=False)
        parser.add_argument('productQuantity',  required=False)
        # parser.add_argument('productUom',  required=False)
        parser.add_argument('productUomId',  required=False)
        parser.add_argument('productSellingPrice', required=False)
        parser.add_argument('noOfOrders', required=False)
        parser.add_argument('totalAmount',  required=False)
        parser.add_argument('gstPercentage',  required=False)
        parser.add_argument('gstAmount',  required=False)
        parser.add_argument('netAmount',  required=False)
        parser.add_argument('delName', required=False)
        parser.add_argument('delAddress',  required=False)
        parser.add_argument('delCity',  required=False)
        parser.add_argument('delPincode', required=False)
        parser.add_argument('delPhone',  required=False)
        parser.add_argument('paymentMode', required=False)
        parser.add_argument('transactionStatus',  required=False)
        parser.add_argument('failureReason', required=False)
        parser.add_argument('shippingCharge',  required=False)
        parser.add_argument('cancellationFlag', required=False)
        parser.add_argument('cancellationReason', required=False)
        parser.add_argument('stdDeliveryTime', required=False)
        parser.add_argument('preDeliveryTime',  required=False)
        parser.add_argument('specialOffer', required=False)
        parser.add_argument('deliveryStatus',  required=False)
        parser.add_argument('deliveredTime',  required=False)
        parser.add_argument('deliveredBy',  required=False)
        parser.add_argument('deliveredTo',  required=False)
        parser.add_argument('userId', required=False)
        parser.add_argument('updatedBy',  required=False)
        parser.add_argument('updatedDate',  required=False)
        parser.add_argument('assignedTo', required=False)

        self.uid = get_jwt_identity()

        self.user = get_jwt_claims()

    # to add orders to a particular user

    def post(self):
        try:

            args = parser.parse_args()
            conn = mysql.connect()
            cursor = conn.cursor()

            # created_by = self.uid
            # created_date = timestamp()
            created_by = 1
            created_date = datetime.datetime.now()




            # if args['paymentMode']=='Wallet':
            #     pm='WP'
            # elif args['paymentMode'] == 'Net Banking':
            #     pm='NET'
            # elif args['paymentMode'] == 'DebitCard':
            #     pm='DEB'
            # elif args['paymentMode'] == 'CashCard':
            #     pm='CC'
            # elif args['paymentMode'] == 'CreditCard':
            #     pm='CRE'
            # else:
            #     pm=args['paymentMode']
            # cursor.execute("SELECT config_id FROM configuration_master WHERE config_value=%s",args.productUom)
            # uom = cursor.fetchone()[0]

            cursor.execute("insert into orders(merchant_id, total_amount,gst_percentage,gst_amount,net_amount,del_name,del_address,del_city, "
                           "del_pincode,del_phone,payment_mode,transaction_status,failure_reason,shipping_charge, "
                           "cancellation_flag,cancellation_reason,std_delivery_time,preferred_delivery_time, "
                           "special_offer,delivery_status,delivered_time,delivered_by,delivered_to,user_id, "
                           "created_by,created_date,assigned_to) value (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
                           "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(
                               args.merchantId,
                               args.totalAmount,
                               args.gstPercentage,
                               args.gstAmount,
                               args.netAmount,
                               args.delName,
                               args.delAddress,
                               args.delCity,
                               args.delPincode,
                               args.delPhone,
                               "COD",
                               args.transactionStatus,
                               args.failureReason,
                               args.shippingCharge,
                               args.cancellationFlag,
                               args.cancellationReason,
                               args.stdDeliveryTime,
                               args.preDeliveryTime,
                               args.specialOffer,
                               args.deliveryStatus,
                               args.deliveredTime,
                               args.deliveredBy,
                               args.deliveredTo,
                               args.userId,
                               created_by,
                               created_date,
                               args.assignedTo
                               ))

            result = cursor.rowcount
            if result >= 1:
                cursor.execute("SELECT no_of_items FROM products WHERE product_id=%s",(args.productId))
                noofItem = cursor.fetchone()[0]-1
                cursor.execute("UPDATE products SET no_of_items=%s WHERE product_id=%s",(noofItem, args.productId))
                cursor.execute("SELECT order_id FROM paypre_ecom.orders ORDER BY order_id DESC")
                a = cursor.fetchone()[0]
                cursor.execute("INSERT INTO order_details(merchant_id, category_id, no_of_orders, product_id, product_uom_id, product_quantity, "
                "product_selling_price, special_offer, total_amount, order_id)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(
                    args.merchantId,
                    args.categoryId,
                    args.noOfOrders, 
                    args.productId, 
                    args.productUomId, 
                    args.productQuantity, 
                    args.productSellingPrice,
                    args.specialOffer, 
                    args.totalAmount, 
                    a))
                
                result = cursor.rowcount
                

            cursor.execute("SELECT LAST_INSERT_ID()")
            cursor.fetchall()

            cursor.execute("DELETE FROM user_cart WHERE product_id =%s and user_id=%s",(args.productId,args.userId))
            conn.commit()
            conn.close()

            if result >= 1:

                return {
                        'message': 'success',
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
    
    def put(self):
        conn = mysql.connect()
        cursor = conn.cursor()
        try:
            args = parser.parse_args()
            
            if args.transactionStatus:
                cursor.execute("UPDATE orders SET transaction_status=%s WHERE order_id=%s", (args.transactionStatus, args.orderId))
                conn.commit()
                conn.close()

                if cursor.rowcount >=1:
                    return{
                        "status":1,
                        "message":"updated successfully!"
                        
                    }

                else:
                    return{
                        "status":0,
                        "message":"Data is not updated!"
                    }

        except Exception as e:
            print(e)
            return{
                        "status":0,
                        "message":"Data is not updated!"
                    }

    # to get all the orders
    def get(self):
        conn = mysql.connect()
        cursor = conn.cursor()
        args = parser.parse_args()
        print(f'args {args}')
        if args.userId:
            cursor.execute("SELECT distinct orders.order_id FROM orders inner join order_details on order_details.order_id = orders.order_id where orders.user_id=%s and orders.merchant_id= %s ",(args.userId, args.merchantId))
        elif args.deliveryStatus and args.merchantId:
            cursor.execute("SELECT distinct orders.order_id FROM orders inner join order_details on order_details.order_id = orders.order_id where orders.delivery_status=%s and orders.merchant_id= %s ",(args.deliveryStatus, args.merchantId))

        elif args.orderId:
            cursor.execute("SELECT distinct orders.order_id FROM orders inner join order_details on order_details.order_id = orders.order_id where orders.order_id=%s and orders.merchant_id= %s ",(args.orderId, args.merchantId))
        elif args.merchantId:
            cursor.execute("SELECT distinct orders.order_id FROM orders inner join order_details on order_details.order_id = orders.order_id WHERE orders.merchant_id=%s",(args.merchantId))
        else:
            cursor.execute("SELECT distinct orders.order_id FROM orders inner join order_details on order_details.order_id = orders.order_id")
        ids = cursor.fetchall()
        print(f'ids {ids}')
        if ids:
            data = []
            for id in ids:
                # print(f'id {id}')
                cursor.execute("SELECT * ,users.email FROM orders inner join users on users.merchant_id = orders.merchant_id WHERE order_id=%s  ",(id))
                uniqueData = cursor.fetchone()
                cursor.execute("SELECT user_name FROM users WHERE user_id=%s",(uniqueData[23]))
                userName = cursor.fetchone()
                
                # print(f'dic {dic}')
                # print(f'uniqueData {uniqueData}')
                productList = []
                cursor.execute("SELECT * FROM order_details  WHERE order_id=%s", (id))
                productData = cursor.fetchall()
                totalAmount = 0
                for eachProduct in productData:
                    totalAmount += eachProduct[9]
                    cursor.execute("SELECT P.product_name, P.image_url, C.category_name, CM.config_value FROM products P LEFT JOIN categories C ON P.category_id = C.category_id "
                    "LEFT JOIN configuration_master CM ON P.product_uom = CM.config_id WHERE P.product_id = %s",(eachProduct[4]))
                    allNames = cursor.fetchone()
                    # print(f'all name {allNames}')
                    # print(f'product ID {eachProduct[4]}, categoryID {eachProduct[2]} merchantID {eachProduct[1]}')
                    productName = productImg = categoryName = productUom = "no value available"
                    # print(f' all name condition {allNames}')
                    if allNames:
                        # print(f' came inside all name')
                        productName = allNames[0]
                        productImg = allNames[1]
                        categoryName = allNames[2]
                        productUom = allNames[3]
                    
                    productList.append({
                        "merchantId":str(eachProduct[1]),
                        "categoryId":str(eachProduct[2]),
                        "categoryName":str(categoryName),
                        "noOfOrder":str(eachProduct[3]),
                        "productId":str(eachProduct[4]),
                        "productName":str(productName),
                        "productImg": str(productImg),
                        "productUomId":str(eachProduct[5]),
                        "productUom": str(productUom),
                        "productQuantity":str(eachProduct[6]),
                        "productSellingPrice":str(eachProduct[7]),
                        "specialOffer":str(eachProduct[8]),
                        "totalAmount":str(eachProduct[9])
                    })
                    # else:
                    #     return {
                    #         "message": "no data available",
                    #         "status code": 0
                    #     }
                
                data.append({
                    "orderId":str(uniqueData[0]),
                    "total_amount":str(uniqueData[2]),
                    "gst_percentage":str(uniqueData[3]),
                    "gst_amount":str(uniqueData[4]),
                    "net_amount":str(uniqueData[5]),
                    "del_name":str(uniqueData[6]),
                    "del_address":str(uniqueData[7]),
                    "del_city":str(uniqueData[8]),
                    "del_pincode":str(uniqueData[9]),
                    "del_phone":str(uniqueData[10]),
                    "payment_mode":str(uniqueData[11]),
                    "transaction_status":str(uniqueData[12]),
                    "failure_reason":str(uniqueData[13]),
                    "shipping_charge":str(uniqueData[14]),
                    "cancellation_flag":str(uniqueData[15]),
                    "cancellation_reason":str(uniqueData[16]),
                    "stdDeliveryTime":str(uniqueData[17]),
                    "preDeliveryTime":str(uniqueData[18]),
                    "deliveryStatus":str(uniqueData[20]),
                    "deliveredTime":str(uniqueData[21]),
                    "deliveredBy":str(uniqueData[29]),
                    "deliveredTo":str(uniqueData[22]),
                    "userId":str(uniqueData[23]),
                    "orderDate": str(uniqueData[25]),
                    "email":str(uniqueData[27]),
                    "assignedTo":str(uniqueData[28]),
                    "userName":(userName[0] if userName else userName),
                    "products":productList
                })
                

            return {
                "data": data,
                "status code": 1
            }

        else :
            return {
                "message": "bulk order not found",
                "status code": 0
            }
#         gets the delivery details


class Deliverydetails(Resource):
    # @jwt_required
    def __init__(self):

        parser.add_argument('deliveryStatus', required=False)
        parser.add_argument('deliveredTime', required=False)
        parser.add_argument('deliveredTo', required=False)
        parser.add_argument('userId', required=False)
        parser.add_argument('orderId', required=False)
        parser.add_argument('assignedTo', required=False)

        self.uid = get_jwt_identity()
        self.user = get_jwt_claims()

    def put(self):
        try:

            args = parser.parse_args()
            updated_by = 1
            updated_date = datetime.datetime.now()
            conn = mysql.connect()
            cursor = conn.cursor()
            if args.deliveryStatus.lower() == 'd':
                print('came to if condition')
                cursor.execute("update orders set delivery_status=%s, delivered_time=%s, delivered_to=%s,updated_by=%s,updated_date=%s, assigned_to=%s where user_id=%s and order_id=%s",(
                    args.deliveryStatus,
                    args.deliveredTime,
                    args.deliveredTo, 
                    updated_by,
                    updated_date,
                    args.assignedTo,
                    args.userId,
                    args.orderId
                ))
            else:
                cursor.execute("update orders set delivery_status=%s, updated_by=%s,updated_date=%s, assigned_to=%s where user_id=%s and order_id=%s",(
                    args.deliveryStatus, 
                    updated_by,
                    updated_date,
                    args.assignedTo,
                    args.userId,
                    args.orderId
                ))

            

            result = cursor.rowcount
            print('first query executed')
            cursor.execute("select A.del_name, A.del_phone, A.preferred_delivery_time, B.email, B.user_id "
                            " from orders AS A join users AS B on B.user_id=A.user_id "
                           "where A.order_id=%s", (args.orderId))
            order_data = cursor.fetchone()
            print('second query executed')

            del_name = order_data[0]
            del_phone = order_data[1]
            del_date = order_data[2]
            email = order_data[3]
            userid = order_data[4]
            conn.commit()
            if result != 0:
                print('if result ')
                sms_notification(del_phone, del_name, del_date, args.orderId, 'OD')
                mail_notification(userid, del_name, del_date, args.orderId, 'OD')

                return {

                    'message': 'updated successfully',
                    'statusCode': 1,
                    "data":args

                }

            else:

                return {

                    'message': 'Data is not updated',
                    'statusCode': 0

                }
        except Exception as e:
            print(e)
            return {

                "message": e,
                "statusCode": 0
            }


# to get the payment order

class Paymentorder(Resource):
    # @jwt_required

    def get(self):
        try:

            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM paypre_ecom.orders ORDER BY order_id DESC LIMIT 1")

            result = cursor.fetchall()
            conn.commit()

            data=[]
            # print(data,"dta")
            if result:             
                for row in result:

                    data_dt={"orderId":row[0]+1}
                    data.append(data_dt)

                return {
                    'data': data,
                    'statusCode': 1
                }
            else:
                return {
                    'data': 'Data is not updated',
                    'statusCode': 0
                }
        except Exception as e:
            print(e)
            return {
                "message": e,
                "statusCode": 0
            }


# to list pending order list
class Pendinglist(Resource):
    # @jwt_required
    def __init__(self):
        parser.add_argument('deliveryStatus', help='description is required', required=False)
        parser.add_argument('merchantId', help='description is required', required=False)

    def get(self):
        args = parser.parse_args()

        if args.deliveryStatus or args.merchantId:

            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute("SELECT orders.*, categories.category_name, products.product_name,products.image_url,"
            "configuration_master.config_name FROM orders INNER JOIN categories ON orders.category_id = categories.category_id "
            " INNER JOIN products ON orders.product_id = products.product_id INNER JOIN configuration_master"
            " ON orders.product_uom = configuration_master.config_id "
            "where delivery_status=%s and orders.merchant_id=%s",(args.deliveryStatus,args.merchantId))

            result = cursor.fetchall()

            conn.commit()

            user = []

            if result:
                for row in result:

                    data = {
                            "orderId": row[0], 
                            "merchantId":row[1],
                            "categoryId": row[2],
                            "productId": row[3],
                            "productQuantity": float(row[4]),
                            "productUom":row[5],
                            "productSellingPrice": float(row[6]),
                            "noOfOrders": int(row[7]), 
                            "totalAmount": float(row[8]),
                            "gstPercentage": float(row[9]),
                            "gstAmount": float(row[10]), 
                            "netAmount": float(row[11]), 
                            "delName": (row[12]),
                            "delAddress": row[13], 
                            "delCity": row[14],
                            "delPincode": row[15],
                            "delPhone": row[16], 
                            "paymentMode": row[17],
                            "transactionStatus": row[18],
                            "failureReason": row[19], 
                            "shippingCharge": float(row[20]),
                            "cancellationFlag": row[21],
                            "cancellationReason": row[22],
                            "stdDeliveryTime": myconverter(row[23]), 
                            "preferedDeliveryTime": myconverter(row[24]),
                            "specialOffer": row[25],
                            "deliveryStatus": row[26],
                            "deliveredTime": myconverter(row[27]),
                            "deliveredBy": row[28], 
                            "deliveredTo": row[29],
                            "userId": int(row[30]),
                            "categoryName": row[35], 
                            "productName": row[36],
                            "productImage": row[37],
                            "configName":row[38]

                        }

                    user.append(data)

                return {
                    "data": user,
                    "statusCode": 1
                }
            else:
                return {
                'message': 'data not found',
                'statusCode': 0
                }
        else:
            return {
                'message': 'data not found',
                'statusCode': 0
                }


# to upload bulk orders


class BulkOrder(Resource):
    # @jwt_required
    def __init__(self):
        parser.add_argument('categoryId', required=False)
        parser.add_argument('productId', required=False)
        parser.add_argument('productQuantity', required=False)
        parser.add_argument('productUom', required=False)
        parser.add_argument('productUom', required=False)
        
        parser.add_argument('productSellingPrice', required=False)
        parser.add_argument('noOfOrders', required=False)
        parser.add_argument('totalAmount', required=False)

        
        parser.add_argument('products', type=dict, action='append', required=False)
        parser.add_argument('gstPercentage', required=False)
        parser.add_argument('gstAmount', required=False)
        parser.add_argument('netAmount', required=False)
        parser.add_argument('delName', required=False)
        parser.add_argument('totalAmount', required=False)
        parser.add_argument('delAddress', required=False)
        parser.add_argument('delCity', required=False)
        parser.add_argument('delPincode', required=False)
        parser.add_argument('delPhone', required=False)
        parser.add_argument('paymentMode', required=False)
        parser.add_argument('transactionStatus', required=False)
        parser.add_argument('failureReason', required=False)
        parser.add_argument('shippingCharge', required=False)
        parser.add_argument('cancellationFlag', required=False)
        parser.add_argument('cancellationReason', required=False)
        parser.add_argument('stdDeliveryTime', required=False)
        parser.add_argument('preDeliveryTime', required=False)
        parser.add_argument('specialOffer', required=False)
        parser.add_argument('deliveryStatus', required=False)
        parser.add_argument('deliveredTime', required=False)
        parser.add_argument('deliveredBy', required=False)
        parser.add_argument('deliveredTo', required=False)
        parser.add_argument('userId', required=False)
        parser.add_argument('updatedBy', required=False)
        parser.add_argument('updatedDate', required=False)
        parser.add_argument('del_name', required=False
        )
        self.uid = get_jwt_identity()
        self.user = get_jwt_claims()

    def post(self):

        # try:
            conn = mysql.connect()
            cursor = conn.cursor()

            args = parser.parse_args()
            print("data", args)
            created_by = 1

            created_date = datetime.datetime.now()

            order_id = []
            print(order_id,"orderid")
            result_data = []
            print(result_data,"resultdata")
            if args['paymentMode'] == 'Wallet':
                pm = 'WP'
            elif args['paymentMode'] == 'Net Banking':
                pm = 'NET'
            elif args['paymentMode'] == 'DebitCard':
                pm = 'DEB'
            elif args['paymentMode'] == 'CashCard':
                pm = 'CC'
            elif args['paymentMode'] == 'CreditCard':
                pm = 'CRE'
            elif args['paymentMode'] == 'Online Payment':
                pm = 'OP'
            else:
                pm = args['paymentMode']
            
            for i,elements in enumerate(args.products):
                print(f'i {i}')

                cursor.execute("insert into orders(category_id,product_id,quantity,product_uom,selling_price, no_of_order,"
                    "total_amount,gst_percentage,gst_amount,net_amount,del_name,del_address,del_city,del_pincode,"
                    "del_phone,payment_mode,transaction_status,failure_reason,shipping_charge,cancellation_flag,"
                    "cancellation_reason,std_delivery_time,preferred_delivery_time, special_offer,delivery_status,"
                    "delivered_time,delivered_by,delivered_to,user_id,created_by,created_date, merchant_id) "
                    "values (   %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        elements['categoryId'],
                        elements['productId'], 
                        elements['productQuantity'], 
                        elements['productUom'], 
                        elements['productSellingPrice'],
                        elements['noOfOrders'], 
                        elements['totalAmount'], 
                        args.gstPercentage, 
                        args.gstAmount,
                        args.netAmount, 
                        args.delName, 
                        args.delAddress, 
                        args.delCity, 
                        args.delPincode,
                        args.delPhone, 
                        pm, 
                        args.transactionStatus, 
                        args.failureReason,
                        args.shippingCharge, 
                        args.cancellationFlag, 
                        args.cancellationReason,
                        args.stdDeliveryTime, 
                        args.preDeliveryTime, 
                        elements['specialOffer'], 
                        args.deliveryStatus,
                        args.deliveredTime, 
                        args.deliveredBy, 
                        args.deliveredTo, 
                        args.userId,    
                        created_by,
                        created_date, 
                        elements['merchantId']
                        ))
                
                result = cursor.rowcount
                print(result,"..............")

                a = cursor.execute("SELECT LAST_INSERT_ID()")
                
                b = cursor.fetchone()                   
                cursor.execute(
                    "DELETE FROM user_cart WHERE product_id ='" + str(elements['productId']) + "' and user_id = '" + str(args[
                        'userId']) + "'")

                for bb in b:
                    order_id.append(bb)

                
            conn.commit()

            dt = {
                "orderId": order_id,
                "netAmount": args['netAmount'],
                "gstPercentage": args['gstPercentage'],
                "gstAmount": args['gstAmount'],
                "orderDate": str(created_date)
            }
            
            result_data.append(dt)

                            
            if result != 0:
                sms_notification(args['delPhone'], args['delName'], args['preDeliveryTime'], order_id, 'OP', args['delAddress'])
                mail_notification(args['userId'], args['delName'], args['preDeliveryTime'], order_id, 'OP')
                return {
                        'message': 'success',
                        'statusCode': 1,
                        'data': result_data
                    }
            else:
                return {
                        'message': 'Data is not Inserted',
                        'statusCode': 0
                }

        # except Exception as e:
        #     print("exception", e)
        #     return {"message": str(e), "statusCode": 0}


class MerchantOrders(Resource):
    # @jwt_required
    def __init__(self):
        parser.add_argument('merchantId', required=False)
        self.uid = get_jwt_identity()
        self.user = get_jwt_claims()
    
    def get(self):
        args = parser.parse_args()
        conn = mysql.connect()
        cursor = conn.cursor()


        cursor.execute("SELECT orders. *, categories.category_name, products.product_name,products.image_url,"
                               "configuration_master.config_value FROM orders INNER JOIN categories ON "
                               "orders.category_id = categories.category_id INNER JOIN products ON "
                               "orders.product_id = products.product_id INNER JOIN configuration_master ON "
                               "orders.product_uom = configuration_master.config_id where orders.merchant_id=%s order by order_id DESC",args.merchantId)

        result = cursor.fetchall()

        conn.commit()
        user = []
        if result :
            for row in result:
                data = {"orderId": row[0], 
                        "merchantId":row[1],
                        "categoryId": row[2],
                        "productId": row[3],
                        "productQuantity": float(row[4]),
                        "productUom":row[5],
                        "productSellingPrice": float(row[6]),
                        "noOfOrder": int(row[7]), 
                        "totalAmount": float(row[8]),
                        "gstPercentage": float(row[9]),
                        "gstAmount": float(row[10]), 
                        "netAmount": float(row[11]), 
                        "delName": (row[12]),
                        "delAddress": row[13], 
                        "delCity": row[14],
                        "delPincode": row[15],
                        "delPhone": row[16], 
                        "paymentMode": row[17],
                        "transactionStatus": row[18],
                        "failureReason": row[19], 
                        "shippingCharge": float(row[20]),
                        "cancellationFlag": row[21],
                        "cancellationReason": row[22],
                        "stdDeliveryTime": myconverter(row[23]), 
                        "preferedDeliveryTime": myconverter(row[24]),
                        "specialOffer": row[25],
                        "deliveryStatus": row[26],
                        "deliveredTime": myconverter(row[27]),
                        "deliveredBy": row[28], 
                        "deliveredTo": row[29],
                        "userId": int(row[30]),
                        "categoryName": row[35], 
                        "productName": row[36],
                        "productImage": row[37],
                        "configValue":row[38]
                        }

                user.append(data)

            return {
                "data": user,
                "statusCode": 1
                }
        else:
            return {
                'data': user,
                'statusCode': 0
         }

class TodayTransactionCount(Resource):
    def get(self):
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("select count(transaction_status) from orders where delivered_time=curdate() and delivery_status='Y'")
        result = cursor.fetchall()

        conn.commit()

        data = []

        for r in result:

            data_dt = {"todayTransactionCount":r[0]}
            data.append(data_dt)

        return {

            'data': data,
            'statusCode': 1

        }

class TodayTransactionList(Resource):
    def get(self):
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("select * from orders where delivered_time=curdate() and delivery_status='Y'")
        result = cursor.fetchall()

        conn.commit()

        data = []
    
        for row in result:

            data_dt = {"orderId": row[0], 
                        "merchantId":row[1],
                        "categoryId": row[2],
                        "productId": row[3],
                        "productQuantity": float(row[4]),
                        "productUom":row[5],
                        "productSellingPrice": float(row[6]),
                        "noOfOrder": int(row[7]), 
                        "totalAmount": float(row[8]),
                        "gstPercentage": float(row[9]),
                        "gstAmount": float(row[10]), 
                        "netAmount": float(row[11]), 
                        "delName": (row[12]),
                        "delAddress": row[13], 
                        "delCity": row[14],
                        "delPincode": row[15],
                        "delPhone": row[16], 
                        "paymentMode": row[17],
                        "transactionStatus": row[18],
                        "failureReason": row[19], 
                        "shippingCharge": float(row[20]),
                        "cancellationFlag": row[21],
                        "cancellationReason": row[22],
                        "stdDeliveryTime": myconverter(row[23]), 
                        "preferedDeliveryTime": myconverter(row[24]),
                        "specialOffer": row[25],
                        "deliveryStatus": row[26],
                        "deliveredTime": myconverter(row[27]),
                        "deliveredBy": row[28], 
                        "deliveredTo": row[29],
                        "userId": int(row[30]),
                        }   
            data.append(data_dt)

        return {

            'data': data,
            'statusCode': 1

        }


class TodayPayment(Resource): 
    def get(self):
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT sum(total_amount) FROM paypre_ecom.orders where delivered_time=curdate() and delivery_status='Y'")
        result = cursor.fetchall()

        conn.commit()

        data = []

        for row in result:

            data_dt = {"TodayPayment": float(row[0])}
            data.append(data_dt)

        return {

            'data': data,
            'statusCode': 1

        }       




class LargeOrders(Resource):
    
    def __init__(self):
        parser.add_argument('categoryId', required=False)
        parser.add_argument('productId', required=False)
        parser.add_argument('productQuantity', required=False)
        parser.add_argument('productUom', required=False)
        parser.add_argument('productUom', required=False)
        parser.add_argument('productSellingPrice', required=False)
        parser.add_argument('noOfOrders', required=False)
        parser.add_argument('totalAmount', required=False)
        parser.add_argument('products', type=dict, action='append', required=False)
        parser.add_argument('gstPercentage', required=False)
        parser.add_argument('gstAmount', required=False)
        parser.add_argument('netAmount', required=False)
        parser.add_argument('delName', required=False)
        parser.add_argument('totalAmount', required=False)
        parser.add_argument('delAddress', required=False)
        parser.add_argument('delCity', required=False)
        parser.add_argument('delPincode', required=False)
        parser.add_argument('delPhone', required=False)
        parser.add_argument('paymentMode', required=False)
        parser.add_argument('transactionStatus', required=False)
        parser.add_argument('failureReason', required=False)
        parser.add_argument('shippingCharge', required=False)
        parser.add_argument('cancellationFlag', required=False)
        parser.add_argument('cancellationReason', required=False)
        parser.add_argument('stdDeliveryTime', required=False)
        parser.add_argument('preDeliveryTime', required=False)
        parser.add_argument('specialOffer', required=False)
        parser.add_argument('deliveryStatus', required=False)
        parser.add_argument('deliveredTime', required=False)
        parser.add_argument('deliveredBy', required=False)
        parser.add_argument('deliveredTo', required=False)
        parser.add_argument('userId', required=False)
        parser.add_argument('updatedBy', required=False)
        parser.add_argument('updatedDate', required=False)
        parser.add_argument('del_name', required=False)
        parser.add_argument('merchantId', required=False)
        parser.add_argument('orderId', required=False)
        parser.add_argument("assignedTo", required=False)
        self.uid = get_jwt_identity()
        self.user = get_jwt_claims()

    def post(self):

        # try:
            conn = mysql.connect()
            cursor = conn.cursor()

            args = parser.parse_args()
            print("data", args)
            created_by = 1

            created_date = datetime.datetime.now()

            order_id = []
            print(order_id,"orderid")
            result_data = []
            print(result_data,"resultdata")
            if args['paymentMode'] == 'Wallet':
                pm = 'WP'
            elif args['paymentMode'] == 'Net Banking':
                pm = 'NET'
            elif args['paymentMode'] == 'DebitCard':
                pm = 'DEB'
            elif args['paymentMode'] == 'CashCard':
                pm = 'CC'
            elif args['paymentMode'] == 'CreditCard':
                pm = 'CRE'
            elif args['paymentMode'] == 'Online Payment':
                pm = 'OP'
            else:
                pm = args['paymentMode']

            totalAmount = 0

            for i,elements in enumerate(args.products):
                totalAmount += float(elements['totalAmount'])

            
            for i,elements in enumerate(args.products):
                print(f'i {i}')
                if i == 0:
                    cursor.execute("insert into orders(total_amount,gst_percentage,gst_amount,net_amount,del_name,del_address,del_city,del_pincode,"
                        "del_phone,payment_mode,transaction_status,failure_reason,shipping_charge,cancellation_flag,"
                        "cancellation_reason,std_delivery_time,preferred_delivery_time,special_offer, delivery_status,"
                        "delivered_time,delivered_to,user_id,created_by,created_date,merchant_id, assigned_to,delivered_by) "
                        "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (
                            totalAmount,
                            args.gstPercentage, 
                            args.gstAmount,
                            args.netAmount, 
                            args.delName, 
                            args.delAddress, 
                            args.delCity, 
                            args.delPincode,
                            args.delPhone, 
                            pm, 
                            args.transactionStatus, 
                            args.failureReason,
                            args.shippingCharge, 
                            args.cancellationFlag, 
                            args.cancellationReason,
                            args.stdDeliveryTime, 
                            args.preDeliveryTime, 
                            elements['specialOffer'], 
                            args.deliveryStatus,
                            args.deliveredTime,  
                            args.deliveredTo, 
                            args.userId,    
                            created_by,
                            created_date, 
                            elements['merchantId'],
                            args.assignedTo,
                            args.deliveredBy
                            ))
                    
                    result = cursor.rowcount
                    print(result,"..............")

                    # a = cursor.execute("SELECT LAST_INSERT_ID() FROM orders")
                    cursor.execute("SELECT order_id FROM paypre_ecom.orders ORDER BY order_id DESC")
                    a = cursor.fetchone()[0]
                    conn.commit()
                print(f' a {a}')
                # cursor.execute("SELECT config_id FROM configuration_master WHERE config_value= %s",(elements['productUom']))
                # print(f'cursor {i} executed')
                # uom = cursor.fetchone()[0]
                # print(f'fetched {i} uom {uom}')
                cursor.execute("INSERT INTO order_details(merchant_id, category_id, no_of_order, product_id, product_uom_id, product_quantity, "
                "product_selling_price, special_offer, total_amount, order_id)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(
                    elements['merchantId'],
                    elements['categoryId'],
                    elements['noOfOrders'], 
                    elements['productId'], 
                    elements['productUomId'],  
                    elements['productQuantity'], 
                    elements['productSellingPrice'],
                    elements['specialOffer'], 
                    elements['totalAmount'], 
                    a))
                
                print(f'cursor {i} insert 2 executed')
                
                # b = cursor.fetchone()                   
                cursor.execute(
                    "DELETE FROM user_cart WHERE product_id ='" + str(elements['productId']) + "' and user_id = '" + str(args[
                        'userId']) + "'")
                cursor.execute("SELECT no_of_items FROM products WHERE product_id=%s",(elements['productId']))
                noofItem = cursor.fetchone()[0]-1
                cursor.execute("UPDATE products SET no_of_items=%s WHERE product_id=%s",(noofItem, elements['productId']))
                print(f'delete {i} executed')
                # for bb in b:
                #     order_id.append(bb)

                
            conn.commit()

            # dt = {
            #     "orderId": order_id,
            #     "netAmount": args['netAmount'],
            #     "gstPercentage": args['gstPercentage'],
            #     "gstAmount": args['gstAmount'],
            #     "orderDate": str(created_date)
            # }
            
            # result_data.append(dt)

                            
            if result != 0:
                sms_notification(args['delPhone'], args['delName'], args['preDeliveryTime'], order_id, 'OP', args['delAddress'])
                mail_notification(args['userId'], args['delName'], args['preDeliveryTime'], order_id, 'OP')
                # return {
                #         'message': 'success',
                #         'statusCode': 1,
                #         'data': result_data
                #     }
                args['orderDate'] = str(created_date)
                args['orderId'] = a
                return {
                        'message': 'orders inserted successfully',
                        'statusCode': 1,
                        'data':args
                }
                        
            else:
                return {
                        'message': 'Data is not Inserted',
                        'statusCode': 0
                }

    # def get(self):
    #     conn = mysql.connect()
    #     cursor = conn.cursor()
    #     args = parser.parse_args()
    #     # print(f'args {args}')
    #     if args.userId:
    #         cursor.execute("SELECT distinct orders.order_id FROM orders inner join order_details on order_details.order_id = orders.order_id where orders.user_id=%s and orders.merchant_id= %s ",(args.userId, args.merchantId))
    #     elif args.deliveryStatus and args.merchantId:
    #         cursor.execute("SELECT distinct orders.order_id FROM orders inner join order_details on order_details.order_id = orders.order_id where orders.delivery_status=%s and orders.merchant_id= %s ",(args.deliveryStatus, args.merchantId))
    #     elif args.orderId:
    #         cursor.execute("SELECT distinct orders.order_id FROM orders inner join order_details on order_details.order_id = orders.order_id where orders.order_id=%s and orders.merchant_id= %s ",(args.orderId, args.merchantId))
    #     elif args.merchantId:
    #         cursor.execute("SELECT distinct orders.order_id FROM orders inner join order_details on order_details.order_id = orders.order_id WHERE orders.merchant_id=%s",(args.merchantId))
    #     else:
    #         cursor.execute("SELECT distinct orders.order_id FROM orders inner join order_details on order_details.order_id = orders.order_id")
    #     ids = cursor.fetchall()
    #     # print(f'ids {ids}')
    #     if ids:
    #         data = []
    #         for id in ids:
    #             # print(f'id {id}')
    #             cursor.execute("SELECT * ,users.email FROM orders inner join users on users.merchant_id = orders.merchant_id WHERE order_id=%s  ",(id))
    #             uniqueData = cursor.fetchone()
    #             cursor.execute("SELECT user_name FROM users WHERE user_id=%s",(uniqueData[23]))
    #             userName = cursor.fetchone()
                
    #             # print(f'dic {dic}')
    #             # print(f'uniqueData {uniqueData}')
    #             productList = []
    #             cursor.execute("SELECT * FROM order_details  WHERE order_id=%s", (id))
    #             productData = cursor.fetchall()
    #             totalAmount = 0
    #             for eachProduct in productData:
    #                 totalAmount += eachProduct[9]
    #                 cursor.execute("SELECT P.product_name, P.image_url, C.category_name, CM.config_value FROM products P LEFT JOIN categories C ON P.category_id = C.category_id "
    #                 "LEFT JOIN configuration_master CM ON P.product_uom = CM.config_id WHERE P.product_id = %s",(eachProduct[4]))
    #                 allNames = cursor.fetchone()
    #                 # print(f'all name {allNames}')
    #                 # print(f'product ID {eachProduct[4]}, categoryID {eachProduct[2]} merchantID {eachProduct[1]}')
    #                 productName = productImg = categoryName = productUom = "no value available"
    #                 # print(f' all name condition {allNames}')
    #                 if allNames:
    #                     # print(f' came inside all name')
    #                     productName = allNames[0]
    #                     productImg = allNames[1]
    #                     categoryName = allNames[2]
    #                     productUom = allNames[3]
                    
    #                 productList.append({
    #                     "merchantId":str(eachProduct[1]),
    #                     "categoryId":str(eachProduct[2]),
    #                     "categoryName":str(categoryName),
    #                     "noOfOrder":str(eachProduct[3]),
    #                     "productId":str(eachProduct[4]),
    #                     "productName":str(productName),
    #                     "productImg": str(productImg),
    #                     "productUomId":str(eachProduct[5]),
    #                     "productUom": str(productUom),
    #                     "productQuantity":str(eachProduct[6]),
    #                     "productSellingPrice":str(eachProduct[7]),
    #                     "specialOffer":str(eachProduct[8]),
    #                     "totalAmount":str(eachProduct[9])
    #                 })
    #                 # else:
    #                 #     return {
    #                 #         "message": "no data available",
    #                 #         "status code": 0
    #                 #     }
                
    #             data.append({
    #                 "orderId":str(uniqueData[0]),
    #                 "total_amount":str(uniqueData[2]),
    #                 "gst_percentage":str(uniqueData[3]),
    #                 "gst_amount":str(uniqueData[4]),
    #                 "net_amount":str(uniqueData[5]),
    #                 "del_name":str(uniqueData[6]),
    #                 "del_address":str(uniqueData[7]),
    #                 "del_city":str(uniqueData[8]),
    #                 "del_pincode":str(uniqueData[9]),
    #                 "del_phone":str(uniqueData[10]),
    #                 "payment_mode":str(uniqueData[11]),
    #                 "transaction_status":str(uniqueData[12]),
    #                 "failure_reason":str(uniqueData[13]),
    #                 "shipping_charge":str(uniqueData[14]),
    #                 "cancellation_flag":str(uniqueData[15]),
    #                 "cancellation_reason":str(uniqueData[16]),
    #                 "stdDeliveryTime":str(uniqueData[17]),
    #                 "preDeliveryTime":str(uniqueData[18]),
    #                 "deliveryStatus":str(uniqueData[20]),
    #                 "deliveredTime":str(uniqueData[21]),
    #                 "deliveredBy":str(uniqueData[29]),
    #                 "deliveredTo":str(uniqueData[22]),
    #                 "userId":str(uniqueData[23]),
    #                 "orderDate": str(uniqueData[25]),
    #                 "email":str(uniqueData[27]),
    #                 "assignedTo":str(uniqueData[28]),
    #                 "userName":(userName[0] if userName else userName),
    #                 "products":productList
    #             })
                
    #         # pprint(data)
    #         return {
    #             "data": data,
    #             "status code": 1
    #         }

    #     else :
    #         return {
    #             "message": "bulk order not found",
    #             "status code": 0
    #         } 

    def get(self):
        conn = mysql.connect()
        cursor = conn.cursor()
        args = parser.parse_args()
        if args.orderId and args.deliveryStatus:
            cursor.execute("SELECT orders.*, users.email, users.user_name "
            "FROM orders "
            "INNER JOIN users ON users.user_id = orders.user_id "
            "WHERE orders.order_id IN (SELECT DISTINCT order_details.order_id FROM order_details WHERE order_details.order_id = orders.order_id) AND orders.order_id=%s and orders.merchant_id= %s AND orders.delivery_status=%s",(args.orderId, args.merchantId,args.deliveryStatus))
        elif args.userId:
            cursor.execute("SELECT orders.*, users.email, users.user_name "
            "FROM orders "
            "INNER JOIN users ON users.user_id = orders.user_id "
            "WHERE orders.order_id IN (SELECT DISTINCT order_details.order_id FROM order_details WHERE order_details.order_id = orders.order_id) AND orders.user_id=%s and orders.merchant_id= %s ",(args.userId, args.merchantId))
        elif args.deliveryStatus and args.merchantId:
            cursor.execute("SELECT orders.*, users.email, users.user_name "
            "FROM orders "
            "INNER JOIN users ON users.user_id = orders.user_id "
            "WHERE orders.order_id IN (SELECT DISTINCT order_details.order_id FROM order_details WHERE order_details.order_id = orders.order_id) AND orders.delivery_status=%s and orders.merchant_id= %s ",(args.deliveryStatus, args.merchantId))
        elif args.orderId:
            cursor.execute("SELECT orders.*, users.email, users.user_name "
            "FROM orders "
            "INNER JOIN users ON users.user_id = orders.user_id "
            "WHERE orders.order_id IN (SELECT DISTINCT order_details.order_id FROM order_details WHERE order_details.order_id = orders.order_id) AND orders.order_id=%s and orders.merchant_id= %s ",(args.orderId, args.merchantId))
        elif args.merchantId:
            cursor.execute("SELECT orders.*, users.email, users.user_name "
            "FROM orders "
            "INNER JOIN users ON users.user_id = orders.user_id "
            "WHERE orders.order_id IN (SELECT DISTINCT order_details.order_id FROM order_details WHERE order_details.order_id = orders.order_id) AND orders.merchant_id=%s",(args.merchantId))
        else:
            cursor.execute("SELECT orders.*, users.email, users.user_name "
            "FROM orders "
            "INNER JOIN users ON users.user_id = orders.user_id "
            "WHERE orders.order_id IN (SELECT DISTINCT order_details.order_id FROM order_details WHERE order_details.order_id = orders.order_id)")

        result = cursor.fetchall()
        data = []
        if result:
            for uniqueData in result:
                cursor.execute("SELECT OD.*, P.product_name, P.image_url , C.category_name, " 
                "(SELECT CM.config_value FROM products PP LEFT JOIN configuration_master CM ON PP.product_uom = CM.config_id WHERE PP.product_id = P.product_id) AS config_value "
                "FROM order_details OD "
                "LEFT JOIN products P ON P.product_id = OD.product_id "
                "LEFT JOIN categories C ON C.category_id = OD.category_id "
                "WHERE OD.order_id =%s ",(uniqueData[0]))
                orders = cursor.fetchall()
                productList=[]
                if orders:
                    for ec in orders:
                        sampleDic = {}
                        for i,j in enumerate(ec):
                            sampleDic[i] = j
                        pprint(sampleDic)
                    for eachProduct in orders:
                        productList.append({
                            "merchantId":str(eachProduct[1]),
                            "categoryId":str(eachProduct[2]),
                            "noOfOrder":str(eachProduct[3]),
                            "productId":str(eachProduct[4]),
                            "productUomId":str(eachProduct[5]),
                            "productQuantity":str(eachProduct[6]),
                            "productSellingPrice":str(eachProduct[7]),
                            "specialOffer":str(eachProduct[8]),
                            "totalAmount":str(eachProduct[9]),
                            "productName":str(eachProduct[11]),
                            "productImg": str(eachProduct[12]),
                            "categoryName":str(eachProduct[13]),
                            "productUom": str(eachProduct[14])
                            
                        })

                data.append({
                        "orderId":str(uniqueData[0]),
                        "total_amount":str(uniqueData[2]),
                        "gst_percentage":str(uniqueData[3]),
                        "gst_amount":str(uniqueData[4]),
                        "net_amount":str(uniqueData[5]),
                        "del_name":str(uniqueData[6]),
                        "del_address":str(uniqueData[7]),
                        "del_city":str(uniqueData[8]),
                        "del_pincode":str(uniqueData[9]),
                        "del_phone":str(uniqueData[10]),
                        "payment_mode":str(uniqueData[11]),
                        "transaction_status":str(uniqueData[12]),
                        "failure_reason":str(uniqueData[13]),
                        "shipping_charge":str(uniqueData[14]),
                        "cancellation_flag":str(uniqueData[15]),
                        "cancellation_reason":str(uniqueData[16]),
                        "stdDeliveryTime":str(uniqueData[17]),
                        "preDeliveryTime":str(uniqueData[18]),
                        "deliveryStatus":str(uniqueData[20]),
                        "deliveredTime":str(uniqueData[21]),
                        "deliveredTo":str(uniqueData[22]),
                        "userId":str(uniqueData[23]),
                        "orderDate": str(uniqueData[25]),
                        "assignedTo":str(uniqueData[28]),
                        "deliveredBy":str(uniqueData[29]),
                        "email":str(uniqueData[30]),
                        "userName":str(uniqueData[31]),
                        "products":productList
                    })
            return {
                "data": data,
                "status code": 1
            }

        else:
           return {
                "message": "bulk order not found",
                "status code": 0
            } 

class AssignedDelivery(Resource):
    def __init__(self):
        super().__init__()
        parser.add_argument("userId", required=False)
        parser.add_argument("merchantId", required=False)
        parser.add_argument('deliveryStatus', required=False)

    def get(self):
        conn = mysql.connect()
        cursor = conn.cursor()
        args = parser.parse_args()
        cursor.execute("SELECT orders.*, users.email, users.user_name "
        "FROM orders "
        "INNER JOIN users ON users.user_id = orders.user_id "
        "WHERE orders.order_id IN (SELECT DISTINCT order_details.order_id FROM order_details WHERE order_details.order_id = orders.order_id) and orders.merchant_id=%s and orders.assigned_to=%s and orders.delivery_status=%s",(args.merchantId,args.userId,args.deliveryStatus))

        result = cursor.fetchall()
        data = []
        if result:
            for uniqueData in result:
                cursor.execute("SELECT OD.*, P.product_name, P.image_url , C.category_name, " 
                "(SELECT CM.config_value FROM products PP LEFT JOIN configuration_master CM ON PP.product_uom = CM.config_id WHERE PP.product_id = P.product_id) AS config_value "
                "FROM order_details OD "
                "LEFT JOIN products P ON P.product_id = OD.product_id "
                "LEFT JOIN categories C ON C.category_id = OD.category_id "
                "WHERE OD.order_id =%s ",(uniqueData[0]))
                orders = cursor.fetchall()
                productList=[]
                if orders:
                    for ec in orders:
                        sampleDic = {}
                        for i,j in enumerate(ec):
                            sampleDic[i] = j
                        pprint(sampleDic)
                    for eachProduct in orders:
                        productList.append({
                            "merchantId":str(eachProduct[1]),
                            "categoryId":str(eachProduct[2]),
                            "noOfOrder":str(eachProduct[3]),
                            "productId":str(eachProduct[4]),
                            "productUomId":str(eachProduct[5]),
                            "productQuantity":str(eachProduct[6]),
                            "productSellingPrice":str(eachProduct[7]),
                            "specialOffer":str(eachProduct[8]),
                            "totalAmount":str(eachProduct[9]),
                            "productName":str(eachProduct[11]),
                            "productImg": str(eachProduct[12]),
                            "categoryName":str(eachProduct[13]),
                            "productUom": str(eachProduct[14])
                            
                        })

                data.append({
                        "orderId":str(uniqueData[0]),
                        "total_amount":str(uniqueData[2]),
                        "gst_percentage":str(uniqueData[3]),
                        "gst_amount":str(uniqueData[4]),
                        "net_amount":str(uniqueData[5]),
                        "del_name":str(uniqueData[6]),
                        "del_address":str(uniqueData[7]),
                        "del_city":str(uniqueData[8]),
                        "del_pincode":str(uniqueData[9]),
                        "del_phone":str(uniqueData[10]),
                        "payment_mode":str(uniqueData[11]),
                        "transaction_status":str(uniqueData[12]),
                        "failure_reason":str(uniqueData[13]),
                        "shipping_charge":str(uniqueData[14]),
                        "cancellation_flag":str(uniqueData[15]),
                        "cancellation_reason":str(uniqueData[16]),
                        "stdDeliveryTime":str(uniqueData[17]),
                        "preDeliveryTime":str(uniqueData[18]),
                        "deliveryStatus":str(uniqueData[20]),
                        "deliveredTime":str(uniqueData[21]),
                        "deliveredTo":str(uniqueData[22]),
                        "userId":str(uniqueData[23]),
                        "orderDate": str(uniqueData[25]),
                        "assignedTo":str(uniqueData[28]),
                        "deliveredBy":str(uniqueData[29]),
                        "email":str(uniqueData[30]),
                        "userName":str(uniqueData[31]),
                        "products":productList
                    })
            return {
                "data": data,
                "status code": 1
            }
        else:
            return {
                "message": "bulk order not found",
                "status code": 0
            } 



