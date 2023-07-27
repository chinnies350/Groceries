from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)
from app.libs import hashPassword, timestamp, myconverter

from bson import ObjectId
import datetime
import json



parser = reqparse.RequestParser()

# to manage all the payments
class UserRights(Resource):
    def __init__(self):
        parser.add_argument('roleAccessId', required=False)
        parser.add_argument("rightsList", required=False, type=dict, action="append")
        parser.add_argument('userRole', required=False)
        parser.add_argument('menuId', required=False)
        parser.add_argument('rights', required=False)
        parser.add_argument('editRights', required=False)
        parser.add_argument('deleteRights', required=False)
        parser.add_argument('viewRights', required=False)
        parser.add_argument('updateRights', required=False)
        parser.add_argument('importRights', required=False)
        self.uid = get_jwt_identity()
        self.user = get_jwt_claims()

    def post(self):

        created_by = self.uid
        created_date = datetime.datetime.now()

        conn = mysql.connect()
        cursor = conn.cursor()

        args = parser.parse_args()
        rightList = args.rightsList
        try:
            for i in range(len(args.rightsList)):
                print(args.rightsList[i]["menuId"],"mmmmmmmmmmmmmmmmmmmmmmmmmmmmm")                    
                cursor.execute("INSERT INTO user_access_rights(user_role,menu_id,rights,edit_rights,delete_rights,view_rights,"
                "update_rights,import_rights,created_by,created_date)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(
                    args.userRole,
                    rightList[i]["menuId"],
                    rightList[i]["rights"],
                    rightList[i]["editRights"],
                    rightList[i]["deleteRights"],
                    rightList[i]["viewRights"],
                    rightList[i]["updateRights"],
                    rightList[i]["importRights"],
                    created_by,
                    created_date
                    ))
                
                result = cursor.rowcount
                conn.commit()

            if result >= 1:
                return {
                    'message': 'inserted successfully',
                    'statusCode': 1
                }

            else:
                return {
                    'message': 'Data is not inserted',
                    'statusCode': 0
                }
         
            
        except Exception as e:
            print("exception isss", str(e))
            return{
                "statusCode": 0,
                "response": "Error Occured!"
            }
        finally:
            conn.close()

    def put(self):

        args = parser.parse_args()

        conn = mysql.connect()
        cursor = conn.cursor()

        updatedBy = self.uid
        updatedDate = datetime.datetime.now()

        cursor.execute("UPDATE user_access_rights SET user_role=%s,menu_id=%s,rights=%s,edit_rights=%s,delete_rights=%s,"
        "view_rights=%s,update_rights=%s,import_rights=%s, updated_by=%s, updated_date=%s WHERE role_access_id=%s", (            
            args.userRole,
            args.menuId,
            args.rights,
            args.editRights,
            args.deleteRights,
            args.viewRights,
            args.updateRights,
            args.importRights,
            updatedBy,
            updatedDate,
            args.roleAccessId
        ))

        conn.commit()
        conn.close()

        if cursor.rowcount>=1:
            return {
                'message': 'updated successfully',
                'statusCode': 1
            }

        else:
            return {
                'message': 'Data is not updated',
                'statusCode': 0
            }

    def get(self):
        data=[]
        args = parser.parse_args()

        conn = mysql.connect()
        cursor = conn.cursor()
        
        if args.userRole:
            cursor.execute("select * from user_access_rights WHERE user_role=%s",args.userRole)
            result = cursor.fetchall()
            for r in result:
                cursor.execute("select config_value from configuration_master WHERE config_id=%s",r[2])
                menu_name = cursor.fetchone()[0]
                data.append(
                    {   
                        "roleAccessId":r[0],
                        "userRole":r[1],
                        "menuId":r[2],
                        "menuName":menu_name,
                        "rights":r[3],
                        "editRights":r[4],
                        "deleteRights":r[5],
                        "viewRights":r[6],
                        "updateRights":r[7],
                        "importRights":r[8]
                    }
                )
            if data:  
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
            cursor.execute("select Distinct(user_role) from user_access_rights ")
            result = cursor.fetchall()
            conn.commit()
            conn.close()   

            for i in result:
                data.append({
                    "userRole":i[0]
                })  
            if data:  
                return {
                    'data': data,
                    'statusCode':1
                }
            else:
                return {
                    'message':"No data found",
                    "statusCode":0
                }  

        

    def delete(self):

        args = parser.parse_args()

        conn = mysql.connect()
        cursor = conn.cursor()

        # cursor.execute("update user_access_rights set status='D' where payment_id=%s and merchant_id=%s",(
        #     args.paymentId, 
        #     args.merchantId
        # ))
        cursor.execute("DELETE FROM user_access_rights WHERE role_access_id=%s",args.roleAccessId)
        conn.commit()
        conn.close()

        if cursor.rowcount>=1:
            return {
                'message': 'deleted successfully',
                'statusCode': 1
            }

        else:
            return {
                'message': 'Data is not deleted',
                'statusCode': 0
            }