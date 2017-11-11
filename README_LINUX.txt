####################################################
README FOR TAGSTORE
####################################################

this file is part of tagstore, an alternative way of storing and retrieving information
Copyright (C) 2010-2014  Karl Voit, Christoph Friedl, Wolfgang Wintersteller


***************************
1. Please do read README.org
***************************

***************************
2. additional notes for GNU/Linux
***************************

Starting tagstore:

tagstore Manager can be stared by Gnome/Ubuntu-based application
launcher or via shell script as shown below:

sh -c "cd /your/path/to/tagstore && python tagstore_manager.py"


In case you want to start tagstore.py automatically, please add the
following line to ~/.config/autostart/python.desktop:

Exec=sh -c "cd /your/path/to/tagstore && python tagstore.py &"
