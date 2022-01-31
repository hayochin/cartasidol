from flask import Flask, request
from flask.helpers import url_for
from flask.templating import render_template
from pymongo import MongoClient
from werkzeug.utils import redirect
from flask_cors import CORS
from bson.json_util import dumps
from bson import ObjectId

app = Flask(__name__)
client = MongoClient("mongodb+srv://admin:admin@dportenis.sx1nl.mongodb.net/Cartitas") #se usó la linea de conexión a atlas por si lo prueba, así no tiene que inyectar codigo o escribir mucho
db = client.Cartitas #seleccionamos la db Cartitas
CORS(app)#es para evitar el problema de origen en las solicitudes

@app.route("/")#la pagina principal
def home():
    resultados = todos()
    if not resultados:
        return render_template("index.html")
    return render_template("index.html",res= resultados)#mandamos resultados para que muestra las cartitas en el inicio

@app.route("/agregarCarta",methods=["POST"])#función para agregar productos
def agregarCarta():
    try:        #mandamos el objeto con todo lo necesario, los datos se obtienen del el form
        resultado = db.Idols.insert_one({
            "personaje":request.form.get('personaje'),
            "nombreCarta":request.form.get('nombreCarta'),
            "img":request.form.get('img'),
            "atributos":{
                "Smile": request.form.get('Smile'),
                "Pure": request.form.get('Pure'),
                "Cool": request.form.get('Cool'),
                "HP": request.form.get('HP')
                }
        })        
        nombre = (db.Idols.find_one({'_id':ObjectId(resultado.inserted_id)}))['nombreCarta']#obtenemos el nombre del objeto insertado   
        #se pudo haber mandando directameente el nombre obtenido del form, pero esto a la vez nos sirve de validación
        return redirect(url_for('carta',nombreCarta = nombre))#redireccionamos a la página de la carta
    except:
        return redirect(url_for("agregar_p"))#si no se pudo, retornamos la misma pagina en blanco

@app.route("/agregar_p")#pagina donde se hará el registro de cartas
def agregar_p():
    return render_template("agregar.html")
@app.route("/todos")#arroja todas las cartitas
def todos():
    ResultadosC=[]
    compas= list(db.Idols.find())#tomamos todos los elementos en la colección
    try:
        #para este paso se guardarán los objetos en un array para después regresarolos en un json
        for a in compas:
            ResultadosC.append({
                "_id":str(ObjectId(a['_id'])),
                "personaje":a['personaje'],
                "nombreCarta":a['nombreCarta'],
                "img":a['img'],
                "atributos":a['atributos']
            })
 
        return str(dumps(ResultadosC))#se pasa a Json y de ahí a string (el jsonify no detecta bien unos campos)
    except:
        return False
@app.route("/carta/<nombreCarta>",methods=['POST','GET'])
def carta(nombreCarta):    
    nombre = nombreCarta.replace("&"," ")#limpiamos la cadena de entrada, ya que al mandarla por el url se utilizó un caracter para los espacios
    compas = db.Idols.find_one({'nombreCarta':nombre})#buscamos la carta por su nombre de carta
    return render_template("carta.html",id= (compas['_id']),personaje=compas['personaje'],nombreCarta=compas['nombreCarta'],atributos = compas['atributos'],img=compas['img'])#vamos a la pagina de la carta encontrada
@app.route("/filtroNombre/",methods=['POST'])#busqueda por nombre
def filtroNombre():
    nombre=request.form.get("nombre")
    ResultadosC = []
    compas= db.Idols.find({"personaje":{'$regex': nombre}}) #filtramos con el nombre que llega
    for a in list(compas):
        ResultadosC.append({
            "_id":str(ObjectId(a['_id'])),
            "personaje":a['personaje'],
            "nombreCarta":a['nombreCarta'],
            "img":a['img'],
            "atributos":a['atributos']
        })
    return render_template("index.html",res= str(dumps(ResultadosC)))#regresamos a la pagina principal pero mostrando solo lo encontrado
@app.route("/update/<id>",methods=['POST','GET'])#función para actualizar las cartas
def update(id):
    try:
        resultado = db.Idols.find_one_and_update({'_id':(ObjectId(id))},
        {'$set':{
             "personaje":request.form.get('personaje'),
             "img":request.form.get('img'),
             "atributos":{
                 "Smile":str(request.form.get('Smile')),
                 "Pure":str(request.form.get('Pure')),
                 "Cool":str(request.form.get('Cool')),
                 "HP":str(request.form.get('HP'))
             }
             }
            })         
        resultado= db.Idols.find_one({'_id':(ObjectId(id))})#reiniciamos la página para que vea los cambios 
        return redirect(url_for('carta',nombreCarta= resultado['nombreCarta']))
    except:
        resultado= db.Idols.find_one({'_id':(ObjectId(id))})#si se encontró un problema en el update, reiniciamos la pagian con los datos actuales
        return redirect(url_for('carta',nombreCarta= resultado['nombreCarta']))

@app.route("/borrar/<id>",methods=['POST','GET']) #función para borrar
def borrar(id):    
    try:#tomando el id, eliminamos la carta
        a = db.Idols.delete_one({'_id':ObjectId(id)})
        return redirect(url_for('home'))#al finalizar redireccionamos a la pagina de inicio
    except:
        nombre= (db.Idols.find_one({'_id':ObjectId(id)}))['nombreCarta']
        return redirect(url_for('carta',nombreCarta= nombre))#en caso de tener un problema con el delete, lo dejamos en la misma pagina
if __name__ =="__main__":
        app.run(host="0.0.0.0",port=5000, debug=True)