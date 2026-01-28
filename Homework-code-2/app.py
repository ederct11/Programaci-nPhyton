from flask import Flask, request, render_template_string
import uuid
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt


app = Flask(__name__)


app.config['JWT_SECRET_KEY'] = 'informacion-clasificada'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=1)

jwt = JWTManager(app)
host = 'mongodb://localhost'
port = 27017
db_name = 'laptop_flask'
# admin , manager , user
user_collection = None
laptop_collection = None

def connect_db():
    try:
        client = MongoClient(host+":"+str(port)+"/")
        db = client[db_name]
        client.admin.command('ping')
        global user_collection
        user_collection = db.users
        global laptop_collection
        laptop_collection = db.laptops
        print("✅ Conexión a MongoDB exitosa")
        print(f"DB Check : {db!=None}")        
        print(f"DB laptop_collection : {laptop_collection!=None}") 
        print(f"DB user_collection : {user_collection!=None}")         
    except Exception as e:
        pass
 
# Returns list    
def check_if_usr_exist(username): 
    global user_collection
    print(f"Debug username: {username}")
    query = {"username" : {"$eq": username }}
    return list(user_collection.find(query))
    
def create_usr(usr):
    global user_collection
    result = user_collection.insert_one(usr)
    print( f"DEBUG ID value {result.inserted_id} type {type(result.inserted_id)}")
    usr["_id"] = str(result.inserted_id)
    return usr

def create_admin_if_exist(usr):
    check_admin = check_if_usr_exist(usr["username"])
    if len(check_admin) > 0:
        return check_admin
    else:
        return create_usr(usr)

def get_token_role():
    try:
        claims = get_jwt()
        return claims.get('role','user')
    except:
        return None
    

def manager_required(f):
    @jwt_required()
    def custom_validation(*args,**kwargs):
        role = get_token_role()
        if role == 'manager' or role == 'admin' :
            return f(*args,**kwargs)
        else:
            print(f"Debug Role: {role}")
            return {
                'error': 'Acceso denegado',
                'message': 'Solo los manager pueden acceder a este endpoint'
            }, 403
    return custom_validation


def admin_required(f):
    @jwt_required()
    def manager_validation(*args,**kwargs):
        role = get_token_role()
        if role == 'admin':
            return f(*args,**kwargs)
        else:
            print(f"Debug Role: {role}")
            return {
                'error': 'Acceso denegado',
                'message': 'Solo los admin pueden acceder a este endpoint'
            }, 403
    return manager_validation  



@app.route('/api/laptop/<string:id>/',methods = ["GET", "DELETE"])
@jwt_required()
def get_laptop(id):   
    print(f"METHOD {request.method}")
    global laptop_collection
    found = laptop_collection.find_one({"_id": ObjectId(id)})
    found["_id"] = str(found["_id"])
    if request.method == "GET":        
        if id is not None:
            return found, 200
        else:
            return {"messsage": "laptop with "+id+" not found"}, 404
    else:
        if id is not None:
            laptop_collection.delete_one({"_id": ObjectId(id)})
            return found , 200
        else:
            return {}, 204
    
def normalize_id(item):
    item["_id"] = str(item["_id"])
    return item    
    
@app.route('/api/laptops/')
@jwt_required()
def get_laptops(): 
    RAM = request.args.get("RAM",0)
    OS =  request.args.get("OS",0)   
    query = {"RAM" : {"$gte": int(RAM) },
             "OS" : {"$gte": int(OS) }}
    global laptop_collection    
    result = list(laptop_collection.find(query))
    results = list(map(lambda lap: normalize_id(lap), result))
    return result, 200

def insert_laptop(body):
    global laptop_collection    
    result = laptop_collection.insert_one(body)
    body["_id"] = str(result.inserted_id)
    return body

@app.route('/api/laptop/', methods = ["POST"])
@manager_required
def post_laptops():   
    return insert_laptop(request.json), 200    
 
@app.route('/api/laptop/<string:id>/', methods=["PATCH"])
@jwt_required()
def put_laptop(id):
    body = request.json
    price = body.get("price")
    name = body.get("name")
    found = laptop_collection.find_one({"_id": ObjectId(id)})
    query = {"$set":{}}
    if found is not None:
        if price != None:
            query["$set"]["price"] = price
        if name != None:
            query["$set"]["name"] = name
        laptop_collection.update_one({"_id": ObjectId(id)}, query)
        found = laptop_collection.find_one({"_id": ObjectId(id)})
        found["_id"] = str(found["_id"])
        return found , 200
    else:
        return {"messsage": "laptop with "+id+" not found"}, 404

@app.route('/api/admin/signIn/manager', methods= ['POST'])
@admin_required
def admin_sign_in():
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return { 'error': 'Datos inválidos', 
                'message': 'Se requieren username y password'}, 400
    else:
        username = request.json['username']
        password = request.json['password']
        if len(check_if_usr_exist(username)) >0:
            return {
            'error': 'Datos inválidos',
            'message': 'el usuario ya existe'}, 400
        else:
            new_user = {
                'username': username,
                'password_hash': generate_password_hash(password),
                'created_at': datetime.now(),
                'role': 'manager'
            }
            user_created = create_usr(new_user)
            
            return { 'username': username, '_id': user_created["_id"], 'role': 'manager'}, 201
   

