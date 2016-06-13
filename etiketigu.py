#    (C) Copyright 2016 Pierre Vittet
#    This file is part of etikedo.
#    etikedo is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3, or (at your option)
#    any later version.
#    etikedo is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with GMWarn; see the file COPYING3.  If not see
#    <http://www.gnu.org/licenses/>.



import scribus
import sys
import Tkinter, Tkconstants, tkFileDialog
import email
import re

CONST_LINE_NUMBER = 8
CONST_COL_NUMBER = 3
CONST_COL_SIZE = 36
CONST_LINE_SIZE = 70
CONST_TOP_MARGIN = 4
CONST_LEFT_MARGIN = 0

MAX_PAGE_CONTACTS = CONST_LINE_NUMBER * CONST_COL_NUMBER


def init_config():
    scribus.setUnit(scribus.UNIT_MILLIMETERS)

def select_files():
  root = Tkinter.Tk()
  files = tkFileDialog.askopenfilenames(parent=root,title='Choose files')
  files_list = root.tk.splitlist(files)
  #root.destroy()
  return files_list


def get_info(info, clean_msg):
    name_ex = re.compile("<td>"+info+"</td><td>(.*?)</td>")
    res = name_ex.search(clean_msg)
    if (res is None):
        return ""
    else:
        return res.group(1)

class Contact:
    def __init__(self, name, address, city, region, code, country):
        self.name=name
        self.address=address
        self.city=city
        self.region=region
        self.code=code
        self.country=country

    def print_contact(self):
        cstr = self.name+"\n"
        cstr = cstr + self.address+"\n"
        cstr = cstr + self.code +" "+ self.city+"\n"
        cstr = cstr + self.region +"\n"
        cstr = cstr + self.country +"\n"
        return cstr

def extract_address(files_list):
    contacts=[]
    for idx, afile in enumerate(files_list):
        msg = email.message_from_file(open(afile, 'r')).get_payload()
        #we now want to suppress every style related comment
        style_ex = re.compile("<([a-zA-Z]*)\s[^>]*>")
        clean_msg= style_ex.sub(r'<\1>', msg)
        clean_msg= re.sub(r'\n|\r|\t',r' ', clean_msg)
        name = get_info("Nomo:",clean_msg)
        address = get_info("Stratadreso",clean_msg)
        city = get_info("Urbo",clean_msg)
        region= get_info("Regiono",clean_msg)
        code= get_info("Po\xc5\x9dtkodo",clean_msg)
        country= get_info("Lando",clean_msg)
        contacts.append(Contact(name, address, city, region, code, country))
    return contacts


def fill_page(contacts):
    #where contacts is an array or at most max_contact contacts
    assert(len(contacts) < MAX_PAGE_CONTACTS)
    
    nb_lines = (len(contacts) / (CONST_COL_NUMBER))  
    if((len(contacts) % CONST_COL_NUMBER) != 0):
        nb_lines = nb_lines+1
    for curline in range (0, nb_lines):
        nb_col = min(len(contacts) - (curline * CONST_COL_NUMBER), CONST_COL_NUMBER) 
        for curcol in range (0, nb_col):
            x = CONST_COL_SIZE * curline
            y = CONST_LINE_SIZE * curcol
            txtFrameName= "etiketo"+str(curline)+str(curcol)
            scribus.createText(y, x, CONST_LINE_SIZE, CONST_COL_SIZE, txtFrameName)
            contact_idx=curline*CONST_COL_NUMBER+curcol
            scribus.setText(contacts[contact_idx].print_contact(), txtFrameName)
            scribus.setTextDistances(6, 0, 3, 0, txtFrameName) 
            scribus.setFontSize(10, txtFrameName)
            scribus.setFont("Liberation Serif Regular", txtFrameName)

def fill_addresses(contacts):
    #on a page, we can put MAX_PAGE_CONTACTS contacts.
    nb_pages = (len(contacts) / MAX_PAGE_CONTACTS) + 1
    for curPage in range(0, nb_pages):
        start_contact = curPage * MAX_PAGE_CONTACTS
        end_contact = start_contact + (MAX_PAGE_CONTACTS -1)
        fill_page(contacts[start_contact:end_contact])
        if(end_contact < len(contacts)):
            scribus.newPage(-1)
            scribus.gotoPage(scribus.pageCount()-1)

init_config()
files_list = select_files()
contacts= extract_address(files_list)
fill_addresses(contacts)
