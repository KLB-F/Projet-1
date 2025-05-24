# -*- coding: utf-8 -*-
"""
Fichier permettant de déterminer le meilleur modèle parmi 2 proposer.

Méthodes : 
    1- On sélectionne les panneaux les plus proches de ceux que l'on veut étudier
    2- On créer des courbes I/V à partir de ces panneaux
    3- On examine quelles modèles performe le mieux
    
Rq : La variances est donnés par la moyenne de l'écart-types à la courbe pour chaque panneaux dans différente conditions
"""

import pvlib
import pvlib.pvsystem as pvsys
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

import Modele as mod

#Constantes
Gn = 1000 #Eclairement solaire nominale (en W/m²)
Tn = 25+273.15 #Température nomniale obtenue dans les conditions STC (en K)
q = 1.6e-19 #Charge élémentaire 
K = 1.38e-23 #Constante de Boltzmann (J/K)
Eg = 1.12*1.60218e-19 #Energie du gap (J)

#Resistance en Série
Rs = 1.43
IncRs = 0.60

Isc_ref = 0.5
Voc_ref = 2

## Creation des données ##

#   # Choix des panneaux #

datasheet = pvsys.retrieve_sam('cecmod') #Importation des donnés

#Choix des 5 paramètrages des panneaux solaire les plus adaptées :
dist_panneau = {}
panneaux_choisit = [[-1, ''] for i in range(5)]

for elm in datasheet: #Calcul de la distance vis-a-vis du panneau à étudier
    dist_panneau[elm] = (abs(Rs-datasheet[elm]['R_s'])+abs(Isc_ref-datasheet[elm]['I_sc_ref'])+abs(Voc_ref-datasheet[elm]['V_oc_ref']))**(1/3)

for elm in datasheet:
    if -1 in [panneaux_choisit[i][0] for i in range(len(panneaux_choisit))]:
        panneaux_choisit[0] = [dist_panneau[elm] ,elm]
        panneaux_choisit = sorted(panneaux_choisit)
    else:
        if panneaux_choisit[-1][0] > dist_panneau[elm] and dist_panneau[elm] > 2.7:
            panneaux_choisit[-1] = [dist_panneau[elm], elm]
            panneaux_choisit = sorted(panneaux_choisit)

panneaux_choisit = [panneaux_choisit[i][1] for i in range(len(panneaux_choisit))]

## Affichage (Optionelle)

"""
G = 1000
T = Tn

#Calcul des paramètres
param_panneaux = [pvsys.calcparams_desoto(G, T, datasheet[elm]['alpha_sc'], datasheet[elm]['a_ref'], datasheet[elm]['I_L_ref'], datasheet[elm]['I_o_ref'], datasheet[elm]['R_sh_ref'], datasheet[elm]['R_s']) for elm in panneaux_choisit]
curve_panneaux = [pvsys.singlediode(panneaux[0], panneaux[1], panneaux[2], panneaux[3], panneaux[4]) for panneaux in param_panneaux]

plt.clf()

for i in range(len(panneaux_choisit)):
    V = np.linspace(0, curve_panneaux[i]['v_oc'], 100)
    I = [pvsys.i_from_v(v, param_panneaux[i][0], param_panneaux[i][1], param_panneaux[i][2], param_panneaux[i][3], param_panneaux[i][4]) for v in V]
    plt.plot(V, I)

plt.show()
"""

# %%
#   # Creation des donnés bruités #

condition_donnes = {"G":[200, 400, 800, 1050], "T":[15, 20, 25, 30]}
#Creation des conditions selon 4 preset : Automne, Printemps, Ete (début), Ete (canicule)

donnes_panneau = dict()
param_p = dict()

