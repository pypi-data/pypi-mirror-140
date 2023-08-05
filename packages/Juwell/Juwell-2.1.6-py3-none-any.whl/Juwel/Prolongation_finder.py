#!/usr/bin/env python3

# Diese kleine, aber nützliche Funktion dient dazu, dass das Juwel-Programm
# bei der Auswertung der Optionen in der Auslaufsdatum-Selectbox erkenn kann,
# ob da eine Jahreszahl als Frist angegeben wurde, oder ein Wort
# wie zB "unlimited" oder "unbegrenzt"
# Mit dem Ouptut dieser Funktion kann Juwel dann entweder anhand der Jahreszahl
# die Datumsfrist errechnen oder anhand des Strings (zB "unlimited") eine
# fiktive Datumsfrist von 1.1.3000 angeben

# Der Grund, warum diese Funktion Prolongation_finder heißt, ist weil
# das Juwel-Programm das heutige Datum bezieht und dann mit der
# per GUI-selectbox ausgewählten Jahreszahl verlängert (="prolongiert"),
# um die Datumsfrist (Ablauffrist) zu ermitteln
# Da der Hauptteil des Algorithmus im If-Zweig "expiration" des
# Skripts Json_transf stattfindet, und hier nur die
# prolongierende Jahreszahl ermittelt wird, wurde diese Funktion so genannt

def get_prolongation(my_string):
    string_list = my_string.split()

    my_int = 0
    for word in string_list:
        if word.isdigit():
            my_int = int(word)

    if my_int != 0:
        return my_int
    elif my_int == 0:
        return my_string
