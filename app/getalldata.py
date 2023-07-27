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


parser = reqparse.RequestParser()
parser.add_argument('next', help='', required=False)


class Alloffers(Resource):
#     @jwt_required
    def __init__(self):
        parser.add_argument(
                'offerId', help='offer id is required', required=False)
        parser.add_argument(
                'productId', help='product id is required', required=False)
        parser.add_argument(
                'categoryId', help='category id is required', required=False)
        parser.add_argument(
                'productName', help='product name required', required=False)
        parser.add_argument(
                'description', help='description is required', required=False)
        parser.add_argument(
                'productQty', help='Product quantity is required', required=False)
        parser.add_argument(
                'productUom', help='Product UOM is required', required=False)
        parser.add_argument(
                'productUomId', help='Product UOM is required', required=False)
        parser.add_argument(
                'mrp', help='mrp is required', required=False)
        parser.add_argument(
                'sellingPrice', help='selling price is required', required=False)
        parser.add_argument(
                'imageUrl', help='image url is required', required=False)
        parser.add_argument(
                'offerStartDate', help='offer start date is required', required=False)
        parser.add_argument(
                'offerEndDate', help='offer end date is required', required=False)
        parser.add_argument(
                'productStatus', help='Product status required', required=False)
        parser.add_argument(
                'sellerId', help='Product status required', required=False)

        self.uid = get_jwt_identity()

        self.user = get_jwt_claims()

    def get(self):
        try:

                conn = mysql.connect()
                cursor = conn.cursor()

                cursor.execute(
                "select special_offer. *,configuration_master.config_value, categories.category_name from special_offer INNER JOIN configuration_master ON special_offer.product_uom=configuration_master.config_id inner join categories on special_offer.category_id=categories.category_id")

                result = cursor.fetchall()

                conn.commit()

                if result:
                        data = []
                        for r in result:
                                cursor.execute("SELECT config_value FROM configuration_master WHERE config_id=%s", r[7])
                                uom_value = cursor.fetchone()[0]
                                data_dt = {
                                "offerId": r[0], 
                                "productId": r[1], 
                                "categoryId": r[3], 
                                "productName": r[4],
                                "description": r[5], 
                                "productQty": float(r[6]), 
                                "mrp": float(r[8]),
                                "sellingPrice": float(r[9]), 
                                "imageUrl": r[10], 
                                "offerStartDate": myconverter(r[11]),
                                "offerEndDate": myconverter(r[12]), 
                                "productStatus": r[13], 
                                "productUom": uom_value,
                                "productUomId":r[7],
                                "merchantId": r[2],
                                "categoryName":r[19]}
                                data.append(data_dt)
                        return {
                                'data': data,
                                'statusCode': 1
                        }
                else:
                        return {
                                'message': 'no data found',
                                'statusCode': 0
                        }
        except Exception as e:
                print(e)