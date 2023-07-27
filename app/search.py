from flask_restful import Resource, reqparse
from app import bcrypt, jwt, mysql
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims,
                                get_current_user)
from app.libs import timestamp


parser = reqparse.RequestParser()
parser.add_argument('next', help='', required=False)




# autocomplete api

class SearchItem(Resource):
    # @jwt_required
    def __init__(self):
        parser.add_argument('searchItem', required=False)
        parser.add_argument('merchantId', required=False)
        parser.add_argument("userId", required=False)

        # self.uid = get_jwt_identity()
        # self.user = get_jwt_claims()

    def get(self):
        try:
            args = parser.parse_args()

            conn = mysql.connect()
            cursor = conn.cursor()

            if args.searchItem and args.merchantId:
                cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
                "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
                "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
                "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
                "Inner join categories on products.category_id = categories.category_id where products.merchant_id=%s and product_name LIKE %s  ", (args.userId, args.userId,args.merchantId, args.searchItem))
            
            elif args.merchantId:
                cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
                "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
                "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
                "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
                "Inner join categories on products.category_id = categories.category_id where products.merchant_id=%s", (args.userId, args.userId,args.merchantId))
               

            elif args.searchItem:
                cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
                "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
                "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 "
                "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
                "Inner join categories on products.category_id = categories.category_id where product_name LIKE %s ", (args.userId, args.userId,args.searchItem))
              

            else:
    
                cursor.execute("select products. *, configuration_master.config_value, categories.category_name, "
                "IF( %s IN (SELECT UC.user_id FROM products PP INNER JOIN user_cart UC ON UC.product_id = PP.product_id WHERE PP.product_id = products.product_id ) , 'Y','N') AS id, "
                "IF( %s IN (SELECT WC.user_id AS 'YES' FROM products PP INNER JOIN user_wishlist WC ON WC.product_id = PP.product_id WHERE PP.product_id = products.product_id ), 'Y','N') AS id1 " 
                "from products INNER JOIN configuration_master ON products.product_uom = configuration_master.config_id "
                "Inner join categories on products.category_id = categories.category_id",(args.userId, args.userId,))

            result = cursor.fetchall()
            products = []
            for product in result:
                cursor.execute("SELECT sub_category_name FROM sub_categories WHERE sub_category_id=%s",(product[3]))
                subName = cursor.fetchone()
                products.append({
                    "productId": product[0],
                    "merchantId":product[1], 
                    "categoryId": product[2],
                    "subCategoryId": product[3], 
                    "productName": product[4],
                    "description": product[5], 
                    "productQuantity": float(product[6]),
                    "productUomId": product[7], 
                    "productMrp": float(product[8]),
                    "productSellingPrice": float(product[9]), 
                    "productImage": product[10], 
                    "bestSelling": product[11],
                    "productStatus": product[12], 
                        
                    "productUom": product[18],
                    "categoryName": product[19], 
                    "subCategoryName":(subName[0] if subName else subName),
                    "cartExist":product[20],
                    "wishlistExist":product[21]

                })
            conn.commit()

            if products:
                return {
                    'data': products,
                    'statusCode': 1
                }
            else:
                return {
                    'data': 'no data',
                    'statusCode': 1
                }

            

               
        except Exception as e:
            print(e)
            return {"message": e, "statusCode": 0}

    

class SearchSeller(Resource):
    # @jwt_required
    def __init__(self):
        parser.add_argument(
            'searchSeller', help='clientId is required', required=False)



        self.uid = get_jwt_identity()

        self.user = get_jwt_claims()


    def post(self):
        try:
            data = parser.parse_args()

            conn = mysql.connect()
            cursor = conn.cursor()

            if data.get('searchSeller'):


                # cur.execute("SELECT product_name FROM products WHERE product_name LIKE 'jui%';")

                cursor.execute("select products.*, categories.category_name from products INNER JOIN sellers ON products.seller_id= sellers.seller_id Inner join categories on products.category_id = categories.category_id where seller_name LIKE '"+data['searchSeller']+"%'")

                result = cursor.fetchall()

                print(result)

                products=[]

                for product in result:
                    data = {"productId":product[0], "categoryId":product[1],  "productName":product[3],"description":product[4],"productQuantity":float(product[5]),"productMrp":float(product[7]),"productImage":product[9],"bestSelling":product[10],"productStatus":product[11],"categoryName":product[17]}

                    products.append(data)


                conn.commit()

                if data!=[]:


                    return {

                                'data': products,
                                'statusCode': 1
                            }
                else:
                    return {

                        'data': 'no data',
                        'statusCode': 1
                    }
            else:

                cursor.execute("select products.*, categories.category_name from products INNER JOIN sellers ON products.seller_id= sellers.seller_id Inner join categories on products.category_id = categories.category_id")

                result = cursor.fetchall()

                print(result)

                products=[]

                for product in result:
                    data = {"productId":product[0], "categoryId":product[1],  "productName":product[3],"description":product[4],"productQuantity":float(product[5]),"MRP":float(product[7]),"productImage":product[9],"bestSelling":product[10],"productStatus":product[11],"categoryName":product[17]}

                    products.append(data)


                conn.commit()

                if data!=[]:


                    return {

                                'data': products,
                                'statusCode': 1
                            }
                else:
                    return {

                        'data': 'no data',
                        'statusCode': 1
                    }


        except Exception as e:
            return {"message": e, "statusCode": 0}