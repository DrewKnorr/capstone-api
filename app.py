from flask import Flask, request, jsonify, send_file
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_heroku import Heroku
from zipfile import ZipFile

from os import listdir
from os.path import isfile, join

import os
import time
import random
import datetime
import io
import pathlib
from werkzeug.utils import secure_filename


app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"]="postgres://fokcqswvoacwjk:0ed441d457d7049d3673557cbb6a93bdd9132545cb85c9a99ed3295ba0b297ea@ec2-107-21-209-1.compute-1.amazonaws.com:5432/ddnnuguma3dfrb"

heroku = Heroku(app)
db = SQLAlchemy(app)

UPLOAD_FOLDER='uploads\orderFiles'
ALLOWED_EXTENSIONS= set(['.stl','.obj'])

app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER



class Users_support(db.Model):
    id= db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    fname = db.Column(db.String(80),nullable=False)
    lname = db.Column(db.String(80),nullable=False)
    email = db.Column(db.String(200),nullable=False, unique=True)
    role = db.Column(db.String(25), nullable=False)

    def __init__(self,username,password,fname, lname,email,role):
        self.username = username
        self.password = password
        self.fname = fname
        self.lname = lname
        self.email = email
        self.role= role


class Users(db.Model):
    id= db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    fname = db.Column(db.String(80),nullable=False)
    lname = db.Column(db.String(80),nullable=False)
    email = db.Column(db.String(200),nullable=False, unique=True)
    role = db.Column(db.String(25), nullable=False)
    email_auth = db.Column(db.Boolean,default=False, nullable=False)
    status= db.Column(db.Boolean,default=False, nullable=False)

    
    def __init__(self,username,password,fname, lname,email,role,email_auth,status):
        self.username = username
        self.password = password
        self.fname = fname
        self.lname = lname
        self.email = email
        self.role= role
        self.email_auth = email_auth
        self.status = status


