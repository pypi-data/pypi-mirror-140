#!/usr/bin/env python3

# Diese Funktion soll dem Textparser, der die config-File einliest,
# erleichtern, die User-Eingaben zu verstehen.
# Vielleicht gibt der User Begriffe an, die ein Mensch sofort versteht,
# die aber von den vorgegebenen Input-Möglichkeiten für das Juwel-Programm
# abweichen. Der GUI_element_finder nimmt bedeutungsgleiche Wörter für GUI-Elemente
# entgegen und wandelt sie alle in die gleichen Strings um.

def find_gui_element(gui_element):
    gui_element = gui_element.lower()
    
    if gui_element[-3:] == "xes":
        gui_element = gui_element[:-2]
    if gui_element[-1] == "s":
        gui_element = gui_element[:-1]


    if "_" in gui_element:
        gui_element = gui_element.replace("_", "")
    if " " in gui_element:
        gui_element = gui_element.replace(" ", "")


    if "dropdown" in gui_element or "list" in gui_element or "option" in gui_element:
        gui_element = "selectbox"

    if "button" in gui_element or "check" in gui_element:
        gui_element = "checkbox"

    if "text" in gui_element:
        gui_element = "textfield"

    if "alender" in gui_element or "date" in gui_element or "datum" in gui_element:
        gui_element = "calendar"
    

    return gui_element
