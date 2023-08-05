#!/usr/bin/env python3

# -*- coding: utf-8 -*-

import codecs
import datetime
import json
import os
import tkinter as tk

from Juwel import Date_formatter
from Juwel import Prolongation_finder
from Juwel import Text_parser
#import Date_formatter
#import Prolongation_finder
#import Text_parser

from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from pathlib import Path
from tkcalendar import *
from tkinter import *
from tkinter import filedialog
from tkinter import ttk

###################################################################
# Heutiges Datum beziehen und aufdröseln ~~~~~~~~~~~~~~~~~~~~~~~~~~
###################################################################

global today
today = datetime.date.today()

global y
y = today.year

global m
m = today.month

global d
d = today.day





##########################################################################################
# root vorab globalisieren, damit es in Save and exit destroyed werden kann ~~~~~~~~~~~~~~
##########################################################################################


global root
root = Tk()

# root ist in diesem Fall das "Grundfenster", auf dem alles aufbaut




###################################################################
# Neueste Datei eines Verzeichnisses bekommen ~~~~~~~~~~~~~~~~~~~~~
###################################################################

def get_newest_file():
    
    home = str(Path.home())    
    DIR_PATH = f'{home}/.juwel/'

    most_recent_file = None
    most_recent_timestamp = 0

    for element in os.listdir(DIR_PATH):
        mtime = os.stat(os.path.join(DIR_PATH, element)).st_mtime
        if mtime > most_recent_timestamp:
            most_recent_timestamp = mtime
            most_recent_file = element
    return most_recent_file

# Vorgabe war hier, dass Juwel im lokalen Ordner die neueste Datei findet
# und zur Metadaten-Erstellung auswählt, sofern nichts anderes gewählt wurde
    

###################################################################
# Browsefunktion per Klick ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
###################################################################

def browse_file():
    filepath.set(filedialog.askopenfilename())
    show_path_label.config(text="You are currently creating a sidecar file for: \n" + filepath.get())
    
# Juwel soll per Browse-Fenster eine Datei auswählen können, zu der es
# eine Metadaten-File anlegen soll


def browse_folder():
    filepath.set(filedialog.askdirectory())
    show_path_label.config(text="You are currently creating a sidecar file for: \n" + filepath.get())

# Juwel soll per Browse-Fenster einen Ordner auswählen können, zu der es
# eine Metadaten-File anlegen soll



###################################################################
# Namen der Sidecarfile bekommen ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
###################################################################

def get_sidecar_filename():
    if filepath.get() != "empty":
        pathname = filepath.get()        
        pathname = pathname.split("/")[-1]
        if "." in pathname:
            pathname = pathname.split(".")[0]
        filename = pathname + ".meta"
        print(filename)        
    elif filepath.get() == "empty":
        filename = get_newest_file()
        filename = filename.split(".")[0] + ".meta"        

    return filename   
    

# Zu der im Schritt "Browsefunktion per Klick" ausgwählte Datei oder Ordner
# soll eine Metadaten-File angelegt werden. Die darf natürlich als Namen
# nicht eine super lange Pfadangabe haben, sondern nur den Namen der Originaldatei
# und als Endung ".meta"
# In dieser Funktion wird die Pfadangabe in den eigentlichen Dateinamen aufgesplittet



###################################################################
# Eventhandlig für freie Textfelder ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
###################################################################


def mouse_on_entry(event):
    for item in config:
        j = config.index(item)
        if config[j]['GUI_type'] == "textfield":
            if var_dict[j].get() == config[j]['default']:
                entry_dict[j].delete(0, "end") # delete all the text in the entry
                entry_dict[j].insert(0, '') #Insert blank for user input
                entry_dict[j].config(fg = 'black')

def mouse_off_entry(event):
    for item in config:
        j = config.index(item)
        if config[j]['GUI_type'] == "textfield":
            if entry_clicked_dict[j].get() == 0:
                entry_dict[j].insert(0, config[j]['default'])
                entry_dict[j].config(fg = 'grey')

