from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)
from app.libs import timestamp


parser = reqparse.RequestParser()
parser.add_argument('next', help='', required=False)



# to manage the contact detais of the store
class Contact(Resource):
    @jwt_required
    def __init__(self):
        parser.add_argument(
            'terms', help='clientId is required', required=False)
        parser.add_argument(
            'aboutus', help='entity is required', required=False)
        parser.add_argument(
            'facebook', help='branch is required', required=False)
        parser.add_argument(
            'whatsapp', help='title is required', required=False)
        parser.add_argument(
            'twitter', help='description is required', required=False)
        parser.add_argument(
            'youtube', help='description is required', required=False)
        parser.add_argument(
            'contactNo', help='description is required', required=False)
        parser.add_argument(
            'address1', help='description is required', required=False)
        parser.add_argument(
            'address2', help='description is required', required=False)
        parser.add_argument(
            'policy', help='description is required', required=False)
        parser.add_argument(
            'email', help='description is required', required=False)
        parser.add_argument(
            'minDelChargeLimit', help='description is required', required=False)
        parser.add_argument(
            'delCharges', help='description is required', required=False)
        parser.add_argument(
            'gstPercentage', help='description is required', required=False)
        parser.add_argument(
            'contactStatus', help='contact status is required', required=False)

        parser.add_argument(
            'id', help='id is required', required=False)



        self.uid = get_jwt_identity()

        self.user = get_jwt_claims()

    # insert contact details
    def post(self):
        try:

            data = parser.parse_args()

            print(data)



            createdBy = self.uid
            createdDate = timestamp()

            conn = mysql.connect()
            cursor = conn.cursor()



            cursor.execute("insert into contact_details(terms,aboutus,facebook,whatsapp,twitter,youtube,contact_no,address_line1,address_line2,policy,email,min_del_charge_limit,delivery_charges,gst_percentage,contact_status,created_by,created_date) value (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(data['terms'], data['aboutus'], data['facebook'],data['whatsapp'],data['twitter'],data['youtube'],data['contactNo'],data['address1'],data['address2'],data['policy'],data['email'],(data['minDelChargeLimit']),(data['delCharges']),(data['gstPercentage']),data['contactStatus'],createdBy,createdDate))

            conn.commit()

            return {

                        'message': 'data inserted successfully',
                        'statusCode': 1
                    }
        except Exception as e:
            return {"message": e, "statusCode": 0}

    # view contact details

    def get(self):
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("select * from contact_details")

        result = cursor.fetchall()
        conn.commit()



        data=[]

        for r in result:
            data_dt = {"contactId": r[0], "terms": r[1], "aboutus": r[2], "facebook": r[3], "whatsapp": r[4],
                       "twitter": r[5], "youtube": r[6], "contactNo": r[7], "address1": r[8], "address2": r[9],
                       "policy": r[10], "email": r[11], "minDelChargeLimit": float(r[12]),
                       "deliveryCharges": float(r[13]), "gstPercentage": float(r[14]), "contactStatus": r[15]}
            data.append(data_dt)
        return {
            'data': data,
            'statusCode':1
        }

    # update contact details

    def put(self):
        try:
            data = parser.parse_args()

            print(data)

            updatedBy = self.uid
            updatedDate = timestamp()

            conn = mysql.connect()
            cursor = conn.cursor()



            cursor.execute("update contact_details set terms='" + data['terms'] + "', aboutus='" + data[
                'aboutus'] + "',facebook='" + data['facebook'] + "', whatsapp='" + data[
                                        'whatsapp'] + "',twitter='" + data['twitter'] + "',youtube='"+data['youtube']+"',contact_no='" + data[
                                        'contactNo'] + "',address_line1='" + data[
                                        'address1'] + "',address_line2='" + data[
                                        'address2'] + "',policy='" + data[
                                        'policy'] + "',email='" + data[
                                        'email'] + "',min_del_charge_limit='"+data['minDelChargeLimit']+"',delivery_charges='"+data['delCharges']+"',gst_percentage='"+data['gstPercentage']+"',contact_status='"+data['contactStatus']+"',updated_by='" + updatedBy + "', updated_date='"+updatedDate+"' where contact_id='" + data['id'] + "'")



            result = cursor.rowcount

            conn.commit()


            if result != 0:

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
            return {"message": e, "statusCode": 0}

    # delete contact details

    def delete(self):

        data = parser.parse_args()

        id = data['id']

        conn = mysql.connect()
        cursor = conn.cursor()



        cursor.execute("UPDATE contact_details SET contact_status='D' WHERE contact_id ='"+data['id']+"'")


        conn.commit()



        result = cursor.rowcount


        return {

                'message': 'deleted successfully',
                'statusCode': 1

            }
