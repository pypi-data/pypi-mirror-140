#!/usr/bin/env python3

import datetime
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta

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



def find_expiration(prolongation_value):
    today = datetime.date.today()

    if isinstance(prolongation_value, int):
        expiration_date = today + relativedelta(years=prolongation_value)
    elif isinstance(prolongation_value, str):
        expiration_date = "01/01/3000"

    return expiration_date 


def format_date(date, date_format):

        if isinstance(date, str):
                date_list = date.split("/")
                year = date_list[2]
                if len(year) == 2:
                        date2 = datetime.datetime.strptime(date, '%m/%d/%y')
                elif len(year) == 4:
                        date2 = datetime.datetime.strptime(date, '%m/%d/%Y')
        else:
                date2 = date

        date_format = date_format.lower()

        if date_format == "deutsch" or date_format == "german":
                date_formatted = date2.strftime('%d.%m.%Y')        
        elif date_format == "international":
                date_formatted = date2.strftime('%Y-%m-%d')
        elif date_format == "us" or date_format == "american" or date_format == "amerikanisch":                
                d = date2.day
                y = date2.year
                m = date2.month
                
                if m==1:
                        str_month = "JAN"
                elif m==2:
                        str_month = "FEB"
                elif m==3:
                        str_month = "MAR"
                elif m==4:
                        str_month = "APR"
                elif m==5:
                        str_month = "MAY"
                elif m==6:
                        str_month = "JUN"
                elif m==7:
                        str_month = "JUL"
                elif m==8:
                        str_month = "AUG"
                elif m==9:
                        str_month = "SEP"
                elif m==10:
                        str_month = "OCT"
                elif m==11:
                        str_month = "NOV"
                elif m==12:
                        str_month = "DEC"
                
                date_formatted = str_month + " " + str(d) + ", " + str(y)
                                

        return date_formatted


def main(selectbox_option_value, date_format):
    
    prolongation_value = get_prolongation(selectbox_option_value)
    expiration_date = find_expiration(prolongation_value)
    formatted_date = format_date(expiration_date, date_format)

    return formatted_date