for panneau in panneaux_choisit:
    param_p[panneau] = []
    donnes_panneau[panneau] = []
    for i in range(len(condition_donnes['G'])):
        param_p[panneau].append(pvsys.calcparams_desoto(condition_donnes['G'][i], condition_donnes['T'][i], datasheet[panneau]['alpha_sc'], datasheet[panneau]['a_ref'], datasheet[panneau]['I_L_ref'], datasheet[panneau]['I_o_ref'], datasheet[panneau]['R_sh_ref'], datasheet[panneau]['R_s']))
        curve_p = pvsys.singlediode(param_p[panneau][-1][0], param_p[panneau][-1][1], param_p[panneau][-1][2], param_p[panneau][-1][3], param_p[panneau][-1][4])
        V = np.array(list(np.linspace(0, curve_p['v_oc']*2/3, 10))+list(np.linspace(curve_p['v_oc']*2/3, curve_p['v_oc']-0.01, 10)))
        I = [pvsys.i_from_v(v, param_p[panneau][-1][0], param_p[panneau][-1][1], param_p[panneau][-1][2], param_p[panneau][-1][3], param_p[panneau][-1][4]) for v in V]
        
        #Ajout du bruit
        np.random.seed(seed=255) #Pour la reproductibilité
        V = [v+np.random.normal(0, abs(v*0.008/np.sqrt(3)), 1)[0] for v in V]
        I = [i+np.random.normal(0, abs(i*0.02/np.sqrt(3)), 1)[0] for i in I]
        
        donnes_panneau[panneau].append(pvlib.ivtools.utils.rectify_iv_curve(V, I)) #Ajout des donnés après rectification par rectify_iv_curve



## Affichage (Opt)


plt.rcParams['figure.figsize'] = [6*4, 4*3] #On change la taille des plots affiché

plt.clf()

for panneau in panneaux_choisit:
    for i in range(len(condition_donnes['G'])):
        plt.plot(donnes_panneau[panneau][i][0], donnes_panneau[panneau][i][1], label=str(panneau+' | G = '+str(condition_donnes['G'][i])+' | T = '+str(condition_donnes['T'][i])))

plt.legend()
plt.show()

plt.rcParams['figure.figsize'] = [6, 4] #On change la taille des plots affiché

# %%
## Comparaison des modeles ##

# Modele 1 - FitSandiaSample

res_fss_d = {}
res_fss_dist = {}

res_fss_mean = 0

