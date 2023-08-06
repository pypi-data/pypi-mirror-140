#!/usr/bin/env python3

# -*- coding: utf-8 -*-

import codecs
import datetime
import json
import os
import tkinter as tk

from Juwel_2 import Formatted_expiration_finder
from Juwel_2 import text_parser
from Juwel_2 import Widget_index_finder

from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from pathlib import Path
from tkcalendar import *
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import asksaveasfile
from tkinter import ttk



class Juwel:

    def __init__(self, config_list):           
        self.version = "Version 2.1.16"
        self.last_change = "Date of last change: " + "25.02.2022"

        self.root = Tk()
        
        self.config = config_list
      
        self.root.title('Juwel - Metadaten-Tool')

##############################################################
# ~~~~~~~~~~~~~~ Menubar erstellen ~~~~~~~~~~~~~~~~~~~~~~~~~~~
##############################################################

        self.home = str(Path.home())        
        self.initial_path = f'{self.home}/.juwel/'
        self.config_filepath = StringVar()
        self.filepath = StringVar()
        self.cancel = False

        self.menubar = Menu(self.root)
        self.root.config(menu=self.menubar)

        self.menu_0 = Menu(self.menubar, tearoff = "off")
        self.menubar.add_cascade(menu=self.menu_0, label='Menu \u22EE')
        self.menu_0.add_command(label="Load configuration", command=self.load_config)

        self.submenu_select = Menu(self.menu_0, tearoff=0)
        self.menu_0.add_cascade(label="Select", menu=self.submenu_select)
        self.submenu_select.add_command(label="Select file to attach metadata", command=self.browse_file)
        self.submenu_select.add_command(label="Select directory to attach metadata", command=self.browse_folder)

        self.submenu_save = Menu(self.menu_0, tearoff=0)
        self.menu_0.add_cascade(label="Save", menu=self.submenu_save)       
        self.submenu_save.add_command(label="Save metadata", command=self.save)
        self.submenu_save.add_command(label="Save metadata and exit", command=self.save_and_exit)
        
        self.menu_0.add_command(label="Exit", command=self.exit)
   
        

        self.currently_creating_text = "    Currently creating a sidecarfile for: "
        self.menu_1 = Menu(self.menubar, tearoff = "off")
        self.menubar.add_cascade(menu=self.menu_1, label=self.currently_creating_text, font=("Arial", 8))
        self.menu_1.add_command(label="Change file", command=self.browse_file)
        self.menu_1.add_command(label="Change directory", command=self.browse_folder)

        self.menu_2 = Menu(self.menubar, tearoff = "off")
        self.menubar.add_cascade(menu=self.menu_2, label="\u22EE  Save  \u22EE ", font=("Arial", 8))
        self.menu_2.add_command(label="Save metadata", command=self.save)
        self.menu_2.add_command(label="Save metadata and exit", command=self.save_and_exit)

        self.menu_3 = Menu(self.menubar, tearoff = "off")
        self.menubar.add_cascade(menu=self.menu_3, label="Help  \u22EE ", font=("Arial", 8))
        self.menu_3.add_command(label="Show version info", command=self.show_version)        


# ~~~~~~~~~~~ Ende (Menubar erstellen) Ende ~~~~~~~~~~~~~~~~~~~~
################################################################        

        self.mainframe = ttk.Frame(self.root)
        self.mainframe.grid()

        self.row_number = 0
        self.column_number = 0
        
        self.today = datetime.date.today()
        self.y = self.today.year
        self.m = self.today.month
        self.d = self.today.day  

        self.subframe = {}        
        self.label = {}
        self.abstand = {}
        self.variable = {}
        self.selectbox = {}
        self.checkbox = {}
        self.checkbox_frame = {}
        self.entry = {}
        self.entry_clicked = {}
        self.entry_mouse_entered = {}
        self.last_entered_widget = None
        self.last_clicked_widget = None
        self.text_has_input = {}
        self.calendar = {}
        self.expiration_variable = {}
        self.expiration_label = {}


        self.extension_suggestion = ""
        self.filename_suggestion = ""
        self.metadata = {}

        for element in self.config:
            j = self.config.index(element)   
            self.set_row_and_column(j, element)
            self.subframe[j] = ttk.Frame(self.mainframe)
            self.subframe[j].grid(row=self.row_number, column=self.column_number, pady=(0, 35))
            if element["GUI_type"] == "selectbox":           
                self.make_selectbox(j, element)                
            elif element["GUI_type"] == "checkbox":          
                self.make_checkbox(j, element)
            elif element["GUI_type"] == "textfield":
                self.make_textfield(j, element)
            elif element["GUI_type"] == "calendar":
                self.make_calendar(j, element)
            elif element["GUI_type"] == "expiration":
                self.make_expiration(j, element)

        self.root.mainloop()


