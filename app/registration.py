from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)
from app.libs import hashPassword, timestamp, hashdePassword
import datetime
parser = reqparse.RequestParser()
parser.add_argument('next', help='', required=False)



# to register new users

class Registration(Resource):

    def __init__(self):
        parser.add_argument(
            'name', help='name is required', required=False)
        parser.add_argument(
            'email', help='email is required', required=False)
        parser.add_argument(
            'contact', help='contact number is required', required=False)
        parser.add_argument(
            'password', help='password is required', required=False)
        parser.add_argument('userRole', required=False)
        parser.add_argument('merchantId', required=False)

        self.uid = get_jwt_identity()

        self.user = get_jwt_claims()

    def post(self):
        args = parser.parse_args()
        email = []
        phone = []
        name = []
        print(f'args {args}')
        if args.email and args.contact and args.password:
            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute("select * from users")
            result = cursor.fetchall()

            for r in result:
                name.append(r[2])
                list_email = r[3]
                list_phone = r[4]
                email.append(list_email)
                phone.append(list_phone)

            if args.email in email:
                print(email)
                return {

                        'message': 'Email is already registered',
                        'statusCode': 0
                    }
            elif args.contact in phone:
                print(phone)
                return {
                    'message': 'contact number is already registered',
                    'statusCode': 0
                }
            
            elif args.name in name:
                print(name)
                return {
                    'message': 'user name is already registered',
                    'statusCode': 0
                }

            else:
                    created_by = 1

                    user_status='A'

                    created_date = datetime.datetime.now()

                    cursor.execute("insert into users(merchant_id,user_name,email,primary_phone,password,user_role,user_status,created_by,created_date)"
                    " value (%s,%s,%s,%s,%s,%s,%s,%s,%s)",(
                        args.merchantId,
                        args.name, 
                        args.email, 
                        args.contact,
                        hashPassword(args.password),
                        args.userRole,
                        user_status,
                        created_by,
                        created_date
                        ))
                    conn.commit()
                    return {

                        'message': 'data inserted successfully',
                        'statusCode': 1
                    }
        else:
            
            user_status = 'A'
            created_by = 1
            created_date = datetime.datetime.now()
            password_u="fruitveg"
            passw = hashPassword(password_u)
            print(f'hash password    {passw}')
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("insert into users(merchant_id,user_name,email,password,user_role,user_status,created_by,created_date) "
            "value (%s,%s,%s,%s,%s,%s,%s,%s)",(
                args.merchantId,
                args.name, 
                args.email, 
                passw, 
                args.userRole, 
                user_status,
                created_by, 
                created_date
                ))

            conn.commit()
            return {
                'message': 'data inserted successfully',
                'statusCode': 1
            }


class SellerRegistration(Resource):
    def __init__(self):
        parser.add_argument(
            'sellerId', help='name is required', required=False)
        parser.add_argument(
            'sellerName', help='name is required', required=False)
        parser.add_argument(
            'email', help='email is required', required=False)
        parser.add_argument(
            'phone', help='contact number is required', required=False)
        parser.add_argument(
            'password', help='password is required', required=False)
        parser.add_argument('userRole', required=False)

        self.uid = get_jwt_identity()

        self.user = get_jwt_claims()

    def post(self):
        data = parser.parse_args()
        print(data)
        email = []
        phone = []
        password = []

        if data.get('email') and data.get('phone') and data.get('password'):
            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute("select * from sellers")
            result = cursor.fetchall()

            for r in result:

                list_email = r[2]
                list_phone = r[3]
                list_password = r[4]
                email.append(list_email)
                phone.append(list_phone)
                password.append(list_password)
            if data['email'] in email:
                print(email)
                return {

                        'message': 'Email is already registered',
                        'statusCode': 0
                    }
            elif data['phone'] in phone:
                print(phone)
                return {

                    'message': 'contact number is already registered',
                    'statusCode': 0
                }


            else:

                    

                seller_status='A'

                cursor.execute("insert into sellers(seller_name,email,phone,password,seller_status) value (%s,%s,%s,%s,%s)",(data['sellerName'], data['email'], data['phone'],data['password'],seller_status))


                conn.commit()



                return {

                    'message': 'data inserted successfully',
                    'statusCode': 1
                }
        else:

            # seller_status = 'A'
            
            # password_u="fruitveg"
            # conn = mysql.connect()
            # cursor = conn.cursor()
            # cursor.execute(
            #     "insert into sellers(seller_id,seller_name,email,password,seller_status) value (%s,%s,%s,%s,%s)",
            #     (data['sellerId'],data['sellerName'], data['email'], password_u, seller_status))


            # conn.commit()

            # return {

            #     'message': 'data inserted successfully',
            #     'statusCode': 1
            # }
            return {

                    'message': 'data not inserted',
                    'statusCode': 0
                }


# to set new password

class Forgotpassword(Resource):

    def __init__(self):
        parser.add_argument(
            'email', help='email is required', required=False)
        parser.add_argument(
            'password', help='password is required', required=False)



    def post(self):

        data = parser.parse_args()
        email=[]
        phone=[]

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("select email,primary_phone from users")
        result = cursor.fetchall()

        for r in result:
            list_email = ((r[0]))
            list_phone = ((r[1]))
            email.append(list_email)
            phone.append(list_phone)


        if data['email'] in email or phone:

                cursor.execute("update users set password='" + hashPassword(data['password']) + "' where email='" + str(data['email'])  + "' or primary_phone='"+str(data['email'])+"'")
                conn.commit()
                conn.close()
                return {
                    'message': 'Password updated successfully',
                    'statusCode': 1
                }

        return {
            'message':'Your emailId is not registered',
            'statusCode': 0
        }
# to change password

class ChangePassword(Resource):

    def __init__(self):
        parser.add_argument(
            'email', help='email is required', required=False)
        parser.add_argument(
            'oldPassword', help='oldPassword is required', required=False)
        parser.add_argument(
            'newPassword', help='newPassword is required', required=False)



    def post(self):

        data = parser.parse_args()
        email=[]
        phone=[]

        password=data['oldPassword']

        conn = mysql.connect()
        cursor = conn.cursor()


        cursor.execute("select email,primary_phone from users")
        result = cursor.fetchall()

        for r in result:
            list_email = ((r[0]))
            list_phone = ((r[1]))
            email.append(list_email)
            phone.append(list_phone)
        
        print(f'email {email}')

        if data['email'] in email or phone:
                conn = mysql.connect()
                cursor = conn.cursor()


                cursor.execute("select password from users where email='"+data['email']+"'")
                passresult = cursor.fetchall()



                for p in passresult:
                    password_ = (''.join(list(p[0])))



                    chk_pwd=hashdePassword(password_,password)

                    print("test",chk_pwd)

                    if chk_pwd==True:



                        cursor.execute("update users set password='" + hashPassword(data['newPassword']) + "' where email='" + str(data['email'])  + "' or primary_phone='"+str(data['email'])+"'")

                        conn.commit()



                        return {

                            'message': 'Password updated successfully',
                            'statusCode': 1
                        }
                    else:
                        return {

                            'message': 'Password dosnt match',
                            'statusCode': 0
                        }




        return {
            'message':'Your emailId is not registered',
            'statusCode': 0
        }



