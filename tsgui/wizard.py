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

from PyQt4 import QtGui, QtCore, Qt

class Wizard(QtGui.QWizard):


    def __init__(self, parent = None):
        '''
        Constructor
        '''
        QtGui.QWizard.__init__(self, parent)

        self.__wizard = QtGui.QWizard()
        self.__wizard.setWindowFlags(QtCore.Qt.WindowTitleHint)
        self.__wizard.resize(800, 590)
        self.__wizard.setButtonText(self.__wizard.NextButton, 
                                    self.trUtf8("Next"))
        self.__wizard.setButtonText(self.__wizard.BackButton, 
                                    self.trUtf8("Back"))
        self.__wizard.setButtonText(self.__wizard.CancelButton, 
                                    self.trUtf8("Cancel"))
        self.__wizard.setButtonText(self.__wizard.FinishButton, 
                                    self.trUtf8("Finish"))
        
        self.__wizard.addPage(self.__create_welcome_page())
        self.__wizard.addPage(self.__create_fundamentals_page())
        self.__wizard.addPage(self.__create_intro_page())
        self.__wizard.addPage(self.__create_first_steps_page())
        self.__wizard.addPage(self.__create_setting_page())
        self.__wizard.addPage(self.__create_tagging_page())
        self.__wizard.addPage(self.__create_ending_page())
    
        self.__wizard.setWindowTitle(self.trUtf8("Help Wizard"))
        
    def __create_welcome_page(self):
        page = QtGui.QWizardPage()
        page.setTitle(self.trUtf8("Welcome to tagstore!"))
        
        widget = QtGui.QWidget()
        scrollarea = QtGui.QScrollArea()
        scrollarea.setWidgetResizable(True)
    
        text_label = QtGui.QLabel(self.trUtf8("Danke, dass sie sich fuer tagstore entschieden haben.<br>"
                                         "Das Programm wurde erfolgreich installiert und dieser Assistent wird bei dem Einrichten des ersten \"Store\" helfen."))
        
        text_label.setWordWrap(True)
        text_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
    
        layout = QtGui.QVBoxLayout()
        layout.addWidget(text_label)
        
        widget.setLayout(layout)
        scrollarea.setWidget(widget)
        
        scrolllayout = QtGui.QVBoxLayout()
        scrolllayout.addWidget(scrollarea)
        
        page.setLayout(scrolllayout)
    
        return page
    
    
    def __create_intro_page(self):
        page = QtGui.QWizardPage()
        page.setTitle(self.trUtf8("What is tagstore?"))
        
        widget = QtGui.QWidget()
        scrollarea = QtGui.QScrollArea()
        scrollarea.setWidgetResizable(True)
    
        text_label = QtGui.QLabel(self.trUtf8("Tagstore ist ein Program, welches dabei helfen soll, Dateien auf dem Computer schneller wieder zu finden.<br>"
                                         "Dies geschiet durch sogenanntes tagging.<br>"
                                         "Tagging ist ein Verfahren, bei dem ein Benutzer einem Stueck Information (z.B: Digitale Bilder, MP3, Videos,..) sogenannte Tags zuordnet.<br>"
                                         "Ein Tag ist ein Schluesselwort oder Term welcher dabei helfen soll ein Stueck Information zu beschreiben und es dadurch schneller wieder gefunden werden kann.<br>"
                                         "Bei tagstore koennen, je nach Einstellung, kategorisierende und/oder beschreibende Tags g/benutzt werden. "))
        
        text_label.setWordWrap(True)
        text_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
    
        layout = QtGui.QVBoxLayout()
        layout.addWidget(text_label)
        
        widget.setLayout(layout)
        scrollarea.setWidget(widget)
        
        scrolllayout = QtGui.QVBoxLayout()
        scrolllayout.addWidget(scrollarea)
        
        page.setLayout(scrolllayout)
    
        return page
    
    def __create_first_steps_page(self):
        page = QtGui.QWizardPage()
        page.setTitle(self.trUtf8("First steps"))
        
        widget = QtGui.QWidget()
        scrollarea = QtGui.QScrollArea()
        scrollarea.setWidgetResizable(True)
        
        text_label = QtGui.QLabel(self.trUtf8("Bei dem ersten Start des Programmes, muss ein sogenannter \"Store\" angelegt werden. <br>"
                                                "Jeder Benutzer muss zumindest einen Store anlegen. Weitere Stores fuer verschiedene Zwecke (beruflich, privat, Videos, Downloads, ...) koennen jederzeit nachtraeglich erstellt werden.<br>"
                                                "Um einen Store anzulegen wird zuerst im tagstore Manager der Tab \"Store-Verwaltung\" ausgewaehlt und danach auf \"Neuer Tagstore\" geklickt. Daraufhin erscheint ein neues Fenster, in welchem ein Ordner ausgewaehlt wird, der den Store beinhalten soll. <br>"
                                                "Wenn ein der Store erfolgreich angelegt wurde, sollte die Stuktur in dem Ordenr, welcher fuer den Store ausgewehlt wurde, so aussehen:"))
        
        text_label2 = QtGui.QLabel(self.trUtf8("INSERT ENGLISH TEXT"))
        
        image_label = QtGui.QLabel()
        image_label.setPixmap(QtGui.QPixmap(self.trUtf8("./tsresources/images/structure_en.png")))
        
        text_label.setWordWrap(True)
        text_label2.setWordWrap(True)
        text_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        text_label2.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
    
        layout = QtGui.QVBoxLayout()
        layout.addWidget(text_label)
        layout.addWidget(image_label)
        layout.addWidget(text_label2)
        
        widget.setLayout(layout)
        scrollarea.setWidget(widget)
        
        scrolllayout = QtGui.QVBoxLayout()
        scrolllayout.addWidget(scrollarea)
        
        page.setLayout(scrolllayout)
    
        return page
    
    
    def __create_ending_page(self):
        page = QtGui.QWizardPage()
        page.setTitle(self.trUtf8("Have fun!"))
        
        widget = QtGui.QWidget()
        scrollarea = QtGui.QScrollArea()
        scrollarea.setWidgetResizable(True)
        
        text_label = QtGui.QLabel(self.trUtf8("Das tagstore-Team wuenscht viel Spass beim taggen!<br>"
                                               "Bei Unklarheiten zu einem Reiter einfach auf den Hilfeknopf oben rechts in der Ecke eines jeden Reiters klicken."))
        
        text_label.setWordWrap(True)
        text_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(text_label)
        
        widget.setLayout(layout)
        scrollarea.setWidget(widget)
        
        scrolllayout = QtGui.QVBoxLayout()
        scrolllayout.addWidget(scrollarea)
        
        page.setLayout(scrolllayout)
    
        return page
    
    def __create_setting_page(self):
        page = QtGui.QWizardPage()
        page.setTitle(self.trUtf8("Store settings"))
        
        widget = QtGui.QWidget()
        scrollarea = QtGui.QScrollArea()
        scrollarea.setWidgetResizable(True)
        
        tab_image_lable = QtGui.QLabel()
        dropdown_image_lable = QtGui.QLabel()
        settings_image_lable = QtGui.QLabel()
        tab_image_lable.setPixmap(QtGui.QPixmap(self.trUtf8("./tsresources/images/tabs_en.png")))
        dropdown_image_lable.setPixmap(QtGui.QPixmap(self.trUtf8("./tsresources/images/store_dropdown.png")))
        settings_image_lable.setPixmap(QtGui.QPixmap(self.trUtf8("./tsresources/images/my_tags_tag_lines_en.png")))
        
        text_label1 = QtGui.QLabel(self.trUtf8("Jeder Store der angelegt wurde, kann ueber den Manager jederzeit konfiguriert werden. Dieser ist in verschiedene Tabs/Reiter unterteilt."))
        text_label2 = QtGui.QLabel(self.trUtf8("Wenn eine Einstellung fuer jeden Store gemacht werden kann, wird der gewuenschte Store ueber ein \"Dropdown Menu\" ausgewaehlt. Dieses befindet sich unter der Beschreibung des Tabs."))
        text_label3 = QtGui.QLabel(self.trUtf8("Unter dem Tab/Reiter \"Meine Tags\" kann fuer jeden Store nachgeschaut werden, ob eine oder zwei Tag-Zeilen verwendet werden. In der erste Tag-Zeile werden beschreibende und in der zweiten kategorisierende Tags verwendet."))
        text_label4 = QtGui.QLabel(self.trUtf8("Wird nur eine Zeile verwendet, kann eingestellt werden, ob in dieser nur vom Benutzter vordefinierte Tags (\"Meine Tags\") erlaubt werden oder nicht. Dies soll die Verwendung von aehnlichen Tags verhindern(z.B: Uni, Universitaet). <br>"
                                                      "Solche Tags koennen mit einem klick auf \"Hinzufuegen\" der Liste von Tags hinzugefuegt werden oder mit \"Loeschen\" von ihr geloescht werden. <br>"
                                                      "Werden zwei Zeilen verwendet, kann nur noch fuer die zweite Tag-Zeile eingestellt werden, ob diese nur \"meine Tags\" verwenden soll."))
        text_label1.setWordWrap(True)
        text_label2.setWordWrap(True)
        text_label3.setWordWrap(True)
        text_label4.setWordWrap(True)
        text_label1.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        text_label2.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        text_label3.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        text_label4.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(text_label1)
        layout.addWidget(tab_image_lable)
        layout.addWidget(text_label2)
        layout.addWidget(dropdown_image_lable)
        layout.addWidget(text_label3)
        layout.addWidget(settings_image_lable)
        layout.addWidget(text_label4)
    
        widget.setLayout(layout)
        scrollarea.setWidget(widget)
        
        scrolllayout = QtGui.QVBoxLayout()
        scrolllayout.addWidget(scrollarea)
        
        page.setLayout(scrolllayout)
        
        return page
    
    def __create_tagging_page(self):
        page = QtGui.QWizardPage()
        page.setTitle(self.trUtf8("Tagging"))
        
        widget = QtGui.QWidget()
        scrollarea = QtGui.QScrollArea()
        scrollarea.setWidgetResizable(True)
        
        tagging_label = QtGui.QLabel()
        tagging_label.setPixmap(QtGui.QPixmap(self.trUtf8("./tsresources/images/tagging_en.png")))
        
        text_label1 = QtGui.QLabel(self.trUtf8("Wenn ein neues \"Item\" (Datei, Ordner) in den Ordner \"Ablage\" hinzugefuegt wird, erscheint der sogenannte \"Tag-Dialog\"."))
        text_label2 = QtGui.QLabel(self.trUtf8("Hier befindet sich die sogenannten \"Tag-Clouds\"(1), eine Liste der noch nicht getaggten Objekte(2) und je nach Einstellung eine oder zwei Tag-Zeilen. Die erste Tag-Zeile(3) ist fuer beschreibenden und die zweite(4) fuer kategorisierende Tags.<br>"
                                               "Mit einem klick auf \"Tag\"(5) wird das ausgewaehlte Objekt getaggt und ein klick auf \"Manager...\"(6) oeffnet den tagstore Manager.<br>"
                                               "Wenn man ein Objekt nicht sofort taggen will, kann man auf \"Spaeter bearbeiten\"(7) klicken.<br>"
                                               "Items, die noch nicht getaggt sind, erscheinen so lange in der Liste vom \"Tag-Dialog\", bis entsprechende Items wieder geloescht werden oder mit Tags versehen wurden."))
                                   
        text_label1.setWordWrap(True)
        text_label2.setWordWrap(True)
        text_label1.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        text_label2.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(text_label1)
        layout.addWidget(text_label2)
        layout.addWidget(tagging_label)
        
        widget.setLayout(layout)
        scrollarea.setWidget(widget)
        
        scrolllayout = QtGui.QVBoxLayout()
        scrolllayout.addWidget(scrollarea)
        
        page.setLayout(scrolllayout)
        
        return page
    
    def __create_fundamentals_page(self):
        page = QtGui.QWizardPage()
        page.setTitle(self.trUtf8("Fundamentals"))
        
        widget = QtGui.QWidget()
        scrollarea = QtGui.QScrollArea()
        scrollarea.setWidgetResizable(True)
        
        text_label = QtGui.QLabel(self.trUtf8("Wir verwenden im Weiteren folgende Begriffe:<br><br>"
                                  "Ein <b>*Item*</b> ist der Ueberbegriff von Datei<br>"
                                  "und Ordner. Sie koennen auch Ordner in tagstore ablegen.<br><br>"
                                  "Ein <b>*store*</b> ist ein Ordner, der auf Ihrer<br>"
                                  "lokalen Festplatte angelegt wird, um eine Menge von Items zu verwalten.<br><br>"
                                  "Ein <b>*tag*</b> ist ein Schlagwort."))
        
        text_label.setWordWrap(True)
        text_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(text_label)
        
        widget.setLayout(layout)
        scrollarea.setWidget(widget)
        
        scrolllayout = QtGui.QVBoxLayout()
        scrolllayout.addWidget(scrollarea)
        
        page.setLayout(scrolllayout)
        
        return page
                
    
    def get_view(self):
        return self.__wizard

## end 