#! /usr/bin/env python
#_*_ coding: utf-8 _*_

from getpass import getpass
import os, sys,gnupg,cgi

#La commande du desssous permet de réinitialiser le dossier contenant toutes les clés
#os.system('rm -rf /home/miloud/PycharmProjects/PyGPG/gpghome/')
#######################################################################
# Création du dossier contenant les clés
gpg = gnupg.GPG(gnupghome='gpghome/')
########################################

###########Génération d'une clé############################
#Nous demandons a l'utilisateur de saisir son adresse mail ainsi que le mot de passe
varmail = raw_input("Entrez votre adresse mail : ")
varname = raw_input("Entrez un nom : ")
#La méthode getpass() permet de masquer l'entrée du mot de passe
varpass = getpass()
##############################################################

#Nous formatons les informations relevées avec la méthode gen_key_input()
input_data = gpg.gen_key_input(name_real=varname, name_email=varmail, passphrase=varpass, key_length=2048)
#Nous générons la clé
key = gpg.gen_key(input_data)
print 'KEY'
print key
########################
#Export de la clé

print
print "EXPORT DE LA CLE"

#nous formatons la variable key en string afin de pouvoir l'utiliser dans la méthode export_keys()
#key = str(key)
var = str(varmail)

#Export des clés publiques et privés
ascii_armored_public_keys = gpg.export_keys(key)
ascii_armored_private_keys = gpg.export_keys(key, True)

#Nous écrivons les clés publiques et privés dans deux fichiers distincts
with open(var+'.asc', 'w') as f:
    f.write(ascii_armored_public_keys)
    f.write(ascii_armored_private_keys)
print
print "EXPORT FAIT"
#####################

# Listing key

print gpg.list_keys()

#########################"""