def entry_onclick(event):
    for item in config:
        j = config.index(item)
        if config[j]['GUI_type'] == "textfield":
            entry_clicked_dict[j].set(1)

def entry_unclicked(event):
    for item in config:
        j = config.index(item)
        if config[j]['GUI_type'] == "textfield":
            entry_clicked_dict[j].set(0)

# In freien Textfeldern soll immer in grau der jeweilige Defaultwert stehen
# klickt der Cursor ins Textfeld hinein, soll der graue Defaultwert verschwinden
# und die manuellen Eingaben sind in schwarzen Buchstaben


###################################################################
# Eventhandlig für Expiration Date ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
###################################################################

def changeText(self):
    for item in config:        
        if item["GUI_type"] == "expiration":
            j = config.index(item)
            d_format = config[j]["format"]

            exp_string = exp_var_dict[j].get()
            int_or_str = Prolongation_finder.get_prolongation(exp_string)

            if isinstance(int_or_str, int):
                exp_date = today + relativedelta(years=int_or_str)
            elif isinstance(int_or_str, str):
                exp_date = "01/01/3000"             
                
            exp_date_formatted = Date_formatter.format_date(exp_date, d_format)
            new_text = "   Expired in: " + str(exp_date_formatted)
            variable_input = exp_date_formatted
            
            exp_label_dict[j].config(text=new_text)
            var_dict[j].set(variable_input)

# Je nach ausgewählter Frist in einer Selectbox, soll rechts daneben in einem Label
# instantly angezeigt werden, was das ausgewählte Datum dazu ist

            
###################################################################
# Funktion zum Metadaten speichern ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
###################################################################

def save():

    for item in config:
        j = config.index(item)
        inter_list1 = []
        if config[j]["GUI_type"] == "calendar":
            date_cal = cal_dict[j].get_date()
            d_format = config[j]['format']
            date_obj = Date_formatter.format_date(date_cal, d_format)
            metadata_dict[config[j]["key"]] = date_obj
        elif j in var_dict:
            if not(isinstance(var_dict[j], dict)):
                metadata_dict[config[j]["key"]] = var_dict[j].get()
            elif isinstance(var_dict[j], dict):
                metadata_dict[config[j]["key"]] = {}
                for k in var_dict[j]:
                    if (var_dict[j][k].get() != "none"):
                        inter_list1.append(var_dict[j][k].get())
                        metadata_dict[config[j]["key"]] = inter_list1

                    
                   
    metadata_json = json.dumps(metadata_dict, indent = 4)

    


    print(metadata_json)


    
    sidecar_filename = get_sidecar_filename()
   
    
    with open(sidecar_filename, "w") as outfile:
            json.dump(metadata_dict, outfile, indent = 4)
    
    return 0

# Nachdem man alle Auswahlmöglichkeiten zu seinen Wünschen in der GUI getätigt hat
# kann man die ausgewählten Inputs in der Metadaten-File speichern
# Diese wird in Json-Format gespeichert
# In einem nächsten (noch nicht implementierten Schritt) soll das Json-Format
# in ein Format ohne Sonderzeichen überführt werden


###################################################################
# Save and exit function ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
###################################################################

def save_and_exit():

    save()

    root.destroy()



###################################################################
# JSON-config-File öffnen und in einer Dictionary speichern ~~~~~~~
###################################################################

def json_transformer():
 
    global config
    config = Text_parser.read_template()




    
