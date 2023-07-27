from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)
from app.libs import hashPassword, timestamp
import datetime

parser = reqparse.RequestParser()
parser.add_argument('next', help='', required=False)




class Feedback(Resource):
    # @jwt_required
    def __init__(self):

        parser.add_argument('feedbackId', required=False)
        parser.add_argument('userId', required=False)
        parser.add_argument('merchantId', required=False)
        parser.add_argument('userRating', required=False)
        parser.add_argument('comments', required=False)
        parser.add_argument('orderId', required=False)

        self.uid = get_jwt_identity()
        self.user = get_jwt_claims()

    # to manage user feedbacks

    def post(self):
        try:
            args = parser.parse_args()
            conn = mysql.connect()
            cursor = conn.cursor()

            # created_by = self.uid
            created_by = 1
            created_date = datetime.datetime.now()
            print(f' args {args}')

            cursor.execute("insert into feedback(user_id,merchant_id,user_rating,comments,created_by,created_date,order_id)"
            "value (%s,%s,%s,%s,%s,%s,%s)",(
                args.userId,
                args.merchantId,
                args.userRating,
                args.comments,
                created_by,
                created_date,
                args.orderId
                ))

            result = cursor.rowcount

            conn.commit()
            conn.close()


            if result >=1:
                return {
                        'message': 'Inserted successfully',
                        'statusCode': 1
                }

            else:
                return {
                    'message': 'Data is not Inserted',
                    'statusCode': 0
                }
        except Exception as e:
            return {"message": e, "statusCode": 0}

    # to get all the feedbacks

    def get(self):
        args = parser.parse_args()
        conn = mysql.connect()
        cursor = conn.cursor()
        data = []

        if args.merchantId:
            cursor.execute("select * from feedback fb inner join users u on u.user_id=fb.user_id where fb.merchant_id=%s",(args.merchantId))
        else:
            cursor.execute("select * from feedback fb inner join users u on u.user_id=fb.user_id")
        feedback_details = cursor.fetchall()
        print('cursor executed')

        conn.commit()

        for row in feedback_details:
            data.append(
                {
                "userId": row[0],
                "merchantId":row[1],
                "feedbackId":row[2], 
                "userRating": row[3], 
                "comments": row[4],
                "orderId":row[9],
                "email":row[13]
                })

        if data:
            return {
                "data": data,
                "statusCode": 1
            }
        else:
            return {
                "message": "No data found",
                "statusCode": 0
            }
    # delete feedback of an user

    def delete(self):
        try:

            args = parser.parse_args()

            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM feedback WHERE feedback_id =%s", args.feedbackId)
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
        except Exception as e:
            return {"message": e, "statusCode": 0}

    # to update feedback

    def put(self):
        try:

            args = parser.parse_args()

            conn = mysql.connect()
            cursor = conn.cursor()

            # updated_by = self.uid
            updated_by = 1
            updated_date = datetime.datetime.now()

            cursor.execute("UPDATE feedback SET user_id=%s,merchant_id=%s, user_rating=%s,comments=%s,updated_by=%s,updated_date=%s WHERE feedback_id =%s",(
                args.userId,
                args.merchantId,
                args.userRating,
                args.comments,
                updated_by,
                updated_date,
                args.feedbackId
            ))

            result = cursor.rowcount

            conn.commit()
            conn.close()


            if result >=1:
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
            return {
                "message": e, 
                "statusCode": 0
                }
