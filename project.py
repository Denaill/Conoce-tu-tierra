import MySQLdb
import re
import tkinter
import os
import PyPDF2
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def preguntar(pregunta):
    db = MySQLdb.connect("127.0.0.1","root","","colombia")
    cursor = db.cursor()

    LISTAR = '(traer|listar|dame|deme|obtener|cuales|dime|cuentame|cual|quiero|saber|mas)?'
    DE = '(de\s?|tiene\s?|es\s?|los\s?|las\s?)?'
    PERTENECEN = '(que\s?|todos\s?|pertenece\s?|son\s?)?'
    MUNICIXDEPART = LISTAR + PERTENECEN + DE +'(municipios|ciudades) '+ PERTENECEN + DE +'(?P<place>\w+)'
    DEPARTXMUNICI = '(?P<place1>\w+) ' + '(a\s)?' +'(que\s?|qué\s?)?' +' (departamento) '+ PERTENECEN 
    DEPARTXMUNICI2 = LISTAR + '(es\s)?' +'(el\s?)?' +' (departamento) '+ DE + '(?P<place2>\w+)'
    BUSQUEDAINTER = LISTAR + LISTAR + LISTAR + DE + '(?P<place3>\w+)'
    ERROR = '(Error)'


    palabra = re.search(MUNICIXDEPART, pregunta)
    if palabra:
        print (palabra.group('place'))
        departamento = (palabra.group('place'))
        consulta = "SELECT id_departamento FROM departamentos WHERE departamento ='%s'"%(departamento)

        cursor.execute(consulta)
        resultados = cursor.fetchall()
        id_departamento = 0
        for registro in resultados:
            id_departamento = registro[0]

        sql = "SELECT municipio FROM municipios WHERE departamento_id = %d"%(id_departamento)
        cursor.execute(sql)
        lista = ""
        resultados = cursor.fetchall()
        for registro in resultados:
            nombre = registro[0]
            lista = lista + (" ,%s"%(nombre))
        return lista
    
    palabra = re.search(DEPARTXMUNICI, pregunta)
    if palabra:
        print (palabra.group('place1'))
        municipio = (palabra.group('place1'))
        consulta = "SELECT departamento_id FROM municipios WHERE municipio = '%s'"%(municipio)

        cursor.execute(consulta)
        resultados = cursor.fetchall()
        departamento_id = 0
        for registro in resultados:
            departamento_id = registro[0]
        
        sql = "SELECT departamento FROM departamentos WHERE id_departamento = %d"%(departamento_id)
        cursor.execute(sql)
        resultados = cursor.fetchall()
        for registro in resultados:
            nombre = registro[0]
            return ("el municipio de %s pertenece a %s"%(municipio,nombre))

    palabra = re.search(DEPARTXMUNICI2, pregunta)
    if palabra:
        print (palabra.group('place2'))
        municipio = (palabra.group('place2'))
        consulta = "SELECT departamento_id FROM municipios WHERE municipio = '%s'"%(municipio)

        cursor.execute(consulta)
        resultados = cursor.fetchall()
        departamento_id = 0
        for registro in resultados:
            departamento_id = registro[0]
        
        sql = "SELECT departamento FROM departamentos WHERE id_departamento = %d"%(departamento_id)
        cursor.execute(sql)
        resultados = cursor.fetchall()
        for registro in resultados:
            nombre = registro[0]
            return ("el municipio de %s pertenece a %s"%(municipio,nombre))
    
    palabra = re.search(BUSQUEDAINTER, pregunta)
    if palabra:
        print (pregunta[20:])
        busqueda = pregunta[20:]
        driver = webdriver.Firefox()
        driver.get("http://www.google.com")
        elem = driver.find_element_by_name("q")
        elem.clear()
        elem.send_keys(busqueda)
        elem.submit()
        elem.send_keys(Keys.RETURN)
        assert "No results found." not in driver.page_source

    palabra = re.search(ERROR, pregunta)
    if palabra:
        return "Error en la consulta"

def grabando():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Que deseas saber de Colombia?")
        audio = r.listen(source)
        print("Buscando ...")
    usuario = "Error"
    try:
        print("Usted dijo: "+r.recognize_google(audio, language ='es-LA'))
        usuario = r.recognize_google(audio, language ='es-LA')
    except:
        pass
    consulta = preguntar(usuario.lower())
    tts = gTTS(consulta,'es')
    tts.save('voz.mp3')
    playsound('voz.mp3')
    os.remove('voz.mp3')

def escribiendo():
    pregunta = str(entrada.get())
    preguntar(pregunta)

def ayuda():
    os.popen('Documentos\Ayuda.pdf')

#VENTANA DE TKINTER
ventana = tkinter.Tk()
ventana.geometry('705x370')
ventana.title('Conoce tu tierra')
ventana.resizable(width=False,height=False)
ventana.configure(background='dark green')
#Fondo de ventana
imagen = tkinter.PhotoImage(file="Imagenes/fondo.png")
imagen = imagen.subsample(1,1)
label = tkinter.Label(image=imagen)
label.place(x=0,y=0)
#Icono
icono = ventana.iconbitmap('Imagenes/favicon.ico')
#Menu
menu = tkinter.Menu(ventana)
menu.add_command(label="Ayuda", command=ayuda)
menu.add_command(label="Salir", command=ventana.quit)
#Cargar menu
ventana.config(menu=menu)
#Botones, entradas y labels
entrada = tkinter.Entry(ventana)
grabar = tkinter.Button(text="Preguntame",command=grabando)
escribir = tkinter.Button(text="Preguntame sin hablar", command=escribiendo)
#Cargar todo
grabar.pack()
escribir.pack()
entrada.pack(ipadx=29,ipady=3)
#Posiciones
grabar.place(x=70,y=230)
escribir.place(x=505,y=230)
entrada.place(x=507,y=200)


ventana.mainloop()