###########################################################################
# Erstellen verschachtelter Frames, um die beiden Scrollbars zu ermöglichen
###########################################################################


    # Erstellen des Hauptfensters
                
    root.title('Juwel - Metadaten-Tool')
    root.geometry("500x1000")

    main_frame = Frame(root)
    main_frame.pack(fill=BOTH, expand=1)

    my_canvas = Canvas(main_frame, bd=0, highlightthickness=0)
    my_canvas.pack(side=LEFT, fill=BOTH, expand=1)

    inner_canvas = Canvas(my_canvas, bd=0, highlightthickness=0)
    inner_canvas.pack(side=TOP, fill=BOTH, expand=1)

    my_scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=inner_canvas.yview)
    my_scrollbar.pack(side=RIGHT, fill=Y)
 

    mx_scrollbar = ttk.Scrollbar(my_canvas, orient=HORIZONTAL, command=inner_canvas.xview)
    mx_scrollbar.pack(side=BOTTOM, fill=X, expand=0)

    inner_canvas.configure(yscrollcommand=my_scrollbar.set)
    my_canvas.bind('<Configure>', lambda e: inner_canvas.configure(scrollregion = inner_canvas.bbox("all")))


    inner_canvas.configure(xscrollcommand=mx_scrollbar.set)
    inner_canvas.bind('<Configure>', lambda e: inner_canvas.configure(scrollregion = inner_canvas.bbox("all")))

    second_frame = Frame(inner_canvas, bd=0, highlightthickness=0)
    inner_canvas.create_window((0,0), window=second_frame, anchor="n")

    

########################################################################################################
# Für die Speicherung von den GUI-Variablen werden Dictionarys erstellt ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
########################################################################################################

    # var_dict = Dictionary für alle Input-Variablen
    global var_dict
    var_dict = {}

    # canvas_dict = Dictionary für alle Canvases
    global canvas_dict
    canvas_dict = {}

    # abstand_dict = Dictionary für alle Abstand-Labels
    global abstand_dict
    abstand_dict = {}

    # label_dict = Dictionary für alle Labels
    global label_dict
    label_dict = {}    

    # select_dict = Dictionary für alle Selectboxes
    global select_dict
    select_dict = {}

    # check_dict = Dictionary für alle Checkboxes
    global check_dict
    check_dict = {}

    # entry_dict = Dicitionary für alle freien Textfelder
    global entry_dict
    entry_dict = {}

    # entry_clicked_dict = Dictionary für alle Variablen, ob in das Textfeld geklickt wurde
    global entry_clicked_dict
    entry_clicked_dict = {}

    # cal_dict = Dictionary für alle Kalender
    global cal_dict
    cal_dict = {}

    # exp_var_dict = Dicitionary für ausgewählten Options-String in der Expiration Selectbox
    global exp_var_dict
    exp_var_dict = {}


    # exp_label_dict = Dicitonary für Output-Labels für Expiration Date
    global exp_label_dict
    exp_label_dict = {}

    # outer_canvas_list = Array für äußere Canvases, wenn eine neue Zeile entstehen soll
    global outer_canvas_list
    outer_canvas_list = []

    # outer_canvas_dict = Dictionary für äußere Canvases, wenn eine neue Zeile entstehen soll
    global outer_canvas_dict
    outer_canvas_dict = {}
    
    
###################################################################
# ein Zähler für die äußeren Canvases ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
###################################################################


    global canvas_number
    canvas_number = 0

# Dies dient dazu, dass das Programm nachher bei den einzelnen GUI-Elementen, wenn die Eigenschaft "newline"
# gewählt ist, dass das GUI-Element in einem neuen Canvas reingepackt wird, damit es in einer neuen Zeile
# angeordnet ist


##########################################################################################
# eine Stringvariable für den in der Browse-Funktion selektierten Dateinamen ~~~~~~~~~~~~~
##########################################################################################

    global filepath
    filepath = StringVar()
    filepath.set("empty")


########################################################################################################
# Für jedes Element in der Dictionary namens config wird der Objekttyp geprüft und im Fenster realisiert
########################################################################################################
   
