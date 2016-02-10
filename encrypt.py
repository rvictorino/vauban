#! /usr/bin/env python
#_*_ coding: utf-8 _*_

import os, sys,gnupg,cgi
import Tkinter, tkFileDialog
import pylab

# SELECTION FICHIER
print "Please provide location of configuration file."
root = Tkinter.Tk()
root.withdraw()
file_path = tkFileDialog.askopenfilename()


#pylab.figure()
#pylab.show()

print "Made it."
###################

# SELECTION DU DESTINATAIRE

user = raw_input("Entrez l'adresse mail du destinataire : ")
user = str(user)

#########################"

#CRYPTAGE DU FICHIER
gpg = gnupg.GPG(gnupghome='gpghome/')

with open(file_path, 'rb') as f:
    status = gpg.encrypt_file(
        f, recipients=[user],
        output=os.path.basename(file_path)+'.gpg')

print "##################################################"
print "CRYPTAGE FICHIER"
print 'ok: ', status.ok
print 'status: ', status.status
print 'stderr: ', status.stderr