class Orders(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    printmaster =  db.Column(db.String(80))
    file_path = db.Column(db.String(200),nullable=False)
    material = db.Column(db.String(15), nullable=False)
    resolution = db.Column(db.Float, nullable=False)
    color = db.Column(db.String(15), nullable=False)
    order_num = db.Column(db.String(25),nullable=False,unique=True)
    print_time = db.Column(db.String(100))
    cost = db.Column(db.Float)
    status = db.Column(db.String(25),nullable=False)
    date_of_order = db.Column(db.DateTime())

    def __init__(self, username, printmaster,file_path,material,resolution,color,order_num,print_time,cost,status,date_of_order):
        self.username = username
        self.printmaster = printmaster
        self.file_path = file_path
        self.material = material
        self.resolution = resolution
        self.color = color
        self.order_num = order_num
        self.print_time = print_time
        self.cost = cost
        self.status = status
        self.date_of_order = date_of_order


class PrintMasterRegisterQueue(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(80),nullable=False)
    role = db.Column(db.String(10),nullable=False)
    printer = db.Column(db.String(45),nullable=False)
    experiance = db.Column(db.Integer,nullable=False)
    def __init__(self,username,role,printer , experiance):
        self.username=username
        self.role=role
        self.printer = printer
        self.experiance = experiance


class PrintMasterQueue(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(80),nullable=False)
    status = db.Column(db.Boolean)
    position_in_queue = db.Column(db.Integer)

    def __init__(self,username, status, position_in_queue):
        self.username=username
        self.status=status
        self.position_in_queue=position_in_queue


        
class Payments(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    f_name = db.Column(db.String(80),nullable=False)
    l_name = db.Column(db.String(80),nullable=False)
    street_addr = db.Column(db.String(200),nullable=False)
    state= db.Column(db.String(100),nullable=False)
    zip_code = db.Column(db.Integer, nullable=False)
    country = db.Column(db.String(100),nullable=False)
    cc = db.Column(db.Integer,nullable=False)
    experation = db.Column(db.String(10),nullable=False)
    cvv = db.Column(db.Integer,nullable=False)
    cost = db.Column(db.Float,nullable=False)
    print_master = db.Column(db.String(100),nullable=False)
    order_num = db.Column(db.String(100), nullable=False, unique=True)
    date_of_payment = db.Column(db.DateTime())

    def __init__(self,f_name,l_name,street_addr,state,zip_code,country,cc,experation,cvv,cost,print_master,order_num,date_of_payment):
        self.f_name=f_name
        self.l_name=l_name
        self.street_addr=street_addr
        self.state = state
        self.zip_code =zip_code
        self.country = country
        self.cc = cc 
        self.experation = experation
        self.cvv = cvv
        self.cost = cost
        self.print_master = print_master
        self.order_num = order_num
        self.date_of_payment = date_of_payment



@app.route("/get/pm/queue", methods=["GET"])
def get_pm_queue():
    pm_queue = db.session.query(PrintMasterQueue.id, PrintMasterQueue.username, PrintMasterQueue.status, PrintMasterQueue.position_in_queue).all()

    return jsonify(pm_queue)




@app.route("/get/all/users", methods=["GET"])
def get_all_users():
    user_items = db.session.query(
        Users.id, 
        Users.username, 
        Users.password,Users.fname, 
        Users.lname,Users.email, 
        Users.role, 
        Users.email_auth, 
        Users.status
        ).all()

    

    return jsonify(user_items)


@app.route("/get/all/support/users", methods=["GET"])
def get_support_users():
    support_users = db.session.query(
        Users_support.id, 
        Users_support.username, 
        Users_support.password,
        Users_support.fname, 
        Users_support.lname,
        Users_support.email, 
        Users_support.role, 
        Users_support.email
        ).all()



    return jsonify(support_users)

@app.route("/get-standard-users", methods=["GET"])
def get_all_standard_users():
    user_items = db.session.query(
        Users.id,
        Users.username, 
        Users.role
        ).filter(Users.role=='user').all()

    return jsonify(user_items)

@app.route("/get-admin-users", methods=["GET"])
def get_all_admin_users():
    user_items = db.session.query(Users.id,Users.username, Users.role).filter(Users.role=='admin').all()

    return jsonify(user_items)

@app.route("/get/pm/users", methods=["GET"])
def get_all_pm_users():
    user_items = db.session.query(Users.id,Users.username, Users.role).filter(Users.role=='print-master').all()

    return jsonify(user_items)

@app.route("/check/pm/<username>", methods=["GET"])
def check_pm_users(username):
    user_items = db.session.query(Users.id,Users.username, Users.role).filter(Users.username ==username).first()

    request_check = PrintMasterRegisterQueue.query.filter(PrintMasterRegisterQueue.username==user_items.username).first()

    if request_check ==None:
        return jsonify({"in-queue":False})
    else:
        return jsonify({"in-queue":True})
    

@app.route("/profile/<username>", methods=["GET"])
def get_profile(username):
    user= db.session.query(Users.id,Users.username, Users.fname, Users.lname, Users.email).filter(Users.username==username).first()

    return jsonify(user)

@app.route("/user/login", methods=["GET","POST"])
def user_login():
    
    
    if request.content_type =="application/json":
        input_data= request.get_json(force=True)
        username = input_data.get("username")
        password = input_data.get("password")
        user = Users.query.filter(Users.username==username).first()
     
        
        if user== None :    
            return jsonify({"errText":"User Not Found"})
        if user.password != password:
                return jsonify({"errText":"Usernamne or Password Incorrect"})
        return jsonify({
            "username":username,
            "role":user.role
            
        })
    
    return "FAILED"

@app.route("/delete/user/<id>", methods=["DELETE"])
def delete_user(id):
    user = Users.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"errText":"User Deleted"}) 


    



@app.route("/user/new", methods=["POST"])
def post_new_standard_user():

    if request.content_type =="application/json":
        post_data=request.get_json(force=True)
        username = post_data.get("username")
        password = post_data.get("password")
        fname = post_data.get("fname")
        lname = post_data.get("lname")
        email = post_data.get("email")

        user_check = Users.query.filter(Users.username==username).first()

        if user_check == None:

            role = "user"
            email_auth = False
            status=False
            record = Users(username, password,fname,lname, email, role,email_auth, status)        
            db.session.add(record)
            db.session.commit()
        else:
            return jsonify({"errText":"Username Taken"})
        return(jsonify({"errText":"User Created!"}))
    return jsonify("ERROR: Request Must Be Sent As JSON")

@app.route("/auth/email/<id>", methods=["PUT"])
def auth_email(id):
    user = Users.query.get(id)
    if(user.email_auth==False):
        user.email_auth = True
        db.session.commit()
        return jsonify("EMAIL AUTHENICATED")
    else:
        return jsonify("EMAIL ALREADY ADDED")


