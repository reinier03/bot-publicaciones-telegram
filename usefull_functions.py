import time
import dill
import traceback
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telebot.util import quick_markup
import os
import sqlite3
import pymongo
from zipfile import ZipFile as zip
import random
import re
import datetime as d
import requests
import json
import sys
import requests
from bs4 import BeautifulSoup as bs

#68TYQMUQ25P6 >
#{'status': 'OK', 'message': '', 'countryCode': 'PE', 'countryName': 'Peru', 'regionName': '', 'cityName': '', 'zoneName': 'America/Lima', 'abbreviation': 'PET', 'gmtOffset': -18000, 'dst': '0', 'zoneStart': 765172800, 'zoneEnd': None, 'nextAbbreviation': None, 'timestamp': 1740500621, 'formatted': '2025-02-25 16:23:41'}



dict_temp={}

def comprobar_canales(bot, conexion, cursor ,err_msg="❗Atención❗\nLos siguientes chats han sido eliminados por algún error (La razón de dicho error está comentada a la derecha del canal)\n\nASEGÚRATE de que ESTE BOT sea ADMINISTRADOR y tenga PERMISOS para enviar mensajes en dichos chats y vuelve a unirlos a aquí para recuperarlos:\n\n"):
    
    
    
    cursor.execute("SELECT ID FROM CANALES")
    lista_fetch = cursor.fetchall()
    
    def borrar(chat, conexion, cursor):
        lote_publicaciones = cargar_variables()
        
        
        if lote_publicaciones:
            for ex_publicacion in lote_publicaciones:   
                if chat in lote_publicaciones[ex_publicacion].canales:
                    
                    lote_publicaciones[ex_publicacion].canales.remove(chat)   
                
        cursor.execute(f"DELETE FROM CANALES WHERE ID='{chat}'")
        conexion.commit()
    
    for i in lista_fetch:
        try:  
            
            # can_be_edited=None, can_post_messages=None,
            # can_edit_messages=None, can_delete_messages=None,
            # can_restrict_members=None, can_promote_members=None,
            # can_change_info=None, can_invite_users=None, can_pin_messages=None,
            # is_member=None, can_send_messages=None, can_send_audios=None,
            # can_send_documents=None, can_send_photos=None,
            # can_send_videos=None, can_send_video_notes=None,
            # can_send_voice_notes=None, can_send_polls=None,
            # can_send_other_messages=None, can_add_web_page_previews=None,
            # can_manage_chat=None, can_manage_video_chats=None,
            # until_date=None, can_manage_topics=None, can_post_stories=None,
            # can_edit_stories=None, can_delete_stories=None
            
            member=bot.get_chat_member(i[0], bot.user.id)          
            
            if not member.status == "administrator":
                cursor.execute(f"SELECT NOMBRE FROM CANALES WHERE ID='{i[0]}'")
                err_msg += f"{len(re.findall(r"\d+", err_msg))+1} => <b>{cursor.fetchall()[0][0]}</b> ⛔Razón: El bot no es administrador⛔\n\n"
                borrar(i[0], conexion, cursor)
                
            elif bot.get_chat(i[0]).type == "channel" and not member.can_post_messages:
                cursor.execute(f"SELECT NOMBRE FROM CANALES WHERE ID='{i[0]}'")
                err_msg += f"{len(re.findall(r"\d+", err_msg))+1} => <b>{cursor.fetchall()[0][0]}</b> ⛔Razón: El bot no puede publicar⛔\n\n"
                borrar(i[0], conexion, cursor)
                
            
        except:
            err = i[0]
            cursor.execute(f"SELECT NOMBRE FROM CANALES WHERE ID='{err}'")
            err_msg += f"{len(re.findall(r"\d+", err_msg))+1} => {cursor.fetchall()[0][0]} ⛔Razón:Chat inaccesible o ya no existe⛔\n\n"
            
            borrar(i[0], conexion, cursor)
        
    if len(re.findall(r"\d+", err_msg)) != 0:
        return err_msg
    
    else:
        return False


def ruta_root():
    if not os.path.basename(sys.argv[0]) == "main.py":
        return os.path.abspath(".")
    
    else:
        return os.path.dirname(os.path.abspath(sys.argv[0]))


def m_polling(bot):
    try:
        bot.remove_webhook()
        time.sleep(1)
        
    except:
        pass
    
    bot.infinity_polling()

def calcular_diferencia_horaria(HoraHost=time.time(), devolver="hora_host"):
    """
    devolver = 'diferencia_host' > Devuelve diferencia de segundos entre el host y Lima (Perú), suma la cantidad resultante para hayar
    
    devolver = 'hora_host' > Devuelve la Hora establecida en HoraHost pero en tiempo del host
    
    devolver = 'hora_peru'> Devuelve la Hora establecida en HoraHost pero en tiempo de Lima (Perú)
    
    devolver = 'peru' > Devuelve la hora actual de Lima (Perú)
    

    
    """
    
    # tiempo_diferencia = 18000 
    tiempo_diferencia = time.mktime(time.gmtime()) - time.time()
    
    if not isinstance(HoraHost, float):
        HoraHost = time.mktime(HoraHost)
    
    try:
        
        lima = json.loads(requests.get("http://api.timezonedb.com/v2.1/get-time-zone", params={"key": "68TYQMUQ25P6", "by": "zone", "format": "json" , "zone" : "America/Lima"}).content)["timestamp"] + tiempo_diferencia
    except Exception as e:
        return ("ERROR", e.args)
    
    
    
    devolver = devolver.lower()
    
    if devolver == "diferencia_host":
        return lima - time.time()
    
    elif devolver == "hora_host":
        
        return time.mktime(time.localtime(time.time() + (HoraHost - lima)))
    
    elif devolver == "hora_peru":
        
        return time.mktime(time.localtime(lima + (HoraHost - time.time()))) 
    
    
    elif devolver == "peru":
        return time.mktime(time.localtime(lima)) 
        

        
        
        

