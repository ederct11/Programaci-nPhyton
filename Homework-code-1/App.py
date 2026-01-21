from flask import Flask, request
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

@app.route('/')
def hello():
    return "<h1> Hola Mundo </h1>"

@app.route('/hello/<string:name>')
def grettings(name):
    return "<h1> Hola Mundo "+ name +  "</h1>"


#https://www.alkosto.com/fuente

#https://www.alkosto.com/?fuente=google&medio=cpc&campaign=AK_COL_SEM_PEF_CPC_PB_AON_TLP_TLP_Brand-General-AON_PAC&keyword=alkosto&gad_source=1&gad_campaignid=2018735487&gbraid=0AAAAADlnVbhjpa2yNJXbRpygnnsX8VizY&gclid=CjwKCAiAvaLLBhBFEiwAYCNTf7C40kfNPJpky3V0zSRGu-gSyhJjIbLtlSTqw3Q8kPaLJiK2O4N3lBoCGjoQAvD_BwE
#https://listado.mercadolibre.com.co/laptop#D[A:laptop]&origin=UNKNOWN&as.comp_t=SUG&as.comp_v=lapto&as.comp_id=SUG
#https://www.amazon.com/s?k=laptop&__mk_es_US=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=1FUXXWEL7GE7T&sprefix=laptop%2Caps%2C167&ref=nb_sb_noss_1

saludo = {"ES": "Hola Mundo",
          "EN": "Hello World"}

@app.route('/dynamic-hello/<string:name>/')
def data(name):
    language = request.args.get("language", "EN")
    uppercase = request.args.get("uppercase", False)
    phase = saludo[language] + " " + name
    if uppercase == "True" or uppercase == "true":
        phase = phase.upper()
    return "<h1>" + phase + "</h1>"

laptops = { "1": {"name": "Asus", "RAM": 4, "SSD": 256, "OS": 10, "price": 1577000},
        "2": {"name": "Janus", "RAM": 8, "SSD": 128, "OS": 10, "price": 1258000},
        "3": {"name": "Acer", "RAM": 24, "SSD": 512, "OS": 11, "price": 2439000},
        "4": {"name": "Lenovo", "RAM": 8, "SSD": 256, "OS": 11, "price": 1400000},
        "5": {"name": "HP", "RAM": 24, "SSD": 512, "OS": 11, "price": 4819000} }


@app.route('/api/laptop/<string:id>/',methods = ["GET"])
def get_laptop(id):   
    if id in laptops:
        return laptops[id], 200
    else:
        return {"message": "forniture with "+id+" not found"}, 404
    
@app.route('/api/laptops/')
def get_laptops(): 
    RAM = request.args.get("RAM",0)
    OS =  request.args.get("OS",0)   
    filtered = list(filter(lambda key : laptops[key]["RAM"] >= int(RAM) 
                           and laptops[key]["OS"] >= int(OS) , laptops))
    return list(map(lambda k: laptops[k], filtered))


@app.route('/api/laptop/', methods = ["POST"])
def post_laptops():
    body = request.json
    copy = body.copy()
    new_id = body["id"]
    if new_id in laptops:
        return {"message": "laptop with id "+new_id + " already exist" }, 409    
    else:
        del body["id"]
        laptops[new_id] = body   
        return copy, 201
    

@app.route('/api/laptop/<string:id>/', methods=["PATCH"])
def put_laptop(id):
    body = request.json
    price = body.get("price")
    name = body.get("name")
    if id in laptops:
        if price != None:
            laptops[id]["price"] = price
        if name != None:
            laptops[id]["name"] = name
        return laptops[id], 200
    else:
        return {"messsage": "laptop with "+id+" not found"}, 404
    

@app.route('/api/laptops/', methods=["DELETE"])
def delete_laptops():
    global laptops
    if laptops:
        laptops_copy = laptops.copy()
        laptops.clear()
        return {"message": "All laptops deleted"}, 200
    else:
        return {"message": "No laptops to delete"}, 404
    

if __name__ == '__main__':
    app.run(debug=True,
            port=8002, 
            host='0.0.0.0')