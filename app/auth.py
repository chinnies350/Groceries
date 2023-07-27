from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)

import datetime
from pprint import pprint

parser = reqparse.RequestParser()
parser.add_argument('next', help='', required=False)


class UserObject:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@jwt.user_claims_loader
def add_claims_to_access_token(user):
    return user.__dict__


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.uid

# user login authentication


class UserLogin(Resource):
    def __init__(self, app=None):
        parser.add_argument('loginId', help='Email id or contact required', required=False)
        parser.add_argument('password', help='Password is required', required=False)
        parser.add_argument('remember', help='remember is required', required=False)
        parser.add_argument('merchantId', help='remember is required', required=False)

    def post(self):
        try:
            args = parser.parse_args()
           
            email = args['loginId']
            password = args['password']
            merchantId = args['merchantId']
            
            
            conn = mysql.connect()
            cursor = conn.cursor()

            # cursor.execute("select * from users where email='" + str(email) + "' or primary_phone='" + str(
            #     email.split('.')[0]) + "' or user_id='" + str(email).split('.')[0] + "'")
            if len(email) <= 10:
                cursor.execute("select * from users where email=%s or primary_phone=%s or user_id =%s",(email,email,email) )
            else:
                print('first else condition')
                cursor.execute("select * from users where email=%s or primary_phone=%s",(email,email) )
            result = cursor.fetchall()
            print(result)
            conn.commit()
            
            if result :
                for r in result:  
                    sampleDic= {}
                    pprint(f'r {r}')
                    for i,j in enumerate(r):
                        sampleDic[i] = j 
                    
                    pprint(sampleDic)
                    print(f' password checking {bcrypt.check_password_hash(r[5],password)}')
                    print(r[20])                 
                    args['username'] = r[2]
                    user_role = r[18]

                    if user_role == "SA" and bcrypt.check_password_hash(r[5],password):
                        user = UserObject(
                            uid=args['username'])

                        expires = datetime.timedelta(days=1)
                        access_token = create_access_token(identity=user, expires_delta=expires)
                        refresh_token = create_refresh_token(identity=user, expires_delta=expires)

                        return {

                            'access_token': access_token,
                            'refresh_token': refresh_token,
                            'uid': r[0],
                            'userName':r[2],
                            'email':r[3],
                            'primaryPhone':r[4],                            
                            'userRole' : r[18]

                        }, 200
                   
            
                    elif bcrypt.check_password_hash(r[5],password)  and str(r[1]) == args.merchantId :

                        user = UserObject(
                            uid=args['username'])

                        expires = datetime.timedelta(days=1)
                        access_token = create_access_token(identity=user, expires_delta=expires)
                        refresh_token = create_refresh_token(identity=user, expires_delta=expires)

                        return {

                            'access_token': access_token,
                            'refresh_token': refresh_token,
                            'uid': r[0],
                            "merchantId":r[1],
                            "userName":r[2],
                            "email":r[3],
                            "primaryPhone":r[4],
                            "delAddress1":r[6],
                            "delCity1":r[7],
                            "delPincode1":r[8],
                            "delState1":r[9],
                            "addType1":r[10],
                            "defaultAddress":r[16],
                            "userRole":r[18],
                            "userStatus":r[19]

                        }, 200
                    else:
                        print(f'b last else condition')
                        return {"message": "Incorrect password", 'statusCode': 0}, 401
            else:
                print(f'last else condition')
                return {"message": "Incorrect password", 'statusCode': 0}, 401

           
        except Exception as e:
            print(e)
# access tokens


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        expires = datetime.timedelta(days=1)

        access_token = create_access_token(identity=current_user, expires_delta=expires)
        return {'access_token': access_token}


class AllUsers(Resource):
    def get(self):
        return {'message': 'List of users'}

    def delete(self):
        return {'message': 'Delete all users'}


class SecretResource(Resource):
  
    def __init__(self):
        self.uid = get_jwt_identity()
        self.user = get_jwt_claims()
        self.currentUser = get_current_user()
        self.raw = get_raw_jwt()

    def get(self):
        return {
            'uid': self.uid,
            'user': self.user,
            'currentUser': self.currentUser,
            'raw': self.raw,

        }

# check the user is already registered or not
class Checkuser(Resource):

    def __init__(self):
        parser.add_argument(
            'emailId', help='emailId is required', required=False
        )
        parser.add_argument(
            'merchantId', help='emailId is required', required=False
        )

        self.uid = get_jwt_identity()
        self.user = get_jwt_claims()

    def get(self):
        data = parser.parse_args()

        user = UserObject(
            uid=data['emailId'])

        expires = datetime.timedelta(days=1)

        access_token = create_access_token(identity=user, expires_delta=expires)

        conn = mysql.connect()
        cursor = conn.cursor()




        cursor.execute("select * from users where email='"+data['emailId']+"' or primary_phone='"+data['emailId']+"' and merchant_id='"+data['merchantId']+"'")

        result = cursor.fetchall()

        conn.commit()





        data = []

        if result == ():
            return {

                'data': "No data",
                'statusCode': 0

            },400
        else:
            for r in result:

                data_dt = {'access_token': access_token,"userId": r[0], "userName": r[2], "email": r[3], "phone": r[4], "password": r[5],
                           "address1": r[6], "city1": r[7], "pincode1": r[8],"state":r[9],"addressType1":r[10], "address2": r[11], "city2": r[12],
                           "pincode2": r[13],"state2":r[14],"addressType2":r[15],"defaultAddress":r[16], "secondaryContactNo": r[17],"userRole":r[18],"userStatus":r[19]}
                data.append(data_dt)

            return {

                'data': data,
                'statusCode': 1

            },200

# access token for random user without login account
class Randomuser(Resource):
    def __init__(self, app=None):
        parser.add_argument(
            'loginId', help='Email id or contact required', required=False)

        parser.add_argument(
            'password', help='Password is required', required=False)
        parser.add_argument(
            'remember', help='remember is required', required=False)

    def post(self):


                        user = UserObject(
                            uid="easyfruitveg")


                        expires = datetime.timedelta(days=1)
                        access_token = create_access_token(identity=user,expires_delta=False)
                        refresh_token = create_refresh_token(identity=user)

                        return {

                            'access_token': access_token,
                            'refresh_token': refresh_token,


                        },200


class Checkseller(Resource):

    def __init__(self):
        parser.add_argument(
            'emailId', help='emailId is required', required=False
            )
            
        self.uid = get_jwt_identity()
        self.user = get_jwt_claims()
            
    def get(self):
        data = parser.parse_args()
            
        user = UserObject(
                    uid=data['emailId'])
            
        expires = datetime.timedelta(days=1)
            
        access_token = create_access_token(identity=user, expires_delta=expires)
            
        conn = mysql.connect()
        cursor = conn.cursor()          
                      
            
        cursor.execute("select * from sellers where email='"+data['emailId']+"' ")
            
        result = cursor.fetchall()
            
        conn.commit()
            
            
            
            
            
        data = []
            
        if result == ():
            return {
            
                'data': "No data",
                'statusCode': 0
            
            },400
        else:
            for r in result:
            
                data_dt = {'access_token': access_token,"sellerId": r[0], "sellerName": r[1], "email": r[2], "phone": r[3], "password": r[4],
                                       
                                       "pincode": r[5],"userRole":r[20],"sellerStatus":r[15]}
                data.append(data_dt)
            
            return {
            
                'data': data,
                'statusCode': 1
            
                },200