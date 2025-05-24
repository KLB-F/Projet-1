# -*- coding: utf-8 -*-
"""
Fichier contenant toutes les fonctions nécessaire à la modélisation du panneau solaire qui ne sont pas incluent dans pvlib
"""

import pvlib
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import pvlib

#Constantes
Gn = 1000 #Eclairement solaire nominale (en W/m²)
Tn = 25+273.15 #Température nomniale obtenue dans les conditions STC (en K)
q = 1.6e-19 #Charge élémentaire 
K = 1.38e-23 #Constante de Boltzmann (J/K)
Eg = 1.12*1.60218e-19 #Energie du gap (J)


def Calcul_alphasc(listeI, listeTemp, listeG, affCourbe=False):
    """
    Permet de calculer alpha_sc par régression linéaire
    
    Parameters
    ----------
    listeI : list
        Liste contenant les valeurs de I pour les différentes courbes (A)
    listeTemp : list
        Liste contenant les différentes températures correspondant aux différentes températures EN KELVIN
    affCourbe : bool
        Affiche ou non les courbes Isc = f(T) réel et modéliser

    Returns :
        Isc : le courant court circuit à T = 25°C
        alpha_sc :  la valeur du coefficent alpha_sc

    """
    Isc = []
    for i in range(len(listeI)):
        #Determination de Isc pour chacune des listes de I
        Isc.append(np.mean(sorted(np.array(listeI[i])*Gn/listeG[i], reverse=True)[:3]))
    Pcoef = np.polyfit(listeTemp, Isc, deg=1) #Calcul de Isc & alpha_sc

    def Pcalc(x):
        return Pcoef[1]+Pcoef[0]*x
    #Affichage des courbes
    if affCourbe:
        plt.clf()
        plt.plot(listeTemp, Isc, '.', label='Expérimentation')
        plt.plot(listeTemp, [Pcalc(x) for x in listeTemp], label="Modélisation")
        plt.title('Courbe Isc = f(T)')
        plt.xlabel("Température (K)")
        plt.ylabel('Isc(G = Gn) (A)')
        plt.legend()
        plt.show()
    return Pcalc(Tn), Pcoef[0]
    
def Calcul_betaVoc(listeV, listeTemp, affCourbe=False):
    """
    Permet de calculer beta_Voc par régression linéaire
    
    Parameters
    ----------
    listeV : list
        Liste contenant les valeurs de V pour les différentes courbes (V)
    listeTemp : list
        Liste contenant les différentes températures correspondant aux différentes températures EN KELVIN
    affCourbe : bool
        Affiche ou non les courbes Voc = f(T) réel et modéliser

    Returns :
        Voc : le courant court circuit à T = 25°C
        beta_voc :  la valeur du coefficent alpha_sc

    """
    Voc = []
    for V in listeV:
        #Determination de Isc pour chacune des listes de I
        Voc.append(np.mean(sorted(V, reverse=True)[:3]))
    Pcoef = np.polyfit(listeTemp, Voc, deg=1) #Calcul de Isc & alpha_sc
    

    def Pcalc(x):
        return Pcoef[1]+Pcoef[0]*x
    #Affichage des courbes
    if affCourbe:
        plt.clf()
        plt.plot(listeTemp, Voc, '.', label='Expérimentation')
        plt.plot(listeTemp, [Pcalc(x) for x in listeTemp], label="Modélisation")
        plt.title('Courbe Voc = f(T)')
        plt.xlabel("Température (K)")
        plt.ylabel('Voc (V)')
        plt.legend()
        plt.show()
    return Pcalc(Tn), Pcoef[0]

def Lin_CourbeIV(V, I, v):
    """Renvoie la valeur de la courbe I/V donné en paramètre pour la tension v donné en linéarisant si besoin"""
    Vp = np.unique(V)
    Ip = [I[list(V).index(u)] for u in Vp]
        
    v1, v2 = sorted(list([[abs(Vp[i]-v), i] for i in range(len(Vp))]))[:2]
    i1= v1[1]
    i2 = v2[1]
    
    pente = (Ip[i1]-Ip[i2])/(Vp[i1]-Vp[i2])
    return Ip[i1]+pente*(v-Vp[i1])
    
def Inter_lin_courbeIV(V, I, Rapp, udeb, umax):
    """
    Renvoie le couple (u, i) du circuit lié à Rapp

    Parameters
    ----------
    V : list
        Liste des tension de la courbe I/V
    I : list
        Liste des courants de la courbe I/V
    Rapp : 
        Resistance apparente
    udeb :
        tension précédente
    umax :
        tension court-circuit

    Retourne : le couple (u,i) dans le circuit
    """
    
    PasMax = 200
    alpha = np.arctan(1/Rapp)
    eps = 0.001
    uM = umax
    um = 0
    u = max(udeb-PasMax, 0)
    jmax = 100
    j = 0
    #Dichotomie
    Pscal = -np.sin(alpha)*u+np.cos(alpha)*Lin_CourbeIV(V, I, u)
    while abs(Pscal) > eps and j < jmax:
        #print(u, Pscal, uM, um, Lin_CourbeIV(V, I, u))
        if Pscal < 0:
            uM = (u+uM)/2
        else:
            um = (u+um)/2
        u = (uM+um)/2
        Pscal = -np.sin(alpha)*u+np.cos(alpha)*Lin_CourbeIV(V, I, u)
        j+=1
    return (u, Lin_CourbeIV(V, I, u))

def DEBOGAGE_afficherInterIV(I, V, Rapp):
    """
    Affiche le point de fonctionnement trouvé entre la caractéristique d'une résistance Rapp et une courbe I/V

    Parameters
    ----------
    I : list
        La liste des courants I associé à celles des tension V
    V : list
        La liste des courants I associé à celles des tension V
    Rapp : float
        Résistance apparente
    """
    plt.clf()
    plt.plot(V, I, '.')
    plt.plot(V, [v/Rapp for v in V])
    res = Inter_lin_courbeIV(V, I, Rapp, 0, max(V))
    plt.plot([res[0]], [res[1]], '.r')
    plt.show()
    print(res)
    
