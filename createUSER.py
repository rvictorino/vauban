#! /usr/bin/env python
#_*_ coding: utf-8 _*_

from getpass import getpass
import os, sys,gnupg,cgi

os.system('rm -rf /home/miloud/PycharmProjects/PyGPG/gpghome/')
gpg = gnupg.GPG(gnupghome='gpghome/')

#Génération d'une clé
varmail = raw_input("Entrez votre adresse mail :")
varpass = getpass()

input_data = gpg.gen_key_input(name_email=varmail, passphrase=varpass)
key = gpg.gen_key(input_data)
print 'KEY'
print key
########################

