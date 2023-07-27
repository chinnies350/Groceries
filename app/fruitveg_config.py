from flask_restful import Resource, reqparse
from app import bcrypt, config, jwt, mysql
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)


parser = reqparse.RequestParser()
parser.add_argument('next', help='', required=False)




class Configuration(Resource):
    # @jwt_required
    def __init__(self):
        parser.add_argument(
            'configName', help='name is required', required=False)
        parser.add_argument(
            'configValue', help='value is required', required=False)
        parser.add_argument(
            'configType', help='value is required', required=False)
        parser.add_argument(
            'configId', help='id is required', required=False)
        parser.add_argument(
            'merchantId', help='id is required', required=False)


    # to add configuration values

    def post(self):
        # try:
        args = parser.parse_args()
        conn = mysql.connect()
        cursor = conn.cursor()
        if args.configName == "charge limit" or args.configName == 'delivery hour':
            cursor.execute("SELECT * FROM configuration_master WHERE config_name=%s and merchant_id=%s", (args.configName, args.merchantId))
            alreadyExt = cursor.fetchone()[0]
            if alreadyExt>=1:
                return {
                    "message": '{} already exist'.format(args.configName),
                    "statusCode": 0
                }
    
        cursor.execute("SELECT * FROM configuration_master WHERE config_name=%s and merchant_id=%s and config_value=%s", (args.configName, args.merchantId, args.configValue))
        alreadyExt = cursor.fetchone()

        if alreadyExt:
            return {
                    "message": 'already exist',
                    "statusCode": 0
                }
       
            
        cursor.execute("INSERT INTO configuration_master(config_name,config_value,config_status,config_type,merchant_id) VALUES "
        "(%s,%s,%s,%s,%s)",(
            args.configName, 
            args.configValue, 
            'A',
            args.configType,
            args.merchantId
            ))

        conn.commit()

        if cursor.rowcount>=1:

            return {

                        'message': 'success',
                        'statusCode': 1
                    }
        # except Exception as e:
        #     return {"message": e, "statusCode": 0}

    # to view configuration

    def get(self):
        args = parser.parse_args()
        try:
            data = []
            conn = mysql.connect()
            cursor = conn.cursor()

            if args.configName:
                cursor.execute("select * from configuration_master where config_name=%s and merchant_id=%s", (args.configName, args.merchantId))
                result = cursor.fetchall()
                print(result)
                conn.commit()
            elif args.configType:            
                cursor.execute("SELECT * FROM configuration_master WHERE config_Type=%s and merchant_id=%s",(args.configType, args.merchantId))
                result = cursor.fetchall()
            
            elif args.merchantId: 
                cursor.execute("SELECT * FROM configuration_master WHERE merchant_id=%s",(args.merchantId))
                result = cursor.fetchall()

            else:
                cursor.execute("SELECT * FROM configuration_master ")
                result = cursor.fetchall()

            for r in result:
                data.append({
                    "configId":r[0],
                    "configName":r[1], 
                    "configValue":r[2],
                    "configStatus":r[3],
                    "configType":r[4],
                    "merchantId":r[5]
                })
                
            print(data)
            if data:
                return {
                    'data':data,
                    'statusCode':1
                }
            else:
                return {
                    'message':"No data found",
                    'statusCode':1
                }
        except Exception as e:
            print(e)
            return {"message": e, "statusCode": 0}

            
    # to update configuration

    def put(self):
        data = parser.parse_args()
        args = parser.parse_args()

        conn = mysql.connect()
        cursor = conn.cursor()

        # cursor.execute("update configuration_master set config_value='" + data['configValue'] + "' where config_id='" + data[
        #                 'configId'] + "'")
        cursor.execute("SELECT * FROM configuration_master WHERE config_name=%s and merchant_id=%s and config_value=%s and config_id != %s", (args.configName, args.merchantId, args.configValue, args.configId))
        alreadyExt = cursor.fetchone()
        if alreadyExt:
                return {
                        "message": 'already exist',
                        "statusCode": 0
                    }
        cursor.execute("update configuration_master set config_value=%s where config_id=%s and merchant_id=%s",(args.configValue,args.configId ,args.merchantId))



        result = cursor.rowcount

        conn.commit()

        print('result', result)

        if result != 0:

            return {

                'message': 'updated successfully',
                'statusCode': 1

            }

        else:

            return {

                'message': 'Data is not updated',
                'statusCode': 0

            }

    # def delete(self):
    #     args = parser.parse_args()
    #     conn = mysql.connect()
    #     cursor = conn.cursor()
    #     # try:
    #     value = args.configValue
    #     cursor.execute("SELECT config_id FROM configuration_master WHERE config_value=`%s`" % )
    #     dat = cursor.fetchone()[0]
    #     print(f'dat {dat}')

    #     return {
    #         "message":str(dat),
    #         "status code": 1 
    #     }
        # except:
        #     return {
        #         "message": "failed",
        #         "status code": 0
        #     }


class ConfigName(Resource):
    def __init__(self) :
        super().__init__()
        pass
    def get(self):
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT config_name FROM paypre_ecom.configuration_master WHERE config_name IS NOT null")
        result = cursor.fetchall()
        if result:
            data = []
            for r in result:
                data.append({
                    "configName":r[0]
                })

        if data:
                return {
                    'data':data,
                    'statusCode':1
                }
        else:
                return {
                    'message':"No data found",
                    'statusCode':1
                }