############################## Selectbox ##################################        

    for item in config:
        j = config.index(item)
        element = config[j]
        if element["GUI_type"] == "selectbox":
            if element["newline"] == "yes" or (canvas_number == 0):
                outer_canvas_dict[canvas_number] = Canvas(second_frame, bd=0, highlightthickness=0)
                outer_canvas_dict[canvas_number].pack(side=TOP)
                
                canvas_dict[j] = Canvas(outer_canvas_dict[canvas_number], bd=0, highlightthickness=0)
                canvas_dict[j].pack(side="left")
                canvas_number += 1 
            elif element["newline"] == "no":
                canvas_dict[j] = Canvas(outer_canvas_dict[canvas_number-1], bd=0, highlightthickness=0)
                canvas_dict[j].pack(side="left")            
            
            label_dict[j] = Label(canvas_dict[j], text=element['key'])
            label_dict[j].config(font=("Arial", 10))
            label_dict[j].grid(row=0, column=0, sticky=W, pady=2)
            
            var_dict[j] = StringVar()
            var_dict[j].set(element['default'])
            
            options = element['values']
            
            select_dict[j] = OptionMenu(canvas_dict[j], var_dict[j], *options)
            select_dict[j].grid(row=0, column=1, sticky=W, pady=2)

            abstand_dict[j] = Label(outer_canvas_dict[canvas_number-1])
            abstand_dict[j].config(width=10, height=5)
            if j+1 < len(config):
                if config[j+1]["newline"] == "yes":                
                    abstand_dict[j].pack()
                elif config[j+1]["newline"] == "no":
                    abstand_dict[j].pack(side=LEFT)
            else:
                abstand_dict[j].pack()
###################################################### Checkbox ########################################            
        elif element["GUI_type"] == "checkbox":
            if element["newline"] == "yes" or (canvas_number == 0):
                outer_canvas_dict[canvas_number] = Canvas(second_frame, bd=0, highlightthickness=0)
                outer_canvas_dict[canvas_number].pack(side=TOP)
                
                canvas_dict[j] = Canvas(outer_canvas_dict[canvas_number], bd=0, highlightthickness=0)
                canvas_dict[j].pack(side="left")
                canvas_number += 1 
            elif element["newline"] == "no":
                canvas_dict[j] = Canvas(outer_canvas_dict[canvas_number-1], bd=0, highlightthickness=0)
                canvas_dict[j].pack(side="left")
            # Zunächst (bei jedem der folgenden GUI-Element-Arten) wird immer geschaut, ob die "newline"-Option
            # gewählt ist. Falls ja, dann wird das Element in ein neues Canvas gepackt, was automatisch zum Zeilenumbruch führt
            # Falls nein, wird das aktuelle GUI-Element zum zuletzt erstellten Canvas mit hineingefügt, was automatisch dazu führt,
            # dass es mit dem letzten GUI-Element in einer horizontalen Zeile steht
            # Dafür müssen die Anzahl der erstellten Canvases mitgezählt werden, deshalb wurde weiter oben eine Variable namens
            # canvas_number erstellt
            
            label_dict[j] = Label(canvas_dict[j], text=element['key'])
            label_dict[j].config(font=("Arial", 10))
            label_dict[j].grid(row = 0, column = 0, sticky = W, pady = 2)
            
            check_dict[j] = {}
            var_dict[j] = {}
            
            for item in element['values']:
                k = str(element['values'].index(item))
                var_dict[j][k] = StringVar()
                check_dict[j][k] = Checkbutton(canvas_dict[j], text=item, variable=var_dict[j][k], onvalue=item, offvalue="none")
                check_dict[j][k].deselect()
                check_dict[j][k].grid(row = k, column = 1, sticky = W, pady = 2)
            # Jede Checkbox-Struktur hat mehrere auswählbare Checkbox-Optionen, diese werden in einer inneren Schleife "instanziiert"
            #
            abstand_dict[j] = Label(outer_canvas_dict[canvas_number-1])
            abstand_dict[j].config(width=10, height=7)
            if j+1 < len(config):
                if config[j+1]["newline"] == "yes":                
                    abstand_dict[j].pack()
                elif config[j+1]["newline"] == "no":
                    abstand_dict[j].pack(side=LEFT)
            else:
                abstand_dict[j].pack()
