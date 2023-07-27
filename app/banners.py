from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)
from app.libs import timestamp
import datetime

parser = reqparse.RequestParser()

# to manage carousel images and data

class Banners(Resource):
    # @jwt_required
    def __init__(self):
        parser.add_argument('imageDescription',  required=False)
        parser.add_argument('imageUrl',  required=False)
        parser.add_argument('imageStatus',  required=False)
        parser.add_argument('imageId',  required=False)
        parser.add_argument('merchantId',  required=False)
        parser.add_argument('imageType',  required=False)
        self.uid = get_jwt_identity()
        self.user = get_jwt_claims()

    # insert carousel details
    def post(self):
        try:
            args = parser.parse_args()
            print(f'args {args}')

            # updatedBy = self.uid
            created_by = 1
            # updateby = data['updatedBy']
            created_date = datetime.datetime.now()

            conn = mysql.connect()
            cursor = conn.cursor()
            if not args.imageDescription:
                cursor.execute("insert into carousel(merchant_id,image_url,image_status,created_by,created_date, image_type) "
                "value (%s,%s,%s,%s,%s,%s)",(
                    args.merchantId,
                    args.imageUrl,
                    args.imageStatus,
                    created_by,
                    created_date,
                    args.imageType
                ) )
     
            else:  
                cursor.execute("insert into carousel(merchant_id,image_description,image_url,image_status,created_by,created_date, image_type) "
                "value (%s,%s,%s,%s,%s,%s,%s)",(
                    args.merchantId,
                    args.imageDescription,
                    args.imageUrl,
                    args.imageStatus,
                    created_by,
                    created_date,
                    args.imageType
                ) )   
            print('cursor executed')                                

            conn.commit()
            conn.close()

            print('cursor commit')
            return {
                        'message': 'data inserted successfully',
                        'statusCode': 1
                    }
        except Exception as e:
            print(e)
            return {"message": e, "statusCode": 0}

    # view carousel details
    def get(self):
        args = parser.parse_args()
        try:
            data = []
            conn = mysql.connect()
            cursor = conn.cursor()

            if args.merchantId:
                cursor.execute("select * from carousel where merchant_id=%s", args.merchantId)
                result = cursor.fetchall()
                conn.commit()
            elif args.imageId:
                cursor.execute("select * from carousel where image_id=%s", args.imageId)
                result = cursor.fetchall()
                conn.commit()
            elif args.imageType:
                cursor.execute("select * from carousel where image_type=%s", args.imageType)
                result = cursor.fetchall()
                conn.commit()
            else:
                cursor.execute("select * from carousel")
                result = cursor.fetchall()
                conn.commit()

            if result :           

                for r in result:
                    data.append(
                        {
                        "imageId": r[0], 
                        "merchantId": r[1],
                        "imageDescription": r[2],
                        "imageUrl": r[3],
                        "imageStatus":r[4],
                        "imageType":r[9]
                        }
                    )
                    
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
            return {"message": e, "statusCode": 0}

    # update carousel details
    def put(self):
        try:
            args = parser.parse_args()
            conn = mysql.connect()
            cursor = conn.cursor()

            updated_by = 1
            updated_date=datetime.datetime.now()
            if not args.imageDescription:
                 cursor.execute("update carousel set merchant_id=%s, image_url=%s, image_status=%s, updated_by=%s, updated_date=%s, image_type=%s where image_id=%s", (
                    args.merchantId,
                    args.imageUrl,
                    args.imageStatus,
                    updated_by,
                    updated_date,  
                    args.imageType,              
                    args.imageId
                ))
            else:
                cursor.execute("update carousel set merchant_id=%s, image_description=%s, image_url=%s, image_status=%s, updated_by=%s, updated_date=%s, image_type=%s where image_id=%s", (
                    args.merchantId,
                    args.imageDescription,
                    args.imageUrl,
                    args.imageStatus,
                    updated_by,
                    updated_date,  
                    args.imageType,              
                    args.imageId
                ))

            conn.commit()
            conn.close()

            result = cursor.rowcount
            # mysqlobj.conn.close()

            if result>=1:
                return {
                    'data': 'updated successfully',
                    'statusCode': 1
                }

            else:
                return {
                    'data': 'Data is not updated',
                    'statusCode': 0
                }

        except Exception as e:
            print(e)
            return {"message": e, "statusCode": 0}


    #delete carousel details
    def delete(self):
        try:
            args = parser.parse_args()

            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute("update carousel set image_status='D' where image_id=%s", args.imageId)
            result = cursor.rowcount
            conn.commit()
            conn.close()

            if result>=1:
                return {
                    'data': 'deleted successfully',
                    'statusCode': 1
                }

            else:
                return {
                    'data': 'Data is not deleted',
                    'statusCode': 0
                }


        except Exception as e:
            return {"message": e, "statusCode": 0}



class ActiveBanners(Resource):
    def __init__(self):
        parser.add_argument('imageId',  required=False)
        parser.add_argument('merchantId',  required=False)
        parser.add_argument('imageType',  required=False)

    def get(self):
        args =  parser.parse_args()
        try:
            data = []
            conn = mysql.connect()
            cursor = conn.cursor()
            if args.merchantId and args.imageType:
                cursor.execute("SELECT * FROM carousel WHERE merchant_id=%s AND image_status='A' AND image_type=%s", (args.merchantId, args.imageType))
                result = cursor.fetchall()
                conn.commit()
            elif args.imageId and args.merchantId:
                cursor.execute("SELECT * FROM carousel WHERE image_id=%s AND image_status='A' AND  merchant_id=%s", (args.imageId, args.merchantId))
                result = cursor.fetchall()
                conn.commit()
            elif args.merchantId:
                cursor.execute("SELECT * FROM carousel WHERE merchant_id=%s AND image_status='A'", args.merchantId)
                result = cursor.fetchall()
                conn.commit()
            elif args.imageId:
                cursor.execute("SELECT * FROM carousel WHERE image_id=%s AND image_status='A'", args.imageId)
                result = cursor.fetchall()
                conn.commit()
            elif args.imageType:
                cursor.execute("SELECT * FROM carousel WHERE image_type=%s AND image_status='A'", args.imageType)
                result = cursor.fetchall()
                conn.commit()
            else:
                cursor.execute("SELECT * FROM carousel WHERE image_status='A'")
                result = cursor.fetchall()
                conn.commit()

            if result :           

                for r in result:
                    data.append(
                        {
                        "imageId": r[0], 
                        "merchantId": r[1],
                        "imageDescription": r[2],
                        "imageUrl": r[3],
                        "imageStatus":r[4],
                        "imageType":r[9]
                        }
                    )
                    
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
            return {"message": e, "statusCode": 0}
