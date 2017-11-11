#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
## this file is part of tagstore, an alternative way of storing and retrieving information
## Copyright (C) 2010  Karl Voit, Michael Pirrer
##
## This program is free software; you can redistribute it and/or modify it under the terms
## of the GNU General Public License as published by the Free Software Foundation; either
## version 3 of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
## without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
## See the GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along with this program;
## if not, see <http://www.gnu.org/licenses/>.

from PyQt4 import QtGui, QtCore
from tscore.configwrapper import ConfigWrapper
from tscore.tsconstants import TsConstants
from tsgui.wizard import Wizard

class HelpDialog(QtGui.QDialog):


    def __init__(self, tab, parent = None):
        '''
        Constructor
        '''
        QtGui.QDialog.__init__(self, parent)
        
        self.__tab = tab
              
        self.setWindowFlags(QtCore.Qt.WindowTitleHint)
        
        self.__config_wrapper = ConfigWrapper(TsConstants.CONFIG_PATH)
        
        self.__wizard = Wizard()
        
        self.setWindowTitle("tagstore Manager Help")
        
        self.setWindowIcon(QtGui.QIcon('./tsresources/images/help.png'))
           
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.__base_layout = QtGui.QVBoxLayout()
        self.__descr_layout = QtGui.QHBoxLayout()
        self.__bb_layout = QtGui.QHBoxLayout()
        self.setLayout(self.__base_layout)
        
        self.__description_label = QtGui.QLabel()
        self.__description_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.__cancel_button = QtGui.QPushButton(self.trUtf8("Close"))
        self.__wizard_button = QtGui.QPushButton(self.trUtf8("Show Wizard"))
        self.__visible_checkbox = QtGui.QCheckBox(self.trUtf8("Show this automatically"))
        
        self.__descr_layout.addWidget(self.__description_label)      
        
        self.__visible_checkbox.setChecked(True)
        
        if self.__tab == "tagdialog":
            self.__description_label.setText(self.trUtf8("In diesem Fenster werden die Items, die sich in der Ablage befinden getaggt. <br>"
                                                         "Auf der rechten Seite Oben befindet sich eine Liste der noch nicht getagten Items. Um ein solches zu taggen wird zuerst eines ausgewaehlt, danach werden die Tags in die darunterliegende/n \"Tag-Zeile/n\" (je nach Einstellung) geschrieben und jeweils mit einem \",\" getrennt.<br>"
                                                         "Mit einem abschliessenden Klick auf \"Tag\" wird das ausgewaehlte Item getaggt.<br>"
                                                         "Auf der linken Seite befindet sich eine sogenannte \"TagCloud\" (fuer jede \"Tag-Zeile\" eine) in der sich Vorschlaege fuer Tags befinden, wobei die Groesse des Tags angibt, wie oft dieser verwendet wurde (je groesser desto haeufiger).<br>"
                                                         "Die in Orange dargestellten Tags wurden mit Hilfe eines Algorithmus, speziell fuer das ausgewaehlte Item und ihren Taggingverhalten ausgesucht."))
            self.__tagging_label = QtGui.QLabel()
            self.__tagging_label.setPixmap(QtGui.QPixmap(self.trUtf8("./tsresources/images/tagging_en.png")))
            self.__descr_layout.addWidget(self.__tagging_label)   
            self.setWindowTitle(self.trUtf8("Help tag-dialog"))
            if not self.__config_wrapper.get_show_tag_help():
                self.__visible_checkbox.setChecked(False)
        elif self.__tab == "My Tags":
            self.__description_label.setText(self.trUtf8("Unter dem Reiter \"Meine Tags\" kann fuer jeden Store nachgeschaut werden, ob eine oder zwei Tag-Zeilen verwendet werden. In der erste Tag-Zeile werden beschreibende und in der zweiten kategorisierende Tags verwendet.<br>"
                                                         "Wird nur eine Zeile verwendet, kann eingestellt werden, ob in dieser nur vom Benutzter vordefinierte Tags (\"Meine Tags\") erlaubt werden oder nicht. Dies soll die Verwendung von aehnlichen Tags verhindern(z.B: Uni, Universitaet). <br>"
                                                         "Solche Tags koennen mit einem klick auf \"Hinzufuegen\" der Liste von Tags hinzugefuegt werden oder mit \"Loeschen\" von ihr geloescht werden. <br>"
                                                         "Werden zwei Zeilen verwendet, kann nur noch fuer die zweite Tag-Zeile eingestellt werden, ob diese nur \"meine Tags\" verwenden soll."))
            if not self.__config_wrapper.get_show_my_tags_help():
                self.__visible_checkbox.setChecked(False)
        elif self.__tab == "Datestamps":
            self.__description_label.setText(self.trUtf8("Unter diesem Reiter kann eingestellt werden, ob beim taggen, das Datum automatisch in die \"Tagline\" eingetragen wird."))
            if not self.__config_wrapper.get_show_datestamps_help():
                self.__visible_checkbox.setChecked(False)
        elif self.__tab == "Expiry Date":
            self.__description_label.setText(self.trUtf8("Unter diesem Reiter kann eingestellt werden, wann ein bestimmtes Objekt, mit Hilfe eines Praefixes, ablaeuft und in den Ordner \"abgelaufene_Daten\" verschoben wird.<br>"
                                                         "Diesr Praefix kann in der Zeile am unteren Ende des Tabs definiert werden."))
            if not self.__config_wrapper.get_show_expiry_date_help():
                self.__visible_checkbox.setChecked(False)
        elif self.__tab == "Re-Tagging":
            self.__description_label.setText(self.trUtf8("Unter diesem Reiter koennen bereits getaggte Objekte neu getaggt werden. Dazu wird ein Objekt ausgewaehlt und anschliessend auf \"Re-Tag\" geklickt."))
            if not self.__config_wrapper.get_show_retagging_help():
                self.__visible_checkbox.setChecked(False)
        elif self.__tab == "Rename Tags":
            self.__description_label.setText(self.trUtf8("Unter diesem Reiter koennen Tags, die zum taggen verwendet wurden, umbenannt werden, womit sich auch die Ordnerstruktur aendert.<br>"
                                                         "Dazu wird ein Tag ausgewaehlt und anschliessend auf \"Umbenennen\" geklickt."))
            if not self.__config_wrapper.get_show_rename_tags_help():
                self.__visible_checkbox.setChecked(False)
        elif self.__tab == "Store Management":
            self.__description_label.setText(self.trUtf8("Unter diesem Reiter kann ein neuer \"Store\" angelegt oder ein bereits vorhandener geloescht oder umbenannet werden. Dies geschiet durch einen Klick auf \"Neuer tagstore\", \"Loeschen ...\" oder \"Umbenennen ...\".<br>"
                                                         "Zum loeschen oder umbenennen muss der gewuenschte \"Store\" ausgewaehlt werden.<br>"
                                                         "Wenn erwuenscht, kann auch die Ordnerstruktur des ausgewaehlten \"Stores\", mit einem klick auf \"Struktur neu erstellen ...\" neu erstellt werden"))
            if not self.__config_wrapper.get_show_store_management_help():
                self.__visible_checkbox.setChecked(False)
        elif self.__tab == "Sync Settings":
            self.__description_label.setText(self.trUtf8("Unter diesem Reiter kann ein Tag zum synchronisieren mit Android definiert werden. Alle Items, welche mit diesem Tag getaggt werden, werden automatisch synchronisiert."))
            if not self.__config_wrapper.get_show_sync_settings_help():
                self.__visible_checkbox.setChecked(False)
                
        self.__description_label.setWordWrap(True)
        
        self.__bb_layout.addWidget(self.__visible_checkbox)
        self.__bb_layout.addWidget(self.__wizard_button)
        self.__bb_layout.addWidget(self.__cancel_button)
        self.__base_layout.addLayout(self.__descr_layout)
        self.__base_layout.addLayout(self.__bb_layout)
        
        self.__visible_checkbox.stateChanged.connect(self.__handle_checkbox)
 
        self.connect(self.__cancel_button, QtCore.SIGNAL('clicked()'), self.__handle_close)
        self.connect(self.__wizard_button, QtCore.SIGNAL('clicked()'), self.__handle_show_wizard)
        
    def __handle_close(self):
        self.close()
        
    def __handle_show_wizard(self):
        self.__wizard.get_view().show()
        
    def __handle_checkbox(self, state):
        if state:
            tmp_state = "true"
        else:
            tmp_state = "false"
        
        if self.__tab == "tagdialog":
            self.__config_wrapper.set_show_tag_help(tmp_state)
        elif self.__tab == "My Tags":
            self.__config_wrapper.set_show_my_tags_help(tmp_state)
        elif self.__tab == "Datestamps":
            self.__config_wrapper.set_show_datestamps_help(tmp_state)
        elif self.__tab == "Expiry Date":
            self.__config_wrapper.set_show_expiry_date_help(tmp_state)
        elif self.__tab == "Re-Tagging":
            self.__config_wrapper.set_show_retagging_help(tmp_state)
        elif self.__tab == "Rename Tags":
            self.__config_wrapper.set_show_rename_tags_help(tmp_state)
        elif self.__tab == "Store Management":
            self.__config_wrapper.set_show_store_management_help(tmp_state)
        elif self.__tab == "Sync Settings":
            self.__config_wrapper.set_show_sync_settings_help(tmp_state)
            
## end        