# ADMIN SECTION
@app.route("/admin/new", methods=["POST"])
def post_new_admin_user():
    if request.content_type =="application/json":
        post_data=request.get_json()
        username = post_data.get("username")
        password = post_data.get("password")
        fname = post_data.get("fname")
        lname = post_data.get("lname")
        email = post_data.get("email")
        role = "admin"
        

        record = Users_support(username, password,fname,lname,email, role)
        db.session.add(record)
        db.session.commit()
        return(jsonify("Admin User Added"))
    return jsonify("ERROR: Request Must Be Sent As JSON")

@app.route("/delete/admin/<id>", methods=["DELETE"])
def delete_admin(id):
    user = Users_support.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"errText":"User Deleted"}) 

@app.route("/admin/login", methods=["GET","POST"])
def admin_login():

    if request.content_type =="application/json":
        input_data= request.get_json(force=True)
        username = input_data.get("username")
        password = input_data.get("password")
        user = Users_support.query.filter(Users_support.username==username).first()

        
        if user.password == None or user.password != password:
  
            return jsonify({"errText":"Usernamne or Password Incorrect"})
        
        return jsonify({
            "username":username,
            "role":user.role
        })
  
    return jsonify({"errText":"Authenication Failed"})


# PRINTMASTER SECTION


@app.route("/post/pm/user", methods=["GET","POST"])
def post_new_pm_user():
    if request.content_type =="application/json":
        input_data= request.get_json(force=True)
        username = input_data.get("username")
        password = input_data.get("password")
        printer = input_data.get("printer")
        experiance=input_data.get("experiance")

        user = Users.query.filter(Users.username==username).first()

        
        if user.password == None or user.password != password:
            return jsonify({"errText":"Usernamne or Password Incorrect"})
        
        if user.role == 'user':
            new_reg = PrintMasterRegisterQueue(user.username, user.role,printer,experiance)
            db.session.add(new_reg)
            db.session.commit()
            return jsonify("Added To Queue")

        else:
            return jsonify("Already Setup As Print Master")        

@app.route("/approve/pm/request/<id>", methods=["PUT"])
def approve_request(id):
    request = PrintMasterRegisterQueue.query.get(id)
    user = db.session.query(Users.id, Users.username, Users.role).filter(Users.username==request.username).first()
    user_id = user.id
    update_user = Users.query.get(user_id)
    update_user.role="print-master"
    db.session.delete(request)


    new_record = PrintMasterQueue(user.username, True, 0)
    
    db.session.add(new_record)

    db.session.commit()
    return jsonify({"errText":"Request Approved"}) 

@app.route("/get/pm/request-queue", methods=["GET"])
def get_all_requests():
    reg_items = db.session.query(
        PrintMasterRegisterQueue.id,
        PrintMasterRegisterQueue.username, 
        PrintMasterRegisterQueue.role , 
        PrintMasterRegisterQueue.printer, 
        PrintMasterRegisterQueue.experiance).all()

    return jsonify(reg_items)

@app.route("/delete/pm/request/<id>", methods=["DELETE"])
def delete_request(id):
    reg_item = PrintMasterRegisterQueue.query.get(id)
    db.session.delete(reg_item)
    db.session.commit()
    return jsonify({"errText":"Request Removed"}) 


@app.route("/get/files/<file_path>",methods=["GET"])
def get_files(file_path):
    base_path =join(UPLOAD_FOLDER,file_path)

    
    
    
    with ZipFile(f'data_{file_path}.zip', 'w') as zipObj:
        for folderName, subfolders, filenames in os.walk(base_path):
            for filename in filenames:
                filePath = os.path.join(folderName, filename)
                zipObj.write(filePath)

    zipObj.close()

    
    return send_file(
        f'data_{file_path}.zip',
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename=f'data_{file_path}.zip'
    )


# Orders

@app.route("/get/order/<id>", methods=["GET"])
def get_order(id):
    order = db.session.query(
        Orders.id, 
        Orders.username, 
        Orders.printmaster, 
        Orders.material, 
        Orders.resolution, 
        Orders.color, 
        Orders.order_num,
        Orders.print_time,
        Orders.cost,
        Orders.status,
        Orders.date_of_order
        ).filter(Orders.id==id).first()

    return jsonify(order)
@app.route("/get/<username>/orders",methods=["GET"])        
def get_orders(username):
    orders = db.session.query(
        Orders.id, 
        Orders.username, 
        Orders.printmaster, 
        Orders.material, 
        Orders.resolution, 
        Orders.color, 
        Orders.order_num,
        Orders.print_time,
        Orders.cost,
        Orders.status,
        Orders.date_of_order
        ).filter(Orders.printmaster==username).all()


    return jsonify(orders)


