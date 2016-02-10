#! /usr/bin/env python
#_*_ coding: utf-8 _*_

from getpass import getpass
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

# Entrez mot de passe

mdp = getpass()

#########################

#DECRYPTAGE
gpg = gnupg.GPG(gnupghome='gpghome/')

with open(file_path, 'rb') as f:
    status = gpg.decrypt_file(
        f,passphrase =mdp,
        output=os.path.splitext(os.path.basename(file_path))[0])

print "##################################################"
print "DECRYPTAGE FICHIER"
print 'ok: ', status.ok
print 'status: ', status.status
print 'stderr: ', status.stderr