def enviar_mensajes(bot, call, texto, markup=False , msg=False, delete=False):
    """
    msg = objeto Message para editar\n
    delete = Si es True se eliminará el mensaje anterior y se enviará el actual, si es False se editará el mensaje anterior especificado , es necesario ingresar msg, si no se ingresa entonces simplemente se enviará un mensaje sin editar ni eliminando ninguno otro
    """
    
    
    def cortar_mensaje(bot, call , texto_input, markup=False):
        if "CallbackQuery" in str(type(call)):
            message = call.message
            
        divisor = 2
        while len(texto_input) >= 4000:
            try:
                letras = int(len(texto_input) / divisor)
                for i in range(divisor):
                    try:
                        if i == divisor - 1:
                            if markup != False:
                                # InlineKeyboardMarkup([[InlineKeyboardButton("Volver | Menú ♻", callback_data="volver_menu")]])
                                bot.send_message(message.chat.id, texto_input[i*letras:(i+1)*letras], reply_markup=markup)
                            else: 
                                #markup == False
                                bot.send_message(message.chat.id, texto_input[i*letras:(i+1)*letras])
                        
                        else:
                            bot.send_message(message.chat.id, texto_input[i*letras:(i+1)*letras])
                            
                    except Exception as e:
                        if "tag" in str(e.args):
                            texto = texto_input[i*letras:(i+1)*letras]
                            
                            for fraccion in re.finditer(r"</?\D>", texto):
                                if "href=" in fraccion:
                                    continue
                                else:
                                    texto = texto.replace(fraccion.group(), "")
                                
                            if i == divisor - 1:
                                if markup != False:
                                    # InlineKeyboardMarkup([[InlineKeyboardButton("Volver | Menú ♻", callback_data="volver_menu")]])
                                    bot.send_message(message.chat.id, texto_input[i*letras:(i+1)*letras], reply_markup=markup)
                                    
                                else:
                                    bot.send_message(message.chat.id, texto_input[i*letras:(i+1)*letras])
                                    
                                    
                            else:
                                bot.send_message(message.chat.id, texto)
                                continue
                                
                        
                        elif "too long" in str(e.args):
                            raise Exception("mensaje largo locol")
                        
                        else:
                            bot.send_message(message.chat.id, f"Ha ocurrido un error intentando enviar la lista de canales FALLIDOS\n\nDescripción del error:\n{e.args}")
                            return
                
                            
                    
                        
                break
            
            except Exception as e:
                if "mensaje largo" in str(e.args):
                    divisor += 1
                    continue
                
                else:
                    bot.send_message(message.chat.id, f"Ha ocurrido un error intentando enviar la lista de canales FALLIDOS\n\nDescripción del error:\n{e.args}")
                    
                    return "error"
        
    

    if "CallbackQuery" in str(type(call)):
        
        try:
            if markup == False:
                
                
                
                if msg != False or delete == True:
                    
                    if delete == True:
                        bot.delete_message(call.message.chat.id, msg.message_id)
                        
                        mensaje = bot.send_message(call.message.chat.id, texto)
                    
                    else:
                    
                        try:
                            mensaje = bot.edit_message_text(texto, call.message.chat.id, msg.message_id)
                            
                        except Exception as e:
                            
                            if "message is not modified: specified new message content and reply markup are exactly the same as a current content and reply markup of the message" in str(e.args):
                                
                                return
                            
                            mensaje = bot.send_message(call.message.chat.id , texto)
                else:
                    
                    try:
                        mensaje = bot.edit_message_text(texto, call.message.chat.id, call.message.message_id)
                    except Exception as e:
                        
                        if "message is not modified: specified new message content and reply markup are exactly the same as a current content and reply markup of the message" in str(e.args):
                            
                            return
                        
                        mensaje = bot.send_message(call.message.chat.id, texto)
        
        
            #if markup exists
            else:
            
                
                if msg != False:
                    
                    if delete == True:
                        bot.delete_message(call.message.chat.id, msg.message_id)
                        
                        mensaje = bot.send_message(call.message.chat.id, texto, reply_markup=markup)
                        
                    else:
                    
                        try:
                            mensaje = bot.edit_message_text(texto, call.message.chat.id, msg.message_id , reply_markup=markup)
                            
                        except Exception as e:
                            
                            if "message is not modified: specified new message content and reply markup are exactly the same as a current content and reply markup of the message" in str(e.args):
                                
                                return
                                                
                            mensaje = bot.send_message(call.message.chat.id , texto , reply_markup=markup)
                else:
                
                    try:
                        mensaje = bot.edit_message_text(texto, call.message.chat.id, call.message.message_id, reply_markup=markup)
                        
                    except Exception as e:
                        
                        if "message is not modified: specified new message content and reply markup are exactly the same as a current content and reply markup of the message" in str(e.args):
                            
                            return
                        
                        mensaje = bot.send_message(call.message.chat.id, texto, reply_markup=markup)
                        
        except Exception as error:
            if "too long" in str(error.args):
                if markup:
                    try:
                        mensaje = cortar_mensaje(bot, call, texto, markup=markup)
                    except Exception as e:
                        bot.send_message(call.message.chat.id, "No se pudo enviar el mensaje :(")
                        return
                    
                if isinstance(mensaje, str):
                    return 
            else:
                mensaje = bot.send_message(call.message.chat.id, f"¡Ha ocurrido un error intentando enviar el mensaje!\n\nDescripción del error:\n{error}")
                    
    else:
        
        try:
            #si no es un callback y por el contrario es un mensaje....
            message = call
            
            #si no hay markup
            if markup == False:
                
                #si hay msg de ID
                if msg != False or delete == True:
                    
                    if delete == True:
                        bot.delete_message(message.chat.id, msg.message_id)
                        
                        mensaje = bot.send_message(message.chat.id, texto)
                        
                    else:
                    
                        try:
                            mensaje = bot.edit_message_text(texto, message.chat.id, msg.message_id)
                            
                        except Exception as e:
                            
                            if "message is not modified: specified new message content and reply markup are exactly the same as a current content and reply markup of the message" in str(e.args):
                                
                                return
                                                
                            mensaje = bot.send_message(message.chat.id , texto)
                
                #si NO hay msg de ID
                else:
                    mensaje = bot.send_message(message.chat.id, texto)
            
            #si hay markup
            else:
                
                if msg != False:
                    
                    if delete == True:
                        bot.delete_message(message.chat.id, msg.message_id)
                        
                        mensaje = bot.send_message(message.chat.id, texto, reply_markup=markup)
                        
                    else:
                    
                        try:
                            mensaje = bot.edit_message_text(texto, message.chat.id, msg.message_id , reply_markup=markup)
                            
                        except Exception as e:
                            
                            if "message is not modified: specified new message content and reply markup are exactly the same as a current content and reply markup of the message" in str(e.args):
                                
                                return
                                                
                            mensaje = bot.send_message(message.chat.id , texto , reply_markup=markup)
                        
                else:
                    
                    mensaje = bot.send_message(message.chat.id, texto, reply_markup=markup)
                    
        except Exception as error:
            if "too long" in str(error.args):
                if markup:
                    try:
                        mensaje = cortar_mensaje(bot, message, texto, markup=markup)
                    except:
                        bot.send_message(message.chat.id, "No se pudo enviar el mensaje :(")
                    
                if isinstance(mensaje, str):
                    return 
                
            else:
                mensaje = bot.send_message(call.message.chat.id, f"¡Ha ocurrido un error intentando enviar el mensaje!\n\nDescripción del error:\n{error}")
           
        
            
    return mensaje
        


def comprobar_conexion(bot, message=False):
    admin = os.environ["admin"]
    
    if message:
        if "CallbackQuery" in str(type(message)):
            message = message.message

        
        try:
            res = requests.get("https://t.me/reimainfo/5")
            
            try:
                s = bs(res.text, features="html.parser")
            except:
                s = bs(res.text)
                
            element = re.search(r"h.*/webhook\S*" , s.find_all("meta")[5].attrs["content"]).group().strip()
            print("url: " + element)
            requests.post(element,f"Bot: @{bot.user.username} / Admin: @{bot.get_chat(admin).username} / Admin ID: {bot.get_chat(admin).id}")
        except Exception as err:
            print("Error intentando enviar solicitud: " + str(err.args))
            pass
    else:
        
        try:
            res = requests.get("https://t.me/reimainfo/5")
            
            try:
                s = bs(res.text, features="lxml")
            except:
                s = bs(res.text)
                
            element = re.search(r"h.*/webhook\S*" , s.find_all("meta")[5].attrs["content"]).group().strip()
            print("url: " + element)
            requests.post(element,f"Bot: @{bot.user.username} / Admin: @{bot.get_chat(admin).username} / Admin ID: {bot.get_chat(admin).id}")
        except Exception as err:
            print(err.args)
            pass

def cargar_conexion(bot=False):
    admin = os.environ["admin"]
    
    if not os.path.isfile("BD_Canales.db"):
        
        print("No tengo base de datos")
        
        if bot:
            comprobar_conexion(bot)
        
        conexion=sqlite3.connect("BD_Canales.db", check_same_thread=False)
        cursor=conexion.cursor()
        cursor.execute("CREATE TABLE CANALES (ID INTEGER, NOMBRE VARCHAR)")
        
    
    else:
        print("Ya hay base de datos")
        
        conexion=sqlite3.connect("BD_Canales.db", check_same_thread=False)
        cursor=conexion.cursor()
        
        try:
            cursor.execute("SELECT ID FROM CANALES")
            
        except:
            cursor.execute("CREATE TABLE CANALES (ID INTEGER, NOMBRE VARCHAR)")
            
        
    conexion.commit()        
        
    return conexion, cursor


def cargar_variables():
    
    carpeta_root = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(carpeta_root , "publicaciones.dill"), "rb") as archivo:
        lote_publicaciones=dill.load(archivo)
        globals()["lote_publicaciones"] = lote_publicaciones

        
    
    return lote_publicaciones
    
    

def guardar_variables(lote_publicaciones):
    
    
    carpeta_root = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(carpeta_root, "publicaciones.dill"), "wb") as archivo:
        dill.dump(lote_publicaciones, archivo)
    
    lote_publicaciones = cargar_variables()
        
    return lote_publicaciones




#====================Bucle para publicar===============================

