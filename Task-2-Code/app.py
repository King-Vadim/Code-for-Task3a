from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy import Nullable
from datetime import datetime, time
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

#initialise flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_BINDS"] = {
    'products_db': 'sqlite:///products.db',
    'orders_db': 'sqlite:///orders.db'
    }
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "a4jb2mfkah34lasmfsn21ma"

wsgi_app = app.wsgi_app

#####LOGIN SYSTEM BEGIN#####

#initialise database & login manager
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

#user model
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    accounttype = db.Column(db.String(250), nullable=False)

###Database for products###
class products(db.Model):
    __bind_key__ = 'products_db'
    id = db.Column(db.Integer, primary_key=True)
    pname = db.Column(db.String(250), nullable=False)
    price = db.Column(db.Numeric(precision=4, scale=2), nullable=False)
    pdesc = db.Column(db.String(250), nullable=False)
    ptype = db.Column(db.String(250), nullable=False)

###Database for orders###
class orders(db.Model):
    __bind_key__ = 'orders_db'
    id = db.Column(db.Integer, primary_key=True)
    ordername = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    postalcode = db.Column(db.String(10), nullable=False)
    productname = db.Column(db.String(50),nullable=False)
    quantity = db.Column(db.Integer,nullable=False)

#create database
with app.app_context():
    db.create_all()

#load user for login
@login_manager.user_loader
def loaduser(user_id):
    return Users.query.get(int(user_id))

#register page
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == "POST":
        name = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        accounttype = request.form.get("account-type")

        if Users.query.filter_by(email=email).first():
            return render_template("signup.html", error="email already exists")
        hashedpassword = generate_password_hash(password,method="pbkdf2:sha256")

        new_user = Users(username=name, email=email, password=hashedpassword, accounttype=accounttype)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("signup.html")

#login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = Users.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.accounttype == "customer":
                return redirect(url_for("cdashboard"))
            elif user.accounttype == "producer":
                return redirect(url_for("pdashboard"))
        else:
            return render_template("login.html", error="Invalid email or password")
    return render_template("login.html")

#logout page
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('shophome'))

#####LOGIN SYSTEM END#####

#home page
@app.route('/')
def home():
    return render_template('index.html')

#about us page
@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

#contact us page
@app.route('/contactus', methods=['GET', 'POST'])
def contactus():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    conn = sqlite3.connect("enquiry.db")
    cur = conn.cursor()

    cur.execute("INSERT INTO enquiry (name, email, message) VALUES (?,?,?)", (name,email,message))
    conn.commit()
    conn.close()

    return render_template('contactus.html')

#main shop page
@app.route('/shophome')
def shophome():
    return render_template('shophome.html')

###CUSTOMER DASHBOARD PAGES BEGIN###


#dashboard for customers
@app.route('/cdashboard')
@login_required
def cdashboard():
    if current_user.accounttype != "customer":
        return "Access denied: customers only", 403
    print(f"Current user: {current_user.email}")
    return render_template('customer-dashboard.html')

@app.route('/cdashboardorders')
@login_required
def cdashboard_order():
    if current_user.accounttype != "customer":
        return "Access denied: customers only", 403
    print(f"Current user: {current_user.email}")
    all_orders = orders.query.all()
    return render_template("cdashboard-orders.html", orders=all_orders)

#CUSTOMER DASHBOARD PAGES END###

###PRODUCER DASHBOARD PAGES BEGIN###

#main dashboard page for producers
@app.route('/pdashboard')
@login_required
def pdashboard():
    if current_user.accounttype != "producer":
        return "Access denied: producer only", 403
    print(f"Current user: {current_user.email}")
    return render_template('producer-dashboard.html')

#pdashboard view all stock page
@app.route('/pdashboardview')
@login_required
def pdashboard_view():
    if current_user.accounttype != "producer":
        return "Access denied: producer only", 403
    all_products = products.query.all()
    return render_template('pdashboard-view.html', products=all_products)

