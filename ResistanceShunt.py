# -*- coding: utf-8 -*-
"""
Fichier traçant une courbe I/V et effectuant une régression linéaire sur les 7 derniers points
"""

import numpy as np
import matplotlib.pyplot as plt

#Resistance Serie
V = [0, 0.86, 1.81, 2.7, 3.4, 3.84, 2.04, 3.7, 4.03, 3.95, 4.04, 4.22, 4.58, 4.6]
I = [0, 0, 0.02, 0.35, 1.01, 1.46, 0.04, 1.31, 1.82, 1.93, 2.02, 2.36, 2.85, 3.06]

plt.clf()
plt.plot(V, I, '.')
plt.xlabel('V (V)')
plt.ylabel('I (A)')
plt.show()

mesV = V[7:]
mesI = I[7:]

Pres = np.polyfit(mesV, mesI, deg=1, full=True)
Pcoef = Pres[0]
Pinc = Pres[1][0]

incertitude = np.sqrt(Pinc)/np.sqrt(3)
print('Resistance Série : ',Pcoef[0],' Incertitude : ',incertitude, ' Ohm')
