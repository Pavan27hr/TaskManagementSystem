from flask import Flask
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Your-Secret-Key'
app.config['MYSQL_HOST'] = 'Your-DB-HOST'
app.config['MYSQL_USER'] = 'Your-DB-User'
app.config['MYSQL_PASSWORD'] = 'Your-DB-Passwordd'
app.config['MYSQL_DB'] = 'Your-DB-Name'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

from app import routes