############################################################### Freies Textfeld ##############################
        elif element["GUI_type"] == "textfield":
            if element["newline"] == "yes" or (canvas_number == 0):
                outer_canvas_dict[canvas_number] = Canvas(second_frame, bd=0, highlightthickness=0)
                outer_canvas_dict[canvas_number].pack(side=TOP)
                
                canvas_dict[j] = Canvas(outer_canvas_dict[canvas_number], bd=0, highlightthickness=0)
                canvas_dict[j].pack(side="left")
                canvas_number += 1 
            elif element["newline"] == "no":
                canvas_dict[j] = Canvas(outer_canvas_dict[canvas_number-1], bd=0, highlightthickness=0)
                canvas_dict[j].pack(side="left")
            
            label_dict[j] = Label(canvas_dict[j], text=element['key'])
            label_dict[j].config(font=("Arial", 10))
            label_dict[j].grid(row = 0, column = 0, sticky = W, pady = 2)
            
            var_dict[j] = StringVar()
            
            entry_clicked_dict[j] = IntVar()
            entry_clicked_dict[j].set(0)
            
            entry_dict[j] = Entry(canvas_dict[j], width=40, bd=1, textvariable= var_dict[j])
            entry_dict[j].insert(0, element['default'])
            
            entry_dict[j].bind("<Enter>", mouse_on_entry)
            entry_dict[j].bind("<Leave>", mouse_off_entry)
            entry_dict[j].bind("<FocusIn>", entry_onclick)
            entry_dict[j].bind("<FocusOut>", entry_unclicked)
            entry_dict[j].config(fg = 'grey')            
            entry_dict[j].grid(row = 0, column = 1, sticky = W, pady = 2)

            abstand_dict[j] = Label(outer_canvas_dict[canvas_number-1])
            abstand_dict[j].config(width=10, height=4)
            if j+1 < len(config):
                if config[j+1]["newline"] == "yes":                
                    abstand_dict[j].pack()
                elif config[j+1]["newline"] == "no":
                    abstand_dict[j].pack(side=LEFT)
            else:
                abstand_dict[j].pack()
########################################################### Kalender ########################################        
        elif element["GUI_type"] == "calendar":
            if element["newline"] == "yes" or (canvas_number == 0):
                outer_canvas_dict[canvas_number] = Canvas(second_frame, bd=0, highlightthickness=0)
                outer_canvas_dict[canvas_number].pack(side=TOP)
                
                canvas_dict[j] = Canvas(outer_canvas_dict[canvas_number], bd=0, highlightthickness=0)
                canvas_dict[j].pack(side="left")
                canvas_number += 1 
            elif element["newline"] == "no":
                canvas_dict[j] = Canvas(outer_canvas_dict[canvas_number-1], bd=0, highlightthickness=0)
                canvas_dict[j].pack(side="left")
            
            label_dict[j] = Label(canvas_dict[j], text=element['key'])
            label_dict[j].config(font=("Arial", 10))
            label_dict[j].pack(side = "top")           
            
            cal_dict[j] = Calendar(canvas_dict[j], cursor="hand1", selectmode="day", year=y, month=m, day=d)
            cal_dict[j].pack()

            abstand_dict[j] = Label(outer_canvas_dict[canvas_number-1])
            abstand_dict[j].config(width=10, height=20)
            if j+1 < len(config):
                if config[j+1]["newline"] == "yes":                
                    abstand_dict[j].pack()
                elif config[j+1]["newline"] == "no":
                    abstand_dict[j].pack(side=LEFT)
            else:
                abstand_dict[j].pack()
