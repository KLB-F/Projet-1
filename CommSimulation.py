# -*- coding: utf-8 -*-
"""
Fichier de communication avec l'arduino en vue d'une simulation du comportement du hacheur.

Entrés :
    Arduino : Rapport cyclique a - format d'entré "[a]\n\r"
Sorties : 
    Arduino : Tension et Puissance sous la forme "b[(int)Puissance];[(int)Tension]f"
    Affichage des courbes obtenues via simulation

"""

import serial
import Modele as mod
import numpy as np
import matplotlib.pyplot as plt
import pvlib

R = 20 #Resistance de la charge

# Création de la modélisation du panneau solaire

I =  np.array([0, 0, 1, 3, 19, 38, 119, 241, 305, 305, 305, 217, 198, 183, 305])
V = np.array([2160, 2150, 2150, 2150,2120, 2080, 1900, 1510, 690, 420, 210, 1670, 1720, 1760, 30])

V, I = pvlib.ivtools.utils.rectify_iv_curve(V, I) #Fonction qui trie les valeurs, enleve les duplicats ...

param = pvlib.ivtools.sde.fit_sandia_simple(V, I, v_oc=2150, i_sc = 305) #Modele simple diode estimation


Vliste = np.linspace(0, 2150, 1000)
Iliste = np.array([pvlib.pvsystem.i_from_v(v, param[0], param[1], param[2], param[3], param[4]) for v in Vliste])

#

def ResistanceApp(PWM):
    """Renvoie la resistance de la charge apparente (Ohm)
    Parameters:
        PWM : unsigned char
        Rapport cyclique du hacheur"""
    return R*((1-PWM/256)**2)

#Initialisation

u = max(V)/2

PWML = []
U = []
Ic = []
Pe = []

arduino = serial.Serial(port='COM5', baudrate=115200, timeout=0.1)
PWM = -1

#Boucle

j = 0

lastTime = -1

while j < 250:
    comm = ''
    while comm == '' or comm == "''":
        comm = str(arduino.readline())[1:] #Pas de communication
    comm = int(comm.split('\\r')[0].split("\\n")[0][1:]) # On convertie en int
    PWM = int(comm)
    if PWM != -1:
        PWML.append(PWM)
        Rapp = ResistanceApp(PWM)
        u, i = mod.Inter_lin_courbeIV(Vliste, Iliste, Rapp, 0, max(V))
    for k in range(5):
        arduino.write(bytes(str(int(u*i))+";"+str(int(u))+"f", 'utf-8'))
        u, i = mod.Inter_lin_courbeIV(Vliste, Iliste, Rapp, 0, max(V))
    Ic.append(int(i))
    U.append(int(u))
    Pe.append(int(u*i))
    j = j +1

#Affichage

plt.clf()
plt.plot(V, np.array(Vliste)*np.array(Iliste), '.')
plt.plot(U, Pe, '.')
plt.show()
