from flask_restful import Resource, reqparse
from app import mysql

parser = reqparse.RequestParser()
class OrdersFilters(Resource):
    def __init__(self):
        parser.add_argument("delivery_status", required=True)
    
    def get(self):
        args = parser.parse_args()
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM orders WHERE delivery_status='%s'""" % (args.delivery_status))
        result = cursor.fetchall()
        conn.commit()


        filterOrder = []

        if result:
            for row in result:
                filterOrder.append({
                    "merchant_id":str(row[1]),
                    "category_id":str(row[2]),
                    "product_id":str(row[3]),
                    "quantity":str(row[4]),
                    "product_uom":str(row[5]),
                    "selling_price":str(row[6]),
                    "no_of_order":str(row[7]),
                    "total_amount":str(row[8]),
                    "gst_percentage":str(row[9]),
                    "gst_amount":str(row[10]),
                    "net_amount":str(row[11]),
                    "del_name":str(row[12]),
                    "del_address":str(row[13]),
                    "del_city":str(row[14]),
                    "del_pincode":str(row[15]),
                    "del_phone":str(row[16]),
                    "payment_mode":str(row[17]),
                    "transaction_status":str(row[18]),
                    "failure_reason":str(row[19]),
                    "shipping_charge":str(row[20]),
                    "cancellation_flag":str(row[21]),
                    "cancellation_reason":str(row[22]),
                    "std_delivery_time":str(row[23]),
                    "preferred_delivery_time":str(row[24]),
                    "special_offer":str(row[25]),
                    "delivery_status":str(row[26]),
                    "delivered_time":str(row[27]),
                    "delivered_by":str(row[28]),
                    "delivered_to":str(row[29]),
                    "user_id":str(row[30])

                })

            return {
                    "data":filterOrder,
                    "statusCode":1

                }
        else:
            return {
                    'message': "No data found!",
                    'statusCode':0

                }