for panneau in panneaux_choisit:
    res_fss_d[panneau] = []
    res_fss_dist[panneau] = 0
    
    P = [list(np.array(donnes_panneau[panneau][i][1])*np.array(donnes_panneau[panneau][i][0])) for i in range(len(donnes_panneau[panneau]))]
    max_pow_point = [P[i].index(max(P[i])) for i in range(len(donnes_panneau[panneau]))]
    temp_dict = {"i":np.array([donnes_panneau[panneau][i][1] for i in range(len(donnes_panneau[panneau]))]),
                 "v":np.array([donnes_panneau[panneau][i][0] for i in range(len(donnes_panneau[panneau]))]),
                 "ee":np.array(condition_donnes['G'][:]),
                 "tc":np.array(condition_donnes['T'][:]),
                 "i_sc":np.array([max(donnes_panneau[panneau][i][1]) for i in range(len(donnes_panneau[panneau]))]),
                 "v_oc":np.array([max(donnes_panneau[panneau][i][0]) for i in range(len(donnes_panneau[panneau]))]),
                 "i_mp":np.array([donnes_panneau[panneau][i][1][max_pow_point[i]] for i in range(len(donnes_panneau[panneau]))]),
                 "v_mp":np.array([donnes_panneau[panneau][i][0][max_pow_point[i]] for i in range(len(donnes_panneau[panneau]))])}
    temp_spec = {"cells_in_series":datasheet[panneau]["N_s"], 
                 "alpha_sc":datasheet[panneau]["alpha_sc"],
                 "beta_voc":datasheet[panneau]['beta_oc'],
                 "gamma_r":datasheet[panneau]['gamma_r']}
    temp_const = {"E0":Gn,"T0":Tn,"k":K,"q":q}
    
    for i in range(len(condition_donnes['G'])):
        try:
            res_fss_d[panneau].append(pvlib.ivtools.sde.fit_sandia_simple(temp_dict['v'][i],temp_dict["i"][i], temp_dict['v_oc'][i], temp_dict['i_sc'][i]))
        except:
            print('Panneau : ', panneau, " a éliminé")
    #Calcul de l'erreur
    for i in range(len(res_fss_d[panneau])):
        
        Ireal = np.array([pvsys.i_from_v(v, param_p[panneau][i][0], param_p[panneau][i][1], param_p[panneau][i][2], param_p[panneau][i][3], param_p[panneau][i][4]) for v in temp_dict['v']])
        Iexp = np.array([pvsys.i_from_v(v, res_fss_d[panneau][i][0], res_fss_d[panneau][i][1], res_fss_d[panneau][i][2], res_fss_d[panneau][i][3], res_fss_d[panneau][i][4]) for v in temp_dict['v'][i]])
        res_fss_dist[panneau] += (np.isnan(Iexp-Ireal).any(axis=0)**2).sum()/(len(np.isnan(Iexp-Ireal).any(axis=0))-1)

    ##Affichage de la courbe obtenue / courbe originale

    def Aff_CourbeFitSSimple(panneau):
        """Affiche les courbe d'un panneau pour le modele CEC"""
        plt.rcParams['figure.figsize'] = [6*2, 4*1.3] #On change la taille des plots affiché
        for i in range(1):
            curve_p = pvsys.singlediode(param_p[panneau][-1][0], param_p[panneau][-1][1], param_p[panneau][-1][2], param_p[panneau][-1][3], param_p[panneau][-1][4])
            V = np.linspace(0, curve_p['v_oc']-0.01, 100)
            Imod = [pvsys.i_from_v(v, res_fss_d[panneau][i][0], res_fss_d[panneau][i][1], res_fss_d[panneau][i][2], res_fss_d[panneau][i][3], res_fss_d[panneau][i][4]) for v in temp_dict['v'][i]]
            plt.plot(temp_dict['v'][i], Imod, label="Courbe sim. n°"+str(i))
            plt.plot(temp_dict['v'][i], [pvsys.i_from_v(v, param_p[panneau][-1][0], param_p[panneau][-1][1], param_p[panneau][-1][2], param_p[panneau][-1][3], param_p[panneau][-1][4]) for v in temp_dict['v'][i]], label=str(panneau+' | G = '+str(condition_donnes['G'][i])+' | T = '+str(condition_donnes['T'][i])))
        plt.legend()
        plt.show()
        plt.rcParams['figure.figsize'] = [6, 4] #On change la taille des plots affiché

print(" Modele FitSandiaSimple; Variance : ", np.mean([res_fss_dist[elm] for elm in res_fss_dist]))
# Modele 2 - FitDesoto

res_cec_r = {}
res_cec_dist = {}

res_des_mean = 0

