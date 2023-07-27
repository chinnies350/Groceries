from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql
from pprint import pprint

parser = reqparse.RequestParser()


class StockList(Resource):
    def __init__(self) :
        super().__init__()
        parser.add_argument("merchantId", required=False)
        parser.add_argument("categoryId", required=False)
        parser.add_argument("subCategoryId", required=False)

    def get(self):
        args = parser.parse_args()
        conn = mysql.connect()
        cursor = conn.cursor()
        if args.categoryId and args.merchantId:
                cursor.execute("SELECT products.*,categories.category_name  FROM products INNER JOIN categories ON products.category_id = categories.category_id WHERE no_of_items <= 0 AND products.category_id=%s AND products.merchant_id=%s",(args.categoryId, args.merchantId))
        elif args.subCategoryId and args.merchantId:
            cursor.execute("SELECT products.*,categories.category_name  FROM products INNER JOIN categories ON products.category_id = categories.category_id WHERE no_of_items <= 0 AND sub_category_id=%s AND products.merchant_id=%s",(args.subCategoryId, args.merchantId))
        elif args.merchantId:
            cursor.execute("SELECT products.*,categories.category_name  FROM products INNER JOIN categories ON products.category_id = categories.category_id WHERE no_of_items <= 0 AND products.merchant_id=%s",(args.merchantId))
        elif args.categoryId:
            cursor.execute("SELECT products.*,categories.category_name  FROM products INNER JOIN categories ON products.category_id = categories.category_id WHERE no_of_items <= 0 AND products.category_id=%s",(args.categoryId))
        elif args.subCategoryId:
            cursor.execute("SELECT products.*,categories.category_name  FROM products INNER JOIN categories ON products.category_id = categories.category_id WHERE no_of_items <= 0 AND sub_category_id=%s",(args.subCategoryId))
        else:
            cursor.execute("SELECT products.*,categories.category_name  FROM products INNER JOIN categories ON products.category_id = categories.category_id WHERE no_of_items <= 0")
        product_details = cursor.fetchall()
        if product_details:
            products = []
            sampleDic = {}
            for i, j in enumerate(product_details):
                sampleDic[i]=j

            pprint(sampleDic)
            for product in product_details:
                
                cursor.execute("SELECT config_value FROM configuration_master WHERE config_id=%s", product[7])
                uom_value = cursor.fetchone()
                if uom_value:
                    uom_value = uom_value[0]
                products.append(
                    {"productId": product[0], 
                    "merchantId": product[1],
                    "categoryId": product[2],
                    "subCategoryId": product[3], 
                    "productName": product[4],
                    "description": product[5], 
                    "productQuantity": str(product[6]), 
                    "productUom": uom_value,
                    "productUomId":str(product[7]),
                    "productMrp": str(product[8]),
                    "productSellingPrice": str(product[9]), 
                    "productImage": product[10], 
                    "bestSelling": product[11],
                    "productStatus": product[12],
                    "no_of_items": product[17],                                  
                    "categoryName": product[18],
                                        })
            return {
                    "data": products,
                    "statusCode": 1
                }

        else:
            return {
                    'message': 'data not found',
                    'statusCode': 0
                    }