#pdashboard add new item to stock page
@app.route('/pdashboardadd', methods=["GET","POST"])
@login_required
def pdashboard_add():
    if current_user.accounttype != "producer":
        return "Access denied: producer only", 403
    if request.method == 'POST':
        pname = request.form.get("pname")
        ptype = request.form.get("product-type")
        pdesc = request.form.get("desc")
        price = request.form.get("price")

        new_product = products(pname=pname, price=price, pdesc=pdesc, ptype=ptype)
        db.session.add(new_product)
        db.session.commit()

        return render_template('pdashboard-add.html')

    return render_template('pdashboard-add.html')

#pdashboard modify a item in stock page
@app.route('/pdashboardmodify')
@login_required
def pdashboard_modify():
    if current_user.accounttype != "producer":
        return "Access denied: producer only", 403

    if request.method == 'POST':
        pname = request.form.get("pname")
        price = request.form.get("price")
        pdesc = request.form.get("desc")

    all_products = products.query.all()
    return render_template('pdashboard-modify.html', products=all_products)

@app.route('/update-product', methods=['POST'])
def update_product():
    p_id = request.form.get('id')
    name = request.form.get('pname')
    price = request.form.get('price')
    desc = request.form.get('pdesc')

    product = products.query.get_or_404(p_id)

    product.pname = name
    product.price = price
    product.pdesc = desc
    db.session.commit()

    return redirect(url_for("pdashboard_modify"))

#pdashboard remove item from stock page
@app.route('/pdashboardremove')
@login_required
def pdashboard_remove():
    if current_user.accounttype != "producer":
        return "Access denied: producer only", 403
    all_products = products.query.all()
    return render_template('pdashboard-remove.html', products=all_products)

@app.route('/delete-product/<int:id>', methods=['POST'])
def delete_product(id):
    product_to_delete = products.query.get_or_404(id)

    try:
        db.session.delete(product_to_delete)
        db.session.commit()
        flash("Product removed successfully!")
    except:
        db.session.rollback()
        flash("There was an error deleting that product.")

    return redirect(url_for('pdashboard_remove'))


###PRODUCER DASHBOARD PAGES END###

###PRODUCT PAGES BEGIN###

@app.route('/product/fruit-basket', methods=['POST', 'GET'])
def fruitbasket():
    total_price = 0
    if request.method == 'POST':
        qty = request.form.get('quantity')
    return render_template('product-fruit-basket.html', total_price=total_price)

@app.route('/product/veg-basket', methods=['POST', 'GET'])
def vegbasket():
    total_price = 0
    if request.method == 'POST':
        qty = request.form.get('quantity')
    return render_template('product-veg-basket.html', total_price=total_price)

@app.route('/product/variety-basket', methods=['POST', 'GET'])
def varietybasket():
    total_price = 0
    if request.method == 'POST':
        qty = request.form.get('quantity')
    return render_template('product-mix-basket.html', total_price=total_price)

###PRODUCT PAGES END###

###ORDERING/CHECKOUT PAGES BEGIN###

@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    qty = int(request.form.get("quantity", 0))
    productname = request.form.get("productname")
    price = int(request.form.get("price", 0))

    total_price = qty * price
    return render_template('confirm.html', quantity=qty, productname=productname, total_price=total_price)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'GET' or (request.method == 'POST' and 'fullname' not in request.form):
        qty = request.form.get("quantity", request.args.get("quantity", 0, type=int), type=int)
        productname = request.form.get("productname", request.args.get("productname"))
        price = request.form.get("price", request.args.get("price", 0, type=int),type=int)

        return render_template('checkout.html', quantity=qty, productname=productname, total_price=price)

    if request.method == 'POST':
        new_order = orders(ordername=request.form.get("fullname"),
                         email=request.form.get("email"),
                         address=request.form.get("address"),
                         city=request.form.get("city"),
                         postalcode=request.form.get("pc"),
                         productname=request.form.get("productnamec"),
                         quantity=request.form.get("quantityc",0,type=int)
                         )
        db.session.add(new_order)
        db.session.commit()
        return redirect(url_for("checkoutcomplete"))


@app.route('/checkoutcomplete', methods=['GET', 'POST'])
def checkoutcomplete():
    return render_template('checkout-complete.html')

###ORDERING/CHECKOUT PAGES END###


if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