for panneau in panneaux_choisit:
    res_cec_dist[panneau] = 0
    temp_dict = {"i":np.array([donnes_panneau[panneau][i][1] for i in range(len(donnes_panneau[panneau]))]),
                 "v":np.array([donnes_panneau[panneau][i][0] for i in range(len(donnes_panneau[panneau]))]),
                 "ee":np.array(condition_donnes['G'][:]),
                 "tc":np.array(condition_donnes['T'][:]),
                 "i_sc":np.array([max(donnes_panneau[panneau][i][1]) for i in range(len(donnes_panneau[panneau]))]),
                 "v_oc":np.array([max(donnes_panneau[panneau][i][0]) for i in range(len(donnes_panneau[panneau]))]),
                 "i_mp":np.array([donnes_panneau[panneau][i][1][max_pow_point[i]] for i in range(len(donnes_panneau[panneau]))]),
                 "v_mp":np.array([donnes_panneau[panneau][i][0][max_pow_point[i]] for i in range(len(donnes_panneau[panneau]))])}
    ##On calcul les coefficient de températures nécessaires pour le modèle
    
    Isc, alpha_sc = mod.Calcul_alphasc(temp_dict['i'], temp_dict['tc']+273.15, condition_donnes['G'], affCourbe=False) #On oublie pas de convertir en KELVIN
    Voc, beta_voc = mod.Calcul_betaVoc(temp_dict['v'], temp_dict['tc']+273.15)
    
    ##On calcul vraiment les paramètres
    res_cec_r[panneau] = []
    P = [list(np.array(donnes_panneau[panneau][i][1])*np.array(donnes_panneau[panneau][i][0])) for i in range(len(donnes_panneau[panneau]))]
    max_pow_point = [P[i].index(max(P[i])) for i in range(len(donnes_panneau[panneau]))]
    temp_spec = {"cells_in_series":datasheet[panneau]["N_s"], 
                 "alpha_sc":alpha_sc,
                 "beta_voc":beta_voc}
    temp_const = {"E0":Gn,"T0":Tn,"k":K,"q":q}
    
    typee = datasheet[panneau]["Technology"].split('-')[0]+datasheet[panneau]["Technology"].split('-')[-1]
    for i in range(len(condition_donnes['G'])):
        res_cec_r[panneau].append( pvlib.ivtools.sdm.fit_desoto(temp_dict['v_mp'][i], temp_dict['i_mp'][i], temp_dict['v_oc'][i], temp_dict['i_sc'][i], temp_spec['alpha_sc'], temp_spec['beta_voc'], datasheet[panneau]['N_s'], root_kwargs={'jac':False, 'tol':0.06})[0])
    for i in range(len(res_cec_r[panneau])):
        
        curve_p = pvsys.singlediode(param_p[panneau][-1][0], param_p[panneau][-1][1], param_p[panneau][-1][2], param_p[panneau][-1][3], param_p[panneau][-1][4])
        V = temp_dict['v']
        Ireal = np.array([pvsys.i_from_v(v, param_p[panneau][i][0], param_p[panneau][i][1], param_p[panneau][i][2], param_p[panneau][i][3], param_p[panneau][i][4]) for v in V])
        Iexp = np.array([pvsys.i_from_v(v, res_cec_r[panneau][i]["I_L_ref"]+res_cec_r[panneau][i]['alpha_sc']*(condition_donnes['T'][i]-298)*condition_donnes['G'][i]/Gn, res_cec_r[panneau][i]['I_o_ref'], res_cec_r[panneau][i]['R_s'], res_cec_r[panneau][i]['R_sh_ref'], res_cec_r[panneau][i]['a_ref']) for v in V[i]])
        res_cec_dist[panneau] += (np.isnan(Iexp-Ireal).any(axis=0)**2).sum()/(len(np.isnan(Iexp-Ireal).any(axis=0))-1)
        
    def Aff_CourbeFitCECimple(panneau):
        """Affiche les courbe d'un panneau pour le modele CEC"""
        plt.rcParams['figure.figsize'] = [6*2, 4*1.3] #On change la taille des plots affiché
        for i in range(1,3):
            Imod = [pvsys.i_from_v(v, res_cec_r[panneau][i]["I_L_ref"]+res_cec_r[panneau][i]['alpha_sc']*(condition_donnes['T'][i]-298)*condition_donnes['G'][i]/Gn, res_cec_r[panneau][i]['I_o_ref'], res_cec_r[panneau][i]['R_s'], res_cec_r[panneau][i]['R_sh_ref'], res_cec_r[panneau][i]['a_ref']) for v in donnes_panneau[panneau][i][0]]
            plt.plot(donnes_panneau[panneau][i][0], Imod, label="Courbe sim. n°"+str(i))
            plt.plot(donnes_panneau[panneau][i][0], donnes_panneau[panneau][i][1], label=str(panneau+' | G = '+str(condition_donnes['G'][i])+' | T = '+str(condition_donnes['T'][i])))
        plt.legend()
        plt.show()
        plt.rcParams['figure.figsize'] = [6, 4] #On change la taille des plots affiché

print(" Modele FitDesoto; Variance : ", np.mean([res_cec_dist[elm] for elm in res_cec_dist]))