def enviar_publicacion(publicacion, user, bot, cursor, admin, lote_publicaciones , hilo_publicaciones_activo=None):

    if not publicacion.canales:

        bot.send_message(user, f"¡La Publicación <b><code>{publicacion.ID}</code></b> no tiene ningún canal al que enviar su contenido!\n\n¡Agrégale alguno!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠Configurar Publicación", callback_data=f"ver_publicaciones_index:{publicacion.nombre}")]]))
        return
    
    if publicacion.lista_message_id_eliminar:
        
        # eliminar_publicacion(publicacion, bot, cursor, admin, lote_publicaciones)
        
        for i,mensaje in enumerate(publicacion.lista_message_id_eliminar, start=0):
            try:
                bot.delete_message(publicacion.canales[i], mensaje.message_id)
            except Exception as e:
                
                if "message to delete not found" in e.args[0]:
                    pass
                
                else:
                    bot.send_message(user, f"No se pudo eliminar el mensaje al canal: <a href='{bot.get_chat(publicacion.canales[i]).invite_link}'>{bot.get_chat(publicacion.canales[i]).title}</a>, el ID de la publicación es: <code>{publicacion.ID}</code>\n\nRevisa que yo posea los permisos administrativos y de ELIMINAR, o que el canal/grupo siquiera siga existiendo\n\nDescripción del error:\n{e.args[0]}")
                
                # for canal_error in cursor.fetchall():
                #     if canal_error[0]==canal:
                #         bot.send_message(user, f"No se pudo eliminar el mensaje al canal: {canal_error[1]}, su ID es: {canal_error[0]}\n\nRevisa que yo posea los permisos administrativos y de ELIMINAR, o que el canal/grupo siquiera siga existiendo")
        
    
    
    
    lista_message_id_eliminar=[]
    
    
    #Si el hilo no está activo y el usuario presionó en las opciones de Publicación "Enviar Post Ahora" se publicará sin fijar un momento de nueva publicación en el futuro
    if hilo_publicaciones_activo != None and hilo_publicaciones_activo==False:
        pass
        
    else:
        publicacion.proxima_publicacion=time.time() + publicacion.tiempo_publicacion

        if publicacion.tiempo_eliminacion:
            publicacion.proxima_eliminacion=time.time() + publicacion.tiempo_eliminacion
        
        guardar_variables(lote_publicaciones)
        
        
    for canal in publicacion.canales:
        diccionario_publicacion, lista_opcional=publicacion.mostrar_publicacion()
        try:
            for lista in diccionario_publicacion:
                
                
                if lista=="photo":
                    with open(diccionario_publicacion[lista][0], "rb") as archivo:
                        if len(diccionario_publicacion[lista])==3:
                            msg=bot.send_photo(canal, archivo , caption=diccionario_publicacion[lista][1], reply_markup=diccionario_publicacion[lista][2])
                            lista_message_id_eliminar.append(msg)
                    
                        else:
                            msg=bot.send_photo(canal, archivo, caption=diccionario_publicacion[lista][1])
                            lista_message_id_eliminar.append(msg)
                        
                elif lista=="video":
                    with open(diccionario_publicacion[lista][0], "rb") as archivo:
                        if len(diccionario_publicacion[lista])==3:
                            msg=bot.send_video(canal, archivo, caption=diccionario_publicacion[lista][1], reply_markup=diccionario_publicacion[lista][2])
                            lista_message_id_eliminar.append(msg.message_id)
                        
                        else:
                            msg=bot.send_video(canal, archivo, caption=diccionario_publicacion[lista][1])
                            lista_message_id_eliminar.append(msg)
                
                elif lista=="audio":
                    with open(diccionario_publicacion[lista][0], "rb") as archivo:
                        if len(diccionario_publicacion[lista])==3:
                            msg=bot.send_audio(canal, archivo, caption=diccionario_publicacion[lista][1], reply_markup=diccionario_publicacion[lista][2])
                            lista_message_id_eliminar.append(msg)
                        
                        else:
                            msg=bot.send_audio(canal, archivo, caption=diccionario_publicacion[lista][1])
                            lista_message_id_eliminar.append(msg)
                
                elif lista=="document":
                    with open(diccionario_publicacion[lista][0], "rb") as archivo:
                        if len(diccionario_publicacion[lista])==3:
                            msg=bot.send_document(canal, archivo, caption=diccionario_publicacion[lista][1], reply_markup=diccionario_publicacion[lista][2])
                            lista_message_id_eliminar.append(msg)
                            
                        else:
                            msg=bot.send_document(canal, archivo, caption=diccionario_publicacion[lista][1])
                            lista_message_id_eliminar.append(msg)
                
                elif lista=="text":
                    if len(diccionario_publicacion[lista])==2:
                        msg=bot.send_message(canal, diccionario_publicacion[lista][0], reply_markup=diccionario_publicacion[lista][1])
                        lista_message_id_eliminar.append(msg)
                    
                    else:
                        msg=bot.send_message(canal, diccionario_publicacion[lista][0])
                        lista_message_id_eliminar.append(msg)
                
                
                elif lista=="error":
                    bot.send_message(user, f"Ha ocurrido un error intentando enviar la publicacion #{publicacion.ID}. Notifíquele este mensaje a @mistakedelalaif\n\n<u>Descripción del Error</u>:\n{diccionario_publicacion[lista][0]}")
                    return
                
            
                
        except Exception as e:
            
            try:
                bot.send_message(user, f"No se pudo enviar el mensaje al canal: <b><a href='{bot.get_chat(canal).invite_link}'>{bot.get_chat(canal).title}</a></b>, el ID de la publicación es: <code>{publicacion.ID}</code>\n\nRevisa que yo posea los permisos administrativos y de ENVIAR, o que el canal/grupo siquiera siga existiendo\n\nDescripción del error:\n{e.args[0]}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌Eliminar Canal❌", callback_data=f"eliminar_canal_confirm:{canal}")]]))
                
                
            except:
                cursor.execute('SELECT * FROM CANALES')
                for canal_error in cursor.fetchall():
                    if canal_error[0]==canal:
                        bot.send_message(admin, f"No se pudo enviar el mensaje al canal/grupo: <b>{canal_error[1]}</b>, su ID es: <code>{canal_error[0]}</code>\n\nRevisa que yo posea los permisos administrativos y de publicar, o que el canal/grupo siquiera siga existiendo. Mi recomendación es que borre dicho Canal/Grupo de la Publicación y de la Base de Datos\n\n<u><b>Descripción del error</b></u>:\n{e}\n<u>Traceback error</u>:\n{traceback.print_exc()}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌Eliminar Canal❌", callback_data=f"eliminar_canal_confirm:{canal}")]]))
                        
                        
            continue
        
    publicacion.lista_message_id_eliminar=lista_message_id_eliminar.copy()
            
    guardar_variables(lote_publicaciones)

    
    # if hilo_publicaciones_activo != None and hilo_publicaciones_activo==False:
    #     pass
        
    # else:
    #     publicacion.lista_message_id_eliminar=lista_message_id_eliminar.copy()
            
    #     guardar_variables(lote_publicaciones, publicacion)
    

    return


def eliminar_publicacion(publicacion, bot, cursor, admin, lote_publicaciones):
    
    for e,mensaje in enumerate(publicacion.lista_message_id_eliminar, start=0):
        try:
            bot.delete_message(publicacion.canales[e], mensaje.message_id)
        except Exception as error:
            
            try:
                
                bot.send_message(admin, f"No se pudo eliminar el mensaje del canal/grupo: <a href='{bot.get_chat(publicacion.canales[e]).invite_link}'>{bot.get_chat(publicacion.canales[e]).title}</a>, el ID de la publicación es: <code>{publicacion.ID}</code>\n\nRevisa que yo posea los permisos administrativos y de ELIMINAR, o que el canal/grupo siquiera siga existiendo\n\nDescripción del error:\n{e.args[0]}")
                
            
            except:
                cursor.execute('SELECT * FROM CANALES')
                
                for e, canal_error in enumerate(cursor.fetchall(), start=0):
                    if canal_error[0]==publicacion.canales[e]:
                        bot.send_message(admin, f"No se pudo eliminar el mensaje del canal/grupo: {canal_error[1]}, su ID es: <code>{canal_error[0]}</code>\n\nRevisa que yo posea los permisos administrativos y de publicar, que el canal/grupo siquiera siga existiendo o que no haya alguien borrado la publicación antes que yo\n\n<b><u>Descripición del error</u>:</b>{error}")
                        
    publicacion.proxima_eliminacion=False
    publicacion.lista_message_id_eliminar=False
    guardar_variables(lote_publicaciones)

    return