######################################################### Spezielle Selectbox für Auslaufdatum ####################
        elif element["GUI_type"] == "expiration":
            if element["newline"] == "yes" or (canvas_number == 0):
                outer_canvas_dict[canvas_number] = Canvas(second_frame, bd=0, highlightthickness=0)
                outer_canvas_dict[canvas_number].pack(side=TOP)
                
                canvas_dict[j] = Canvas(outer_canvas_dict[canvas_number], bd=0, highlightthickness=0)
                canvas_dict[j].pack(side="left")
                canvas_number += 1 
            elif element["newline"] == "no":
                canvas_dict[j] = Canvas(outer_canvas_dict[canvas_number-1], bd=0, highlightthickness=0)
                canvas_dict[j].pack(side="left")          

            label_dict[j] = Label(canvas_dict[j], text=element['key'])
            label_dict[j].config(font=("Arial", 10))
            label_dict[j].grid(row=0, column=0, sticky=W, pady=2)          

            exp_var_dict[j] = StringVar()
            exp_var_dict[j].set(element['default'])

            exp_string = exp_var_dict[j].get()
            int_or_str = Prolongation_finder.get_prolongation(exp_string)

            if isinstance(int_or_str, int):
                default_date = today + relativedelta(years=int_or_str)
            elif isinstance(int_or_str, str):
                default_date = "01/01/3000"
            # Es wird praktisch immer angestrebt, als Defaultwert die erste Option der Selectbox (eine Jahreszahl)
            # zum heutigen Datum dazu zu addieren
            
            d_format = element["format"]

            formatted_default_date = Date_formatter.format_date(default_date, d_format)
            
            var_dict[j] = StringVar()
            var_dict[j].set(formatted_default_date)
          
            
            options = element['values']
            select_dict[j] = OptionMenu(canvas_dict[j], exp_var_dict[j], *options, command=changeText)
            select_dict[j].grid(row=0, column=1, sticky=W, pady=2)          

            exp_label_dict[j] = Label(canvas_dict[j], text="   Expired in: " + str(formatted_default_date))
            exp_label_dict[j].config(font=("Arial", 10))
            exp_label_dict[j].grid(row=0, column=2, sticky=W, pady=2) 

            abstand_dict[j] = Label(outer_canvas_dict[canvas_number-1])
            abstand_dict[j].config(width=10, height=5)
            if j+1 < len(config):
                if config[j+1]["newline"] == "yes":                
                    abstand_dict[j].pack()
                elif config[j+1]["newline"] == "no":
                    abstand_dict[j].pack(side=LEFT)
            else:
                abstand_dict[j].pack()
   
    
    
########################################################################################################
# Metadaten speichern ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
########################################################################################################
    

    #print(var_dict)

    global metadata_dict
    metadata_dict = {}


    show_path_abstand = Label(second_frame)
    show_path_abstand.config(width=6, height=2)
    show_path_abstand.pack()

    global show_path_label
    show_path_label = Label(second_frame, text="You are currently creating a sidecar file for: \n" + get_newest_file())
    show_path_label.config(font=("Arial", 12))
    show_path_label.pack()


    browse_abstand = Label(second_frame)
    browse_abstand.config(width=6, height=1)
    browse_abstand.pack()


    browse_canvas = Canvas(second_frame)
    browse_canvas.pack()
       
    browse_file_button = Button(browse_canvas, text="Select file", command=browse_file)
    browse_file_button.config(font=("Arial", 10))
    browse_file_button.pack(side='left')

    browse_folder_button = Button(browse_canvas, text="Select folder", command=browse_folder)
    browse_folder_button.config(font=("Arial", 10))
    browse_folder_button.pack(side='left')


    save_abstand = Label(second_frame)
    save_abstand.config(width=6, height=1)
    save_abstand.pack()

    save_canvas = Canvas(second_frame)
    save_canvas.pack()

    save_Button = Button(save_canvas, text="Save", command=save)
    save_Button.config(font=("Arial", 14))
    save_Button.pack(side='left')

    save_and_exit_Button = Button(save_canvas, text="Save and exit", command=save_and_exit)
    save_and_exit_Button.config(font=("Arial", 14))
    save_and_exit_Button.pack(side='left')

# Hier passieren nicht die eigentlichen Funktionen der Speicherung von Metadaten, sondern hier werden nur
# die GUI-Elemente dafür platziert und angeordnet

    
    root.mainloop()