###############################################################################
# ~~~~~~~~~~~~~~~~~ Geometrie strukturieren ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
###############################################################################
                
    def set_row_and_column(self, item_number, element):
        if item_number == 0:
            self.row_number = 0
            self.column_number = 0
        elif item_number != 0:
            if element["newline"] == "yes":
                self.row_number += 1
                self.column_number = 0
            elif element["newline"] == "no":
                self.column_number += 1


###############################################################################
# ~~~~~~~~~~~~~~~~~~~ Zusatzevents (Kettenevents) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
###############################################################################

    def erase_defaultText(self, j):
        self.entry[j].delete(0, "end")
        self.entry[j].insert(0, '')
        self.entry[j].config(fg = 'black')

    def set_defaultText(self, j):
        self.entry[j].config(fg = 'grey')
        self.entry[j].insert(0, self.config[j]['default'])


    def get_sidecar_filename(self, *args):
        if len(self.filepath.get()) != 0:
            pathname = self.filepath.get()        
            pathname = pathname.split("/")[-1]
            if "." in pathname:
                pathname = pathname.split(".")[0]
            self.filename_suggestion = pathname
        elif len(self.filepath.get()) == 0:
            self.filename_suggestion = "Please first choose a file/directory for sidecarfile attachment"

    def get_sidecar_extension(self, *args):
        self.extension_suggestion = ".meta"



###############################################################################
# ~~~~~~~~~~~~~~~~~~~~ Eventhandling ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
###############################################################################


################ Eventhandling der Selectboxen ######################################

    def remove_focus(self, *args):
        self.root.focus()




################ Eventhandling der Entry-Textfelder #################################

    def mouse_on_entry(self, *args):
        x, y = self.root.winfo_pointerxy()
        self.last_entered_widget = self.root.winfo_containing(x,y)
        j = Widget_index_finder.find_index(self.last_entered_widget)        
        if self.entry_clicked[j] != True:   # Warum muss man bei self.entry_clicked[j] nicht checken, ob der Key j existiert 
            if j not in self.text_has_input:            # aber bei self.text_has_input[j] schon checken, ob der Key j existiert?
                self.erase_defaultText(j)
            elif j in self.text_has_input:
                if self.text_has_input[j] == False:
                    self.erase_defaultText(j)
        """
        if self.entry_clicked[j] != True and self.text_has_input[j] != True:
            self.erase_defaultText(j)
        """
                    

    def mouse_off_entry(self, *args):
        x, y = self.root.winfo_pointerxy()
        j = Widget_index_finder.find_index(self.last_entered_widget)
        if self.last_entered_widget != self.root.winfo_containing(x,y):            
            if self.entry_clicked[j] != True:
                if j not in self.text_has_input:
                    self.set_defaultText(j)
                elif j in self.text_has_input:
                    if self.text_has_input[j] == False:
                        self.set_defaultText(j)
            """
            if self.entry_clicked[j] != True and self.text_has_input[j] != True:
                self.set_defaultText(j)
            """
                

    def click_on_entry(self, event):
        self.last_clicked_widget = self.root.focus_get()
        j = Widget_index_finder.find_index(self.last_clicked_widget)
        self.entry_clicked[j] = True
        
        
    def unclick_entry(self, *args):
        new_clicked_widget = self.root.focus_get()
        j = Widget_index_finder.find_index(self.last_clicked_widget)
        if self.last_clicked_widget != new_clicked_widget:
            self.entry_clicked[j] = False
            if self.variable[j].get() == "":
                self.entry[j].config(fg = 'grey')
                self.entry[j].insert(0, self.config[j]['default'])

    def keyreleased_entry(self, *args):        
        self.last_clicked_widget = self.root.focus_get()
        j = Widget_index_finder.find_index(self.last_clicked_widget)
        if self.entry[j].get() != "" and self.entry[j].get() != self.config[j]['default']:
            self.text_has_input[j] = True
        elif self.entry[j].get() == "" or self.entry[j].get() == self.config[j]['default']:
            self.text_has_input[j] = False          
            