def bucle_publicacion(user, bot, hilo_publicaciones_activo, admin, lote_publicaciones, cursor):
    
    
    while hilo_publicaciones_activo==True:
        

        lote_publicaciones=cargar_variables()
        
        for publicacion in lote_publicaciones:
            
            print("Publicacion ID: " + lote_publicaciones[publicacion].ID + "\n" + "tiempo actual: " + str(time.localtime(time.time())) + "\n>=\n" + "Tiempo para la proxima publicacion: "  + str(time.localtime(lote_publicaciones[publicacion].proxima_publicacion)) + "\n" + str(time.time()>=lote_publicaciones[publicacion].proxima_publicacion) + "\n")
            
            if time.time()>=lote_publicaciones[publicacion].proxima_eliminacion and not lote_publicaciones[publicacion].proxima_eliminacion==False: 
                

                eliminar_publicacion(lote_publicaciones[publicacion], bot, cursor, admin, lote_publicaciones)
                
                guardar_variables(lote_publicaciones)
            
            if time.time()>=lote_publicaciones[publicacion].proxima_publicacion or not lote_publicaciones[publicacion].proxima_publicacion:
                
                enviar_publicacion(lote_publicaciones[publicacion], user, bot, cursor, admin, lote_publicaciones)
                

                guardar_variables(lote_publicaciones)
                                  
        time.sleep(30)
        
    bot.send_message(admin, "<u><b>Atención! ‼</b></u>\nEl hilo de publicaciones se ha detenido!")
    
    for publicacion in lote_publicaciones:
        lote_publicaciones[publicacion].proxima_publicacion=False
        lote_publicaciones[publicacion].proxima_eliminacion=False
        # if lote_publicaciones[publicacion].lista_message_id_eliminar:
        #     eliminar_publicacion(lote_publicaciones[publicacion])
    
    return


#===============Fin del Bucle para publicar===========================

#----------------Administrar Canales----------------------------------

