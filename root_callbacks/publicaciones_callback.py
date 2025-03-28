import usefull_functions
import root_callbacks.Canales_callback as Canales_callback
from Publicaciones_class import Publicaciones
import random
import re
import threading
import time
import os
import sqlite3
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, BotCommand
import telebot
import dill
from flask import Flask, request
import pymongo



if os.name=="nt":
    OS="\\"
else:
    OS="/"

l_operacion = ""



        
    # if cargar=="variables" or cargar=="all":
    #     with open("variables.dill", "rb") as archivo:
    #         lote_variables=dill.load(archivo)
    #         for key, item in lote_variables.items():
    #             globals()[str(key)] = item

    #     if cargar == "variables":
    #         return lote_variables
    
    # return lote_publicaciones, lote_variables
    





def main_handler(bot,call, cursor, admin , conexion, lote_publicaciones, lista_canales, lista_seleccionada, hilo_publicaciones_activo, dict_temp, operacion):
    global l_operacion
    
    
    
        
    
    if call.data=="publicacion" or "publicacion/c" in call.data:
        
        
        
        def add_publish(message, canales_seleccionados, msg=False, lote_publicaciones=lote_publicaciones):

            lista_canales=[]
            cursor.execute("SELECT * FROM CANALES")
            lista=cursor.fetchall()
            
            if not msg == False:
                bot.delete_message(msg.chat.id , msg.message_id)
            
            
            
            if not lista:
                markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Agregar canal(es) 💻", callback_data="anadir_canal"))
                bot.send_message(message.chat.id, "<b>¡No hay ningún canal en la lista de canales!</b>\n\nAgrega uno y vuelve aquí", reply_markup=markup)
                return
            
            #funcion para comprobar el tipo de archivos adjuntos a la publicacion
            def comprobar_medios(message, texto_publicacion, lote_publicaciones=lote_publicaciones):
                ruta_root = usefull_functions.ruta_root()
                
                if not "Publicaciones_media" in os.listdir(ruta_root):
                    os.mkdir(os.path.join(ruta_root, "Publicaciones_media"))
                    
                try:
                    if message.content_type=="photo":
                        with open(os.path.join(os.path.abspath(os.path.join(ruta_root ,"Publicaciones_media")) , f"{len(lote_publicaciones)+1}_{os.path.basename(bot.get_file(message.photo[-1].file_id).file_path)}"), "wb") as archivo:
                            archivo.write(bot.download_file(bot.get_file(message.photo[-1].file_id).file_path))
                            archivo_multimedia=[os.path.abspath(archivo.name), "photo"]
                    
                    elif message.content_type == "voice":
                        with open(os.path.join(os.path.abspath(os.path.join(ruta_root ,"Publicaciones_media")), f"{len(lote_publicaciones)+1}_{os.path.basename(bot.get_file(message.voice.file_id).file_path)}"), "wb") as archivo:
                            archivo.write(bot.download_file(bot.get_file(message.voice.file_id).file_path))
                            archivo_multimedia=[os.path.abspath(archivo.name), "voice"]
                            
                    elif message.content_type=="video":
                        with open(os.path.join(os.path.abspath(os.path.join(ruta_root ,"Publicaciones_media")), f"{len(lote_publicaciones)+1}_{os.path.basename(bot.get_file(message.video.file_id).file_path)}"), "wb") as archivo:
                            archivo.write(bot.download_file(bot.get_file(message.video.file_id).file_path))
                            archivo_multimedia=[os.path.abspath(archivo.name), "video"]
                            
                            
                    elif message.content_type=="audio":
                        
                        try:
                            extension="." + str(os.path.basename(os.path.basename(bot.get_file(message.audio.file_id).file_path)).split(".")[-1])
                            nombre=f"{message.audio.performer} - {message.audio.title}{extension}"
                        except:
                            contador=0
                            for i in message.audio.file_name:
                                if not i.isdigit():
                                    break
                                else:
                                    contador+=1
                                    
                            nombre={message.audio.file_name[contador:]}
                            
                        with open(os.path.join(os.path.abspath(os.path.join(ruta_root ,"Publicaciones_media")) , f"{len(lote_publicaciones)+1}_{nombre}"), "wb") as archivo:
                            archivo.write(bot.download_file(bot.get_file(message.audio.file_id).file_path))
                            archivo_multimedia=[os.path.abspath(archivo.name), "audio"]
                            
                            
                    elif message.content_type=="document":
                        with open(os.path.join(os.path.abspath(os.path.join(ruta_root ,"Publicaciones_media")) ,f"{len(lote_publicaciones)+1}_{os.path.basename(bot.get_file(message.document.file_id).file_path)}"), "wb") as archivo:
                            archivo.write(bot.download_file(bot.get_file(message.document.file_id).file_path))
                            archivo_multimedia=[os.path.abspath(archivo.name), "document"]
                            
                except Exception as e:
                    if "file is too big" in str(e.args):
                        bot.send_message(message.chat.id, "Al parecer el archivo que enviaste era demasiado grande :(\nEl límete de tamaño debe der ser 20 MB\n\nOperación cancelada")
                        
                    else:
                        bot.send_message(message.chat.id, f"Ha ocurrido un error desconocido :( Operación cancelada\n\nDescripción del error:\n{e.args}")
                        
                    return "ERROR"
                        
        
                        
                
                else:
                    bot.send_message(message.chat.id, "Al parecer, el archivo adjunto que has enviado no es ni una foto, ni un audio, ni un video, ni un documento.\n\nNo puedo recibirlo, dejaré tu publicación en solamente texto")
                    
                    if message.caption:
                        texto_publicacion[message.chat.id]=[message.caption, False]
                        
                        
                    
                    else:
                        texto_publicacion[message.chat.id]=[False, False]
                        bot.send_message(message.chat.id, "La publicación no tiene ¡NADA! ¡Ni archivos adjuntos ni texto!\nEs mejor que ni la tenga en cuenta :/\n\nOperación cancelada, presiona /panel")
                        return "ERROR"

                    return


                if message.caption:
                    texto_publicacion[message.chat.id]=[message.caption, archivo_multimedia]
                
                else:
                    texto_publicacion[message.chat.id]=[False, archivo_multimedia]
    
    

                return 
            

            

            texto_publicacion={}
            texto_publicacion[message.chat.id]=[]
                        
            
            if message.content_type=="text":
                #si es un mensaje de texto solamente 
                texto_publicacion[message.chat.id].append(message.text)
                #al ser solamente un mensaje de texto, no posee multimedia asi que le agrego el False
                texto_publicacion[message.chat.id].append(False)
                
                
                
            
            else:
                #si no es solamente un mensaje de texto...Comprobar
                res = comprobar_medios(message, texto_publicacion)
                if res == "ERROR":
                    return
            


            try:
                if len(re.findall("{{.}}", texto_publicacion[message.chat.id][0].lower()))%2==1:
                    bot.send_message(message.chat.id, "Al parecer, has abierto alguna secuencia de llaves de {{estilo}} pero no lo haz cerrado\nRecuerda que para abrir un estilo también tienes que cerrarlo con la misma secuencia de llaves\n\n<u>Ejemplo</u>\n{{n}}Texto dentro del estilo{{n}} : <b>Texto dentro del estilo</b>")
                    bot.send_message(message.chat.id, "Te devuelvo atrás :)")
                    return
                
                elif re.findall("{{.}}", texto_publicacion[message.chat.id][0].lower())==[]:
                    texto_publicacion[message.chat.id].append(False)
                    pass
                
    
                
                else: 
                    if re.search("{{b}}", texto_publicacion[message.chat.id][0]):
                        texto_publicacion[message.chat.id].append(InlineKeyboardMarkup())
                        
                    else:
                        texto_publicacion[message.chat.id].append(False)
                        
                        
                    estilos=["{{n}}", "{{s}}", "{{i}}", "{{m}}", "{{b}}"]

                    for estilo in estilos:
                        contador=1
                        for i in re.finditer(estilo, texto_publicacion[message.chat.id][0].lower()):
                            busqueda=re.search(estilo, texto_publicacion[message.chat.id][0])
                            if estilo=="{{n}}":
                                if contador==1:
                                    texto_publicacion[message.chat.id][0]=texto_publicacion[message.chat.id][0].replace(texto_publicacion[message.chat.id][0][busqueda.span()[0]:busqueda.span()[1]], "<b>", 1)
                                    contador=2
                                elif contador==2:
                                    texto_publicacion[message.chat.id][0]=texto_publicacion[message.chat.id][0].replace(texto_publicacion[message.chat.id][0][busqueda.span()[0]:busqueda.span()[1]], "</b>", 1)
                                    contador=1
                                    
                            elif estilo=="{{s}}":
                                if contador==1:
                                    texto_publicacion[message.chat.id][0]=texto_publicacion[message.chat.id][0].replace(texto_publicacion[message.chat.id][0][busqueda.span()[0]:busqueda.span()[1]], "<u>", 1)
                                    contador=2
                                elif contador==2:
                                    texto_publicacion[message.chat.id][0]=texto_publicacion[message.chat.id][0].replace(texto_publicacion[message.chat.id][0][busqueda.span()[0]:busqueda.span()[1]], "</u>", 1)
                                    contador=1
                                    
                            elif estilo=="{{i}}":
                                if contador==1:
                                    texto_publicacion[message.chat.id][0]=texto_publicacion[message.chat.id][0].replace(texto_publicacion[message.chat.id][0][busqueda.span()[0]:busqueda.span()[1]], "<i>", 1)
                                    contador=2
                                elif contador==2:
                                    texto_publicacion[message.chat.id][0]=texto_publicacion[message.chat.id][0].replace(texto_publicacion[message.chat.id][0][busqueda.span()[0]:busqueda.span()[1]], "</i>", 1)
                                    contador=1
                            
                            elif estilo=="{{m}}":
                                if contador==1:
                                    texto_publicacion[message.chat.id][0]=texto_publicacion[message.chat.id][0].replace(texto_publicacion[message.chat.id][0][busqueda.span()[0]:busqueda.span()[1]], "<code>", 1)
                                    contador=2
                                elif contador==2:
                                    texto_publicacion[message.chat.id][0]=texto_publicacion[message.chat.id][0].replace(texto_publicacion[message.chat.id][0][busqueda.span()[0]:busqueda.span()[1]], "</code>", 1)
                                    contador=1
                            
                            elif estilo=="{{b}}":
                                for i in re.finditer("{{b}}", texto_publicacion[message.chat.id][0].lower()):
                                    if contador==1:
                                        comienzo=i.span()[0]
                                        contador=2
                                    elif contador==2:
                                        final=i.span()[1]
                                        copia_texto=texto_publicacion[message.chat.id][0][comienzo:final]
                                        if not re.search(r"%.*%", copia_texto):
                                            bot.send_message(message.chat.id, "¡Haz olvidado poner el texto del botón! No registraré el mensaje hasta que todo esté correcto mirei\n\nTe devuelvo atrás")
                                            return
                                        else:
                                            boton_texto=re.search(r"%.*%", copia_texto).group().replace("%","")
                                            copia_texto.replace(re.search(r"%.*%", copia_texto).group(), "")
                                            
                                            
                                        if not re.search(r"&.*&", copia_texto):
                                            bot.send_message(message.chat.id, "¡Haz olvidado poner el enlace hacia dónde conduce el botón! No registraré el mensaje hasta que todo esté correcto mirei\n\nTe devuelvo atrás")
                                            return

                                        else:
                                            boton_enlace=re.search(r"&.*&", copia_texto).group().replace("&","")
                                            copia_texto.replace(re.search(r"&.*&", copia_texto).group(), "")
                                            
                                            
                                        texto_publicacion[message.chat.id][0]=texto_publicacion[message.chat.id][0].replace(texto_publicacion[message.chat.id][0][comienzo:final], "" , 1)
                                        texto_publicacion[message.chat.id][0]=texto_publicacion[message.chat.id][0].strip()
                                        texto_publicacion[message.chat.id][2].add(InlineKeyboardButton(boton_texto, url=boton_enlace))
                                        contador=1
                                        break
                                    
                            else:
                                continue
                                    
                        
            
            except Exception as e:
                if not texto_publicacion[message.chat.id][0]:
                    texto_publicacion[message.chat.id].append(False)
                    pass
                
                else:
                    bot.send_message(message.chat.id, f"Ha ocurrido una excepción\n\nDescripción:\n{e}")
                    return
            
            if texto_publicacion[message.chat.id][2]:
                try:
                    texto_publicacion[message.chat.id][0]=texto_publicacion[message.chat.id][0].strip()
                    if texto_publicacion[message.chat.id][0]=="":
                        bot.send_message(message.chat.id, "El mensaje que ingresaste no tenía texto!!\nPonle algo de texto y vuelve aquí\n\n<u>Posible causa alternativa:</u>Muy posiblemente también ingresaste un botón {{b}} solamente, esto tampoco cuenta como texto, ingrese algo más aparte del botón\n\n\nTe regreso atrás")
                        return
                except Exception as e:
                    bot.send_message(message.chat.id, f"Ha ocurrido un error guardando el mensaje\n\n<u>Descripción</u>:\n{e}")
                    return
            
            
            
            msg=bot.send_message(message.chat.id, "<b>Por último</b> a continuación de este mensaje, introduce CUÁNTO tiempo estará el mensaje en esos canales (Escríbelo en minutos)\n\n<u>Ejemplo</u>\n'120' : osea, se publicará cada 2 horas ya q 120 minutos lo son, etcétera")
                        
            def definir_tiempo(message, markup_botones_mensaje, canales_seleccionados, archivo_multimedia, texto_publicacion):
                
                
                lote_publicaciones = usefull_functions.cargar_variables()
                
                if not message.text.isdigit():
                    msg=bot.send_message(message.chat.id, "NO! El formato debe de ser en minutos!\nIngresa nuevamente el tiempo (EN MINUTOS) en el que se va a publicar el mensaje en dichos canales")
                    
                    bot.register_next_step_handler(msg, definir_tiempo, markup_botones_mensaje, canales_seleccionados, archivo_multimedia, texto_publicacion)
                    
                    return
                
                else:
                    
                    if markup_botones_mensaje:
                        nombre=f"Objeto_{len(lote_publicaciones)+1}_markup"
                        
                        while lote_publicaciones.get(nombre):
                            print("ID para la publicación no disponible...Buscaré otro")
                            nombre=f"Objeto_{random.randint(1, len(lote_publicaciones)*2)}_markup"
                            
                        if archivo_multimedia:
                            #Renombra el archivo en caso de que haya pasado por el bucle while                        
                            os.rename(archivo_multimedia[0], os.path.join(os.path.dirname(archivo_multimedia[0]), os.path.basename(archivo_multimedia[0]).replace(re.search(r"\d+", os.path.basename(archivo_multimedia[0])).group(), re.search(r"\d+", nombre).group())))
                            
                            archivo_multimedia[0] = os.path.join(os.path.dirname(archivo_multimedia[0]), os.path.basename(archivo_multimedia[0]).replace(re.search(r"\d+", os.path.basename(archivo_multimedia[0])).group(), re.search(r"\d+", nombre).group()))
                            
                        globals()[nombre]=Publicaciones(re.search(r"\d+", nombre).group(),texto_publicacion, canales_seleccionados, int(message.text)*60, nombre ,archivo_multimedia , markup_botones_mensaje)
                        lote_publicaciones[nombre]=globals()[nombre]
                        
                        
                        
                        
                    else:
                        nombre=f"Objeto_{len(lote_publicaciones)+1}_nonmarkup"
                        
                        while lote_publicaciones.get(nombre):
                            print("ID para la publicación no disponible...Buscaré otro")
                            nombre=f"Objeto_{random.randint(1, len(lote_publicaciones)*2)}_nonmarkup"
                        
                        if archivo_multimedia:
                            #Renombra el archivo en caso de que haya pasado por el bucle while                        
                            os.rename(archivo_multimedia[0], os.path.join(os.path.dirname(archivo_multimedia[0]), os.path.basename(archivo_multimedia[0]).replace(re.search(r"\d+", os.path.basename(archivo_multimedia[0])).group(), re.search(r"\d+", nombre).group())))
                            
                            archivo_multimedia[0] = os.path.join(os.path.dirname(archivo_multimedia[0]), os.path.basename(archivo_multimedia[0]).replace(re.search(r"\d+", os.path.basename(archivo_multimedia[0])).group(), re.search(r"\d+", nombre).group()))
                            
                        
                        globals()[nombre]=Publicaciones(re.search(r"\d+", nombre).group(), texto_publicacion, canales_seleccionados, int(message.text)*60, nombre, archivo_multimedia)
                        lote_publicaciones[nombre]=globals()[nombre]
                        
                cuestion=bot.send_message(message.chat.id, "La publicación en cuestión es la siguiente:")
                
                
                diccionario_publicacion, lista_opcional= globals()[nombre].mostrar_publicacion()
                for lista in diccionario_publicacion:
                    try:
                        if lista=="photo":
                            with open(diccionario_publicacion[lista][0], "rb") as archivo:
                                if len(diccionario_publicacion[lista])==3:
                                    msg=bot.send_photo(message.chat.id, archivo, caption=diccionario_publicacion[lista][1], reply_markup=diccionario_publicacion[lista][2])
                                
                                else:
                                    msg=bot.send_photo(message.chat.id, archivo, caption=diccionario_publicacion[lista][1])
                                    
                        elif lista=="voice":
                            with open(diccionario_publicacion[lista][0], "rb") as archivo:
                                if len(diccionario_publicacion[lista])==3:
                                    msg=bot.send_voice(message.chat.id, archivo, caption=diccionario_publicacion[lista][1], reply_markup=diccionario_publicacion[lista][2])
                                
                                else:
                                    msg=bot.send_voice(message.chat.id, archivo, caption=diccionario_publicacion[lista][1])
                                
                        elif lista=="video":
                            with open(diccionario_publicacion[lista][0], "rb") as archivo:
                                if len(diccionario_publicacion[lista])==3:
                                    msg=bot.send_video(message.chat.id, archivo, caption=diccionario_publicacion[lista][1], reply_markup=diccionario_publicacion[lista][2])
                                
                                else:
                                    msg=bot.send_video(message.chat.id, archivo, caption=diccionario_publicacion[lista][1])
                        
                        elif lista=="audio":
                            with open(diccionario_publicacion[lista][0], "rb") as archivo:
                                if len(diccionario_publicacion[lista])==3:
                                    msg=bot.send_audio(message.chat.id, archivo, caption=diccionario_publicacion[lista][1], reply_markup=diccionario_publicacion[lista][2])
                                
                                else:
                                    msg=bot.send_audio(message.chat.id, archivo, caption=diccionario_publicacion[lista][1])
                        
                        elif lista=="document":
                            with open(diccionario_publicacion[lista][0], "rb") as archivo:
                                if len(diccionario_publicacion[lista])==3:
                                    msg=bot.send_document(message.chat.id, archivo, caption=diccionario_publicacion[lista][1], reply_markup=diccionario_publicacion[lista][2])
                                
                                else:
                                    msg=bot.send_document(message.chat.id, archivo, caption=diccionario_publicacion[lista][1])
                            
                        
                        elif lista=="text":
                            if len(diccionario_publicacion[lista])==2:
                                msg=bot.send_message(message.chat.id, diccionario_publicacion[lista][0], reply_markup=diccionario_publicacion[lista][1])
                            
                            else:
                                msg=bot.send_message(message.chat.id, diccionario_publicacion[lista][0])
                        
                        
                        elif lista=="error":
                            msg=bot.send_message(message.chat.id, f"Ha ocurrido un error. Notifíquele este mensaje a @mistakedelalaif\n\n<u>Descripción del Error</u>:\n{diccionario_publicacion[lista][0]}")
                            return
                    except Exception as e:
                        
                        try:
                            bot.delete_message(chat_id=call.message.chat.id , message_id=cuestion.id)
                        except:
                            pass
                        
                        if "Disallowed character in URL host" in str(e.args):
                            
                            bot.send_message(message.chat.id, "<b>¡Has ingresado una URL incorrecta en los botones!</b>\nCuando vayas a crear un botón con alguna URL, como por ejemplo:\n\n{{b}}%Texto del botón% <b>&Enlace del botón&</b>{{b}}\n\nDebes asegurarte de que el campo de <b>&Enlace del botón%</b> tenga una dirección correcta a Internet\n\nCancelaré la Operación actual :(")
                            
                        else:
                            bot.send_message(message.chat.id, f"Al parecer ha ocurrido un error\n\nMuy posiblemente este error se deba a que empezaste con una {{etiqueta}} y pusiste el cierre de esa {{etiqueta}} dentro de otra diferente. Por favor no hagas eso.\nSi igualmente cree que esa no es la causa del error notífiquele a @mistakedelalaif, mi creador\n\n<u><b>Descripción del error</b></u>:\n{e}\n\nCancelaré la Operación actual :(")
                        
                        del lote_publicaciones[nombre]
                        del globals()[nombre]
                        lote_publicaciones = usefull_functions.guardar_variables(lote_publicaciones)
                        
                        return lote_publicaciones
                
                
                for i in lista_opcional:
                    bot.send_message(message.chat.id, i)
                    
                    
                    
                bot.reply_to(msg, f"<b>El ID de esta publicación es</b>: <code>{globals()[nombre].ID}</code>\n\n<b>Los grupos de publicación son</b>: {str([str(f"<a href='{bot.get_chat(i).invite_link}'>{bot.get_chat(i).title}</a>") for i in globals()[nombre].canales])}\n\n<b>Se publicará cada</b>: {globals()[nombre].tiempo_publicacion // 60 // 60} hora(s), {globals()[nombre].tiempo_publicacion // 60 % 60} minutos y {globals()[nombre].tiempo_publicacion % 60} segundos\n\n{str('-'*20)}\nRecuerda el ID por si quieres volver a trabajar con esta publicación a futuro\n\nPresiona /panel para volver atrás")
                
                usefull_functions.guardar_variables(lote_publicaciones)
                
                return lote_publicaciones
            
            # texto_publicacion[message.chat.id]=[message.caption, [os.path.abspath(archivo.name), "document"], InlineKeyboardMarkup()]
            

            
            bot.register_next_step_handler(msg, definir_tiempo, texto_publicacion[message.chat.id][2], canales_seleccionados, texto_publicacion[message.chat.id][1], texto_publicacion[message.chat.id][0])
            
            
        
        
            
            
    
            
        def process_publish(message, operacion=False, conexion=conexion ,cursor=cursor):
            

            
            if message.text=="Cancelar Operación":
                bot.send_message(message.chat.id, "Muy bien :) Cancelaré el proceso anterior", reply_markup=ReplyKeyboardRemove())
                return
        
            elif message.text=="Agregar" or operacion == "Agregar":

                
                try:
                    cursor.execute("SELECT ID FROM CANALES")
                    dict_temp[call.from_user.id] = cursor.fetchall()
                    
                except Exception as e:
                    
                    if "closed cursor" in e.args[0]:
                        try:
                            conexion, cursor = usefull_functions.cargar_conexion()
                            process_publish(message, "agregar", conexion, cursor)
                            
                        except:
                            bot.send_message(message.chat.id, f"¡Error!\n\nError intentando crear una nueva publicacion pero sin existir base de datos\n\nDescripcion del error:\n{e}")
                            
                    
                    
                    elif "no such table" in  e.args[0]:
                        
                        conexion, cursor = usefull_functions.cargar_conexion()
                        
                        msg = bot.send_message(message.chat.id, "No hay ningún canal en la Base de datos como para crear una nueva publicacion!", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Añadir Canal(es)", callback_data="anadir_canal")]]))
                        
                        bot.register_next_step_handler(msg , usefull_functions.channel_register, bot, call, cursor, conexion, lote_publicaciones)
                        
                        
                        
                    else:
                        bot.send_message(message.chat.id, f"¡Error!\n\nError intentando crear una nueva publicacion pero sin existir base de datos\n\nDescripcion del error:\n{e}")
                    
                    
                    return
                        
                        
                if not dict_temp[call.from_user.id]:
                    markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Agregar canal(es) 💻", callback_data="anadir_canal"))
                    bot.send_message(call.message.chat.id, "<b>¡No hay ningún canal en la lista de canales!</b>\n\nAgrega uno y vuelve aquí", reply_markup=markup)
                    return
                
                lista_seleccionada = []
                    
                usefull_functions.agregar_canal_publicacion(bot, call, 0, lista_seleccionada , cursor)
                
        if "deselect" in call.data:
            # call.data = callback_data=f"publicacion/c/deselect'{indice_inicial}:{indice}"
            cursor.execute("SELECT ID FROM CANALES")
            
            dict_temp[call.from_user.id] = cursor.fetchall()
            
            
            lista_seleccionada.remove(dict_temp[call.from_user.id][int(re.search(r":.*", call.data).group().replace(":", ""))][0])
            
            
            usefull_functions.agregar_canal_publicacion(bot, call, int(re.search(r"'.*:", call.data).group().replace(":", "").replace("'", "")), lista_seleccionada, cursor)   
                
        
        elif "select" in call.data:
            #callback_data=f"publicacion/c/select'{indice_inicial}:{indice}"
            cursor.execute("SELECT ID FROM CANALES")
            
            dict_temp[call.from_user.id] = cursor.fetchall()
        
            lista_seleccionada.append(dict_temp[call.from_user.id][int(re.search(r":.*", call.data).group().replace(":", ""))][0])
            
            usefull_functions.agregar_canal_publicacion(bot, call, int(re.search(r"'.*:", call.data).group().replace(":", "").replace("'", "")), lista_seleccionada, cursor)
                

                
            return



        
        
        elif "/s" in call.data:
            
            try:
                if int(re.search(r":.*", call.data).group().replace(":", ""))<0:
                    bot.answer_callback_query(call.id, "¡Ya estás en la primera lista!", True)
                
                elif int(re.search(r":.*", call.data).group().replace(":", ""))>=len(dict_temp[call.from_user.id]):
                    bot.answer_callback_query(call.id, "¡Ya estás en la última lista!", True)

                
                else:
                    usefull_functions.agregar_canal_publicacion(bot, call, int(re.search(r":.*", call.data).group().replace(":", "")), lista_seleccionada, cursor)
                    
            except Exception as e:
                bot.send_message(call.message.chat.id, f"Ha ocurrido un error intentando acceder a la lista de canales.\n\n¿El mensaje al que intentabas acceder no habrá sido enviado hace mucho tiempo?\nMuy posiblemente haya caducado\n\nDescripción del error:\n{e.args}")
                
            
            return
        
        elif "/_sb" in call.data:
            # /_sb = select_bethween
            # "publicacion/c/sb:{indice_inicial}-{indice-1}"
            
            cursor.execute("SELECT ID FROM CANALES")
            
            lista_fetch = cursor.fetchall()
            
            dict_temp[call.from_user.id] = [int(i) for i in re.search(r":.*", call.data).group().replace(":", "").split("-")]
            
            for i in range(dict_temp[call.from_user.id][0], dict_temp[call.from_user.id][1] + 1):
                    
                if lista_fetch[i][0] in lista_seleccionada:
                    continue
                else:
                    lista_seleccionada.append(lista_fetch[i][0])
            
            usefull_functions.agregar_canal_publicacion(bot, call, dict_temp[call.from_user.id][0], lista_seleccionada, cursor)
            
            return
        

        elif "/da" in call.data:
            lista_seleccionada.clear()
            
            usefull_functions.agregar_canal_publicacion(bot, call, int(re.search(r":.*", call.data).group().replace(":", "")), lista_seleccionada, cursor)
            
            
                
        elif "/cancel" in call.data:
            
            lista_seleccionada.clear()
            
            usefull_functions.enviar_mensajes(bot, call, "Operación Cancelada exitosamente :)", InlineKeyboardMarkup([[InlineKeyboardButton("Volver al Menú ♻", callback_data="volver_menu")]]))
            
            return
                
            
        elif "confirm" in call.data:
            
            if not lista_seleccionada:
                usefull_functions.enviar_mensajes(bot, call, "¡No hay ningún canal seleccionado para publicar!\n\nOperación Cancelada :( presiona /panel")
                return
            
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
             
            dict_temp[call.from_user.id] = lista_seleccionada.copy()
            
            msg=bot.send_message(call.message.chat.id, "A continuación, haz la publicación o reenvíala aquí :)\n\n<u><b>Ayuda para crear publicaciones en este bot</b></u>\nA continuación, pondré los formatos que debes de introducir en la izquierda y en la derecha el resultado en el texto que sale:\n\n\n<code>{{n}}Texto en Negrita{{n}}</code> : <b>Texto en negrita</b>\n<code>{{s}}Texto en Subrayado{{s}}</code> : <u>Texto en subrayado</u>\n<code>{{i}}Texto en Itálica{{i}}</code> : <i>Texto en italica</i>\n<code>{{m}}Texto en Monoespaciado{{m}}</code> : <code>Texto en Monoespaciado</code>\n<code>{{b}}%Texto del botón% &Enlace del botón&{{b}}</code> : (el botón es el que está debajo de este mensaje)\n\nTambién puedes adjuntar fotos, audios o documentos al mensaje ;D \n(OJO: El tamaño no puede sobrepasar los 20 MB o obtendrás un error)\n\nAhora envía tu mensaje :D", reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Texto del botón", url="https://google.com")))
            
            lista_seleccionada.clear()
            
            
            bot.register_next_step_handler(msg, add_publish, dict_temp[call.from_user.id] , msg)
        
         
        
        else:
                
            try:
                cursor.execute("SELECT ID FROM CANALES")
                dict_temp[call.from_user.id] = cursor.fetchall()
                
            except Exception as e:
                
                if "no such table" in  e.args[0]:
                    
                    conexion, cursor = usefull_functions.cargar_conexion()
                    
                    msg = bot.send_message(call.message.chat.id, "No hay ningún canal en la Base de datos como para crear una nueva publicacion!", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Añadir Canal(es)", callback_data="anadir_canal")]]))
                    
                    bot.register_next_step_handler(msg , usefull_functions.channel_register, bot, call, cursor, conexion, lote_publicaciones)
                    return
                    
                else:
                    bot.send_message(call.message.chat.id, f"¡Error!\n\nError intentando crear una nueva publicacion pero sin existir base de datos\n\nDescripcion del error:\n{e}")
                    return
                    
                    
            if not dict_temp[call.from_user.id]:
                markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Agregar canal(es) 💻", callback_data="anadir_canal"))
                bot.send_message(call.message.chat.id, "<b>¡No hay ningún canal en la lista de canales!</b>\n\nAgrega uno y vuelve aquí", reply_markup=markup)
                return
            
            lista_seleccionada = []
                
            usefull_functions.agregar_canal_publicacion(bot, call, 0, lista_seleccionada , cursor)
        
        
        return
    
        
        
        


    

    elif call.data=="agregar_publicacion":
        user=call.from_user.id
        
        cursor.execute("SELECT * FROM CANALES")
        lista=cursor.fetchall()
        
        if hilo_publicaciones_activo==True:
            bot.send_message(call.from_user, "¡No puedes modificar el archivo de publicaciones mientras está el hilo de publicaciones activo! Detén las Publicaciones para poder modificar su archivo\n\nTe devuelvo atrás")
            return
        
        if lista== []:
            markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Agregar Canal(es) 💻", callback_data="anadir_canal"))
            
            bot.send_message(call.from_user.id, "<b>¡No hay ningún canal en la lista!</b> ¡Agrega alguno antes!", reply_markup=markup)
            return
        
        
        
        if not lote_publicaciones:
            markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Agregar/Quitar publicación 📋🪒", callback_data="publicacion"))
            bot.send_message(call.from_user.id, "<b>¡No hay ninguna Publicación en la lista!</b>\n¡Agrega alguna antes!", reply_markup=markup)
            return
        
        markup=ReplyKeyboardMarkup(True, True, input_field_placeholder="Selecciona una opción", row_width=2)
        markup.add("Agregar Canal", "Quitar Canal")
        markup.row("Cancelar Operacion")
        
        msg=bot.send_message(call.from_user.id, "Bien, ahora dime ¿Quieres <b>Agregar</b> Canales a una Publicación o <b>Quitar</b> Canales de una Publicación?", reply_markup=markup)
        
        
        def agregar_publicacion_agregar_canal(message):
            markup=ReplyKeyboardMarkup(True, True, input_field_placeholder="Selecciona el ID", row_width=3)
            
            markup.row("Cancelar Operación")
            
            for publicacion in lote_publicaciones:
                ID=str(lote_publicaciones[publicacion].ID)
                markup.add(ID)
                
                
            msg=bot.send_message(message.chat.id, "Selecciona a continuación el ID de la publicación a la que quieres agregarle los canales", reply_markup=markup)
            
            def agregar_publicacion_agregar_canales(message, publicacion):
                if message.text=="Finalizar Operación":
                    bot.send_message(message.chat.id, "Muy bien te devuelvo atrás :)", reply_markup=ReplyKeyboardRemove())
                    return
                
                cursor.execute("SELECT * FROM CANALES")
                lista=cursor.fetchall()
                contador=0
                for tupla_canal in lista:
                    if tupla_canal[1]==message.text:
                        contador+=1
                        publicacion.canales.append(tupla_canal[0])
                        bot.send_message(message.chat.id, "Canal agregado exitosamente a la Publicación",  reply_markup=ReplyKeyboardRemove())
                        usefull_functions.guardar_variables(lote_publicaciones)
                        
                        
                if contador==0:
                    bot.send_message(message.chat.id, "¡No has seleccionado ningún canal de la lista!\n\nTe devuelvo atrás", reply_markup=ReplyKeyboardRemove())
                    return

                else:
                    markup=ReplyKeyboardMarkup(True, True, input_field_placeholder="Elige una opción").add("Si", "No")
                    msg=bot.send_message(message.chat.id, "¿Quieres seguir agregando canales a las Publicaciones?", reply_markup=markup)
                    
                    def agregar_publicacion_repetir(message):
                        if message.text=="Si":
                            bot.send_message(message.chat.id, "Excelente, te enviaré de vuelta a la elección de Publicación :)", reply_markup=ReplyKeyboardRemove())
                            return agregar_publicacion_agregar_canal(message)
                        
                        elif message.text=="No":
                            bot.send_message(message.chat.id, "Muy bien, te devolveré atrás :)", reply_markup=ReplyKeyboardRemove())
                            return 

                        else:
                            bot.send_message(message.chat.id, "No has presionado ninguna de las opciones disponibles, te devolveré atrás", reply_markup=ReplyKeyboardRemove())
                            return
                    
                    bot.register_next_step_handler(msg, agregar_publicacion_repetir)
                    
            
            
            
            def agregar_publicacion_elegir_canal(message, publicacion):
                markup=ReplyKeyboardMarkup(True, True, input_field_placeholder="Elige uno", row_width=3)
                cursor.execute("SELECT * FROM CANALES")
                lista=cursor.fetchall()
                
                markup.row("Finalizar Operación")
                for tupla_canal in lista:
                    if tupla_canal[0] in publicacion.canales:
                        continue
                    
                    markup.add(tupla_canal[1])


                if len(markup.keyboard)==1:
                    bot.send_message(message.chat.id, "Al parecer ya esta Publicación se envía a TODOS los canales <b>disponibles</b>, no hace caso querer agregar a más en su repertorio\n\nTe devuelvo atrás :)")
                    return
                    
                msg=bot.send_message(message.chat.id, "Muy bien, de los siguientes canales, a cuál planeas agregar a esta publicación",reply_markup=markup)
                
                return bot.register_next_step_handler(msg, agregar_publicacion_agregar_canales, publicacion)
            
            
            
            
            def agregar_publicacion_procesar_respuesta(message):
                if message.text=="Cancelar Operación":
                    bot.send_message(message.chat.id, "Muy bien, te devuelvo atrás :)", reply_markup=ReplyKeyboardRemove())
                    return
            
                elif not message.text.isdigit():
                    bot.send_message(message.chat.id, "Tenías que presionar uno de los botones Mastodonte!, te devuelvo atrás", reply_markup=ReplyKeyboardRemove())
                    return
                
                else:
                    contador=0
                    for publicacion in lote_publicaciones:
                        
                        if int(lote_publicaciones[publicacion].ID)==int(message.text):
                            contador+=1
                            bot.send_message(message.chat.id, "Encontré la Publicación :D", reply_markup=ReplyKeyboardRemove())
                            publicacion=lote_publicaciones[publicacion]
                            return agregar_publicacion_elegir_canal(message, publicacion)
                            
                            
                    if contador==0:
                        bot.send_message(message.chat.id, "No había ninguna publicación con ese ID Mastodonte, te devuelvo atrás", reply_markup=ReplyKeyboardRemove())
                        return
            
            bot.register_next_step_handler(msg, agregar_publicacion_procesar_respuesta)
        
        
        def agregar_publicacion_quitar_canal_publicacionID(message):
            markup=ReplyKeyboardMarkup(True, True, input_field_placeholder="Selecciona el ID", row_width=3)
            
            markup.row("Cancelar Operación")
            
            for publicacion in lote_publicaciones:
                ID=str(lote_publicaciones[publicacion].ID)
                markup.add(ID)
                
                
            msg=bot.send_message(message.chat.id, "Selecciona a continuación el ID de la publicación a la que quieres quitarle los canales", reply_markup=markup)
            
            def agregar_publicacion_quitar_canales(message):
                if not message.text.isdigit():
                    bot.send_message(message.chat.id, "¡Debes de presionar los botones!\nNo ingreses nada por tu cuenta!\n\nTe devolveré atrás", reply_markup=ReplyKeyboardRemove())
                    return
                
                contador=0
                for publicacion in lote_publicaciones:
                    if int(lote_publicaciones[publicacion].ID) == int(message.text):
                        contador+=1
                        publicacion=lote_publicaciones[publicacion]
                        break
                        
                if contador==0:
                    bot.send_message(message.chat.id, "¡Debes de presionar los botones!\nNo ingreses nada por tu cuenta!\n\nTe devolveré atrás", reply_markup=ReplyKeyboardRemove())
                    return
                
                else:
                    bot.send_message(message.chat.id, "Publicación encontrada :D", reply_markup=ReplyKeyboardRemove())
                    markup=ReplyKeyboardMarkup(True, True, input_field_placeholder="Elige un Canal para Eliminar de la Publicación")
                    
                    for canal in publicacion.canales:
                        try:
                            markup.add(bot.get_chat(canal).title)
                        except Exception as e:
                            cursor.execute("SELECT * FROM CANALES")
                            lista=cursor.fetchall()
                            for tupla_canal in lista:
                                if tupla_canal[0]==canal:
                                    bot.send_message(message.chat.id, f"Al parecer ha ocurrido un error con <b>{tupla_canal[1]}</b>\n\nMuy posiblemente este canal/grupo me bloqueó o no existe ya, recomiendo deshacerse de él o agregarme nuevamente como administrador con todos los derechos que necesito para publicar y eliminar\n\n<u><b>Descripción del error</b></u>\n{e}")
                                    
                                    markup.add(tupla_canal[1])
                                    break
                                
                    msg=bot.send_message(message.chat.id, "Muy bien, ahora selecciona el Canal/Grupo que quieres que sea eliminado de la Publicación", reply_markup=markup)
                    
                    
                    def agregar_publicacion_quitar_canales_procesar(message, publicacion, lote_publicaciones=lote_publicaciones):
                        contador=0
                        cursor.execute("SELECT * FROM CANALES")
                        lista=cursor.fetchall()
                        for tupla_canal in lista:
                            if tupla_canal[1]==message.text:
                                contador+=1
                                publicacion.canales.remove(tupla_canal[0])
                                usefull_functions.guardar_variables(lote_publicaciones)
                                
                        if contador==0:
                            bot.send_message(message.chat.id, "¡Debiste de haber seleccionado uno de los canales que te ofrecí en los botones!\n\nTe devuelvo atrás", reply_markup=ReplyKeyboardRemove())
                            return
                        else:
                            bot.send_message(message.chat.id, "Canal eliminado de la Publicación exitosamente :)", reply_markup=ReplyKeyboardRemove())
                            markup=ReplyKeyboardMarkup(True, True, input_field_placeholder="Elige una opción")
                            markup.add("Si", "No")
                            bot.send_message(message.chat.id, "¿Quieres ELIMINAR algún otro canal de una Publicación?", reply_markup=markup)
                            
                            
                            def agregar_publicacion_quitar_canales_repetir(message):
                                if message.text=="Si":
                                    bot.send_message(message.chat.id, "Muy bien, regresaré para quitar otro canal de alguna Publicación", reply_markup=ReplyKeyboardRemove())
                                    agregar_publicacion_quitar_canal_publicacionID(message)
                                    
                                elif message.text=="No":
                                    bot.send_message(message.chat.id, "Muy bien, terminaré el proceso\n\nTe devuelvo atrás :)", reply_markup=ReplyKeyboardRemove())
                                    return
                                
                                else:
                                    bot.send_message(message.chat.id, "¡Tenías que escoger una de las opciones!\n\nTe devuelvo atrás", reply_markup=ReplyKeyboardRemove())
                                    return
                            
                            bot.register_next_step_handler(msg, agregar_publicacion_quitar_canales_repetir)
                    
                    bot.register_next_step_handler(msg, agregar_publicacion_quitar_canales_procesar, publicacion)
                        
                
                
            
            bot.register_next_step_handler(msg, agregar_publicacion_quitar_canales)
            
            
            
        
        def agregar_publicacion_process_answer(message):
            
            if message.text=="Cancelar Operacion":
                bot.send_message(message.chat.id, "Operación Cancelada, te devuelvo atrás", reply_markup=ReplyKeyboardRemove())
                return

            elif message.text=="Agregar Canal":
                bot.send_message(message.chat.id, "Muy bien, agregaré canales a la Publicación", reply_markup=ReplyKeyboardRemove())
                agregar_publicacion_agregar_canal(message)
            
            elif message.text=="Quitar Canal":
                bot.send_message(message.chat.id, "Muy bien, quitaré canales de una Publicación", reply_markup=ReplyKeyboardRemove())
                agregar_publicacion_quitar_canal_publicacionID(message)
        
        bot.register_next_step_handler(msg, agregar_publicacion_process_answer)
        


    elif "del_publicaciones" in  call.data:
        
        lote_publicaciones=usefull_functions.cargar_variables()
        
        if len(lote_publicaciones)==0:
            usefull_functions.enviar_mensajes(bot, call, "¡Aún no hay Publicaciones guardadas!\nHaz tu primera Publicación presionando en el botón '<b>Agregar Publicación 📋🪒</b>'" , InlineKeyboardMarkup([[InlineKeyboardButton("Agregar Publicación 📋🪒", callback_data="publicacion")]]))

                
            
            return
            
            
        if "search" in call.data:
            
            if int(re.search(r":.*", call.data).group().replace(":", "")) < 0:
                bot.answer_callback_query(call.id, "¡Ya estás en la primera parte de la lista!", True)
                return
            
            elif int(re.search(r":.*", call.data).group().replace(":", "")) >= len(lote_publicaciones):
                bot.answer_callback_query(call.id, "¡Ya estás en la última parte de la lista!", True)
                return
            
            else:                
                usefull_functions.ver_publicaciones(call, bot, call.from_user.id, cursor, int(re.search(r":.*", call.data).group().replace(":", "")), lote_publicaciones)
            
            return
        
        elif "index" in call.data:
            
            del lote_publicaciones[re.search(r":.*", call.data).group().replace(":", "")]
            
            try:
                del globals()[re.search(r":.*", call.data).group().replace(":", "")]
                
            except:
                print("Error intentando borrar la variable global")
                
            usefull_functions.guardar_variables(lote_publicaciones)


    elif call.data=="eliminar_publicacion":
        #Esto es para establecer un tiempo de eliminación de una publicación

        
        cursor.execute("SELECT * FROM CANALES")
        lista=cursor.fetchall()
        
        
        
        if not lote_publicaciones:

            usefull_functions.enviar_mensajes(bot, call , "<b>¡No hay ninguna Publicación en la lista!</b> ¡Agrega alguna antes!" , InlineKeyboardMarkup([[InlineKeyboardButton("Agregar/Quitar publicación 📋🪒", callback_data="publicacion")]]))

            return
        
        markup = ReplyKeyboardMarkup(True, True, input_field_placeholder="Selecciona el ID de la publicación", row_width=3)
        for publicacion in lote_publicaciones:
            markup.add(str(lote_publicaciones[publicacion].ID))
        
        
        msg=bot.send_message(call.from_user.id, "Ahora, seleccione el ID de la publicación a la que le quiere definir el tiempo para que se elimine\n\nNota:\nEsta eliminación se aplica LUEGO de ser publicada en los Canales y OBVIAMENTE tiene que ser MENOR que el tiempo en el que se hace dicha publicación", reply_markup=markup)
        
        
        def eliminar_publicacion_ID_publicacion(message):
            
            msg=usefull_functions.enviar_mensajes(bot, call, "Comprobaré la publicación" , ReplyKeyboardRemove() , message)

            contador=0
            for publicacion in lote_publicaciones:
                if int(message.text)==lote_publicaciones[publicacion].ID:
                    contador+=1
                    publicacion_elegida=lote_publicaciones[publicacion]
                    break
                    
            if contador==0:
                usefull_functions.enviar_mensajes(bot, call, "¡Presiona uno de los botones!\n\nOperacion Cancelada" , ReplyKeyboardRemove() , msg)
                return
            

            else:
                if (publicacion_elegida.tiempo_publicacion/60)//60>=1:
                    msg = usefull_functions.enviar_mensajes(bot, call, f"Muy bien, ahora INGRESA a continuación de ESTE mensaje, la cantidad de tiempo (en MINUTOS) que querrás que pase para que luego de hecha la publicación esta se elimine\n\n<u>Ejemplo de mensaje</u>:\n'120' : representará 120 minutos lo cual son 2 horas\nEste tiempo OBVIAMENTE tiene que ser MENOR que el tiempo en el que se hace dicha publicación\n\nTiempo actual de esta Publicación en los canales es de: <b>{int(str(int((publicacion_elegida.proxima_publicacion - time.time())/60//60)).replace('-', ''))} hora(s) y {int((publicacion_elegida.tiempo_publicacion/60)%60)} minuto(s)</b>", msg=msg)
                else:
                    msg = usefull_functions.enviar_mensajes(bot, call, f"Muy bien, ahora INGRESA a continuación de ESTE mensaje, la cantidad de tiempo (en MINUTOS) que querrás que pase para que luego de hecha la publicación esta se elimine\n\n<u>Ejemplo de mensaje</u>:\n'120' : representará 120 minutos lo cual son 2 horas\nEste tiempo OBVIAMENTE tiene que ser MENOR que el tiempo en el que se hace dicha publicación\n\nTiempo actual de esta Publicación en los canales es de: <b>{(int(publicacion_elegida.tiempo_publicacion/60))} minuto(s)</b>", msg=msg)


                def eliminar_publicacion_tiempo_publicacion(message, publicacion_elegida, lote_publicaciones=lote_publicaciones):
                    
                    if not message.text.isdigit():
                        usefull_functions.enviar_mensajes(bot,call,"¡Tenías que ingresar una cantidad de minutos!\n\nTe devuelvo atrás", msg=message)

                        return
                    elif int(message.text)>=publicacion_elegida.tiempo_publicacion/60:
                        
                        usefull_functions.enviar_mensajes(bot,call,"¡El tiempo de eliminación no puede ser mayor al tiempo de la próxima publicación del mensaje! Debes de ingresar un valor menor a este\n\nTe devuelvo atrás", msg=message)

                        return
                    
                    else:
                        publicacion_elegida.tiempo_eliminacion=int(message.text)*60
                        
                    if (publicacion_elegida.tiempo_publicacion/60)//60>=1:
                        
                        msg = usefull_functions.enviar_mensajes(bot,call,f"Muy bien, el tiempo de eliminación de la publicación se ha establecido correctamente a: <b>{int(str(int((publicacion_elegida.proxima_eliminacion - time.time())/60//60)).replace('-', ''))} hora(s) y {int((publicacion_elegida.tiempo_eliminacion/60)%60)} minuto(s)</b>", msg=message)
                        
                    else:
                        msg = usefull_functions.enviar_mensajes(bot,call,f"Muy bien, el tiempo de eliminación de la publicación se ha establecido correctamente a: <b>{(int(publicacion_elegida.tiempo_eliminacion/60))} minuto(s)</b>", msg=message)
                        
                    
                    
                    usefull_functions.guardar_variables(lote_publicaciones)
                    
                    usefull_functions.enviar_mensajes(bot,call, f"Muy bien, te devuelvo atrás :)", msg=msg)
                    

                    return                        
                
                bot.register_next_step_handler(msg, eliminar_publicacion_tiempo_publicacion, publicacion_elegida)
                
        bot.register_next_step_handler(msg, eliminar_publicacion_ID_publicacion)
        
        
    elif "ver_publicaciones" in call.data or "operacion" in call.data:
        
        
        lote_publicaciones=usefull_functions.cargar_variables()
        
        if len(lote_publicaciones)==0:
            usefull_functions.enviar_mensajes(bot, call, "¡Aún no hay Publicaciones guardadas!\nHaz tu primera Publicación presionando en el botón '<b>Agregar Publicación 📋🪒</b>'" , InlineKeyboardMarkup([[InlineKeyboardButton("Agregar Publicación 📋🪒", callback_data="publicacion")]]))

                
            
            return
        
        
        if "send" in call.data:
                # call.data == ver_publicaciones_config/send:<nombre de la publicación en lote_publicaciones>

                usefull_functions.enviar_publicacion(lote_publicaciones[re.search(":.*", call.data).group().replace(":", "")], call.from_user.id, bot, cursor,admin, lote_publicaciones, hilo_publicaciones_activo)
                return

        elif "del" in call.data:
            
            if hilo_publicaciones_activo==True:
                bot.send_message(call.from_user.id, "¡No puedo modificar las publicaciones si hay publicaciones en curso!\n\n¡Para el hilo de publicaciones y luego inténtalo!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Detener hilo de publicación 🛑", callback_data="admin_hilo")]], row_width=1))
                return
            
            
            #extraigo el string del diccionario de la publicación
            n_publicacion = re.search(r":.*", call.data).group().replace(":", "")
                
            # copia_lote_publicaciones=lote_publicaciones.copy()

            if lote_publicaciones[n_publicacion].multimedia:
                
                try:
                    os.remove(lote_publicaciones[n_publicacion].multimedia[0])
                    
                except Exception as e:
                    bot.send_message(call.from_user.id, f"Por alguna razón no se ha podido eliminar el fichero adjunto a la publicación\nComúnicale a @mistakedelalaif\n\n<u>Descripción del error</u>:\n{e}")
                
            del lote_publicaciones[n_publicacion]

            

            usefull_functions.guardar_variables(lote_publicaciones)
        
            try:
                bot.edit_message_text("Publicación eliminada exitosamente", call.from_user.id, call.message.message_id, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Volver Atrás 🔙", callback_data="ver_publicaciones")]]))
                
            except:
                bot.send_message(call.from_user.id, "Publicación eliminada exitosamente")
        
        
            return
            
            
        if "ver_publicaciones_search" in call.data:
            
            
            
            if int(re.search(r":.*", call.data).group().replace(":", "")) < 0:
                bot.answer_callback_query(call.id, "¡Ya estás en la primera parte de la lista!", True)
                return
            
            elif int(re.search(r":.*", call.data).group().replace(":", "")) >= len(lote_publicaciones):
                bot.answer_callback_query(call.id, "¡Ya estás en la última parte de la lista!", True)
                return
            
            else:                
                usefull_functions.ver_publicaciones(call, bot, call.from_user.id, cursor, int(re.search(r":.*", call.data).group().replace(":", "")), lote_publicaciones)
            
            return
            
            
        elif "ver_publicaciones_index:" in call.data:
            
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
                            
            publicacion=lote_publicaciones[re.search(r":.*", call.data).group().replace(":", "")]
        

            if publicacion.multimedia:               

                
                dict_temp={}

                
                dict_temp[call.from_user.id], lista_opcional = publicacion.mostrar_publicacion()
                
                
                lote_publicaciones=usefull_functions.cargar_variables()
                        
                try:
                    match publicacion.multimedia[1]:
                        case "photo":
                            if publicacion.markup:
                                if publicacion.texto:
                                    msg=bot.send_photo(call.from_user.id, telebot.types.InputFile(publicacion.multimedia[0]), caption=publicacion.texto , reply_markup=publicacion.markup)
                                    
                                else:
                                    msg=bot.send_photo(call.from_user.id, telebot.types.InputFile(publicacion.multimedia[0]), reply_markup=publicacion.markup)
                            
                            
                            else:
                                if publicacion.texto:
                                    msg=bot.send_photo(call.from_user.id, telebot.types.InputFile(publicacion.multimedia[0]), caption=publicacion.texto)
                                    
                                else:
                                    msg=bot.send_photo(call.from_user.id, telebot.types.InputFile(publicacion.multimedia[0]))
                        
                        case "document" : 
                            if publicacion.markup:
                                if publicacion.texto:
                                    msg=bot.send_document(call.from_user.id, telebot.types.InputFile(publicacion.multimedia[0]), caption=publicacion.texto, reply_markup=publicacion.markup)
                                    
                                else:
                                    msg=bot.send_document(call.from_user.id, telebot.types.InputFile(publicacion.multimedia[0]), reply_markup=publicacion.markup)
                                
                                
                            else:
                            
                                if publicacion.texto:
                                    msg=bot.send_document(call.from_user.id, telebot.types.InputFile(publicacion.multimedia[0]), caption=publicacion.texto)
                                else:
                                    msg=bot.send_document(call.from_user.id, telebot.types.InputFile(publicacion.multimedia[0]))
                                
                        case "voice":
                            if publicacion.markup:
                                if publicacion.texto:
                                    msg=bot.send_voice(call.from_user.id, telebot.types.InputFile(publicacion.multimedia[0]), caption=publicacion.texto, reply_markup=publicacion.markup)
                                else:
                                    msg=bot.send_voice(call.from_user.id, telebot.types.InputFile(publicacion.multimedia[0]), reply_markup=publicacion.markup)
                                
                                
                            else:
                            
                                if publicacion.texto:
                                    msg=bot.send_voice(call.from_user.id, telebot.types.InputFile(publicacion.multimedia[0]), caption=publicacion.texto)
                                else:
                                    msg=bot.send_voice(call.from_user.id, telebot.types.InputFile(publicacion.multimedia[0]))
                        
                        
                        case "audio":
                            if publicacion.markup:
                                if publicacion.texto:
                                    msg=bot.send_audio(call.from_user.id, telebot.types.InputFile(publicacion.multimedia[0]), caption=publicacion.texto, reply_markup=publicacion.markup)
                                else:
                                    msg=bot.send_audio(call.from_user.id, telebot.types.InputFile(publicacion.multimedia[0]), reply_markup=publicacion.markup)
                                
                                
                            else:
                            
                                if publicacion.texto:
                                    msg=bot.send_audio(call.from_user.id, telebot.types.InputFile(publicacion.multimedia[0]), caption=publicacion.texto)
                                else:
                                    msg=bot.send_audio(call.from_user.id, telebot.types.InputFile(publicacion.multimedia[0]))
                                
                        case "video":
                            
                            if publicacion.markup:
                                
                                if publicacion.texto:
                                    msg=bot.send_video(call.from_user.id, telebot.types.InputFile(publicacion.multimedia[0]), caption=publicacion.texto, reply_markup=publicacion.markup)
                                else:
                                    msg=bot.send_video(call.from_user.id, telebot.types.InputFile(publicacion.multimedia[0]), reply_markup=publicacion.markup)
                            
                            else:
                                if publicacion.texto:
                                    msg=bot.send_video(call.from_user.id, telebot.types.InputFile(publicacion.multimedia[0]), caption=publicacion.texto)
                                else:
                                    msg=bot.send_video(call.from_user.id, telebot.types.InputFile(publicacion.multimedia[0]))
                                    
                except Exception as e:
                    bot.send_message(call.message.chat.id, f"¡Ha ocurrido un error intentando enviar el archivo!\n\nDescripción del error:\n{e.args}")
                    return
                    
                            
            else:
                if publicacion.markup:
                    msg=bot.send_message(call.from_user.id, publicacion.texto, reply_markup=publicacion.markup)
                    
                else:
                    msg=bot.send_message(call.from_user.id, publicacion.texto) 
                    
            
            res = usefull_functions.comprobar_canales(bot, conexion, cursor)
            
            if res:
                bot.send_message(call.from_user.id, res)
            # for canal in publicacion.canales:
            #     try:
            #         if not bot.get_chat_member(canal, bot.user.id).can_send_messages:
            #             publicacion.canales.remove(canal)
            #     except:
            #         publicacion.canales.remove(canal)
                                
            lote_publicaciones =  usefull_functions.guardar_variables(lote_publicaciones)
            if hilo_publicaciones_activo:
                lote_publicaciones=usefull_functions.cargar_variables()
                


                if publicacion.tiempo_eliminacion:
                    
                    if publicacion.canales:
                        dict_temp[call.from_user.id]=f"<b>ID de Publicación</b>: <code>{publicacion.ID}</code>\n\n<b>Canales de la Publicación</b>:  {[f"<a href='{bot.get_chat(i).invite_link}'>{bot.get_chat(i).title}</a>"  for i in publicacion.canales]}\n\n<b>Tiempo definido para la publicación</b>: {publicacion.tiempo_publicacion//60//60} hora(s) {(publicacion.tiempo_publicacion//60)%60} minuto(s)  {publicacion.tiempo_publicacion%60} segundo(s)\n\n<b>Tiempo restante para su próxima publicación</b>: {(int(publicacion.proxima_publicacion - time.time() //60) //60)} hora(s) / {int(((publicacion.proxima_publicacion - time.time())//60)%60)} minuto(s)\n\n<b>Tiempo definido para la eliminación</b>: {publicacion.tiempo_eliminacion//60//60} hora(s) {(publicacion.tiempo_eliminacion//60)%60} minuto(s)\n\n<b>Tiempo restante para su próxima eliminación</b>: {int((publicacion.proxima_eliminacion - time.time())//60//60)} hora(s) {int(((publicacion.proxima_eliminacion - time.time())//60)%60)} minuto(s)\n\n"
                        
                    else:
                        dict_temp[call.from_user.id]=f"<b>ID de Publicación</b>: <code>{publicacion.ID}</code>\n\n<b>Canales de la Publicación</b>: <b>♿️ ¡No hay! ¡Agrega alguno! ‼️</b>\n\n<b>Tiempo definido para la publicación</b>: {publicacion.tiempo_publicacion//60//60} hora(s) {(publicacion.tiempo_publicacion//60)%60} minuto(s)  {publicacion.tiempo_publicacion%60} segundo(s)\n\n<b>Tiempo restante para su próxima publicación</b>: {int((publicacion.proxima_publicacion - time.time())//60//60)} hora(s) / {int(((publicacion.proxima_publicacion - time.time())//60)%60)} minuto(s)\n\n<b>Tiempo definido para la eliminación</b>: {publicacion.tiempo_eliminacion//60//60} hora(s) {(publicacion.tiempo_eliminacion//60)%60} minuto(s)\n\n<b>Tiempo restante para su próxima eliminación</b>: {int((publicacion.proxima_eliminacion - time.time())//60//60)} hora(s) {int(((publicacion.proxima_eliminacion - time.time())//60)%60)} minuto(s)\n\n"
                    
                else:
                    
                    if publicacion.canales:
                        
                        
                    
                        dict_temp[call.from_user.id]=f"<b>ID de Publicación</b>: <code>{publicacion.ID}</code>\n\n<b>Canales de la Publicación</b>:  {[f"<a href='{bot.get_chat(i).invite_link}'>{bot.get_chat(i).title}</a>"  for i in publicacion.canales]}\n\n<b>Tiempo definido para la publicación</b>: {int(publicacion.tiempo_publicacion)//60//60} hora(s) {(int(publicacion.tiempo_publicacion)//60)%60} minuto(s)  {int(publicacion.tiempo_publicacion)%60} segundo(s)\n\n<b>Tiempo restante para su próxima publicación</b>: {int(publicacion.proxima_publicacion - time.time() ) // 60 // 60} horas(s) / {int(((publicacion.proxima_publicacion - time.time())//60)%60)} minuto(s) / {int(((publicacion.proxima_publicacion - time.time()))%60)} segundo(s)\n\n"
                        
                    else:
                        
                        dict_temp[call.from_user.id]=f"<b>ID de Publicación</b>: <code>{publicacion.ID}</code>\n\n<b>Canales de la Publicación</b>: <b>♿️ ¡No hay! ¡Agrega alguno! ‼️</b>\n\n<b>Tiempo definido para la publicación</b>: {int(publicacion.tiempo_publicacion)//60//60} hora(s) {(int(publicacion.tiempo_publicacion)//60)%60} minuto(s)  {int(publicacion.tiempo_publicacion)%60} segundo(s)\n\n<b>Tiempo restante para su próxima publicación</b>: {int(publicacion.proxima_publicacion - time.time() ) // 60 // 60} horas(s) / {(int(publicacion.proxima_publicacion - time.time())//60)%60} minuto(s) / {int(((publicacion.proxima_publicacion - time.time()))%60)} segundo(s)\n\n"
                    
                    
            
            else:
                if publicacion.canales:
                    dict_temp[call.from_user.id]=f"<b>ID de Publicación</b>: <code>{publicacion.ID}</code>\n\n<b>Canales de la Publicación</b>:  {[f"<a href='{bot.get_chat(i).invite_link}'>{bot.get_chat(i).title}</a>"  for i in publicacion.canales]}\n\nEl hilo de publicaciones no está activo (no se está publicando)"
                    
                else:
                    dict_temp[call.from_user.id]=f"<b>ID de Publicación</b>: <code>{publicacion.ID}</code>\n\n<b>Canales de la Publicación</b>: <b>♿️ ¡No hay! ¡Agrega alguno! ‼️</b>\n\nEl hilo de publicaciones no está activo (no se está publicando)"
            
            
    
            

            
            markup=InlineKeyboardMarkup(row_width=1)
            
            markup.row(InlineKeyboardButton("Enviar Post Ahora 📨", callback_data=f"ver_publicaciones/send:{re.search(r":.*", call.data).group().replace(":", "")}"))
            markup.row(InlineKeyboardButton("Eliminar Post 📃✖", callback_data=f"ver_publicaciones/del:{re.search(r":.*", call.data).group().replace(":", "")}"))
            
            # "Cambiar hora de Envío 📃✖" Programará la publicación a una hora local concreta. 
            # El tiempo de mi cliente Danny es el de Perú - Lima, el mismo que el de Cuba, para hallar un tiempo fijo, independientemente de dónde sea el host, voy a usar el time.gmtime() que tiene 5 horas de adelanto y restarle las horas para que dé la adecuada
            markup.row(InlineKeyboardButton("Cambiar hora de Envío ⌛", callback_data=f"ver_publicaciones/time_to_post:{re.search(r":.*", call.data).group().replace(":", "")}")) 
            markup.row(InlineKeyboardButton("Cambiar tiempo de repetición de envío 🔃", callback_data=f"ver_publicaciones/change_time:{re.search(r":.*", call.data).group().replace(":", "")}"))
            if not publicacion.canales:
                markup.row(InlineKeyboardButton("♿️ Agregar canales a la Publicación ➕‼️", callback_data=f"ver_publicaciones/cc/anadir:{re.search(r":.*", call.data).group().replace(":", "")}"))
                
            else:
                markup.row(InlineKeyboardButton("Agregar/Eliminar canales a/de la Publicación 👥", callback_data=f"ver_publicaciones/cc/:{re.search(r":.*", call.data).group().replace(":", "")}"))
                
            
            markup.row(InlineKeyboardButton("Volver Atrás 🔙", callback_data="ver_publicaciones"))
                                
            
            
            try:
                bot.reply_to(msg, dict_temp[call.from_user.id], reply_markup=markup)
            except Exception as e:
                try:
                    bot.send_message(call.from_user.id ,dict_temp[call.from_user.id], reply_markup=markup)
                except:
                    bot.send_message(call.from_user.id, f"Se ha producido un error intentando proporcionar la información de la publicación\n\n{e}")
                    
            return
        

            

        elif "time_to_post" in call.data:
            
            msg=bot.send_message(call.from_user.id, "‼Alerta‼ : Esta configuración está adecuada para la zona horaria de Lima/Perú, si tienes dudas contacta con @mistakedelalaif\n\nCon esta opción programarás la Publicación para que sea enviada en una fecha concreta\nA continuación envía la hora en el siguiente formato:\n\n <code>Hora:Minuto:Día:Mes:Año</code>\n\n\n<u>Ejemplo de uso</u>:\n<code>17:35:2:7:2030</code>\n\n(La hora debe estar representada en formato de 24 horas [00-23]el mes debe estar representado en formato númerico [1-12] y el año debe estar representado con sus 4 digitos, no con los últimos 2)\n\n\nA continuación de este mensaje, envía la programación deseada teniendo en cuenta lo explicado, si quieres cancelar pulsa en el botón 'Cancelar Operación'", reply_markup=telebot.types.ReplyKeyboardMarkup(True, True).add("Cancelar Operación"))
            
            
            def time_to_post_register(message, msg ,publicacion, lote_publicaciones=lote_publicaciones, hilo_publicaciones_activo=hilo_publicaciones_activo):

                # try:
                #     bot.delete_message(msg.chat.id, msg.message_id)
                #     bot.delete_message(message.chat.id, message.message_id)
                # except:
                #     pass
                
                message.text=message.text.strip()
                
                
                if message.text.lower()=="Cancelar Operación".lower():
                    bot.send_message(message.chat.id, "Muy bien, Operación Cancelada :)", reply_markup=ReplyKeyboardRemove())
                    
                    return
                
                dict_temp={}
                
                
                    
                dict_temp[message.from_user.id]=message.text.split(":")
                
                if not ":" in message.text:
                    msg=bot.send_message(message.chat.id, "Has introducido un formato incorrecto, recuerda que tiene que ser como el siguiente:\n\n<code>Hora:Minuto:Día:Mes:Año</code>\n\n<u>Ejemplo de uso</u>:\n<code>17:35:2:7:2030</code>\n\nLa hora debe estar representada en formato de 24 horas [00-23]el mes debe estar representado en formato númerico [1-12] y el año debe estar representado con sus 4 digitos, no con 2\n\n\nA continuación de este mensaje, envía la programación deseada teniendo en cuenta lo explicado, si quieres cancelar pulsa en el botón 'Cancelar Operación'" , reply_markup=telebot.types.ReplyKeyboardMarkup(True, True).add("Cancelar Operación"))
                    
                    bot.register_next_step_handler(msg, time_to_post_register, publicacion)   
                    
                    return
                
                
                elif not len(dict_temp[message.from_user.id]) == 5:
                    msg=bot.send_message(message.chat.id, "Has introducido un formato incorrecto, recuerda que tiene que ser como el siguiente:\n\n<code>Hora:Minuto:Día:Mes:Año</code>\n\n<u>Ejemplo de uso</u>:\n<code>17:35:2:7:2030</code>\n\nLa hora debe estar representada en formato de 24 horas [00-23]el mes debe estar representado en formato númerico [1-12] y el año debe estar representado con sus 4 digitos, no con 2\n\n\nA continuación de este mensaje, envía la programación deseada teniendo en cuenta lo explicado, si quieres cancelar pulsa en el botón 'Cancelar Operación'" , reply_markup=telebot.types.ReplyKeyboardMarkup(True, True).add("Cancelar Operación"))
                    
                    bot.register_next_step_handler(msg, time_to_post_register, publicacion)   
                    
                    
                    return
                            

                                        
                try:
                    
                    dict_temp[message.from_user.id]=time.mktime(time.strptime(f"{dict_temp[message.from_user.id][0]}:{dict_temp[message.from_user.id][1]}:{dict_temp[message.from_user.id][2]}:{dict_temp[message.from_user.id][3]}:{dict_temp[message.from_user.id][4]}", r"%H:%M:%d:%m:%Y"))

                    
                    hora = usefull_functions.calcular_diferencia_horaria(dict_temp[message.from_user.id])



                    if call.from_user.id == 1413725506:
                        bot.send_message(message.chat.id, "Hora Actual en Perú: " +  time.ctime(usefull_functions.calcular_diferencia_horaria(devolver="peru")) + "\nContenido del mensaje: " + message.text + "\nHora actual del host: " + time.ctime(time.time()) + "\nHora de envio: " + time.ctime(hora))
                    
                    
                    
                    if time.localtime(hora) <= time.localtime(time.time()):
                        bot.send_message(message.chat.id, "¡Has establecido una programación futura menor al horario actual en Perú!\n\nOperación cancelada", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Menú | Volver ♻", callback_data="volver_menu")]]))
                        return
                    

                    
                    
                    bot.send_message(message.chat.id, "La Publicación se enviará {}".format(time.strftime(r"a las %I:%M %p el día %d del mes %m (%B), en el año %Y", time.localtime(usefull_functions.calcular_diferencia_horaria(hora, "hora_peru") + 1))), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Menú | Volver ♻", callback_data="volver_menu")]]))
                        
                        
                    lote_publicaciones[publicacion].proxima_publicacion = hora
                    
                             

                    
                    usefull_functions.guardar_variables(lote_publicaciones)
                    
                    if hilo_publicaciones_activo == False:
                        
                        bot.send_message(message.chat.id, "¡El hilo de publicaciones no está activo!\n\nActívalo para que la publicación sea hecha en el momento determinado", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Inciar hilo de publicación 💡", callback_data="admin_hilo")]]))
                    
                    
                    
                    
                    
                except Exception as e:
                    bot.send_message(message.chat.id, f"¡Ha ocurrido un error! ¿Has introducido mal el formato?\n\nDescripción del error:\n{e}")
                    return
                    
                return
                
            
            bot.register_next_step_handler(msg, time_to_post_register, msg ,re.search(r":.*", call.data).group().replace(":", ""))

        elif "change_time" in call.data:
            #
            #callback_data=f"ver_publicaciones_config/change_time:{re.search(r":.*", call.data).group().replace(":", "")}"))
            
            
            publicacion=re.search(r":.*", call.data).group().replace(":", "")
                
            msg=bot.send_message(call.from_user.id, "Esta Publicación se envía cada {} hora(s), {} minuto(s) y {} segundo(s)\n\nEnvíe un nuevo intervalo de tiempo de espera entre cada publicación en MINUTOS a continuación de ESTE mensaje".format(lote_publicaciones[publicacion].tiempo_publicacion // 60 // 60, lote_publicaciones[publicacion].tiempo_publicacion // 60 % 60, lote_publicaciones[publicacion].tiempo_publicacion % 60), reply_markup=ReplyKeyboardMarkup(True, True).add("Cancelar Operación"))
            
            def change_time_data(message, lote_publicaciones=lote_publicaciones):
                
                
                if message.text=="Cancelar Operación":
                    bot.send_message(message.chat.id, "Operación cancelada")
                    return
                
                elif not message.text.isdigit():
                    bot.send_message(call.from_user.id, "Debe ser el tiempo en MINUTOS solamente!\n\nOperación cancelada")
                    return
                
                
                bot.send_message(message.chat.id, f"Muy bien, la publicación se efectuará cada {message.text} minuto(s)", reply_markup=ReplyKeyboardRemove())
                
                lote_publicaciones[publicacion].tiempo_publicacion=int(message.text)*60
                
                usefull_functions.guardar_variables(lote_publicaciones)
                
                return
                
            
            bot.register_next_step_handler(msg, change_time_data)
                
        #cc = change_channels
        elif "/cc/" in call.data or "operacion" in call.data:
            # callback_data=f"ver_publicaciones_config/change_channels:{re.search(r":.*", call.data).group().replace(":", "")}"
            
            
            if "anadir" in call.data and not "operacion" in call.data:
                lote_publicaciones = usefull_functions.cargar_variables()


                lista_seleccionada=[]
                
                cursor.execute("SELECT ID FROM CANALES")
                
                dict_temp[call.from_user.id] = cursor.fetchall()
                
                if not dict_temp[call.from_user.id]:
                    
                    usefull_functions.enviar_mensajes(bot, call, "No tienes NINGÚN canal en la Base de Datos\n\nAgrega alguno antes de pensar en agregar alguno a la Publicación" , InlineKeyboardMarkup([[InlineKeyboardButton("Añadir Canal(es)", callback_data=f"anadir_canal")]]))
                    return
                    


                i, e, l_operacion=usefull_functions.change_channels(call, call.from_user.id, bot, 0, lote_publicaciones[re.search(r":.*", call.data).group().replace(":", "")], "anadir" , operacion, cursor=cursor, conexion=conexion)
                
                return
                
            elif "eliminar" in call.data and not "operacion" in call.data:
                
                existe = False
                for i in lote_publicaciones:
                    if i == re.search(r":.*", call.data).group().replace(":", ""):
                        publicacion=lote_publicaciones[i]
                        existe = True
                        break
                

                if existe == False:
                    bot.answer_callback_query(call.id, "¡La Publicación a la que intentas acceder ya no existe!", True)
                    return
                
                
                if not publicacion.canales:
                    
                    usefull_functions.enviar_mensajes(bot, call, "No tienes NINGÚN chat en esta Publicacion\n\nAgrega alguno antes de pensar en borrar", InlineKeyboardMarkup([[InlineKeyboardButton("Añadir Canal(es)", callback_data=f"ver_publicaciones/cc/anadir:{publicacion.nombre}")]]))
                    return
                    
                    
                
                lista_seleccionada.clear()
                        
                i, e, operacion=usefull_functions.change_channels(call, call.from_user.id , bot, 0 , lote_publicaciones[re.search(r":.*", call.data).group().replace(":", "")], "eliminar", operacion)
                
                
                
                return operacion
                
                
            
            if "operacion" in call.data:
            
                if "anadir" in call.data:
                
                
                
                    if "search" in call.data:
                        # call.data = operacion_anadir/search:{indice}&{publicacion.ID}
                        
                        existe = False
                        for i in lote_publicaciones:
                            if int(lote_publicaciones[i].ID) == int(re.search(r"&\d+", call.data).group().replace("&", "")):
                                publicacion=lote_publicaciones[i]
                                existe = True
                                break

                        if existe == False:
                            bot.answer_callback_query(call.id, "¡La Publicación a la que intentas acceder ya no existe!", True)
                            return
                        
                        cursor.execute("SELECT ID FROM CANALES")
                        dict_temp[call.from_user] = cursor.fetchall()
                            
                        if len(dict_temp[call.from_user]) <= int(re.search(r":.*&", call.data).group().replace(":", "").replace("&", "")):
                            bot.answer_callback_query(call.id, "Ya estás en la última parte de la lista!", True)
                            return
                            
                        elif int(re.search(r":.*&", call.data).group().replace(":", "").replace("&", "")) < 0:
                            bot.answer_callback_query(call.id, "Ya estás en la primera parte de la lista!", True)
                            return
                        
                        i, e, l_operacion=usefull_functions.change_channels(call, call.from_user.id, bot, int(re.search(r":\d+", call.data).group().replace(":", "")), publicacion, "anadir", operacion,  lista_seleccionada=lista_seleccionada, cursor=cursor, conexion=conexion)
                        
                        
                        
                        
                    elif "deselect" in call.data:
                        # call.data = f"operacion_anadir/deselect${indice_inicial}:{indice}&{publicacion.ID}"
                        
                        existe = False
                        for i in lote_publicaciones:
                            if int(lote_publicaciones[i].ID) == int(re.search(r"&\d+", call.data).group().replace("&", "")):
                                publicacion=lote_publicaciones[i]
                                existe = True
                                break
                    
                        if existe == False:
                            bot.answer_callback_query(call.id, "¡La Publicación a la que intentas acceder ya no existe!", True)
                            return
                        
                        cursor.execute("SELECT ID FROM CANALES")
                        dict_temp[call.from_user.id]=cursor.fetchall()
                        
                        try:
                            lista_seleccionada.remove(dict_temp[call.from_user.id][int(re.search(r":.*&", call.data).group().replace(":", "").replace("&", ""))][0])
                            
                            i, e , operacion = usefull_functions.change_channels(call, call.from_user.id, bot, int(re.search(r"'.*:", call.data).group().replace(":", "").replace("'", "")), publicacion, "anadir", operacion ,lista_seleccionada, cursor, conexion)
                            
                            # i, e , operacion = usefull_functions.change_channels(call, call.from_user.id, bot, int(re.search(r":.*&", call.data).group().replace(":", "").replace("&", ""))-(int(re.search(r":.*&", call.data).group().replace(":", "").replace("&", ""))%10), publicacion, "anadir", operacion ,lista_seleccionada, cursor, conexion)
                            
                            
                        except Exception as e:
                            bot.send_message(call.message.chat.id, f"Ha ocurrido un error!\n\nDescripción del error:\n{e.args}")
                        
                        
                        
                        
                    
                    elif "select" in call.data:
                        # call.data = f"operacion_anadir/deselect'{indice_inicial}:{indice}&{publicacion.ID}"
                        existe = False                        
                        for i in lote_publicaciones:
                            if int(lote_publicaciones[i].ID) == int(re.search(r"&.*", call.data).group().replace("&", "")):
                                publicacion=lote_publicaciones[i]
                                existe = True
                                break
                        
                        if existe == False:
                            bot.answer_callback_query(call.id, "¡La Publicación a la que intentas acceder ya no existe!", True)
                            return
                        
                        cursor.execute("SELECT ID FROM CANALES")
                        dict_temp[call.from_user.id]=cursor.fetchall()
                        
                        lista_seleccionada.append(dict_temp[call.from_user.id][int(re.search(r":.*&", call.data).group().replace(":", "").replace("&", ""))][0])
                        
                        
                        i, e, l_operacion=usefull_functions.change_channels(call, call.from_user.id, bot, int(re.search(r"'.*:", call.data).group().replace(":", "").replace("'", "")), publicacion, "anadir", operacion ,lista_seleccionada, cursor, conexion)
                            
                            
                        
                    
                        
                    elif "select_bethween" in call.data:
                        # call.data = "operacion_anadir/select_bethween:{indice_inicial}-{indice-1}&{publicacion.ID}"
                        
                        dict_temp[call.from_user.id]=[int(i) for i in re.search(r":.*&", call.data).group().replace("&", "").replace(":", "").split("-")]
                        
                        existe = False
                        
                        for i in lote_publicaciones:
                            if int(lote_publicaciones[i].ID) == int(re.search(r"&.*", call.data).group().replace("&", "")):
                                publicacion=lote_publicaciones[i]
                                existe = True
                                break
                        
                        if existe == False:
                            bot.answer_callback_query(call.id, "¡La Publicación a la que intentas acceder ya no existe!", True)
                            return
                                
                        
                        for i in range(dict_temp[call.from_user.id][0], dict_temp[call.from_user.id][1] + 1):
                            
                            if publicacion.canales[i] in lista_seleccionada:
                                continue
                            else:
                                lista_seleccionada.append(publicacion.canales[i])
                        
                        i, e, l_operacion=usefull_functions.change_channels(call, call.from_user.id, bot, dict_temp[call.from_user.id][0], publicacion, "anadir", operacion ,lista_seleccionada, cursor, conexion)
                        
                        return
                        
                        
                    elif "deselect_all" in call.data:
                        
                        existe = False
                        for i in lote_publicaciones:
                            if int(lote_publicaciones[i].ID) == int(re.search(r"&.*", call.data).group().replace("&", "")):
                                dict_temp[call.from_user.id]=lote_publicaciones[i]
                                existe = True
                                break
                                
                        if existe == False:
                            bot.answer_callback_query(call.id, "¡La Publicación a la que intentas acceder ya no existe!", True)
                            return
                        
                        
                        if not lista_seleccionada :
                            bot.answer_callback_query(call.id, "¡No hay ningún chat seleccionado!")
                            return
                        
                        lista_seleccionada=lista_seleccionada.clear()
                        
                        
                        
                        bot.answer_callback_query(call.id, "Se han deseleccionado TODOS los chats")
                        
                        i, e, l_operacion=usefull_functions.change_channels(call, call.from_user.id, bot, int(re.search(r":.*&", call.data).group().replace(":", "").replace("&", "")), dict_temp[call.from_user.id], "anadir", operacion , lista_seleccionada, cursor, conexion)
                        
                        return
                    
                    elif "confirm" in call.data:
                        
                        
                        if not lista_seleccionada:
                            usefull_functions.enviar_mensajes(bot, call, "¡No hay ningún canal seleccionado!\n\nOperación Cancelada :(\n\nPresiona /panel para regresar")
                            return
                        
                        existe = False                       
                        for i in lote_publicaciones:
                            if int(lote_publicaciones[i].ID) == int(re.search(r"\d+", call.data).group()):
                                publicacion=lote_publicaciones[i]
                                existe = True
                                break
                            
                        
                        
                        
                        for i in lista_seleccionada:
                            
                            if i in publicacion.canales:
                                pass
                            else:
                                publicacion.canales.append(i)
                        
                        usefull_functions.enviar_mensajes(bot, call, "Chats añadidos a la publicación exitosamente :)")    

                        usefull_functions.guardar_variables(lote_publicaciones)
                        
                        lista_seleccionada.clear()
                        
                        
                        
                        return
                        
                        
                        
                        
                        
                
                
                elif "eliminar" in call.data:
                    
                    
                    
                    if "deselect" in call.data:
                        # call.data = f"operacion_eliminar/deselect'{indice_inicial}:{indice}&{publicacion.ID}"
                        existe = False
                        for i in lote_publicaciones:
                            if int(lote_publicaciones[i].ID) == int(re.search(r"&.*", call.data).group().replace("&", "")):
                                
                                publicacion = lote_publicaciones[i]
                                existe = True                                
                                
                                break
                            
                        if existe == False:
                            bot.answer_callback_query(call.id, "¡La Publicación a la que intentas acceder ya no existe!", True)
                            return
                        
                        lista_seleccionada.remove(publicacion.canales[int(re.search(r":.*&", call.data).group().replace(":", "").replace("&", ""))])        
                                            
                        i, e, l_operacion=usefull_functions.change_channels(call, call.from_user.id, bot, int(re.search(r"'.*:", call.data).group().replace(":", "").replace("'", "")), publicacion, "eliminar", operacion ,lista_seleccionada)
                        
                        # i, e, l_operacion=usefull_functions.change_channels(call, call.from_user.id, bot, int(re.search(r":.*&", call.data).group().replace(":", "").replace("&", "")) - int(re.search(r":.*&", call.data).group().replace(":", "").replace("&", "")) %10, dict_temp[call.from_user.id], "eliminar", operacion ,lista_seleccionada)
                        
                        
                    
                    if "select" in call.data:
                        # call.data = f"operacion_eliminar/select'{indice_inicial}:{indice}&{publicacion.ID}"
                        existe = False
                        
                        for i in lote_publicaciones:
                            if int(lote_publicaciones[i].ID) == int(re.search(r"&.*", call.data).group().replace("&", "")):
                                
                                publicacion = lote_publicaciones[i]
                                
                                existe = True

                                break
                                
                        if existe == False:
                            bot.answer_callback_query(call.id, "¡La Publicación a la que intentas acceder ya no existe!", True)
                            return
                        
                        lista_seleccionada.append(publicacion.canales[int(re.search(r":.*&", call.data).group().replace(":", "").replace("&", ""))])
                        
                        # i, e, l_operacion=usefull_functions.change_channels(call, call.from_user.id, bot, int(re.search(r":.*&", call.data).group().replace(":", "").replace("&", "")) - int(re.search(r":.*&", call.data).group().replace(":", "").replace("&", "")) %10, dict_temp[call.from_user.id], "eliminar", operacion ,lista_seleccionada)

                        i, e, l_operacion=usefull_functions.change_channels(call, call.from_user.id, bot, int(re.search(r"'.*:", call.data).group().replace(":", "").replace("'", "")), publicacion, "eliminar", operacion ,lista_seleccionada)
                        
                        return
                    
                    elif "search" in call.data:
                        # call.data = f"operacion_anadir/search:{indice}&{publicacion.ID}"

                        existe = False
                        
                        for i in lote_publicaciones:
                            if int(lote_publicaciones[i].ID) == int(re.search(r"&.*", call.data).group().replace("&", "")):
                                publicacion=lote_publicaciones[i]
                                
                                existe = True
                                break
                        
                        if existe == False:
                            bot.answer_callback_query(call.id, "¡La Publicación a la que intentas acceder ya no existe!", True)
                            return
                        
                        
                        if len(publicacion.canales) <= int(re.search(r":.*&", call.data).group().replace(":", "").replace("&", "")):
                            bot.answer_callback_query(call.id, "Ya estás en la última parte de la lista!", True)
                            return
                            
                        elif int(re.search(r":.*&", call.data).group().replace(":", "").replace("&", "")) < 0:
                            bot.answer_callback_query(call.id, "Ya estás en la primera parte de la lista!", True)
                            return
                            
                            
                        i, e, l_operacion=usefull_functions.change_channels(call, call.from_user.id, bot, int(re.search(r"\d+", call.data).group()), publicacion, "eliminar", operacion,  lista_seleccionada=lista_seleccionada, cursor=cursor, conexion=conexion)
                                
                        
                    

                        

                    
                    elif "select_bethween" in call.data:
                        # callback_data = f"ver_publicaciones_config/change_channels_eliminar_select_bethween:{indice_inicial}-{indice-1}&{publicacion.ID}"
                        
                        dict_temp[call.from_user.id]=[int(i) for i in re.search(r":.*&", call.data).group().replace("&", "").replace(":", "").split("-")]
                        
                        existe = False
                        for i in lote_publicaciones:
                            if int(lote_publicaciones[i].ID) == int(re.search(r"&.*", call.data).group().replace("&", "")):
                                publicacion=lote_publicaciones[i]
                                existe = True
                                break
                        
                        if existe == False:
                            bot.answer_callback_query(call.id, "¡La Publicación a la que intentas acceder ya no existe!", True)
                            return
                        
                        for i in range(dict_temp[call.from_user.id][0], dict_temp[call.from_user.id][1] + 1):
                            
                            if publicacion.canales[i] in lista_seleccionada:
                                continue
                            else:
                                lista_seleccionada.append(publicacion.canales[i])
                        
                        i, e, l_operacion=usefull_functions.change_channels(call, call.from_user.id, bot, dict_temp[call.from_user.id][0], publicacion, "eliminar", operacion ,lista_seleccionada)
                        return
                        
                        
                    elif "deselect_all" in call.data:
                        
                        if not lista_seleccionada :
                            bot.answer_callback_query(call.id, "¡No hay ningún chat seleccionado!", True)
                            return
                        
                        lista_seleccionada=lista_seleccionada.clear()
                        
                    
                        existe = False
                        for i in lote_publicaciones:
                            if int(lote_publicaciones[i].ID) == int(re.search(r"&.*", call.data).group().replace("&", "")):
                                dict_temp[call.from_user.id]=lote_publicaciones[i]
                                existe = True
                                break
                        
                        if existe == False:
                            bot.answer_callback_query(call.id, "¡La Publicación a la que intentas acceder ya no existe!", True)
                            return
                        
                        bot.answer_callback_query(call.id, "Se han deseleccionado TODOS los chats")
                        
                        i, e, l_operacion=usefull_functions.change_channels(call, call.from_user.id, bot, int(re.search(r":.*&", call.data).group().replace(":", "").replace("&", "")), publicacion , "eliminar", operacion, lista_seleccionada)
                        
                        return
                        
                    elif "confirm" in call.data:
                        
                        
                        if not lista_seleccionada:
                            usefull_functions.enviar_mensajes(bot, call, "¡No hay ningún canal seleccionado!\n\nOperación Cancelada :(\n\nPresiona /panel para regresar")
                            return
                        
                        existe = False
                        for i in lote_publicaciones:
                            if int(lote_publicaciones[i].ID) == int(re.search(r":.*", call.data).group().replace(":", "")):
                                dict_temp[call.from_user.id]=lote_publicaciones[i]
                                existe = True
                                break

                        
                        if existe == False:
                            bot.answer_callback_query(call.id, "¡La Publicación a la que intentas acceder ya no existe!", True)
                            return
                        
                        for i in lista_seleccionada:
                            dict_temp[call.from_user.id].canales.remove(i)
                            
                        
                        usefull_functions.enviar_mensajes(bot, call , "Chats eliminados de la publicación exitosamente :)")
                        
                        lista_seleccionada.clear()
                        
                        
                        usefull_functions.guardar_variables(lote_publicaciones)
                        return
                
            
            else:
                

                publicacion = re.search(r":.*", call.data).group().replace(":", "")
                
                markup = telebot.util.quick_markup(
                    {"Añadir Canal(es) ➕":{"callback_data" : f"ver_publicaciones/cc/anadir:{publicacion}"}, 
                    "Eliminar Canal(es) ❌":{"callback_data" : f"ver_publicaciones/cc/eliminar:{publicacion}"}}, 1
                    )
                                    
                

                
                bot.send_message(call.from_user.id, "¿Qué pretendes hacer con los canales de esta publicación?", reply_markup=markup)
            
            
    
        else:
            lote_publicaciones=usefull_functions.cargar_variables()
            usefull_functions.ver_publicaciones(call, bot, call.from_user.id, cursor, 0, lote_publicaciones)
        
        
            
        return