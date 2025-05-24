# Projet-1
Projet n°1 : Lié à mon TIPE

Contexte : mon TIPE porte sur la modélisation d'un panneau solaire et de sa commande à l'aide d'un hacheur BOOST

Dépendances : 
  Python : pvlib, numpy, matplotlib, scipy
  Arduino : Wire, floatToString, DFRobot_INA219

Contenue : 

  CommHacheur.py  : 
    Fichier de communication avec un Arduino : l’Arduino envoie des valeurs de tension et de puissance.
    Elles sont stockées dans des listes pour être affichées sous forme de courbes par la suite.

  CommSimulation.py : 
    Fichier de communication avec l’Arduino en vue d’une simulation du comportement du hacheur.

  Modele.py : 
    Fichier contenant toutes les fonctions nécessaires à la modélisation du panneau solaire qui ne sont pas incluses dans pvlib

  ResistanceShunt.py :
    Fichier traçant une courbe I/V et effectuant une régression linéaire sur les 7 derniers points

  TestModele.py : 
    Fichier permettant de déterminer le meilleur modèle parmi 2 proposés.

  Arduino_CommHacheur.ino : 
    Code injecter dans l'arduino lié au fichier CommHacheur.py
    Calcule et applique le rapport cyclique a selon l'algorithme PAO.
    De plus, il prend en entré la tension et la puissance issue d'un multimètre.

  Arduino_CommSimulation.ino : 
    Code injecter dans l'arduino pour fonctionner avec le fichier CommSimulation.py.
    Il renvoie le rapport cyclique a obtenue grâce à l'algorithme PAO et analyse les entrées issuent de python.
  
    