@app.route("/get/history/<username>" ,methods=["GET"])        
def get_order_history(username):
    orders = db.session.query(
        Orders.id, 
        Orders.username, 
        Orders.printmaster, 
        Orders.material, 
        Orders.resolution, 
        Orders.color, 
        Orders.order_num,
        Orders.print_time,
        Orders.cost,
        Orders.status,
        Orders.date_of_order
        ).filter(Orders.username==username).all()
    
    return jsonify(orders)

@app.route("/get/all/orders", methods=["GET"])
def get_all_orders():
    orders = db.session.query(
        Orders.id, 
        Orders.username, 
        Orders.printmaster, 
        Orders.file_path, 
        Orders.material, 
        Orders.resolution, 
        Orders.color, 
        Orders.order_num,
        Orders.print_time,
        Orders.cost,
        Orders.status,
        Orders.date_of_order
        ).all()

    return jsonify(orders)


@app.route("/upload/files/<order_num>", methods=["PUT"])
def upload_files(order_num):
    target = os.path.join(UPLOAD_FOLDER,order_num)

    if not os.path.isdir(target):
        return jsonify({"errText":"There Was A Problem, Uploading Your Files"})

    
    
    
    file = request.files['file']
    filename = secure_filename(file.filename)
    destination="/".join([target,filename])
    file.save(destination)
    
   
    return jsonify({"errText":"File Uploaded"})

    

@app.route("/post/order", methods=["POST"])
def place_order():
  
    input_data= request
    username = input_data.form['username']
    
    material = input_data.form["material"]
    resolution = input_data.form["resolution"]
    color = input_data.form["color"]
    print_time = "00000"
    cost = "0.00"
    order_num = random.randint(9999,99999999)
    order_num = username[0]+material[0]+resolution+color[0] + str(order_num)
    target = os.path.join(UPLOAD_FOLDER,order_num)

    if not os.path.isdir(target):
        os.mkdir(target)


    file_path = order_num
    status = "in progress"
    date = datetime.datetime.now()

    #print master assignment 
    pm = db.session.query(PrintMasterQueue.position_in_queue, PrintMasterQueue.username).filter(PrintMasterQueue.position_in_queue == 0).first()

    if pm != None:
        printmaster = pm.username
    else:
        return jsonify({"errText":"No Print Masters Available To Take Your Order"})
    order = Orders(username,printmaster,file_path,material,resolution,color,order_num,print_time,cost,status,date)

    db.session.add(order)
    db.session.commit()
    
    return jsonify({
        "errText":"Order Placed",
        "order":order_num
    })


@app.route("/update/order/<id>", methods=["PUT"])
def update(id):

    input_data= request
    print_time = input_data.form['print_time']
    cost = input_data.form['cost']
    status = input_data.form['status']


    update_order = Orders.query.get(id)
    update_order.print_time = print_time
    update_order.cost = cost
    update_order.status = status

    db.session.commit()
        
        
    return jsonify({"errText":"Order Update"}) 

@app.route("/delete/order/<id>", methods=["DELETE"])
def delete_order(id):
    order = Orders.query.get(id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({"errText":"Order Removed"}) 





#payment 


@app.route("/post/payment", methods=["POST","PUT"])
def post_payment():
    input_data= request
    f_name = input_data.form['f_name']
    l_name = input_data.form['l_name']
    street_addr =input_data.form['street_addr']
    state = input_data.form['state']
    zip_code = input_data.form['zip_code']
    country = input_data.form['country']
    cc = input_data.form['cc']
    experation = input_data.form['experation']
    cvv = input_data.form['cvv']
    cost = input_data.form['cost']
    print_master = input_data.form['print_master']
    order_num = input_data.form['order_num']
    date = datetime.datetime.now()


    payment= Payments(f_name,l_name,street_addr,state,zip_code,country,cc,experation,cvv,cost,print_master,order_num,date)


    order = db.session.query(Orders.id, Orders.order_num,Orders.status).filter(Orders.order_num==order_num).first()
    # order.id)
    update_order = Orders.query.get(order.id)
    update_order.status="ready to print"

    db.session.add(payment)
    db.session.commit()
    
    return jsonify({
        "errText":"Payment Approved"
    })



if __name__ =="__main__":
    app.debug = True
    app.run()
    