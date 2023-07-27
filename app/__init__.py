import os
from flask import Flask, request, jsonify

from flask_restful import Api, Resource

from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager


from app.config import Config

from flaskext.mysql import MySQL
from flask_mail import Mail, Message

api = Api()

bcrypt = Bcrypt()
jwt = JWTManager()
mysql = MySQL()

UPLOAD_FOLDER = "D:/previous app/Groceries/static"
image_url="http://192.168.1.17:6000/static/"


def create_app(test_config=None):
    app = Flask(__name__, 
    static_url_path="/static", 
    static_folder="D:/sahaya/Projects/Groceries/static", 
    instance_relative_config=True)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.config.from_object(Config)

    app.config['MYSQL_DATABASE_USER'] = "python"
    app.config['MYSQL_DATABASE_PASSWORD'] = "Pre*270900"
    app.config['MYSQL_DATABASE_DB'] = "paypre_ecom"
    app.config['MYSQL_DATABASE_HOST'] = "192.168.1.221"


    mysql.init_app(app)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # import python files
    from app.auth import UserLogin,SecretResource, Checkuser, Randomuser,Checkseller
    from app.registration import Registration, Forgotpassword, ChangePassword,SellerRegistration
    from app.contact import Contact
    from app.users import Users, TotalUsers
    from app.admin import Info,SellerTransactions
    from app.special_offer import Special
    from app.fruitveg_config import Configuration, ConfigName
    from app.upload import Upload
    from app.getalldata import Alloffers
    from app.banners import Banners
    from app.categories import Categories, Subcategory, Listcategories,ActiveCategories
    from app.products import Products
    from app.wishlist import Wishlist
    from app.orders import Orders, Deliverydetails, Paymentorder, Pendinglist, BulkOrder,TodayTransactionCount,TodayTransactionList,TodayPayment, AssignedDelivery
    from app.cart import Cart, CartCount
    from app.feedback import Feedback
    from app.count_api import Deliverycount, Topten,ToptenSellers,ToptenSellersAmount
    from app.otp import Otp
    from app.search import SearchItem,SearchSeller
    from app.merchants_details import Merchant
    from app.payment_details import Payment, ActivePayment
    from app.user_rights import UserRights
    from app.configuration_master import ConfigurationMaster
    from app.sms import SMS
    from app.features import Features
    from app.android_merchant import AndroidMerchant
    from app.ordersfilters import OrdersFilters
    from app.users import Particularuser
    from app.users import Defaultaddress
    from app.orders import LargeOrders
    from app.banners import ActiveBanners
    from app.products import ActiveProducts
    from app.special_offer import ActiveSpecialOffers
    from app.sub_categories import SubCategories, ActiveSubCategory
    from app.stockEnter import StockEntry
    from app.stockList import StockList

    # declaration of API routes
    api.add_resource(SearchItem, '/searchItem', endpoint="search")
    api.add_resource(Otp, '/otp', endpoint="otp")
    api.add_resource(UserLogin, '/login', endpoint="userLogin")
    api.add_resource(SecretResource, '/token')
    api.add_resource(Randomuser, '/random', endpoint="random")
    api.add_resource(Registration, '/registration', endpoint="signup")
    api.add_resource(SellerRegistration, '/sellerRegistration', endpoint="seller_signup")
    api.add_resource(Contact, '/contactDetails', endpoint="contactDetails")
    api.add_resource(Users, '/userDetails', endpoint="userdetails")
    api.add_resource(Particularuser, '/particularUser', endpoint="particular_user")
    api.add_resource(Defaultaddress, '/defaultAddress', endpoint="defaultAddress")
    api.add_resource(Checkuser, '/checkusers', endpoint="check_users")
    api.add_resource(TotalUsers, '/totalUsers', endpoint="totalUsers")
    api.add_resource(Banners, '/banners', endpoint="banners")
    api.add_resource(Special, '/specialOffer', endpoint="special_offer")   
    api.add_resource(Alloffers, '/getAllOffers', endpoint="get_all_offers")
    api.add_resource(Forgotpassword, '/forgotPassword', endpoint="forgot")
    api.add_resource(ChangePassword, '/changePassword', endpoint="change")
    api.add_resource(Configuration, '/configuration', endpoint="config")
    api.add_resource(Upload, '/uploadImage', endpoint="upload_image")
    api.add_resource(Categories, '/categories', endpoint="category")
    api.add_resource(Subcategory, '/subCategories', endpoint="sub_category")
    api.add_resource(Products, '/products', endpoint="product")
    api.add_resource(Wishlist, '/wishlist', endpoint="wishlist")
    api.add_resource(Orders, '/orders', endpoint="orders")
    api.add_resource(BulkOrder, '/multiOrders', endpoint="multi_orders")
    api.add_resource(Pendinglist, '/pendingList', endpoint="pending_list")    
    api.add_resource(Deliverycount, '/deliverycount', endpoint="delivery_count")
    api.add_resource(Topten, '/topTen', endpoint="top_ten")
    api.add_resource(ToptenSellers, '/topTenSellers', endpoint="top_ten_sellers")
    api.add_resource(ToptenSellersAmount, '/topTenSellersAmount', endpoint="top_ten_sellers_amount")
    api.add_resource(Paymentorder, '/paymentOrder', endpoint="payment_order")
    api.add_resource(Deliverydetails, '/deliveryDetails', endpoint="delivery_details")
    api.add_resource(Cart, '/cart', endpoint="cart")
    api.add_resource(CartCount, '/cartCount', endpoint="cartCount")
    api.add_resource(Feedback, '/feedback', endpoint="feedback")
    api.add_resource(Merchant, '/merchantDetails', endpoint="merchantDetails")
    api.add_resource(SearchSeller, '/searchSeller', endpoint="searchseller")
    api.add_resource(Checkseller, '/checkSeller', endpoint="checkSeller")
    api.add_resource(Info, '/info', endpoint="info")
    api.add_resource(SellerTransactions, '/transaction', endpoint="transaction")
    api.add_resource(TodayTransactionCount, '/todayTransactionCount', endpoint="todayTransactionCount")
    api.add_resource(TodayTransactionList, '/todayTransactionList', endpoint="todayTransactionList")
    api.add_resource(TodayPayment, '/todayPayment', endpoint="todayPayment")
    api.add_resource(Payment, '/paymentDetails', endpoint="paymentDetails")
    api.add_resource(UserRights, '/userRights', endpoint="userRights")
    api.add_resource(ConfigurationMaster, '/configMaster', endpoint="configMaster")
    api.add_resource(SMS, '/sms', endpoint="sms")
    api.add_resource(Features, '/features', endpoint="features")
    api.add_resource(AndroidMerchant, '/androidMerchant', endpoint="androidMerchant")
    api.add_resource(OrdersFilters, "/ordersFilters", endpoint="ordersFilters")
    api.add_resource(LargeOrders, "/largeOrders", endpoint="largeOrders")
    api.add_resource(ActiveBanners, "/activeBanners", endpoint="activeBanners")
    api.add_resource(ActiveProducts, "/activeProducts", endpoint="activeProducts")
    api.add_resource(ActiveSpecialOffers, "/activeSpecialOffers", endpoint="activeSpecialOffers")
    api.add_resource(SubCategories, "/subCategory", endpoint="/subCategory")
    api.add_resource(ActiveSubCategory,"/activeSubCategory",endpoint="activeSubCategory")
    api.add_resource(StockEntry, "/stockEntry", endpoint="stockEntry")
    api.add_resource(StockList, "/stockList", endpoint="stockList")
    api.add_resource(ConfigName, "/configName", endpoint="configName")
    api.add_resource(ActivePayment, "/activePayment", endpoint="activePayment")
    api.add_resource(Listcategories, "/listcategories", endpoint="listcategories")
    api.add_resource(ActiveCategories,"/activeCategories", endpoint="/activeCategories")
    api.add_resource(AssignedDelivery,"/assignedDelivery", endpoint="/assignedDelivery")




    
    # allow access for cors

    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):

        response.headers.add('Content-Type', 'application/json')
        response.headers.add('Access-Control-Allow-Origin', '*')

        response.headers.add('Access-Control-Allow-Headers', 'authorization,content-type,x-auth-token')

        response.headers.add('Access-Control-Allow-Headers', 'x-auth-token,Authorization,authorization,content-type')

        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,get,post,delete,put,options')

        return response

    from app.errors.handlers import errors
    app.register_blueprint(errors)

    api.init_app(app)
    jwt.init_app(app)

    return app
