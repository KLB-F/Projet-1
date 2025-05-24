# -*- coding: utf-8 -*-
"""
Fichier de communication avec un arduino : l'arduino envoie des valeurs de tension et puissance.
Elles sont stockés dans des listes pour être affichés sous forme de courbe ensuite.

Entrées : L'arduino envoie la tension / puissance reçu sous la forme "b[(float)Tension]S[(float)Puissance]\n\r".
Sorties : courbe P/V

"""

import serial
import Modele as mod
import numpy as np
import matplotlib.pyplot as plt
import pvlib

arduino = serial.Serial(port='COM5', baudrate=115200, timeout=0.1)

Puissance = []
Tension = []

j = 0

while j < 1500:
    comm = ''
    while comm == '' or comm == "''":
        comm = str(arduino.readline())[1:] #Pas de communication
    comm = comm.split('\\r')[0].split("\\n")[0][1:] # On enleve le superflue
    Vcomm = [float(elm) for elm in comm.split['S']]
    Puissance.append(Vcomm[1])
    Tension.append(Vcomm[0])
    j = j + 1
    
plt.clf()
plt.plot(Tension, Puissance, '.')
plt.xlabel("Tension (V)")
plt.ylabel("Puissance (W)")
plt.show()
    