# -*- coding: iso-8859-15 -*-


import pygtk
pygtk.require('2.0')
import gtk
import os
import libro
import pygst
pygst.require("0.10")
import gst

from dbr_i18n import _          #For i18n support


# Comprobacion la version de pygtk
if gtk.pygtk_version < (2,3,90):
  print "PyGtk 2.3.90 or later required for this example"
  raise SystemExit


class Controlador:
  """
  Clase Controlador para el control entre la clase vista y las clases Libro, Reproductor y Registro
  """ 

  def setVista(self, v):
    self.v = v


  def __init__(self, r, reg):
    """
    Inicia un objeto Controlador para la gestión de las retrollamadas del interfaz
    r: es un objeto Reproductor
    reg: es un objeto Registro
    """
    self.r = r
    self.l = None
    self.reg = reg


  def obtener_configuracion(self):
    """
    Método para obtener la configuración del DBR. Si es la primera vez que se ejecuta la aplicación, iniciará la creación del fichero de configuración
    """
    lista_indice = []
    registro = self.reg.obtener_configuracion()
    if registro[0] != None:
      self.r.cambiar_volumen(registro[5]-1)
      if os.path.exists(registro[1]):
        self.l = libro.Libro(registro[1], (registro[2]), (registro[3]), registro[4])
        if registro[0] == self.l.obtener_nombre():
          lista_indice = self.l.obtener_indice()
        else:
          self.l = None
      else:
        self.l = None
    else:
      pass
    return lista_indice, registro[2]


  def destroy(self, widget):
    """
    Método para destruir una ventana
    """
    return True


  def carga_fichero_inicial(self):
    """
    Método para reproducir el último libro reproducido al cargar el DBR
    """
    fichero, pos_ini, pos_fin = self.l.obtener_pista()
    self.r.reproducir(fichero, pos_ini, pos_fin)


  def cargaFichero(self, w):
    """
    Método para cargar el fichero que contiene el índice del libro
    """
    # Creacion de un nuevo control de seleccion de fichero
    seleccion = gtk.FileChooserDialog(_("Open book"), None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    seleccion.set_default_response(gtk.RESPONSE_OK)

    # filtro para mostrar solo los archivos llamados ncc.html
    filtro = gtk.FileFilter()
    path = os.path.abspath("ncc")
    seleccion.set_filename(path)
    # Extension permitida para el fichero
    filtro.add_pattern("*.html")
    seleccion.add_filter(filtro)

    response = seleccion.run()
    if response == gtk.RESPONSE_OK:
      try:
        # Se carga el libro
        nombre = seleccion.get_filename()
        self.l = libro.Libro(nombre)


      except IOError:
        self.mostrar_mensaje(_("Failed to open"), _(" The book can not be opened"))


    elif response == gtk.RESPONSE_CANCEL:
      self.mostrar_mensaje(_("Canceled selection"), _("No book has been selected"))
    seleccion.destroy()
    indice = self.l.obtener_indice()
    if len(indice) > 1:
      return indice

  def change_play_pause_tollbutton(self, state):
    if state == gst.STATE_PAUSED:
      self.v.view_play_icon()
    else:
      self.v.view_pause_icon()

  def buscar_libro_callback(self, w, data):
    """
    Método para controlar la búsqueda de los libros almacenados en el fichero de configuración
    """
    reproducir = False
    if self.r.obtener_estado() == "Reproduciendo":
      reproducir = True
      self.r.reproducir_pausar()
    libros = self.reg.buscar_libros()
    if libros != []:
      nombre_libros = []
      for i in range(len(libros)):
        nombre_libros.append(libros[i][0])
      indice_libro = self.mostrar_combobox(_("Find books"), _("Choose the book which you want to open"), nombre_libros)
      if indice_libro != None:
        l_aux = libro.Libro(libros[indice_libro][1])
        if l_aux.obtener_nombre() == libros[indice_libro][0]:
          self.r.detener()
          self.v.limpiar_modelo()
          self.l = l_aux
          self.v.mostrar_libro(self.l.obtener_indice())
          self.sinc_vista_audio()
        else:
          self.mostrar_mensaje(_("Warning"), _("Specified book doesn't match with the book currently in that path"))
      else:
        self.mostrar_mensaje("Warning", _("You have not selected any book"))
    else:
      self.mostrar_mensaje(_("Warning"), _("There are no saved books"))
    if (self.r.obtener_estado() == "Pausado") and reproducir:
      self.r.reproducir_pausar()



  def cerrar_libro_callback(self, w, data):
    """
    Método para controlar el cierre de un libro
    """
    if self.comprobar_libro():
      self.r.detener()
      self.l = None
      self.v.limpiar_modelo()


  def cerrar_aplicacion(self):
    """
    Método que cierra la aplicación y que guarda la posición de lectura y la configuración del reproductor
    """
    if self.comprobar_libro():
      self.r.detener()
      registro = self.l.obtener_datos_para_marca()
      volumen = self.r.obtener_volumen()
      registro.append(volumen)
      self.reg.escribir_configuracion(registro)


  def mostrar_inf_libro_callback(self, w, data):
    """
    Método para mostrar información general del libro
    """
    reproducir = False
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()
      info = self.l.obtener_inf_libro()
      self.mostrar_mensaje(_("Book information"), info)
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently nno playing book"))


  def mostrar_inf_traduccion_callback(self, w, data):
    """
    Método para mostrar información de la traducción del libro
    """
    reproducir = False
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()
      info = self.l.obtener_inf_traduccion()
      self.mostrar_mensaje(_("Book translation information"), info)
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def mostrar_pos_actual_callback(self, w, data):
    """
    Método para mostrar laposición de lectura actual con el formato "hh:mm:ss"
    """
    reproducir = False
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()
      pos = self.r.obtener_ins_actual()
      pos = pos / 1000000000
      segundos, aux = self.l.obtener_pos_actual_audio()
      t = segundos +(pos - aux)
      hora = self.l.establecer_formato_hora(t)
      self.mostrar_mensaje(_("Elapsed playback time"), hora)
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("Tehre are currently no playing book"))


  def mostrar_tiempo_total_callback(self, w, data):
    """
    Método para mostrar el tiempo total de reproducción del libro
    """
    reproducir = False
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()
      tiempo = self.l.obtener_tiempo_total_audio()
      hora = self.l.establecer_formato_hora(tiempo)
      self.mostrar_mensaje(_("Total book's playback time"), hora)
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("Tehre are currently no playing book"))


  def sinc_vista_audio(self):
    """
    Método para sincronizar la vista del índice del libro con la reproducción del audio cuando el programa automáticamente avanza en la reproducción del libro o cuando el usuario pulsa una opción de navegación del menú
    """
    self.v.actualizar_vista(self.l.obtener_pos_indice())
    fichero, pos_ini, pos_fin = self.l.obtener_pista()
    self.r.reproducir(fichero, pos_ini, pos_fin)


  def sinc_audio_vista(self, indice_pos):
    """
    Método para sincronizar el audio con la vista del índice cuando el usuario pulsa una tecla de desplazamiento o cuando hace click con el ratón
    """
    self.r.detener()
    self.l.actualizar_pos_nodos_libro(indice_pos)
    fichero, pos_ini, pos_fin = self.l.obtener_pista()
    self.r.reproducir(fichero, pos_ini, pos_fin)


  def detener_callback(self, w, data):
    """
    Método para controlar la detención en la reproducción, comprobando si hay algun libro cargado
    """
    if self.comprobar_libro():
      self.r.detener()
      self.l.establecer_pos_lectura(0, 0, 0)
      self.sinc_vista_audio()
      if self.r.obtener_estado() == "Reproduciendo":
        self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("Tehre are currently no playing book"))


  def comprobar_libro(self):
    """
    Método que comprueba si hay algun libro cargado
    """
    if self.l == None:
      return False
    else:
      return True

  def obtener_titulo(self):
    return self.l.obtener_nombre()

  def control_estado_callback(self, w, data):
    """
    Método para controlar el cambio de estado del reproductor
    """
    if self.comprobar_libro():
      self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def listar_capitulos_callback(self, w, data):
    """
    Método para controlar la presentación de capítulos y mostrarlos
    """
    reproducir = False
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()
      capitulos, pos_capitulos = self.l.obtener_capitulos()
      if capitulos != []:
        pos_capitulo = self.mostrar_combobox(_("Goo to chapter"), _("Select which chapter do you want to go"), capitulos)
        if pos_capitulo != None:
          self.r.detener()
          self.l.actualizar_pos_nodos_libro(pos_capitulos[pos_capitulo])
          self.sinc_vista_audio()
        else:
          self.mostrar_mensaje(_("Warning"), _("You have not selected any chapter"))
      else:
        self.mostrar_mensaje(_("Error"), _("Don't exist any chapter in the book"))
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def ir_cap_sig_callback(self, w, data):
    """
    Método para pasar al siguiente capítulo
    """
    if self.comprobar_libro():
      cambio = self.l.obtener_capitulo(1)
      if cambio == 1:
        self.r.detener()
        self.l.obtener_pistas(self.l.obtener_nodo_actual())
        self.sinc_vista_audio()
    else:
      self.m.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def ir_cap_ant_callback(self, w, data):
    """
    Método para ir al capítulo anterior
    """
    if self.comprobar_libro():
      cambio = self.l.obtener_capitulo(-1)
      if cambio == 1:
        self.r.detener()
        self.l.obtener_pistas(self.l.obtener_nodo_actual())
        self.sinc_vista_audio()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def ir_pag_sig_callback(self, w, data):
    """
    Método para controlar el paso a la siguiente página indicado por el usuario
    """
    if self.comprobar_libro():
      cambio = self.l.cambiar_pagina(1)
      if cambio == 1:
        self.r.detener()
        self.l.obtener_pistas(self.l.obtener_nodo_actual())
        self.sinc_vista_audio()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def ir_pag_ant_callback(self, w, data):
    """
    Método para controlar el cambio a la página anterior indicado por el usuario
    """
    if self.comprobar_libro():
      cambio = self.l.cambiar_pagina(-1)
      if cambio == 1:
        self.r.detener()
        self.l.obtener_pistas(self.l.obtener_nodo_actual())
        self.sinc_vista_audio()
    else:
      self.mostrar_mensaje(_("Warning"), _("Tehre are currently no playing book"))


  def ir_texto_ant_callback(self, w, data):
    """
    Método para controlar el cambio al bloque de texto anterior indicado por el usuario
    """
    if self.comprobar_libro():
      cambio = self.l.obtener_texto(-1)
      if cambio == 1:
        self.r.detener()
        self.l.obtener_pistas(self.l.obtener_nodo_actual())
        self.sinc_vista_audio()
    else:
      self.mostrar_mensaje(_("Warning"), _("Tehre are currently no playing book"))


  def ir_texto_sig_callback(self, w, data):
    """
    Método para controlar el paso al siguiente bloque de texto indicado por el usuario
    """
    if self.comprobar_libro():
      cambio = self.l.obtener_texto(1)
      if cambio == 1:
        self.r.detener()
        self.l.obtener_pistas(self.l.obtener_nodo_actual())
        self.sinc_vista_audio()
    else:
      self.mostrar_mensaje(_("Warning"), _("Tehre are currently no playing book"))


  def ir_a_pagina_callback(self, w, data):
    """
    Método para controlar la búsqueda de una página indicada por el usuario
    """
    reproducir = False
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()
      pagina = self.mostrar_entrada_texto(_("Go to page"), _("Enter the page which you want to go"), 10)
      if pagina.isdigit():
        cambio, pos = self.l.buscar_pagina(pagina)
        if cambio == 1:
          self.r.detener()
          self.l.obtener_pistas(self.l.nodos_libro[pos])
          self.sinc_vista_audio()
        else:
          self.mostrar_mensaje(_("Warning"), _("Page out of range"))
      else:
        self.mostrar_mensaje(_("Error"), _("You have not entered a number"))
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("Tehre are currently no playing book"))


  def control_aumento_volumen_callback(self, w, data):
    """
    Método para controlar el aumento del volumen indicado por el usuario
    """
    if self.comprobar_libro():
      self.r.cambiar_volumen(1)
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def control_disminucion_volumen_callback(self, w, data):
    """
    Método para controlar la disminución  del volumen
    """
    if self.comprobar_libro():
      self.r.cambiar_volumen(-1)
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def activar_desactivar_sonido_callback(self, w, data):
    """
    Método para controlar la activación o desactivación del sonido
    """
    if self.comprobar_libro():
      self.r.silenciar()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def establecer_marca_callback(self, w, data):
    """
    Método para controlar la creación de una marca en el libro en reproducción
    """
    reproducir = False
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()
      nombre_marca = self.mostrar_entrada_texto(_("Set bookmark"), _("Enter the bookmark name"), 50)
      if nombre_marca != '':
        marca = self.l.obtener_datos_para_marca()
        marca.append(nombre_marca)
        self.reg.crear_marca(marca)
      else:
        self.mostrar_mensaje(_("Error"), _("You have not entered a bookmark name"))
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def listar_marcas_callback(self, w, data):
    """
    Método para listar las marcas de un libro
    """
    reproducir = False
    if self.comprobar_libro():
      nombre_libro = self.l.obtener_nombre()
      marcas = self.reg.obtener_marcas_libro_actual(nombre_libro)
      if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()
      if marcas != []:
        nombre_marcas = []
        for i in range(len(marcas)):
          nombre_marcas.append(marcas[i][0])
        indice_marca = self.mostrar_combobox(_("Bookmark list"), _("Choose the bookmark which you want to go"), nombre_marcas)
        if indice_marca != None:
          self.r.detener()
          self.l.establecer_pos_lectura(marcas[indice_marca][1], marcas[indice_marca][2], marcas[indice_marca][3])
          self.sinc_vista_audio()
        else:
          self.mostrar_mensaje(_("Warning"), _("You have not selected any bookmark"))
      else:
        self.mostrar_mensaje(_("Warning"), _("There are not bookmarks for this book"))
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("Tehre are currently no playing book"))


  def borrado_de_marcas_callback(self, w, data):
    """
    Método para controlar el borrado de una marca del libro en reproducción indicada por el usuario
    """
    reproducir = False
    if self.comprobar_libro():
      nombre_libro = self.l.obtener_nombre()
      marcas = self.reg.obtener_marcas_libro_actual(nombre_libro)
      if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()
      if marcas != []:
        nombre_marcas = []
        for i in range(len(marcas)):
          nombre_marcas.append(marcas[i][0])
        indice_marca = self.mostrar_combobox(_("Bookmarks deletion"), _("Choose the bookmark which you want to delete"), nombre_marcas)
        if indice_marca != None:
          self.reg.borrar_marca(nombre_libro, indice_marca)
        else:
          self.mostrar_mensaje(_("Warning"), _("You have not selected any bookmark"))
      else:
        self.mostrar_mensaje(_("Warning"), _("Don't exist bookmarks for this book"))
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("Tehre are currently no playing book"))


  def mostrar_mensaje(self, titulo, mensaje):
    """
    Método para mostrar un mensaje
    titulo: titulo del mensaje
    mensaje: mensaje que se desea mostrar
    """
    # Creacion de una ventana de dialogo
    ventana_mensaje = gtk.Dialog(titulo, None, 0, (gtk.STOCK_OK, gtk.RESPONSE_OK))

    # creacion de una etiqueta con el mensaje de error
    ventana_mensaje.etiqueta = gtk.Label(mensaje)
    ventana_mensaje.vbox.pack_start(ventana_mensaje.etiqueta, True, True, 0)
    ventana_mensaje.etiqueta.show()
    response = ventana_mensaje.run()
    ventana_mensaje.destroy()


  def mostrar_entrada_texto(self, titulo, texto_etiqueta, longitud):
    """
    Método para mostrar una entrada de texto y obtener el texto introducido por el usuario
  titulo: titulo de la ventana de diálogo
    texto_etiqueta: texto de la etiqueta
    longitud: tamaño máximo de la entrada de texto
    """
    dialogo = gtk.Dialog(titulo, None, 0, (gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    etiqueta = gtk.Label(texto_etiqueta)
    etiqueta.show()
    dialogo.vbox.pack_start(etiqueta)
    entrada = gtk.Entry()
    entrada.set_max_length(longitud)
    entrada.select_region(0, len(entrada.get_text()))
    entrada.show()
    dialogo.vbox.pack_start(entrada, False)
    response = dialogo.run()
    if response == gtk.RESPONSE_OK:
      texto = entrada.get_text()
    else:
      texto = ''
    dialogo.destroy()
    return texto


  def mostrar_combobox(self, titulo, texto_etiqueta, lista):
    """
    Método para mostrar un combobox por pantalla y obtener la opción elegida
    """
    dialogo = gtk.Dialog(titulo, None, 0, (gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    etiqueta = gtk.Label(texto_etiqueta)
    etiqueta.show()
    dialogo.vbox.pack_start(etiqueta)
    combobox = gtk.combo_box_new_text()
    for x in lista:
      combobox.append_text(x)
    combobox.set_active(0)
    combobox.show()
    dialogo.vbox.pack_start(combobox, False)
    response = dialogo.run()
    if response == gtk.RESPONSE_OK:
      elemento_activo = combobox.get_active()
    else:
      elemento_activo = None
    dialogo.destroy()
    return elemento_activo


  def mostrar_ayuda_callback(self, w, data):
    """
    Método para mostrar el fichero de ayuda del DBR
    """
    reproducir = False
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()
    if os.path.exists("docs/ayuda.html"):
      os.system("firefox docs/ayuda.html")
    else:
      self.mostrar_mensaje(_("Warning!"), _("The help file can not be found"))
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()


  def close_about_dialog_callback(self, w, data):

    if self.comprobar_libro():
      if self.r.obtener_estado() == "Pausado":
        self.r.reproducir_pausar()

    if data==gtk.RESPONSE_CANCEL:
      w.destroy()

  def display_about_dialog_callback(self, w, data):
    """
    This method is used for displaying "About DBR" notice
    """
    reproducir = False
    program_name="DBR"
    authors=['Rafael Cantos Villanueva', \
            'Francisco Javier Dorado Martínez']
    translations=_("This program has been translated by:\n\nJuan C. Buño\n")
    license=_("This program is under GNU/General Public License version 3. See accompanying COPYING file for more details.") 
    version="0.1.2"
    copyright="Copyright 2008 RafaelCantos Villanueva"
    website="http://dbr.sourceforge.net"

    ADlg=gtk.AboutDialog()

    if self.comprobar_libro():
      if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()


    ADlg.set_program_name(program_name)
    ADlg.set_version(version)
    ADlg.set_copyright(copyright)
    ADlg.set_authors(authors)
    ADlg.set_translator_credits(translations)
    ADlg.set_license(license)
    ADlg.set_website(website)

    ADlg.connect("response", self.close_about_dialog_callback)
    ADlg.show()

  def mostrar_licencia_callback(self, w, data):
    """
    Método para mostrar la licencia de uso del DBR
    """
    reproducir = False
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()
    if os.path.exists("docs/licencia.html"):
      os.system("firefox docs/licencia.html")
    else:
      self.mostrar_mensaje(_("Warning!"), _("The help file can not be found"))
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()