@app.route('/api/signIn', methods= ['POST'])
def sign_in():
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return { 'error': 'Datos inválidos', 
                'message': 'Se requieren username y password'}, 400
    else:
        username = request.json['username']
        password = request.json['password']
        if len(check_if_usr_exist(username) ) >0:
            return {
            'error': 'Datos inválidos',
            'message': 'el usuario ya existe'}, 400
        else:
            new_user = {
                'username': username,
                'password_hash': generate_password_hash(password),
                'created_at': datetime.now(),
                'role': 'user'
            }
            user_created = create_usr(new_user)
            
            return { 'username': username, '_id': user_created["_id"], 'role': 'user'}, 201
        
@app.route('/api/signIn/customer', methods= ['POST'])
def customer_sign_in():
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return { 'error': 'Datos inválidos', 
                'message': 'Se requieren username y password'}, 400
    else:
        username = request.json['username']
        password = request.json['password']
        if len(check_if_usr_exist(username) ) >0:
            return {
            'error': 'Datos inválidos',
            'message': 'el usuario ya existe'}, 400
        else:
            new_user = {
                'username': username,
                'password_hash': generate_password_hash(password),
                'created_at': datetime.now(),
                'role': 'customer'
            }
            user_created = create_usr(new_user)
            
            return { 'username': username, '_id': user_created["_id"], 'role': 'customer'}, 201
        
@app.route('/api/login', methods= ['POST'])
def log_in():
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return { 'error': 'Datos inválidos', 
                'message': 'Se requieren username y password'}, 400
    else:
        username = request.json['username']
        body_password = request.json['password']
        if len(check_if_usr_exist(username) ) == 0:
            return {
            'error': 'Datos inválidos',
            'message': 'el usuario no existe'}, 400
        else:
            user = check_if_usr_exist(username)[0]
            user_password = user["password_hash"]
            if check_password_hash(user_password, body_password):
                token = create_access_token(identity=username,additional_claims={
                    "user_id" : user.get('user_id'),
                     "role": user.get('role')
                })
                return { 'message': "login correcto",
                        'token': token}, 200
            else:
                 return { 'message': "contraseña incorrecta"}, 401
   
        

#https://www.alkosto.com/fuente

#https://www.alkosto.com/?fuente=google&medio=cpc&campaign=AK_COL_SEM_PEF_CPC_PB_AON_TLP_TLP_Brand-General-AON_PAC&keyword=alkosto&gad_source=1&gad_campaignid=2018735487&gbraid=0AAAAADlnVbhjpa2yNJXbRpygnnsX8VizY&gclid=CjwKCAiAvaLLBhBFEiwAYCNTf7C40kfNPJpky3V0zSRGu-gSyhJjIbLtlSTqw3Q8kPaLJiK2O4N3lBoCGjoQAvD_BwE
#https://listado.mercadolibre.com.co/laptop#D[A:laptop]&origin=UNKNOWN&as.comp_t=SUG&as.comp_v=lapto&as.comp_id=SUG
#https://www.amazon.com/s?k=laptop&__mk_es_US=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=1FUXXWEL7GE7T&sprefix=laptop%2Caps%2C167&ref=nb_sb_noss_1

tienda = {"ES": "TechStore Pro",
         "EN": "TechStore Pro"}

@app.route('/dynamic-home')
def tienda_laptops():
    """Tienda de laptops - página principal"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TechStore - Tienda de Laptops</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(45deg, #9b59b6, #8e44ad); 
                margin: 0; 
                padding: 50px; 
                min-height: 100vh; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
            }
            .card { 
                background: white; 
                padding: 30px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
                text-align: center; 
                max-width: 400px; 
            }
            h1 { 
                color: #333; 
                margin-bottom: 10px; 
            }
            p { 
                color: #666; 
                line-height: 1.6; 
            }
            .highlight { 
                background: #9b59b6; 
                color: white; 
                padding: 5px 10px; 
                border-radius: 20px; 
                display: inline-block; 
                margin: 10px 0; 
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>💻 TechStore - Laptops</h1>
            <p>Tu tienda de confianza para equipos de calidad.</p>
            <div class="highlight">{{ fecha_hora }}</div>
            <p>🗄️ Inventario: <strong>{{ estado_bd }}</strong></p>
        </div>
    </body>
    </html>
    """
    global laptop_collection
    return render_template_string(
        html_content, 
        fecha_hora=datetime.now().strftime("%d/%m/%Y - %H:%M:%S"), 
        estado_bd="En Línea" if laptop_collection != None else "Fuera de Línea"
    )
   
            
if __name__ == '__main__':
    connect_db()
    admin_usr =    {
                'username': "admin",
                'password_hash': generate_password_hash('123456'),
                'created_at': datetime.now(),
                'role': "admin"
            }
    print( f"Admin user: {create_admin_if_exist(admin_usr)}")
    app.run(debug=True,
            port=8002, 
            host='0.0.0.0')