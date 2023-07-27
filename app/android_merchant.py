from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)
from app.libs import timestamp
from pprint import pprint


parser = reqparse.RequestParser()

class AndroidMerchant(Resource):
    def __init__(self):
        parser.add_argument("package", required=False)
    
    def get(self):
        try:
            args = parser.parse_args()
            data = []
            conn = mysql.connect()
            cursor = conn.cursor()
            # print(f'args {args}')
            cursor.execute("SELECT config_value from configuration_master WHERE config_type='AM' ")
            row = cursor.fetchone()[0]
            print(f'row {row}')

            package_name = row.split(',')[0]
            merchant_id = row.split(',')[1]
            # print(f'package name {package_name}')
            if package_name == args.package:
                cursor.execute("SELECT * from merchant_details WHERE merchant_id=%s", merchant_id)
                result = cursor.fetchall()

                for r in result:
                    data.append(
                        {
                            "merchantId":r[0],
                            "merchantName":r[1],
                            "merchantLogo":r[2],
                            "colorCode":r[3],
                            "terms":r[4],
                            "aboutUs":r[5],
                            "facebook":r[6],
                            "instagram":r[7],
                            "twitter":r[8],
                            "contactNumber":r[9],
                            "addressLine1":r[10],
                            "addressLine2":r[11],
                            "policy":r[12],
                            "email":r[13],
                            "minDeliveryChargeLimit":str(r[14]),
                            "deliveryCharges":str(r[15]),
                            "gstPercentage":str(r[16]),
                            "gstNumber":r[17],
                            "status":r[18],
                            "mapUrl":r[23],
                            "stockMaintenance":r[25], 
                            "cancellationAllowed":r[26],
                            "cancellationBeforeHrs":str(r[27])
                        }
                    )
            
                if data:  
                    pprint(data)
                    return {
                        'data': data,
                        'statusCode':1
                    }
                else:
                    return {
                        'message':"No data found",
                        "statusCode":0
                    }
            else:
                return {
                    'message':"Sorry, Try again",
                    "statusCode":0
                }
        except Exception as e:
            print(e)
            return {"message": e, "statusCode": 0}