##################### Eventhandling des Expiration-Widgets ###############################################

    def changeText(self, *args):        
        for item in self.config:        
            if item["GUI_type"] == "expiration":                
                j = self.config.index(item)

                expiration_string = self.expiration_variable[j].get()
                expiration_date_formatted = Formatted_expiration_finder.main(expiration_string, item["format"])

                self.variable[j].set(expiration_date_formatted)
                self.expiration_label[j].config(text="   Expired in: " + self.variable[j].get())

##################### Eventhandling der Menubar ###########################################################

    def load_config(self, *args):
        f = filedialog.askopenfilename(initialdir=self.initial_path)
        if len(f) == 0:
            return
        self.config_filepath.set(f)
        new_parser = text_parser.Text_parser()
        text_parser.Text_parser.change_path(new_parser, self.config_filepath.get())
        new_config = text_parser.Text_parser.read_template(new_parser)
        self.root.destroy()
        self.__init__(new_config)
        

    def browse_file(self, *args):
        f = filedialog.askopenfilename(initialdir=self.initial_path)
        if len(f) == 0: 
            return
        self.filepath.set(f)
        self.menubar.entryconfigure(2, label=self.currently_creating_text + self.filepath.get())

    def browse_folder(self, *args):        
        f = filedialog.askdirectory(initialdir=self.initial_path)
        if len(f) == 0: 
            return            
        self.filepath.set(f)
        self.menubar.entryconfigure(2, label=self.currently_creating_text + self.filepath.get())


    def save(self, *args):
        for item in self.config:
            j = self.config.index(item)
            inter_list1 = []
            if item["GUI_type"] == "calendar":
                print(self.calendar[j].get_date())
                date_calender = self.calendar[j].get_date()
                date_format = item['format']
                date = Formatted_expiration_finder.format_date(date_calender, date_format)
                self.metadata[item["key"]] = date
            elif j in self.variable:
                if not(isinstance(self.variable[j], dict)):
                    self.metadata[item["key"]] = self.variable[j].get()
                elif isinstance(self.variable[j], dict):
                    self.metadata[item["key"]] = {}
                    for inner_item in self.variable[j].values():
                        if inner_item.get() != "none":
                            inter_list1.append(inner_item.get())
                            self.metadata[item["key"]] = inter_list1           
                   
        metadata_json = json.dumps(self.metadata, indent = 4)
        #print(metadata_json)
        self.get_sidecar_filename()
        self.get_sidecar_extension()
        f = asksaveasfile(initialdir=self.initial_path, mode='w', defaultextension=self.extension_suggestion, initialfile=self.filename_suggestion, filetypes=[("Sidecarfile", "*.meta")])
        if f == None: 
            self.cancel = False
            return
        f.write(metadata_json)
        f.close()
        self.cancel = True

    def save_and_exit(self, *args):
        self.save(self)       
        if self.cancel == False:
            return
        elif self.cancel == True:
            self.root.destroy()

    def exit(self, *args):
        self.root.destroy()

    def show_version(self, *args):
        # Toplevel object which will
        # be treated as a new window
        versionInfo_window = Toplevel(self.root)
 
        # sets the title of the
        # Toplevel widget
        versionInfo_window.title("Version info")
 
        # sets the geometry of toplevel
        versionInfo_window.geometry("250x150")
 
        # A Label widget to show in toplevel
        Label(versionInfo_window, text =self.version).grid(row=0, column= 0, sticky=(N, W))
        Label(versionInfo_window, text =self.last_change).grid(row=1, column= 0, sticky=(N, W))