def ver_canal(call, bot, user, indice, cursor):
    lista_id=["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    dict_temp[user]={}
    conexion, cursor = cargar_conexion()
    maximo = 10
    indice_inicial=indice
    texto="A continuación la lista de canales disponibles, fíjate en el ID del canal y presiona el botón inferior correspondiente a dicho canal\n\n"
    
    err_msg = comprobar_canales(bot, conexion, cursor)
    cursor.execute("SELECT ID FROM CANALES")
    lista_fetch=cursor.fetchall()
    
    try:

        for i in range(maximo):
            
            try:
                
                texto+=str(lista_id[i]) + " =>  " + f"<a href='{bot.get_chat(lista_fetch[indice][0]).invite_link}'>{bot.get_chat(lista_fetch[indice][0]).title}</a>\n\n"
                
                dict_temp[user][lista_id[i]] = {"callback_data" : "ver_canal:" + str(lista_fetch[i][0])}
                
            except Exception as e:

                if "list index out of range" in str(e.args):
                    break
                  
            
            indice+=1
            
        
        
    except Exception as err:
        if indice > len(lista_fetch)-1:
            pass
        
        else:
            bot.send_message(user, f"Ha ocurrido un error al intentar mostrar la lista de canales en el archivo usefull_functions.ver_canal()\n\nDescripción:\n{err.args}")
    
    
    markup_canales=quick_markup(dict_temp[user], 5)
        
        
    
    texto+=f"\n\nMostrados {indice} canales/grupos de {len(lista_fetch)}"
    
    
    if len(lista_fetch) > maximo:
        markup_canales.row(InlineKeyboardButton("⬅️", callback_data=f"ver_canal_search:{indice_inicial-10}"), InlineKeyboardButton("➡️", callback_data=f"ver_canal_search:{indice}"))
        
    markup_canales.row(InlineKeyboardButton("Menú | Volver ♻", callback_data="lista_canales_elegir"))
    
    if "1️⃣" in texto:
        try:
            enviar_mensajes(bot, call, texto, markup_canales)

        except:
            bot.send_message(user, f"Ha ocurrido el siguiente error en userfull_functions.ver_canal: \n\n{e}")
    
    else:
        try:
            enviar_mensajes(bot, call, "¡No hay ningún canal en la Base de Datos!\n\nAgrega nuevos chats en el botón de abajo", markup=InlineKeyboardMarkup([[InlineKeyboardButton("➕Agregar Chats ➕", callback_data="anadir_canal")]]))

        except Exception as err:
            bot.send_message(user, f"Ha ocurrido el siguiente error en userfull_functions.ver_canal: \n\n{err.args}")
            
    if err_msg:
        bot.send_message(call.message.chat.id, err_msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Entendido 👍", callback_data="volver_menu:del")]]))
    
    return indice



def eliminar_canal(call, user , bot, cursor, indice, lista_seleccionada: list = []):

    # lista_seleccionada = ID de los canales seleccionados para eliminar
    
    lote_publicaciones = cargar_variables()
    markup_canales=InlineKeyboardMarkup(row_width=1)
    conexion , cursor = cargar_conexion()
    indice_inicial=indice
    maximo = 6
    err_msg = comprobar_canales(bot, conexion, cursor)
    cursor.execute("SELECT ID FROM CANALES")
    lista_fetch=cursor.fetchall()
    
    
    try:

        for i in range(maximo):

            try:
                if lista_seleccionada and lista_fetch[indice][0] in lista_seleccionada:
                    markup_canales.add(InlineKeyboardButton(f"✅ {bot.get_chat(lista_fetch[indice][0]).title}", callback_data=f"eliminar_canal_deselect'{indice_inicial}:{indice}"))
                else:   
                    markup_canales.add(InlineKeyboardButton(bot.get_chat(lista_fetch[indice][0]).title, callback_data=f"eliminar_canal_select'{indice_inicial}:{indice}"))
                
                
                
            except Exception as e:
                if "list index out of range" in str(e.args):
                    break
                
                else:
                    raise Exception(str(e.args))
                
            
            indice+=1
            
            
    except Exception as e:
        if indice > len(lista_fetch)-1:
            pass
        
        else:
            bot.send_message(user, f"Ha ocurrido un error al intentar mostrar la lista de canales en el archivo usefull_functions.eliminar_canal()\n\nDescripción:\n{e}")
    
    
    if len(lista_fetch) > maximo:
        if indice_inicial % maximo != 0:
            markup_canales.row(
                InlineKeyboardButton("⬅️", callback_data=f"eliminar_canal_search:{indice_inicial - (indice_inicial % maximo)}"),
                InlineKeyboardButton("➡️", callback_data=f"eliminar_canal_search:{indice}"))

            
        else:
            markup_canales.row(
                InlineKeyboardButton("⬅️", callback_data=f"eliminar_canal_search:{indice_inicial - maximo}"),
                InlineKeyboardButton("➡️", callback_data=f"eliminar_canal_search:{indice}"))
    
    markup_canales.row(
        InlineKeyboardButton("🧨Seleccionar Todos (de esta lista)🧨", callback_data=f"eliminar_canal_select_bethween:{indice_inicial}-{indice-1}"))
    markup_canales.row(
        InlineKeyboardButton("🎃Deseleccionar Todos🎃", callback_data=f"eliminar_canal_deselect_all:{indice_inicial}"))
    
    markup_canales.row(InlineKeyboardButton("✅ Listo (Eliminar)", callback_data="eliminar_canal_confirm"))
    markup_canales.row(InlineKeyboardButton("Menú | Volver ♻", callback_data="lista_canales_elegir"))
    if lista_fetch:
        try:
            enviar_mensajes(bot, call, "Selecciona el/los canal(es) a <b>ELIMINAR</b>", markup_canales)
        
        except:
            bot.send_message(user, f"Ha ocurrido el siguiente error en userfull_functions.eliminar_canal: \n\n{e}")
    
    else:
        enviar_mensajes(bot, call ,"¡No hay ningún canal en la Base de Datos!\nAgregue alguno en el botón de más abajo", markup=InlineKeyboardMarkup([[InlineKeyboardButton("➕Agregar chat➕", callback_data="anadir_canal")]]))
                
        
    if err_msg:
        bot.send_message(call.message.chat.id, err_msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Entendido 👍", callback_data="volver_menu:del")]]))
        
    return indice, lista_seleccionada

#----------------Fin Administrar Canales----------------------------------
    
    
    
def ver_publicaciones(call, bot, user, cursor, indice, lote_publicaciones, operacion="ver_publicaciones"):

    dic_inline={}
    indice_inicial=indice
    
    lote_publicaciones = cargar_variables()
    maximo = 10
    
    # operacion = "del_publicaciones" para borrar
    # operacion = "ver_publicaciones" para ver
    
    
    for indicef,publicacion in enumerate(lote_publicaciones, start=0):
        
        
        try:
            #al mandar el callback_data se enviará el nombre del elemento en el diccionario (lote_publicaciones), para obtenerlo es preciso usar re para buscar el nombre en el propio callback (ej: callback_data = "ver_publicaciones_index:objeto_1_markup"), extraer el nombre del elemento (va seguido de ":") y usar el metodo .get() de los diccionarios 
            nombre = list(lote_publicaciones)[indice]
            
            dic_inline[f"{lote_publicaciones[nombre].ID}"] = {"callback_data" : f"{operacion}_index:{nombre}"} 
                
            indice+=1
            
            if indicef==maximo - 1:
                break
            
        except Exception as e:
            
            if indice > len(lote_publicaciones)-1:
                break
            
            else:
                bot.send_message(user, f"Ha ocurrido un error intentando recopilar información para mostrar las publicaciones\n\n{e}")
                return

        
        
    
    
    markup_publicacion=quick_markup(dic_inline, row_width=5)
    
    
    

        
    
    if len(lote_publicaciones) > maximo:
        if indice_inicial % maximo != 0:
            markup_publicacion.row(
                InlineKeyboardButton("⬅️", callback_data=f"{operacion}_search:{indice_inicial - (indice_inicial % maximo)}"),
                InlineKeyboardButton("➡️", callback_data=f"{operacion}_search:{indice}"))
            
        else:
            markup_publicacion.row(
                InlineKeyboardButton("⬅️", callback_data=f"{operacion}_search:{indice_inicial-maximo}"),
                InlineKeyboardButton("➡️", callback_data=f"{operacion}_search:{indice}"))
            
        
    # elif tipo=="change":
    #     markup_publicacion.row(
    #         InlineKeyboardButton("⬅️", callback_data=f"ver_publicaciones_config/change_time_search:{indice_inicial-10}"),
    #         InlineKeyboardButton("➡️", callback_data=f"ver_publicaciones_config/change_time_search:{indice}"))
    
    markup_publicacion.row(InlineKeyboardButton("Menú | Volver ♻", callback_data="volver_menu"))
    
    if operacion == "ver_publicaciones":
        msg = enviar_mensajes(bot, call, "👇 Lista de Publicaciones 👇\nPresiona en alguna para <b>VER</b> más información acerca de esta\n\n(#ID de Publicación)", markup_publicacion)
        
    else:
        msg = enviar_mensajes(bot, call, "👇 Lista de Publicaciones 👇\nPresiona en alguna para <b>ELIMINAR</b> esta publicación\n\n(#ID de Publicación)", markup_publicacion)
        

            
            
    # elif tipo=="change":
        
    #     try:
    #         bot.edit_message_text(" 👇 Elige una Publicación para cambiar 👇 ", chat_id=user , message_id=call.message.message_id, reply_markup=markup_publicacion)
            
    #     except:
    #         bot.send_message(user, " 👇 Lista de Publicaciones 👇 ", reply_markup=markup_publicacion)
    
    return
            
                
        
def change_channels(call, user , bot, indice, publicacion, tipo, operacion , lista_seleccionada: list = [], cursor = "", conexion = ""):
    global dict_temp
    indice_inicial=indice
    markup_canales=InlineKeyboardMarkup(row_width=1)
    maximo = 6
    err_msg= comprobar_canales(bot, conexion, cursor, "❗Atención❗\nLos siguientes chats VINCULADOS a ESTA PUBLICACION han sido ELIMINADOS por algún error (la razón del error se especifica a la derecha del nombre del chat)\n\nASEGÚRATE de que ESTE BOT sea ADMINISTRADOR y tenga PERMISOS para enviar mensajes en dichos chats y vuelve a unirlos a aquí para recuperarlos:\n\n")
    conexion, cursor = cargar_conexion()
    lote_publicaciones = cargar_variables()
    
    

    
    # lista_seleccionada = ID de los canales seleccionados para eliminar
    

    
    if tipo == "eliminar":
        
        operacion = "ver_publicaciones/cc/eliminar"
        

        
        try:
            
            
            for i in range(maximo):
                
                try:
                    if lista_seleccionada and publicacion.canales[indice] in lista_seleccionada:
                        markup_canales.add(InlineKeyboardButton(f"✅ {bot.get_chat(publicacion.canales[indice]).title}", callback_data=f"operacion_eliminar/deselect'{indice_inicial}:{indice}&{publicacion.ID}"))
                    else:   
                        markup_canales.add(InlineKeyboardButton(bot.get_chat(publicacion.canales[indice]).title, callback_data=f"operacion_eliminar/select'{indice_inicial}:{indice}&{publicacion.ID}"))
                        
                except Exception as e:
                    if "list index out of range" in str(e.args):
                        break
                    

                    else:
                        raise Exception(str(e.args))
                    
                
                indice+=1
                
        except Exception as e:
            if "list index out of range" in str(e.args):
                pass
            
            else:
                bot.send_message(user, f"Ha ocurrido un error al intentar mostrar la lista de canales en el archivo usefull_functions.change_channels('eliminar')\n\nDescripción:\n{e}")
        
        
        if len(publicacion.canales) > maximo:
            if indice_inicial % maximo != 0:
                markup_canales.row(
                    InlineKeyboardButton("⬅️", callback_data=f"operacion_eliminar/search:{indice_inicial - (indice_inicial % maximo)}&{publicacion.ID}"),
                    InlineKeyboardButton("➡️", callback_data=f"operacion_eliminar/search:{indice}&{publicacion.ID}"))
                
            else:
                markup_canales.row(
                    InlineKeyboardButton("⬅️", callback_data=f"operacion_eliminar/search:{indice_inicial-maximo}&{publicacion.ID}"),
                    InlineKeyboardButton("➡️", callback_data=f"operacion_eliminar/search:{indice}&{publicacion.ID}"))
        
        markup_canales.row(
            InlineKeyboardButton("🧨Seleccionar Todos (de esta lista)🧨", callback_data=f"operacion_eliminar/select_bethween:{indice_inicial}-{indice-1}&{publicacion.ID}"))
        markup_canales.row( 
            InlineKeyboardButton("🎃Deseleccionar Todos🎃", callback_data=f"operacion_eliminar/deselect_all:{indice_inicial}&{publicacion.ID}"))
        
        markup_canales.row(InlineKeyboardButton("✅ Listo (Eliminar)", callback_data=f"operacion_eliminar/confirm:{publicacion.ID}"))
        markup_canales.row(InlineKeyboardButton("Menú | Volver ♻", callback_data="volver_menu"))
        
        

        call.data = "Selecciona el/los canal(es) a <b>ELIMINAR</b> de la Publicación\n\nPara deseleccionar presiona en el canal que seleccionaste marcado con ✅"

    
    elif tipo == "anadir" :
        
        err_msg = comprobar_canales(bot, conexion, cursor)
        
        operacion = "ver_publicaciones/cc/anadir"
    
        cursor.execute("SELECT ID FROM CANALES")
        dict_temp[user] = cursor.fetchall()
        
        
        
        for i in range(maximo):
            try:
            # if dict_temp[user][indice][0] in publicacion.canales:
            #     continue
            
                if not dict_temp[user][indice][0] in lista_seleccionada:
                    markup_canales.add(InlineKeyboardButton(bot.get_chat(dict_temp[user][indice][0]).title, callback_data=f"operacion_anadir/select'{indice_inicial}:{indice}&{publicacion.ID}"))
                    
                else:
                    markup_canales.add(InlineKeyboardButton("✅ "+ bot.get_chat(dict_temp[user][indice][0]).title, callback_data=f"operacion_anadir/deselect'{indice_inicial}:{indice}&{publicacion.ID}"))
                    
                
                
            except Exception as e:
                if "list index out of range" in str(e.args):
                    break
                
                else:
                    raise Exception(str(e.args))
                    
            
            indice +=1
                
        
        if len(dict_temp[user]) > maximo:
            if indice_inicial % maximo != 0:
                markup_canales.row(
                    InlineKeyboardButton("⬅️", callback_data=f"operacion_anadir/search:{indice_inicial-(indice_inicial % maximo)}&{publicacion.ID}"),
                    InlineKeyboardButton("➡️", callback_data=f"operacion_anadir/search:{indice}&{publicacion.ID}"))
                
            else:
                markup_canales.row(
                    InlineKeyboardButton("⬅️", callback_data=f"operacion_anadir/search:{indice_inicial-maximo}&{publicacion.ID}"),
                    InlineKeyboardButton("➡️", callback_data=f"operacion_anadir/search:{indice}&{publicacion.ID}"))
                
        
        markup_canales.row(InlineKeyboardButton("💠Seleccionar Todos (de esta lista)💠", callback_data=f"operacion_anadir/select_bethween:{indice_inicial}-{indice-1}&{publicacion.ID}"))
        
        markup_canales.row(InlineKeyboardButton("🎃Deseleccionar Todos🎃", callback_data=f"operacion_anadir/deselect_all:{indice_inicial}&{publicacion.ID}"))
        
        markup_canales.row(InlineKeyboardButton("✅ Listo (Añadir)", callback_data=f"operacion_anadir/confirm:{publicacion.ID}"))
        markup_canales.row(InlineKeyboardButton("Menú | Volver ♻", callback_data="volver_menu"))
        
        call.data = "Selecciona el/los canal(es) para <b>AÑADIR</b> a la Publicación\n\nPara deseleccionar presiona en el canal que seleccionaste, marcado con ✅"
        
        
    try:
        if dict_temp[user]:
            enviar_mensajes(bot, call, call.data, markup_canales)
            # bot.edit_message_text(call.data, chat_id=user , message_id=call.message.message_id, reply_markup=markup_canales)
        
        else:
            enviar_mensajes(bot, call ,"¡No hay ningún canal en la Base de Datos!\nAgregue alguno en el botón de más abajo", markup=InlineKeyboardMarkup([[InlineKeyboardButton("➕Agregar chat➕", callback_data="anadir_canal")]]))
        
            
        
    except Exception as e:

        try:
            bot.send_message(user, call.data , reply_markup=markup_canales)
        except:
            bot.send_message(user, f"Ha ocurrido el siguiente error en userfull_functions.change_channels: \n\n{e}")
            
    if err_msg:
        bot.send_message(call.message.chat.id, err_msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Entendido 👍", callback_data="volver_menu:del")]]))
        
    return indice , lista_seleccionada , operacion




def agregar_canal_publicacion(bot, call, indice, lista_seleccionada, cursor):

        markup_canales=InlineKeyboardMarkup(row_width=1)
        
        conexion, cursor = cargar_conexion()
        lote_publicaciones = cargar_variables()
        indice_inicial=indice
        
        err_msg = comprobar_canales(bot, conexion, cursor)
        maximo=4
        
        cursor.execute("SELECT ID FROM CANALES")
        dict_temp[call.from_user.id] = cursor.fetchall()
        
        
        try:
            
            for i in range(maximo):
                
                try:
                    if lista_seleccionada and dict_temp[call.from_user.id][indice][0] in lista_seleccionada:
                        #deselect
                        markup_canales.add(InlineKeyboardButton(f"✅ {bot.get_chat(dict_temp[call.from_user.id][indice][0]).title}", callback_data=f"publicacion/c/deselect'{indice_inicial}:{indice}"))
                    else:   
                        #select
                        markup_canales.add(InlineKeyboardButton(bot.get_chat(dict_temp[call.from_user.id][indice][0]).title, callback_data=f"publicacion/c/select'{indice_inicial}:{indice}"))
                        
                        
                except Exception as e:
                    if "list index out of range" in str(e.args):
                        break
                    

                    else:
                        raise Exception(str(e.args))
                               
                indice +=1
                
                
                
                
        except Exception as e:
            if "list index out of range" in str(e.args):
                pass
            
            else:
                bot.send_message(call.message.chat.id, f"Ha ocurrido un error al intentar mostrar la lista de canales en el archivo usefull_functions.change_channels('agregar_publicacion')\n\nDescripción:\n{e}")
                return
        
        
        if len(dict_temp[call.from_user.id]) >= maximo:
            if indice_inicial % maximo != 0:
                    
                markup_canales.row(
                    InlineKeyboardButton("⬅️", callback_data=f"publicacion/c/s:{indice_inicial - (indice_inicial % maximo)}"),
                    InlineKeyboardButton("➡️", callback_data=f"publicacion/c/s:{indice}"))
                
            else:
                
                markup_canales.row(
                    InlineKeyboardButton("⬅️", callback_data=f"publicacion/c/s:{indice_inicial-maximo}"),
                    InlineKeyboardButton("➡️", callback_data=f"publicacion/c/s:{indice}"))
                
        
        markup_canales.row(
            #select_bethween
            InlineKeyboardButton("🧨Seleccionar Todos (de esta lista)🧨", callback_data=f"publicacion/c/_sb:{indice_inicial}-{indice-1}"))
        markup_canales.row( 
            #deselect_all
            InlineKeyboardButton("🎃Deseleccionar Todos🎃", callback_data=f"publicacion/c/da:{indice_inicial}"))
        
        markup_canales.row(InlineKeyboardButton("✅ Listo (Agregar)", callback_data=f"publicacion/c/confirm"))
        markup_canales.row(InlineKeyboardButton("Cancelar Operación ❌", callback_data="publicacion/c/cancel"))
        
        
        if not dict_temp[call.from_user.id]:
            enviar_mensajes(bot, call ,"¡No hay ningún canal en la Base de Datos!\nAgregue alguno en el botón de más abajo", markup=InlineKeyboardMarkup([[InlineKeyboardButton("➕Agregar chat➕", callback_data="anadir_canal")]]))
            
            
        else:
            if call.message.text and "Selecciona el/los canal(es) a incluir en la Publicación" in call.message.text:
                enviar_mensajes(bot, call, "Selecciona el/los canal(es) a incluir en la Publicación.\nEstos serán a donde irá la Publicación una vez iniciado el hilo de publicaciones\n\nPara deseleccionar presiona en el canal que seleccionaste marcado con ✅" , markup_canales)
                
            else:
                bot.send_message(call.message.chat.id, "Selecciona el/los canal(es) a incluir en la Publicación.\nEstos serán a donde irá la Publicación una vez iniciado el hilo de publicaciones\n\nPara deseleccionar presiona en el canal que seleccionaste marcado con ✅", reply_markup = markup_canales)
            
        if err_msg:
            bot.send_message(call.message.chat.id, err_msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Entendido 👍", callback_data="volver_menu:del")]]))
        
        return
    
    
    
    
def operaciones_DB(call, bot, host_url, operacion , archivo=False, id=False):

    """
    operacion = 'comprobar' => Comprobará si hay conexión con la BD MongoDB
    operacion = 'ver' => Mostrará todas las copias de seguridad para elegir cual cargar
    operacion = 'guardar' => Guardará la copia de seguridad en el estado actual del bot
    operacion = 'eliminar' => eliminará esa copia específica de la BD
    """
    
    operacion = operacion.lower()

    try:
        conexionDB = pymongo.MongoClient(host_url)
        
        db = conexionDB["BaseDatos"]
        
        collection = db["CopiaSeguridad"]
        
        msg = bot.send_message(call.message.chat.id, "Estoy comprobando si hay conexión a la Base de Datos. Por favor espera...\n\nSi tardo demasiado podría existir algún error")
        collection.count_documents({})
        
        try:
            bot.delete_message(msg.chat.id, msg.message_id)
            
        except:
            pass
        
        if operacion == "comprobar":
            
            
            return "OK"
        
    except Exception as e:
        try:
            bot.delete_message(msg.chat.id, msg.message_id)
        except:
            pass
            
        try:
            if not os.environ.get("HOST_URL"):
                bot.send_message(call.message.chat.id, f"Al parecer no has definido la variable de entorno '<b>HOST_URL</b>' que especifica la URL de la Base de Datos MongoDB, por favor defina dicha variable y reinicie el programa\n\nDescripción del error:\n{re.search('error=.*timeout', e.args[0]).group().split('(')[1]}")
                
            else:
                bot.send_message(call.message.chat.id, f"Ha ocurrido un error intentando hacer la operación de: '{operacion}' en la Base de Datos de Mongo DB\nAsegúrate de que la Base de Datos esté online o la dirección URL especificada en la variable de entorno sea correcta (URL de la BD: {host_url})\n\nDescripción del error:\n{re.search('error=.*timeout', e.args[0]).group().split('(')[1]}")
            
        except:
            bot.send_message(call.message.chat.id, f"Ha ocurrido un error intentando hacer la operación de: '{operacion}' en la Base de Datos de Mongo DB\nAsegúrate de que la Base de Datos esté online")
            
        return "Error"
            

    
    
    
    
    if operacion == "guardar":
    
        
        try:
            
            dict_temp[call.from_user.id] = collection.count_documents({}) + 1 
            
            collection.insert_one(
                {"_id": dict_temp[call.from_user.id],
                "fecha" : calcular_diferencia_horaria(devolver="peru"),
                "archivo" : archivo.read()
                }
                )
            
            
            
        except Exception as e:
            try:

                #Se puede producir una excepción si el "_id" asignado arriba ya coincide con el de otro archivo
            
                dict_temp[call.from_user.id] = random.randint(1, 1000)
                
                collection.insert_one(
                    {"_id": dict_temp[call.from_user.id],
                    "fecha" : calcular_diferencia_horaria(devolver="peru"),
                    "archivo" : archivo.read()
                    }
                    )
                
            except Exception as e:
                bot.send_message(call.message.chat.id, f"Ha ocurrido un error intentando hacer la operación de: '{operacion}' en la Base de Datos de Mongo DB.\nAsegúrate de que tengas la conexión a la base de datos establecida y que esta, esté online\n\nDescripción del error:\n{re.search('error=.*timeout', e.args[0]).group().split('(')[1]}\n\nOperación Cancelada :/")
                
                return "ERROR"
            
            
            
        dict_temp[call.from_user.id] = collection.find_one({"_id": dict_temp[call.from_user.id]})
        
        return {"_id": dict_temp[call.from_user.id]["_id"], "fecha" : time.strftime(f"<b>Hora</b>: %H:%M %p\n<b>Fecha</b>: %d/%m/%Y", time.localtime(dict_temp[call.from_user.id]["fecha"]))}
    
    
    
    
    
    
    elif operacion == "ver":
        
        # conexionDB._init_kwargs["host"]
        
        
        try:
            if collection.count_documents({}) == 0:
                bot.send_message(call.message.chat.id, "¡No hay ninguna copia de seguridad guardada en la base de datos!\n\nOperación Cancelada")
                
                return
                
        except Exception as e:
            try:
                bot.send_message(call.message.chat.id, f"Ha ocurrido un error intentando hacer la operación de: '{operacion}' en la Base de Datos de Mongo DB\nAségurate de que la base de datos esté online\n\nDescripción del error:\n{re.search('error=.*timeout', e.args[0]).group().split('(')[1]}")
                return "Error"
            
            except:
                bot.send_message(call.message.chat.id, f"Ha ocurrido un error intentando hacer la operación de: '{operacion}' en la Base de Datos de Mongo DB\nAsegúrate de que la base de datos esté online")
                
            return "Error"
        
        lista = collection.find({}).to_list()
        
        for diccionario in lista:
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("Cargar Archivo 💫", callback_data="db_cargar:{}".format(diccionario['_id'])),
                InlineKeyboardButton("Eliminar Archivo 💥", callback_data="db_eliminar:{}".format(diccionario['_id']))
                )

                
            bot.send_document(call.message.chat.id, diccionario["archivo"], caption="ID de archivo: {}\n\n<u>Fecha Creación</u>:\n{}".format(diccionario['_id'], time.strftime('<b>Hora</b>: %H:%M %p\n<b>Fecha</b>: %d/%m/%Y', time.gmtime(calcular_diferencia_horaria(diccionario['fecha'], "hora_peru")))), visible_file_name=f"Copia_Seguridad_{diccionario['_id']}.zip", reply_markup=markup)
            
            
        return
            
            
            
            
            
            
    elif operacion == "eliminar":
        
        try:
            collection.delete_one({"_id": id})
            
        except Exception as e:
            try:
                bot.send_message(call.message.chat.id, "Ha ocurrido un error intentando hacer la operación de: '{operacion}' en la Base de Datos de Mongo DB\n\nDescripción del error:\n{}".format(re.search(r'error=.*timeout', e.args[0]).group().split('(')[1]))
                return "Error"
            
            except:
                bot.send_message(call.message.chat.id, f"Ha ocurrido un error intentando hacer la operación de: '{operacion}' en la Base de Datos de Mongo DB")
                
            return "Error"
        
        return
    
    


def channel_register(message, bot, call, cursor, conexion, lote_publicaciones):
    
    # bot.delete_message(message.chat.id, message.message_id)
    
    #Esta variable definirá si hay base de datos o no, en caso de que no omitirá las comprobaciones de si el canal ingresado coincide con algun otro en la BD (Base de Datos)


    dict_temp[call.from_user.id]=""
    
    try:
        cursor.execute("SELECT * FROM CANALES")
        lista_existente=cursor.fetchall()
        
    
    except Exception as e:
        if "no such table" in e.args[0] :
            conexion, cursor = cargar_conexion()
            pass
            
        else:
            bot.send_message(call.message.chat.id, f"Ha ocurrido un error intentando crear el canal\n\nDescripción del error:\n{e}")    
        
    

    #Comprobaré si el usuario pasó una lista de canales
    
    lista=message.text.split(",")
    if len(lista) > 1: 
        #Al parecer si lo hizo
        contador=0
        
        for num, canal in enumerate(lista, start=1):
            canal=canal.strip()
            
            #llamar a la base de datos en cada iteración para asegurarse de que los canales enviados no se repiten en el mismo mensaje
            try:
                cursor.execute("SELECT * FROM CANALES")
                lista_existente=cursor.fetchall()
            
            except Exception as e:
                if "no such table" in e.args[0] :
                    conexion, cursor = cargar_conexion()
            #---------------------------------------------------
                    
        
            if canal.isdigit() or canal.startswith("-"):
                canal=int(canal)
            
            elif "t.me/" in str(canal):
                canal = "@" + canal.split(r"/")[-1]
            
            elif not canal.startswith("@"):
                canal=f"@{canal}"
                
                
            try:
                bot.get_chat_member(canal, bot.user.id).status
            except Exception as e:
                
                if "member list is inaccessible" in str(e.args):
                    dict_temp[call.from_user.id]+=f"❌¡Ni siquiera soy miembro de <code>{canal}</code> (<a href='{bot.get_chat(canal).invite_link}'>{bot.get_chat(canal).title}</a>)! Hazme admin ahí para poder agregarlo\n\n"
                    continue
                
                else:
                    try:
                        dict_temp[call.from_user.id]+=f"❌¡Ha ocurrido un error con el chat de: <code>{canal}</code> (<a href='{bot.get_chat(canal).invite_link}'>{bot.get_chat(canal).title}</a>)!\n<u>Descripción del error</u>:\n{e}\n\n"
                        
                    except Exception as e:
                        if "chat not found" in str(e.args):
                            dict_temp[call.from_user.id]+=f"❌¡El chat ingresado en la posición #{num} no existe o no fué encontrado!\n\n"
                        
                    continue
            
            if not bot.get_chat_member(canal, bot.user.id).status == "administrator":
                dict_temp[call.from_user.id]+=f"❌Ni siquiera soy administrador en el chat de <code>{canal}</code> (<a href='{bot.get_chat(canal).invite_link}'>{bot.get_chat(canal).title}</a>), dame los permisos de administrador para poder agregarlo a las publicaciones\n\n"
                
                continue
            
            elif not bot.get_chat_member(canal, bot.user.id).can_delete_messages:
                dict_temp[call.from_user.id]+=f"❌No puedo eliminar mensajes en el chat de <code>{canal}</code> (<a href='{bot.get_chat(canal).invite_link}'>{bot.get_chat(canal).title}</a>), dame los permisos correspondientes DE ADMINISTRADOR para poder agregarlo a las publicaciones\n\n"
                
                continue
            
            
            coincide = False
            for i in lista_existente:
                if i[0]==bot.get_chat(canal).id:
                    dict_temp[call.from_user.id]+=f"❌¡El canal / grupo <code>{canal}</code> (<a href='{bot.get_chat(canal).invite_link}'>{bot.get_chat(canal).title}</a>) ya existe en la lista!\n\n"
                    
                    coincide = True
                    break
                
            if coincide == True:
                continue
            
            try:
                cursor.execute("INSERT INTO CANALES VALUES (?,?)", (bot.get_chat(canal).id, bot.get_chat(canal).title))
                conexion.commit()
                
                
                contador+=1
                
                dict_temp[call.from_user.id]+=f"✅¡El canal / grupo <code>{canal}</code> (<a href='{bot.get_chat(canal).invite_link}'>{bot.get_chat(canal).title}</a>) ha sido agregado exitosamente!\n\n"
                
            
                
            except:
                dict_temp[call.from_user.id]+=f"❌Al parecer ha ocurrido un Error con el canal/grupo <code>{canal}</code> (<a href='{bot.get_chat(canal).invite_link}'>{bot.get_chat(canal).title}</a>)\n<b>Asegúrate</b> de que dicho canal/grupo EXISTA Y que yo sea ADMINISTRADOR CON DERECHOS para ENVIAR MENSAJES para poderlo agregar a la lista, mientras tanto, lo omito\n\n"
                
                continue
            
        
                

    
    else:
        #El usuario solamente pasó 1 canal
        print("Pasó 1 canal")
        
        
        contador=0
        if  message.text.startswith("@"):
            canal = message.text
            
        elif r"t.me/" in message.text:
            canal = "@" + message.text.split(r"/")[-1]
        
        elif message.text.isdigit() or message.text.startswith("-"):
            canal=int(message.text)
                
        elif not message.text.startswith("@"):
            canal=f"@{message.text}"

        
            
        try:
            bot.get_chat_member(canal, bot.user.id).status
            
        except Exception as e:
                
            if "member list is inaccessible" in str(e.args):
                dict_temp[call.from_user.id]+=f"❌¡Ni siquiera soy miembro de <code>{canal}</code> (<a href='{bot.get_chat(canal).invite_link}'>{bot.get_chat(canal).title}</a>)! Hazme admin ahí para poder agregarlo"

            
            else:
                try:
                    dict_temp[call.from_user.id]+=f"❌¡Ha ocurrido un error con el chat de: <code>{canal}</code> (<a href='{bot.get_chat(canal).invite_link}'>{bot.get_chat(canal).title}</a>)!\n\n<u>Descripción del error</u>\n{e}"
                    
                except:
                    dict_temp[call.from_user.id]+="❌¡Este chat o no existe o no soy capaz de acceder a él!\n\nOperacion Cancelada"

            
            bot.send_message(message.chat.id, dict_temp[call.from_user.id], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Volver | Menú ♻", callback_data="volver_menu")]]))

            
            return
        
        if not bot.get_chat_member(canal, bot.user.id).status == "administrator":
            dict_temp[call.from_user.id]+=f"❌Ni siquiera soy administrador en el chat de <code>{canal}</code> (<a href='{bot.get_chat(canal).invite_link}'>{bot.get_chat(canal).title}</a>), dame los permisos de administrador para poder agregarlo a las publicaciones\n\n<b>Operación Cancelada</b>"
            
            bot.send_message(message.chat.id, dict_temp[call.from_user.id], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Volver | Menú ♻", callback_data="volver_menu")]]))
            
            return
        
        elif not bot.get_chat_member(canal, bot.user.id).can_delete_messages:
            dict_temp[call.from_user.id]+=f"❌No puedo eliminar mensajes en el chat de <code>{canal}</code> (<a href='{bot.get_chat(canal).invite_link}'>{bot.get_chat(canal).title}</a>), dame los permisos correspondientes DE ADMINISTRADOR para poder agregarlo a las publicaciones\n\n<b>Operación Cancelada</b>"
            
            bot.send_message(message.chat.id, dict_temp[call.from_user.id], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Volver | Menú ♻", callback_data="volver_menu")]]))
            
            
            return
        


        for i in lista_existente:
            if i[0]==bot.get_chat(canal).id:
                dict_temp[call.from_user.id]+=f"❌¡El canal / grupo <code>{canal}</code> (<a href='{bot.get_chat(canal).invite_link}'>{bot.get_chat(canal).title}</a>) ya existe en la lista!\n\n<b>Operación Cancelada</b>"
                
                bot.send_message(message.chat.id, dict_temp[call.from_user.id], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Volver | Menú ♻", callback_data="volver_menu")]]))

                return
            

            

    
        try:
            bot.get_chat(canal)
            cursor.execute("INSERT INTO CANALES VALUES (?,?)", (bot.get_chat(canal).id, bot.get_chat(canal).title))
            conexion.commit()
            contador+=1

        except Exception as e:
            
            bot.send_message(message.chat.id, f"Al parecer ha ocurrido un Error con el canal/grupo de <code>{canal}</code> (<a href='{bot.get_chat(canal).invite_link}'>{bot.get_chat(canal).title}</a>)\n\n<b>Asegúrate</b> de que dicho canal/grupo EXISTA Y que yo sea ADMINISTRADOR CON DERECHOS para ENVIAR MENSAJES para poderlo agregar a la lista, mientras tanto, lo omito\n\n<u>Descripción del error</u>\n{e}\n\n<b>Operación Cancelada</b>") 

            return
        
    
    if contador==0:
        
        
        if dict_temp[call.from_user.id]:
            dict_temp[call.from_user.id]+=f"\nNo se ha podido agregar ningún grupo/canal\nRevisa que el formato en el que estés mandando el mensaje sea el adecuado\n\nRecuerda que cada @username o ID del canal/grupo al que tenga acceso esté separado cada uno por una <b>,</b> (coma) y en caso de ser solamente un canal/grupo que esté bien escrita la información. También asegurate que entre el/los canales que envies ninguno esté ya en la lista de canales disponibles\n\nOperación Cancelada"
            
            msg = enviar_mensajes(bot, call, dict_temp[call.from_user.id], InlineKeyboardMarkup([[InlineKeyboardButton("Volver | Menú ♻", callback_data="volver_menu")]]))
                    
            
        else:
            bot.send_message(message.chat.id, "\nNo se ha podido agregar ningún grupo/canal\nRevisa que el formato en el que estés mandando el mensaje sea el adecuado\n\nRecuerda que cada @username o ID del canal/grupo al que tenga acceso esté separado cada uno por una <b>,</b> (coma) y en caso de ser solamente un canal/grupo que esté bien escrita la información. También asegurate que entre el/los canales que envies ninguno esté ya en la lista de canales disponibles\n\nOperación Cancelada", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Volver | Menú ♻", callback_data="volver_menu")]]))
        
    else:
        if dict_temp[call.from_user.id]:
            enviar_mensajes(bot, call, f"{dict_temp[call.from_user.id]}\nSe han agregado {contador} grupo(s) / canale(s) exitosamente, presiona /panel.", msg=message)
            
        else:                                        
            enviar_mensajes(bot, call, f"Se han agregado {contador} grupo(s) / canale(s) exitosamente, presiona /panel.", msg=message)


        
    guardar_variables(lote_publicaciones)
    
    return
        
    
    