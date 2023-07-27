
# import MySQLdb
# threadsafety = 1

# # mysql db connection


# class MysqlConnnection:
#     def __init__(self, app=None):
#         self.app = app
#         if app is not None:
#             self.init_app(app)

#     def init_app(self, app):

#         print(app.config['MYSQL_DATABASE_NAME'], app.config['MYSQL_DATABASE_USER'], app.config['MYSQL_DATABASE_PWD'], app.config['MYSQL_DATABASE_LINK'])

#         self.conn = MySQLdb.connect(app.config['MYSQL_DATABASE_NAME'], app.config['MYSQL_DATABASE_USER'], app.config['MYSQL_DATABASE_PWD'], app.config['MYSQL_DATABASE_LINK'])

