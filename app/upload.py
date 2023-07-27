from flask_restful import Resource, reqparse
from app import bcrypt, jwt, image_url, UPLOAD_FOLDER
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)
from app.libs import hashPassword, timestamp, myconverter

import datetime
import socket
import os
from werkzeug.datastructures import FileStorage
from app import *

parser = reqparse.RequestParser()
parser.add_argument('next', help='', required=False)


class Upload(Resource):
    # @jwt_required
    def __init__(self):
        parser.add_argument('image', required=False, type=FileStorage, location='files')
        # self.uid = get_jwt_identity()
        # self.user = get_jwt_claims()

    def post(self):
        data = parser.parse_args()
        image = data['image']
        imageType = image.filename.split('.')[-1]
        ti = str(datetime.datetime.now()).split(' ')[0]
        imageName = image.filename.replace(imageType, f'{ti}.{imageType}')
        image.save(os.path.join(UPLOAD_FOLDER, imageName))
        # img = image_url + str(image.filename)
        img = image_url + str(imageName)

        return {
                    'data': img,
                    'statusCode': 1
                }

