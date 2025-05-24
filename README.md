# Projet-1
Projet n°1 : Lié à mon TIPE

Contexte : mon TIPE porte sur la modélisation d'un panneau solaire et de sa commande à l'aide d'un hacheur BOOST

Dépendances : pvlib, numpy, matplotlib, scipy

Contenue : 
  CommHacheur.py  : 
    Fichier de communication avec un Arduino : l’Arduino envoie des valeurs de tension et de puissance.
    Elles sont stockées dans des listes pour être affichées sous forme de courbes par la suite.

  CommSimulation.py : 
    Fichier de communication avec l’Arduino en vue d’une simulation du comportement du hacheur.

  Modele.py : 
    Fichier contenant toutes les fonctions nécessaires à la modélisation du panneau solaire qui ne sont pas incluses dans pvlib

  