############################################################################
# ~~~~~~~~~~~~~~~~ Widgets generieren ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
############################################################################


    def make_label(self, j, element):
        self.label[j] = ttk.Label(self.subframe[j], text=element['key'])
        self.label[j].config(font=("Arial", 10))
        self.label[j].grid(row=0, column=0, sticky=(N, W))

    def make_abstand(self, j):
        self.abstand[j] = Label(self.subframe[j])
        self.abstand[j].config(width=10, height=0)
        self.abstand[j].grid(row=0, column=2, sticky=(N, W))

    


    def make_selectbox(self, j, element):                
        self.make_label(j, element)           
            
        self.variable[j] = StringVar()
        self.variable[j].set(element['default'])
            
        options = element['values']
                
        self.selectbox[j] = OptionMenu(self.subframe[j], self.variable[j], *options)
        self.selectbox[j].grid(row=0, column=1, sticky=(N, W))
        
        self.selectbox[j].bind("<Enter>", self.remove_focus)

        self.make_abstand(j)

        

    def make_checkbox(self, j, element):               
        self.make_label(j, element)   

        self.checkbox_frame[j] = ttk.Frame(self.subframe[j])
        self.checkbox_frame[j].grid(row=0, column=1, sticky=(N, W))        
                
        self.checkbox[j] = {}
        self.variable[j] = {}

        inner_row_number = -1
        for item in element['values']:
            inner_row_number += 1
            k = str(element['values'].index(item))
            self.variable[j][k] = StringVar()
            self.checkbox[j][k] = Checkbutton(self.checkbox_frame[j], text=item, variable=self.variable[j][k], onvalue=item, offvalue="none", command=self.remove_focus)
            self.checkbox[j][k].deselect()
            self.checkbox[j][k].grid(row = inner_row_number, column = 0, sticky=W)

        self.make_abstand(j)


    def make_textfield(self, j, element):                            
        self.make_label(j, element) 
                
        self.variable[j] = StringVar()   

        self.entry_clicked[j] = 0
                          
        self.entry[j] = Entry(self.subframe[j], width=20, bd=1, textvariable=self.variable[j])
        self.entry[j].insert(0, element['default'])

        self.entry[j].bind("<Enter>", self.mouse_on_entry)               
        self.entry[j].bind("<Leave>", self.mouse_off_entry)
        self.entry[j].bind("<FocusIn>", self.click_on_entry)
        self.entry[j].bind("<FocusOut>", self.unclick_entry)
        self.entry[j].bind("<KeyRelease>",self.keyreleased_entry)
                
        self.entry[j].config(fg = 'grey')            
        self.entry[j].grid(row=0, column=1, sticky=(N, W))

        self.make_abstand(j)


    def make_calendar(self, j, element):
        self.make_label(j, element)  
            
        self.calendar[j] = Calendar(self.subframe[j], cursor="hand1", selectmode="day", year=self.y, month=self.m, day=self.d)
        self.calendar[j].grid(row=0, column=1, sticky=(N, W), padx=10, pady = (0,25))

        self.calendar[j].bind("<Enter>", self.remove_focus) 

        self.make_abstand(j)


    def make_expiration(self, j, element):
        self.make_label(j, element)        

        self.expiration_variable[j] = StringVar()
        self.expiration_variable[j].set(element['default'])

        formatted_default_date = Formatted_expiration_finder.main(element['default'], element["format"])
            
        self.variable[j] = StringVar()
        self.variable[j].set(formatted_default_date)
                    
        options = element['values']
        self.selectbox[j] = OptionMenu(self.subframe[j], self.expiration_variable[j], *options, command=self.changeText)
        self.selectbox[j].grid(row=0, column=1)

        self.selectbox[j].bind("<Enter>", self.remove_focus)

        self.expiration_label[j] = Label(self.subframe[j], text="   Expired in: " + self.variable[j].get())
        self.expiration_label[j].config(font=("Arial", 10))
        self.expiration_label[j].grid(row=0, column=2) 

#################################################################################
# ~~~~~~~~~~~ Hier unten kommt praktisch eine Art "Main-Methode" ~~~~~~~~~~~~~~~~
#################################################################################

def main():
    conf_list = text_parser.Text_parser.read_template(text_parser.Text_parser())
    Juwel(conf_list)

if __name__ == "__main__":
    main()




        
