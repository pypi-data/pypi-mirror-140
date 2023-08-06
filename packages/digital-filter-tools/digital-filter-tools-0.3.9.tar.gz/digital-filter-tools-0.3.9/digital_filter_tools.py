# -*- coding: utf8 -*-
# python 3
# (C) Fabrice Sincère

"""An educational module about digital filters

TODO : english translation

Ce module propose des outils pédagogiques pour l'étude des filtres \
numériques :

- passage de l'équation de récurrence aux transformées en z
- passage de l'équation de récurrence à la fonction de transfert en z
- écriture de la fonction de transfert en z en fonction des pôles et zéros
- courbe des réponses impulsionnelle, indicielle, rampe, sinus
- courbe de la réponse à une séquence d'entrée personnalisée
- calcul des zéros et des pôles de la fonction de transfert en z
- diagramme des pôles et zéros
- étude de la stabilité
- courbe de la réponse en fréquence (gain et phase)

Les modules externes suivants sont nécessaires :
- numpy
- matplotlib
- ac-electricity
"""

import sys
import math
import warnings

try:
    import matplotlib.pyplot as plt
except ImportError:
    print("Vous devez installer matplotlib pour tracer les courbes.")
    exit(1)

try:
    import numpy.polynomial.polynomial as nppol
except ImportError:
    print("Vous devez installer le module numpy.polynomial pour \
avoir toutes les fonctionnalités.")
    exit(2)

try:
    from acelectricity import Ratio
except ImportError:
    print("Vous devez installer le module ac-electricity pour \
avoir toutes les fonctionnalités.")
    exit(3)

warnings.simplefilter('default', UserWarning)

__version__ = (0, 3, 9)
__author__ = "Fabrice Sincère <fabrice.sincere@ac-grenoble.fr>"

"""Release History
0.3.7 : add plot_sine_response()
0.2.5 : doctest 2022-01
0.0.1 : initial release 2021-03
"""

if sys.version_info[0] < 3:
    print('You need to run this with Python >=3')
    exit(4)


class FiltreNumerique:
    """Outils pédagogiques pour l'étude des filtres numériques

Ce module propose des outils pédagogiques pour l'étude des filtres \
numériques :

- passage de l'équation de récurrence aux transformées en z
- passage de l'équation de récurrence à la fonction de transfert en z
- écriture de la fonction de transfert en z en fonction des pôles et zéros
- courbe des réponses impulsionnelle, indicielle, rampe, sinus
- courbe de la réponse à une séquence d'entrée personnalisée
- calcul des zéros et des pôles de la fonction de transfert en z
- diagramme des pôles et zéros
- étude de la stabilité
- courbe de la réponse en fréquence (gain et phase)

Les modules externes suivants sont nécessaires :
- numpy
- matplotlib
- ac-electricity

Rappels sur les filtres numériques
==================================

Equation de récurrence
----------------------
x(n) désigne l'entrée et y(n) la sortie.

L'équation de récurrence (algorithme) d'un filtre numérique a la forme \
générale suivante :

a0*y(n) +a1*y(n-1) +a2*y(n-2) + ... = b0*x(n) + b1*x(n-1) + b2*x(n-2) + ...

ou :
a0*y(n) = b0*x(n) + b1*x(n-1) + b2*x(n-2) + ...
          -a1*y(n-1) -a2*y(n-2) -a3*y(n-3) + ...

Par la suite, les paramètres a et b représentent les listes des coefficients \
(réels) de l'équation de récurrence :
a = [a0, a1, a2, ...]  # avec a0 non nul
b = [b0, b1, b2, ...]  # avec au moins un coefficient non nul

Exemple  :
>>> from digital_filter_tools import *
>>> f = FiltreNumerique(a=[2, -0.2], b=[1, 0.5])

Transmittance en z
------------------

On peut aussi définir un filtre numérique par ses pôles et ses zéros.
La transmittance en z s'écrit alors :

          (z-z1).(z-z2)...(z-zm)
H(z) = k. _____________________________
          (z-p1).(z-p2).(z-p3)...(z-pn)

k est un nombre non nul (constante d'amplification)

zeros est la liste des m zéros de la transmittance :
zeros = [z1, z2, ..., zm]
poles est la liste des n pôles de la transmittance :
poles = [p1, p2, ..., pn]
avec les conditions suivantes :
    * n >= m
    * pôles et zéros réels ou complexes par paires conjuguées

Exemple  :
>>> from digital_filter_tools import *
>>> f = FiltreNumerique(k=2, zeros=[0.5], poles=[0, 0.6-0.2j, 0.6+0.2j])
"""

    def __init__(self, fs=1000, **kwargs):
        """Deux manières de créer une instance :

1) à partir des coefficients de l'équation de récurrence
2) à partir des pôles et zéros de la fonction de transfert en z

fs : sampling rate (fréquence d'échantillonnage en Hz)

Exemples :
>>> from digital_filter_tools import *
>>> filtre1 = FiltreNumerique(a=[2, -0.2], b=[1, 0.5])
>>> filtre2 = FiltreNumerique(k=2, zeros=[0.5], poles=[0, 0.6-0.2j, 0.6+0.2j])
"""
        # attributs d'instance / getter
        # self.__a          a
        # self.__a_norm     a_norm
        # self.__b          b
        # self.__b_norm     b_norm
        # self.__poles      poles
        # self.__zeros      zeros
        # self.__k          k
        # self.__jw         jw   # H(jw) transfer function object

        # attributs d'instance / getter / setter
        # self.__fs           sampling rate

        if len(kwargs) == 2 and "a" in kwargs and "b" in kwargs:
            # FiltreNumerique(a, b)
            _a = kwargs["a"]
            _b = kwargs["b"]

            # conversion en float
            self.__a = [float(val) for val in _a]
            self.__b = [float(val) for val in _b]

            # coefficients normalisées
            # une exception est levée en cas de problème sur les coefficients
            self.__a_norm, self.__b_norm = self._normalisation_coeffs()
            # calcul des pôles et zéros
            self.__poles, self.__zeros = self._poles_zeros()

            # un warning est levé en cas de doublons pôles/zéros
            if self.poles_zeros_commun() != []:
                warnings.warn("\nLa fonction de transfert en z possède des pôles et zéros communs")

            # calcul de k
            # plus petit rang coeff b non nul
            for b in self.__b:
                if b != 0.0:
                    break
            self.__k = b/self.__a[0]
            if fs < 0:
                raise ValueError("La fréquence d'échantillonnage doit être\
positive")
            self.__fs = fs
            self.__jw = Ratio.digital_filter(
                fs=self.__fs, b=self.__b_norm, a=self.__a_norm)

        # FiltreNumerique(k, poles, zeros)
        elif (len(kwargs) == 3
              and "poles" in kwargs
              and "zeros" in kwargs
              and "k" in kwargs):

            self.__poles = kwargs["poles"]
            self.__zeros = kwargs["zeros"]

            if len(self.__zeros) > len(self.__poles):
                raise ValueError("La fonction de transfert en z possède \
plus de zéros que de pôles, ce qui n'est pas normal !")

            self.__k = float(kwargs["k"])
            if self.__k == 0.0:
                raise ValueError("k ne doit pas être nul")

            # on vérifie la cohérence des pôles et zéros
            # on calcule les coefficients a et b
            if self.__poles == []:
                _a = [1]
            else:
                _a = list(nppol.polyfromroots(self.__poles))  # complex
            if self.__zeros == []:
                _b = [1]
            else:
                _b = list(nppol.polyfromroots(self.__zeros))

            # on vérifie que les coefficients a et b sont tous réels
            for val in _a:
                # partie imaginaire
                if abs(val.imag) > 1e-8:  # tolérance
                    print("coefficients a", _a)
                    raise ValueError("Les pôles complexes doivent être par \
paire conjuguée")
            for val in _b:
                # partie imaginaire
                if abs(val.imag) > 1e-8:
                    print("coefficients b", _b)
                    raise ValueError("Les zéros complexes doivent être par \
paire conjuguée")

            # passage aux puissances de z négatives
            ordre = max(len(_a), len(_b))-1

            __a = [0.0]*(ordre+1-len(_a))+_a[::-1]  # complex
            __b = [0.0]*(ordre+1-len(_b))+_b[::-1]

            # conversion en float
            self.__a = [val.real for val in __a]
            self.__b = [val.real*self.__k for val in __b]

            # coefficients normalisées
            self.__a_norm, self.__b_norm = self._normalisation_coeffs()
            self.__fs = fs
            self.__jw = Ratio.digital_filter(
                fs=self.__fs, b=self.__b_norm, a=self.__a_norm)

            # un warning est levé en cas de doublons pôles/zéros
            if self.poles_zeros_commun() != []:
                warnings.warn("\nLa fonction de transfert en z possède des pôles et zéros communs")

        else:
            raise ValueError("""Arguments incorrects
a, b attendus
ou k, poles, zeros
""")

    def coeffs_normalises(self):
        """Retourne True si le coefficient a0 de l'équation de récurrence est 1
Retourne False autrement

>>> f = FiltreNumerique(a=[2, -0.2], b=[1, 0.5])
>>> f.coeffs_normalises()
False
"""
        if abs(self.__a[0]-1.0) < 1e-9:  # tolérance
            return True
        return False

    def _normalisation_coeffs(self):
        """Le coefficient a0 de l'équation de récurrence est ramené à 1.
Retourne la liste des coefficients normalisés a et b

Exemple :
>>> f = FiltreNumerique(a=[2, -0.2], b=[1, 0.5])
>>> f._normalisation_coeffs()
([1.0, -0.1], [0.5, 0.25])

Cette méthode est à vocation interne (utilisée par __init__).
Elle permet aussi de contrôler la cohérence des coefficients a et b.
Autrement, depuis l'exterieur, vous avez accès aux attributs a_norm et b_norm :
>>> f = FiltreNumerique(a=[2, -0.2], b=[1, 0.5])
>>> f.a_norm
[1.0, -0.1]
>>> f.b_norm
[0.5, 0.25]
"""
        # on travaille sur des copies
        _a = self.__a.copy()
        _b = self.__b.copy()

        # on vérifie que a0 n'est pas nul
        if self.__a[0] == 0.0:
            raise ValueError("a0 ne doit pas être nul")

        # on enlève les éventuels zéros inutiles en fin de liste
        for i in self.__a[::-1]:
            if i == 0.0:
                _a.pop()  # en enlève le dernier élément
            else:
                break

        for i in self.__b[::-1]:
            if i == 0.0:
                _b.pop()  # en enlève le dernier élément
            else:
                break

        if _b == []:
            raise ValueError("Il faut au moins un coefficient b non nul")

        # normalisation a0 = 1
        if self.__a[0] != 1.0:
            for i, _ in enumerate(_a[:]):
                _a[i] = _a[i]/self.__a[0]
            for i, _ in enumerate(_b[:]):
                _b[i] = _b[i]/self.__a[0]
        return _a, _b

    def filtre_recursif(self):
        """
Retourne True si le filtre est récursif
(a priori réponse impulsionnelle infinie IIR)
False autrement (réponse impulsionnelle finie FIR)

>>> f = FiltreNumerique(a=[2, -0.2], b=[1, 0.5])
>>> f.filtre_recursif()
True
>>> f = FiltreNumerique(a=[1], b=[0.5, 0.5])
>>> f.filtre_recursif()
False
"""
        if len(self.__a_norm) == 1:
            return False
        return True

    def afficher_transmittance_z(self):
        """Affiche la transmittance en z (en puissances de z négatives)
Le coefficient a0 de l'équation de récurrence est ramené à 1.
Remarque : formatage des valeurs avec une précision relative de 1e-9

Exemple :
>>> f = FiltreNumerique(a=[1], b=[0.5, 0.5])
>>> f.afficher_transmittance_z()
H(z) = 0.5 +0.5z⁻¹
>>> f = FiltreNumerique(a=[2, -0.2, 0.01], b=[1, 0.5])
>>> f.afficher_transmittance_z()
        0.5 +0.25z⁻¹
H(z) =  -------------------
        1 -0.1z⁻¹ +0.005z⁻²
"""
        # création numérateur (str)
        num = self._chaine_transmittance_z_partielle(self.__b_norm)

        if self.filtre_recursif():
            # filtre récursif
            # création dénominateur (str)
            denom = self._chaine_transmittance_z_partielle(self.__a_norm)
            taillemax = max(len(denom), len(num))
            debut = "H(z) = "
            print(" "*(len(debut)+1) + num)
            print(debut+" "+"-"*taillemax)
            print(" "*(len(debut)+1) + denom)
        else:
            # filtre non récursif
            print("H(z) = "+num)

    def afficher_transmittance_z_puissance_positive(self):
        """Affiche la transmittance en z (en puissances de z positives)
Le coefficient a0 de l'équation de récurrence est ramené à 1.
Remarque : formatage des valeurs avec une précision relative de 1e-9

Exemple :
>>> f = FiltreNumerique(a=[1], b=[0.5, 0.5])
>>> f.afficher_transmittance_z_puissance_positive()
        0.5z +0.5
H(z) =  ---------
        z
>>> f = FiltreNumerique(a=[2, -0.2, 0.01], b=[1, 0.5])
>>> f.afficher_transmittance_z_puissance_positive()
        0.5z² +0.25z
H(z) =  ---------------
        z² -0.1z +0.005
"""
        ordre = max(len(self.__a_norm), len(self.__b_norm))-1
        # création numérateur (str)
        num = self._chaine_transmittance_z_partielle(self.__b_norm, ordre)
        denom = self._chaine_transmittance_z_partielle(self.__a_norm, ordre)
        taillemax = max(len(denom), len(num))
        debut = "H(z) = "
        print(" "*(len(debut)+1) + num)
        print(debut+" "+"-"*taillemax)
        print(" "*(len(debut)+1) + denom)

    def afficher_transmittance_z_poles_zeros(self):
        """Affiche la transmittance en z sous la forme :
       k(z-z1)(z-z2)...(z-zm)
H(z) = ___________________________
       (z-p1)(z-p2)(z-p3)...(z-pn)

Remarque : formatage des valeurs avec une précision relative de 1e-6

Exemple :
>>> f = FiltreNumerique(a=[2, -0.2, 0.01], b=[1, 0.5])
>>> f.afficher_transmittance_z_poles_zeros()
        0.5(z+0.5).z
H(z) =  ----------------------------
        (z-0.05+0.05j)(z-0.05-0.05j)
"""
        debut = "H(z) = "
        if self.__k == 1.0:
            num = ""
        elif self.__k == -1.0:
            num = "-"
        else:
            num = "{:.6g}".format(self.__k)
        for z in self.__zeros:
            z = _arrondi(z)
            if z != 0.0:
                if z.real == 0.0:
                    num += "(z{:+.6g}j)".format(-(z.imag))
                elif z.imag == 0.0:
                    num += "(z{:+.6g})".format(-z.real)
                else:
                    num += "(z{:+.6g})".format(-z)
            else:
                num += ".z"
        if num == "" or num == "-":
            num += "1"

        denom = ""
        for p in self.__poles:
            p = _arrondi(p)
            if p != 0.0:
                if p.real == 0.0:
                    denom += "(z{:+.6g}j)".format(-(p.imag))
                elif p.imag == 0.0:
                    denom += "(z{:+.6g})".format(-p.real)
                else:
                    denom += "(z{:+.6g})".format(-p)
            else:
                denom += ".z"
        if len(denom) > 0 and denom[0] == ".":
            denom = denom[1:]
        taillemax = max(len(denom), len(num))
        if denom == "":
            # pas de dénominateur
            print(debut+num)
        else:
            print(" "*(len(debut)+1) + num)
            print(debut+" "+"-"*taillemax)
            print(" "*(len(debut)+1) + denom)

    def ordre(self):
        """Retourne l'ordre du filtre.
Dans la fonction de transfert en z avec écriture en puissances négatives,
cela correspond à la plus grande puissance du numérateur ou du dénominateur
(en valeur absolue).

Exemple :
>>> f = FiltreNumerique(a=[2, -0.2, 0.01], b=[1, 0.5])
>>> f.ordre()
2
"""
        return max(len(self.__a_norm), len(self.__b_norm))-1

    def _chaine_transmittance_z_partielle(self, liste_coeffs, puissance=0):
        """
Retourne la transmittance en z sous la forme d'une chaîne de caractères
Il s'agit d'une fonction à usage interne.
Remarque : formatage des nombres avec une précision relative de 1e-6

Exemple :
>>> f = FiltreNumerique(a=[2, -0.2, 0.01], b=[1, 0.5])
>>> f._chaine_transmittance_z_partielle([2, 0.5, -0.2])
'2 +0.5z⁻¹ -0.2z⁻²'
>>> # multiplication par z^3
>>> f._chaine_transmittance_z_partielle([1, 0.5, -0.2], 3)
'z³ +0.5z² -0.2z'
"""
        res = ""
        flag_debut = True  # pas de "+" devant le premier nombre positif affiché
        for i, val in enumerate(liste_coeffs):
            i -= puissance  # z^i
            # coefficients non nuls
            if val != 0.0:
                if i == 0:  # z^0
                    if flag_debut:
                        res += "{:.6g} ".format(val)
                    else:
                        res += "{:+.6g} ".format(val)
                elif i == -1:  # z^1
                    if val == 1.0:
                        if flag_debut:
                            res += "z "
                        else:
                            res += "+z "
                    elif val == -1.0:
                        res += "-z "
                    else:
                        if flag_debut:
                            res += "{:.6g}z ".format(val)
                        else:
                            res += "{:+.6g}z ".format(val)
                else:
                    if val == 1.0:
                        if flag_debut:
                            res += "z{} ".format(_sup(-i))
                        else:
                            res += "+z{} ".format(_sup(-i))
                    elif val == -1.0:
                        res += "-z{} ".format(_sup(-i))
                    else:
                        if flag_debut:
                            res += "{:.6g}z{} ".format(val, _sup(-i))
                        else:
                            res += "{:+.6g}z{} ".format(val, _sup(-i))
                flag_debut = False
        # on enlève l'espace de fin
        return res[:-1]

    def afficher_transformee_en_z(self):
        """Affiche la transformée en z de l'équation de récurrence.
Remarque : formatage des nombres avec une précision relative de 1e-6

Exemple :
>>> f = FiltreNumerique(a=[2], b=[0.5, 0.25])
>>> f.afficher_transformee_en_z()
2*Y(z) = 0.5*X(z) +0.25*X(z)z⁻¹
>>> f = FiltreNumerique(a=[1, -0.1], b=[0.5, 0.25])
>>> f.afficher_transformee_en_z()
Y(z) = 0.5*X(z) +0.25*X(z)z⁻¹
       +0.1*Y(z)z⁻¹
"""
        if self.__a[0] == 0.0:
            raise ValueError("a0 ne peut pas être nul")
        if self.__a[0] == 1.0:
            res = "Y(z) = "
        elif self.__a[0] == -1.0:
            res = "-Y(z) = "
        else:
            res = "{:.6g}*Y(z) = ".format(self.__a[0])

        longueur = len(res)
        flag_debut = True  # pas de "+" devant le premier nombre positif affiché
        for i, val in enumerate(self.__b):
            if val != 0.0:
                if i == 0:  # X(z)
                    if val == 1.0:
                        res += "X(z) "
                    elif val == -1.0:
                        res += "-X(z) "
                    else:
                        res += "{:.6g}*X(z) ".format(val)
                else:
                    if val == 1.0:
                        if flag_debut:
                            res += "X(z)z{} ".format(_sup(-i))
                        else:
                            res += "+X(z)z{} ".format(_sup(-i))
                    elif val == -1.0:
                        res += "-X(z)z{} ".format(_sup(-i))
                    else:
                        if flag_debut:
                            res += "{:.6g}*X(z)z{} ".format(val, _sup(-i))
                        else:
                            res += "{:+.6g}*X(z)z{} ".format(val, _sup(-i))
                flag_debut = False

        if self.filtre_recursif():
            res += "\n" + " "*longueur
            for i, val in enumerate(self.__a[1:]):
                val = -val
                if val != 0.0:
                    if val == 1.0:
                        res += "+Y(z)z{} ".format(_sup(-i-1))
                    elif val == -1.0:
                        res += "-Y(z)z{} ".format(_sup(-i-1))
                    else:
                        res += "{:+.6g}*Y(z)z{} ".format(val, _sup(-i-1))
        # on enlève l'espace de fin
        print(res[:-1])

    def afficher_transformee_en_z_normalisee(self):
        """Affiche la transformée en z de l'équation de récurrence.
Le coefficient a0 est ramené à 1.
Remarque : formatage des nombres avec une précision relative de 1e-6

Exemple :
>>> f = FiltreNumerique(a=[2], b=[0.5, 0.25])
>>> f.afficher_transformee_en_z_normalisee()
Y(z) = 0.25*X(z) +0.125*X(z)z⁻¹
>>> f = FiltreNumerique(a=[1, -0.1], b=[0.5, 0.25])
>>> f.afficher_transformee_en_z_normalisee()
Y(z) = 0.5*X(z) +0.25*X(z)z⁻¹
       +0.1*Y(z)z⁻¹
"""
        res = "Y(z) = "
        longueur = len(res)
        flag_debut = True  # pas de "+" devant le premier nombre positif affiché
        for i, val in enumerate(self.__b_norm):
            if val != 0.0:
                if i == 0:  # X(z)
                    if val == 1.0:
                        res += "X(z) "
                    elif val == -1.0:
                        res += "-X(z) "
                    else:
                        res += "{:.6g}*X(z) ".format(val)
                else:
                    if val == 1.0:
                        if flag_debut:
                            res += "X(z)z{} ".format(_sup(-i))
                        else:
                            res += "+X(z)z{} ".format(_sup(-i))
                    elif val == -1.0:
                        res += "-X(z)z{} ".format(_sup(-i))
                    else:
                        if flag_debut:
                            res += "{:.6g}*X(z)z{} ".format(val, _sup(-i))
                        else:
                            res += "{:+.6g}*X(z)z{} ".format(val, _sup(-i))
                flag_debut = False

        if self.filtre_recursif():
            res += "\n" + " "*longueur
            for i, val in enumerate(self.__a_norm[1:]):
                val = -val
                if val != 0.0:
                    if val == 1.0:
                        res += "+Y(z)z{} ".format(_sup(-i-1))
                    elif val == -1.0:
                        res += "-Y(z)z{} ".format(_sup(-i-1))
                    else:
                        res += "{:+}*Y(z)z{} ".format(val, _sup(-i-1))
        # on enlève l'espace de fin
        print(res[:-1])

    def afficher_equation_recurrence(self):
        """Affiche l'équation de récurrence.
Remarque : formatage des nombres avec une précision relative de 1e-6

Exemple :
>>> f = FiltreNumerique(a=[2], b=[0.5, 0.25])
>>> f.afficher_equation_recurrence()
2*y(n) = 0.5*x(n) +0.25*x(n-1)
>>> f = FiltreNumerique(a=[1, -0.1], b=[0.5, 0.25])
>>> f.afficher_equation_recurrence()
y(n) = 0.5*x(n) +0.25*x(n-1)
       +0.1*y(n-1)
"""
        res = ""
        if self.__a[0] == 1.0:
            res += "y(n) = "
        else:
            res += "{:.6g}*y(n) = ".format(self.__a[0])
        longueur = len(res)
        flag_debut = True  # pas de "+" devant le premier nombre positif affiché
        for i, val in enumerate(self.__b):
            if val != 0.0:
                if i == 0:  # x(n)
                    if val == 1.0:
                        res += "x(n) "
                    elif val == -1.0:
                        res += "-x(n) "
                    else:
                        res += "{:.6g}*x(n) ".format(val)
                else:
                    if val == 1.0:
                        if flag_debut:
                            res += "x(n{}) ".format(-i)
                        else:
                            res += "+x(n{}) ".format(-i)
                    elif val == -1.0:
                        res += "-x(n{}) ".format(-i)
                    else:
                        if flag_debut:
                            res += "{:.6g}*x(n{}) ".format(val, -i)
                        else:
                            res += "{:+.6g}*x(n{}) ".format(val, -i)
                flag_debut = False

        if self.filtre_recursif():
            res += "\n" + " "*longueur
            for i, val in enumerate(self.__a[1:]):
                val = -val
                if val != 0.0:
                    if val == 1.0:
                        res += "+y(n{}) ".format(-i-1)
                    elif val == -1.0:
                        res += "-y(n{}) ".format(-i-1)
                    else:
                        res += "{:+.6g}*y(n{}) ".format(val, -i-1)
        # on enlève l'espace de fin
        print(res[:-1])

    def afficher_equation_recurrence_normalisee(self):
        """Affiche l'équation de récurrence.
Le coefficient a0 est ramené à 1.
Remarque : formatage des nombres avec une précision relative de 1e-6

Exemple :
>>> f = FiltreNumerique(a=[2], b=[0.5, 0.25])
>>> f.afficher_equation_recurrence_normalisee()
y(n) = 0.25*x(n) +0.125*x(n-1)
>>> f = FiltreNumerique(a=[1, -0.1], b=[0.5, 0.25])
>>> f.afficher_equation_recurrence_normalisee()
y(n) = 0.5*x(n) +0.25*x(n-1)
       +0.1*y(n-1)
"""
        res = "y(n) = "
        longueur = len(res)
        flag_debut = True  # pas de "+" devant le premier nombre positif affiché
        for i, val in enumerate(self.__b_norm):
            if val != 0.0:
                if i == 0:  # x(n)
                    if val == 1.0:
                        res += "x(n) "
                    elif val == -1.0:
                        res += "-x(n) "
                    else:
                        res += "{:.6g}*x(n) ".format(val)
                else:
                    if val == 1.0:
                        if flag_debut:
                            res += "x(n{}) ".format(-i)
                        else:
                            res += "+x(n{}) ".format(-i)
                    elif val == -1.0:
                        res += "-x(n{}) ".format(-i)
                    else:
                        if flag_debut:
                            res += "{:.6g}*x(n{}) ".format(val, -i)
                        else:
                            res += "{:+.6g}*x(n{}) ".format(val, -i)
                flag_debut = False

        if self.filtre_recursif():
            res += "\n" + " "*longueur
            for i, val in enumerate(self.__a_norm[1:]):
                val = -val
                if val != 0.0:
                    if val == 1.0:
                        res += "+y(n{}) ".format(-i-1)
                    elif val == -1.0:
                        res += "-y(n{}) ".format(-i-1)
                    else:
                        res += "{:+.6g}*y(n{}) ".format(val, -i-1)
        # on enlève l'espace de fin
        print(res[:-1])

    def tracer_reponse_personnalisee(self, xn, ndebut=-2,
                                     titre='Réponse personnalisée'):
        """Calcule et trace les séquences d'entrée x(n) et de sortie y(n)
xn : séquence d'entrée (type list) x(0), x(1), x(2)...
ndebut : indice du premier échantillon à dessiner (entier <= 0)

Retourne le tuple xn, yn (liste xn et liste yn avec n >= 0)

Exemple :
>>> f = FiltreNumerique(a=[1], b=[0.25, 0.25])
>>> f.tracer_reponse_personnalisee([1, 1, 1, 0, 0, 0], -1)
-1 0 0.0
0 1 0.25
1 1 0.5
2 1 0.5
3 0 0.25
4 0 0.0
5 0 0.0
([1, 1, 1, 0, 0, 0], [0.25, 0.5, 0.5, 0.25, 0.0, 0.0])
"""
        ndebut = int(ndebut)
        if ndebut > 0:
            raise ValueError("ndebut doit être <= 0")

        nn = range(ndebut, len(xn))
        # pour n < 0 : on ajoute les zéros
        xn0 = [0]*(-ndebut)+xn
        # séquence de sortie
        yn0 = list()

        for n, _ in enumerate(xn0):
            y = 0
            for i, bi in enumerate(self.__b_norm):
                if n-i >= 0:
                    y += bi*xn0[n-i]
            for i, ai in enumerate(self.__a_norm):
                if i >= 1 and n-i >= 0:
                    y -= ai*yn0[n-i]
            yn0.append(y)

        for i in nn:
            print(i, xn0[i-ndebut], yn0[i-ndebut])

        fig, ax = plt.subplots()
        ax.set_xlabel('n')
        plt.plot(nn, yn0, 'o', color='blue', label='y(n)')
        plt.plot(nn, xn0, '*', color='red', label='x(n)')

        plt.legend()
        plt.grid()
        plt.title(titre)
        fig.tight_layout()
        plt.show()
        return xn, yn0[-len(xn):]

    def tracer_reponse_indicielle(self, k=1, ndebut=-2, nfin=20,
                                  titre="Réponse indicielle"):
        """Calcule et trace la réponse indicielle
Retourne le tuple xn, yn (liste xn et liste yn avec n >= 0)
Exemple :
>>> f = FiltreNumerique(a=[1, -0.5], b=[0.25, 0.25])
>>> f.tracer_reponse_indicielle(5, -2, 50)
-2 0 0.0
-1 0 0.0
0 5 1.25
1 5 3.125
...
"""
        xn = [k]*(nfin+1)
        return self.tracer_reponse_personnalisee(xn, ndebut=ndebut, titre=titre)

    def tracer_reponse_sinus(self, f=100, k=1, ndebut=-2, nfin=20,
                             titre="Réponse harmonique"):
        """Calcule et trace la réponse à un sinus de fréquence f (en Hz)
Retourne le tuple xn, yn (liste xn et liste yn avec n >= 0)
Exemple :
>>> f = FiltreNumerique(a=[1, -0.5], b=[0.25, 0.25])
>>> f.tracer_reponse_sinus(f=50, ndebut=-2, nfin=40)
-2 0 0.0
-1 0 0.0
0 0.0 0.0
1 0.309016... 0.0772542...
...
"""
        xn = [k*math.sin(2*math.pi*f*i/self.__fs) for i in range(nfin+1)]
        return self.tracer_reponse_personnalisee(xn, ndebut=ndebut, titre=titre)

    def tracer_reponse_impulsionnelle(self, k=1, ndebut=-2, nfin=20,
                                      titre="Réponse impulsionnelle"):
        """Calcule et trace la réponse impulsionnelle
Retourne le tuple xn, yn (liste xn et liste yn avec n >= 0)"""
        xn = [k]+[0]*nfin
        return self.tracer_reponse_personnalisee(xn, ndebut=ndebut, titre=titre)

    def tracer_reponse_rampe(self, k=1, ndebut=-2, nfin=20,
                             titre="Réponse à une rampe"):
        """Calcule et trace la réponse à une rampe
Retourne le tuple xn, yn (liste xn et liste yn avec n >= 0)"""
        xn = [k*i for i in range(nfin+1)]
        return self.tracer_reponse_personnalisee(xn, ndebut=ndebut, titre=titre)

    def tracer_diagramme_poles_zeros(self):
        """Trace le diagramme des pôles et zéros dans le plan complexe,
ainsi que le disque unité.
Retourne le tuple poles, zeros (listes des pôles et zéros) avec une tolérance
de 1e-9

Exemple :
>>> f = FiltreNumerique(a=[1, -1], b=[0.25, 0, 0, 0, -0.25])
>>> f.tracer_diagramme_poles_zeros()
([0.0, 0.0, 0.0, 1.0], [-1.0, (-0-1j), 1j, 1.0])
"""
        # coordonnées des pôles
        p_real = []
        p_imag = []
        for p in self.__poles:
            p_real.append(p.real)
            p_imag.append(p.imag)
        z_real = []
        z_imag = []
        for z in self.__zeros:
            z_real.append(z.real)
            z_imag.append(z.imag)

        nb_poles = len(self.__poles)
        nb_zeros = len(self.__zeros)

        fig, ax = plt.subplots()

        legend_zeros = '{} zero{}'.format(nb_zeros, 's' if nb_zeros > 1 else '')

        zeros0 = []
        for z in self.__zeros:
            zeros0.append(_arrondi_pz(z))  # str

        zeros1 = set(zeros0)  # sans doublons

        for z in zeros1:
            counter = zeros0.count(z)
            if counter > 1:
                legend_zeros += "\n{} [{}]".format(_arrondi(complex(z)),
                                                   counter)

        legend_poles = '{} pole{}'.format(nb_poles, 's' if nb_poles > 1 else '')

        poles0 = []
        for p in self.__poles:
            poles0.append(_arrondi_pz(p))  # str

        poles1 = set(poles0)  # sans doublons

        for p in poles1:
            counter = poles0.count(p)
            if counter > 1:
                legend_poles += "\n{} [{}]".format(_arrondi(complex(p)),
                                                   counter)

        plt.plot(z_real, z_imag, 'o', color='blue',
                 label=legend_zeros)
        plt.plot(p_real, p_imag, 'x', color='red',
                 label=legend_poles)
        # cercle unité
        circle = plt.Circle((0, 0), 1.0, color='#dddddd')
        ax.add_patch(circle)

        ax.set_xlim([min([-1]+p_real+z_real)-0.1, max([1]+p_real+z_real)+0.1])
        ax.set_ylim([min([-1]+p_imag+z_imag)-0.1, max([1]+p_imag+z_imag)+0.1])
        ax.set_ylabel('Imaginary axis')
        ax.set_xlabel('Real axis')
        plt.gca().set_aspect('equal')  # même échelle sur les deux axes
        plt.legend()
        plt.grid()
        plt.title("Poles/zeros diagram")
        fig.tight_layout()
        plt.show()

        poles = []
        for val in self.__poles:
            poles.append(_arrondi(val))

        zeros = []
        for val in self.__zeros:
            zeros.append(_arrondi(val))
        return poles, zeros

    def _poles_zeros(self):
        """Retourne la liste des pôles et zéros de la fonction de transfert en z
(écriture avec puissances positives).
Calcul à partir des coefficients a et b de l'équation de récurrence.
"""
        ordre = max(len(self.__a_norm), len(self.__b_norm))-1
        # polynôme en puissance de z positive
        _ap = [0]*(ordre-len(self.__a_norm)+1) + self.__a_norm[::-1]
        _bp = [0]*(ordre-len(self.__b_norm)+1) + self.__b_norm[::-1]

        # dénominateur en puissance de z positive
        # find the roots of a polynomial
        poles = nppol.polyroots(_ap)  # numpy.ndarray
        # zéros du numérateur
        zeros = nppol.polyroots(_bp)  # numpy.ndarray
        return list(poles), list(zeros)

    def poles_zeros_commun(self):
        """Retourne la liste des pôles et zéros communs
(avec une tolérance de 1e-9)

Exemple :
moyenne glissante sur 4 échantillons
>>> f = FiltreNumerique(a=[1, -1], b=[0.25, 0, 0, 0, -0.25])
>>> f.poles_zeros_commun()
[1.0]
"""
        # précision 1e-9 relatif
        # on supprime l'une des parties réel/imag négligeable
        poles0 = []
        for p in self.__poles:
            poles0.append(_arrondi_pz(p))  # str

        zeros0 = []
        for z in self.__zeros:
            zeros0.append(_arrondi_pz(z))  # str

        # on cherche les valeurs communes aux 2 listes (sans doublons)
        commun = list(set(zeros0).intersection(set(poles0)))   # str

        if commun == []:
            return []
        else:
            res = []
            # Pôles et zéros communs
            for c in commun:
                nb = complex(c)
                for _ in range(min(zeros0.count(c), poles0.count(c))):
                    res.append(_arrondi(nb))
            return res

    def stable(self):
        """
Return True if the filter is stable
(all the poles are inside the unit circle in the z plane)
Return False if the filter is unstable

>>> f = DigitalFilter(a=[1, -1], b=[0.25, 0, 0, 0, -0.25])
>>> f.stable()
True

Détermine la stabilité du filtre numérique en se basant sur les pôles \
de la fonction de transfert en z.
Un filtre est stable car tous les pôles ont un module <= 1

retourne True si le filtre est stable
retourne False si le filtre est instable

>>> f = FiltreNumerique(a=[1, -1], b=[0.25, 0, 0, 0, -0.25])
>>> f.stable()
True
"""
        if self.filtre_recursif() is False:
            # filtre non récursif donc stable
            return True
        else:
            # filtre récursif
            # module des pôles
            eps = 1e-6  # marge précision calcul
            if(max([abs(p) for p in self.__poles]) > 1+eps):
                # filtre instable car il possède des pôles de module > 1
                return False
            # filtre stable car tous les pôles ont un module <= 1
            return True

    def afficher_bilan_stabilite(self):
        """Affiche le bilan de stabilité du filtre

Exemple :
>>> f = FiltreNumerique(a=[2], b=[1,-1])
>>> f.afficher_bilan_stabilite()
Etude de la stabilité
---------------------
Le filtre est non récursif donc il est stable.

>>> f = FiltreNumerique(a=[1, -0.1, 0.02], b=[0.5, 0.25])
>>> f.afficher_bilan_stabilite()
Etude de la stabilité
---------------------
Le filtre est récursif.
La transmittance en z possède 2 pôles.
En module :
|0.05-0.132288j| = 0.141421
|0.05+0.132288j| = 0.141421
Filtre stable car tous les pôles ont un module <= 1

>>> f = FiltreNumerique(a=[1, 2, -0.01], b=[0.5])
>>> f.afficher_bilan_stabilite()
Etude de la stabilité
---------------------
Le filtre est récursif.
La transmittance en z possède 2 pôles.
En module :
|-2.00499| = 2.00499
|0.00498756| = 0.00498756
Filtre instable car il possède des pôles de module > 1

"""
        bilan = """
Etude de la stabilité
---------------------
"""
        if self.filtre_recursif() is False:
            bilan += "Le filtre est non récursif donc il est stable.\n"
        else:
            bilan += "Le filtre est récursif.\n"
            bilan += """La transmittance en z possède {} pôle{}.
En module :
""".format(len(self.__poles), "s" if len(self.__poles) > 1 else "")

            # module des pôles
            for p in self.__poles:
                bilan += "|{:.6g}| = {:.6g}\n".format(p, abs(p))

            eps = 1e-9  # marge précision calcul
            if(max([abs(p) for p in self.__poles]) > 1+eps):
                bilan += "Filtre instable car il possède des pôles de \
module > 1"
            else:
                bilan += "Filtre stable car tous les pôles ont un module <= 1"
        print(bilan)

    def tracer_reponse_en_frequence(self, magnitude_unit='linear'):
        """Trace la réponse en fréquence (gain et phase) du filtre.
Retourne fréquences, amplitudes, déphasages (°) (array)

magnitude_unit : 'dB' ou 'linear'

>>> f = FiltreNumerique(a=[1], b=[0.5, 0.5])
>>> f.fs = 5000
>>> f.tracer_reponse_en_frequence(magnitude_unit='dB')
Plot figure 1 FIR digital filter (fs=5000 Hz)
5 -4.28632e-05 -0.18
5.5 -5.18645e-05 -0.198
...
"""
        if self.filtre_recursif():
            # filtre récursif
            title = 'IIR digital filter (fs={} Hz)'.format(self.__fs)
        else:
            title = 'FIR digital filter (fs={} Hz)'.format(self.__fs)

        # fig, ax1, ax2, l1, l2
        # (matplotlib Figure, AxesSubplot (magnitude/dB), AxesSubplot(phase),
        # Line2D (ax1 plot datas), Line2D (ax2 plot datas)
        xmin = 0.001*self.__fs
        xmax = 0.499*self.__fs
        n = 4981
        if magnitude_unit == 'linear':
            fig, ax1, ax2, l1, l2 = self.__jw.bode(
                xmin=xmin, xmax=xmax, xscale='linear',
                magnitude_unit='default', title=title, n=n)
            plt.show()
            # fréquences, magnitudes, déphasages(°)
            return l1.get_data()[0], l1.get_data()[1], l2.get_data()[1]
        else:
            # magnitude_unit 'dB'
            fig, ax1, ax2, l1, l2 = self.__jw.bode(
                xmin=xmin, xmax=xmax, xscale='linear', title=title, n=n)
            plt.show()
            # fréquences, magnitudes, déphasages(°)
            return l1.get_data()[0], l1.get_data()[1], l2.get_data()[1]

    @property
    def a(self):
        """Return the coefficients of the outputs
>>> f = DigitalFilter(a=[2, -0.2], b=[1, 0.5])
>>> f.a
[2.0, -0.2]

Retourne la liste des coefficients a de l'équation de récurrence
>>> f = FiltreNumerique(a=[2, -0.2], b=[1, 0.5])
>>> f.a
[2.0, -0.2]
"""
        # getter
        # lecture seule
        return self.__a

    @property
    def b(self):
        """Return the coefficients of the inputs

Retourne la liste des coefficients b de l'équation de récurrence"""
        # getter
        return self.__b

    @property
    def a_norm(self):
        """Return the coefficients of the outputs (normalized with a0=1)

Retourne la liste des coefficients a (normalisés avec a0=1)"""
        # getter
        return self.__a_norm

    @property
    def b_norm(self):
        """Return the coefficients of the inputs (normalized with a0=1)

Retourne la liste des coefficients b (normalisés avec a0=1)"""
        # getter
        return self.__b_norm

    @property
    def poles(self):
        """Return the poles [p1, p2, ...] of the Z-transfer function :
          (z-z1).(z-z2)...(z-zm)
H(z) = k. _____________________________
          (z-p1).(z-p2).(z-p3)...(z-pn)

>>> f = DigitalFilter(a=[2, -0.2], b=[1, 0.5])
>>> f.poles
[0.1]

Retourne la liste des pôles [p1, p2, ...] de la transmittance en z
>>> f = FiltreNumerique(a=[2, -0.2], b=[1, 0.5])
>>> f.poles
[0.1]
"""
        # getter
        return self.__poles

    @property
    def zeros(self):
        """Return the zeros [z1, z2, ...] of the Z-transfer function :
          (z-z1).(z-z2)...(z-zm)
H(z) = k. _____________________________
          (z-p1).(z-p2).(z-p3)...(z-pn)

Retourne la liste des zéros [z1, z2, ...] de la transmittance en z :
"""
        # getter
        return self.__zeros

    @property
    def k(self):
        """Return the gain factor k of the Z-transfer function :
          (z-z1).(z-z2)...(z-zm)
H(z) = k. _____________________________
          (z-p1).(z-p2).(z-p3)...(z-pn)

Retourne la constante d'amplification k de la transmittance en z :
"""
        # getter
        return self.__k

    @property
    def hw(self):
        """Fonction de transfert complexe H(jw)

Exemple :
>>> filtre = FiltreNumerique(a=[2, -0.2], b=[1, 0.5])
>>> filtre.fs = 10000
>>> H = filtre.hw
>>> # help(H)
>>> H.properties(150)  # transmittance à 150 Hz
Frequency (Hz) : 150
Angular frequency (rad/s) : 942.478
Complex value : 0.831327-0.0348168j
Magnitude : 0.832055
Magnitude (dB) : -1.596956...
Phase (degrees) : -2.3982
Phase (radians) : -0.0418565
>>> H.db(150)  # gain en dB à 150 Hz
-1.596956...
>>> H.phase_deg(150)  # déphasage en degrés à 150 Hz
-2.3982...
"""
        # getter
        return self.__jw

    @property
    def fs(self):
        """Get or set sampling rate (Hz)

>>> f = FiltreNumerique(a=[2, -0.2], b=[1, 0.5])
>>> f.fs  # default
1000
>>> f.fs = 5000
>>> f.fs
5000
"""
        # getter
        return self.__fs

    @fs.setter
    def fs(self, value):
        if value < 0:
            raise ValueError("La fréquence d'échantillonnage doit être\
positive")
        self.__fs = value
        self.__jw = Ratio.digital_filter(
            fs=self.__fs, b=self.__b_norm, a=self.__a_norm)


# english translation
class DigitalFilter(FiltreNumerique):
    """  TODO : english translation  """

    def __init__(self, fs=1000, **kwargs):
        """  TODO : english translation

>>> from digital_filter_tools import *
>>> filter1 = DigitalFilter(a=[2, -0.2], b=[1, 0.5])
>>> filter2 = DigitalFilter(k=2, zeros=[0.5], poles=[0, 0.6-0.2j, 0.6+0.2j])
"""
        # FiltreNumerique.__init__(self, fs, **kwargs)
        super().__init__(fs, **kwargs)

    def plot_frequency_response(self, magnitude_unit='dB'):
        """Plot the frequency response (gain and phase).
Return frequency, magnitude, phase (°) (tuple of arrays)

magnitude_unit : 'dB' or 'linear'

>>> f = DigitalFilter(a=[1], b=[0.25]*4)
>>> f.fs = 10000
>>> f.plot_frequency_response(magnitude_unit='linear')
Plot figure 1 FIR digital filter (fs=10000 Hz)
10 0.999975 -0.54
11 0.99997 -0.594
...
"""
        return self.tracer_reponse_en_frequence(magnitude_unit=magnitude_unit)

    def plot_poles_zeros(self):
        """Plot poles/zeros diagram and the unit circle in the z plane.
Return poles, zeros (tuple of lists)

>>> f = DigitalFilter(a=[1, -1], b=[0.25, 0, 0, 0, -0.25])
>>> f.plot_poles_zeros()
([0.0, 0.0, 0.0, 1.0], [-1.0, (-0-1j), 1j, 1.0])
"""
        return self.tracer_diagramme_poles_zeros()

    def plot_pulse_response(self, k=1, nbegin=-2, nend=20,
                            title="Pulse response"):
        """Plot pulse response
Return inputs, outputs

>>> f = DigitalFilter(a=[1, -0.5], b=[0.25, 0.25])
>>> f.plot_pulse_response(5, -2, 50)
-2 0 0.0
-1 0 0.0
0 5 1.25
1 0 1.875
...
"""
        return self.tracer_reponse_impulsionnelle(k=k, ndebut=nbegin, nfin=nend,
                                                  titre=title)

    def plot_step_response(self, k=1, nbegin=-2, nend=20,
                           title="Step response"):
        """Plot step response
Return inputs, outputs"""
        return self.tracer_reponse_indicielle(k=k, ndebut=nbegin, nfin=nend,
                                              titre=title)

    def plot_sine_response(self, f=100, k=1, nbegin=-2, nend=20,
                           title="Sine response"):
        """Plot sine response
Return inputs, outputs
f : frequency (Hz)

>>> f = DigitalFilter(a=[1, -0.5], b=[0.25, 0.25])
>>> f.plot_sine_response(f=50, nbegin=-2, nend=40)
-2 0 0.0
-1 0 0.0
0 0.0 0.0
1 0.309016... 0.0772542...
...
"""
        return self.tracer_reponse_sinus(f=f, k=k, ndebut=nbegin, nfin=nend,
                                         titre=title)

    def plot_ramp_response(self, k=1, nbegin=-2, nend=20,
                           title="Ramp response"):
        """Plot ramp response
Return inputs, outputs"""
        return self.tracer_reponse_rampe(k=k, ndebut=nbegin, nfin=nend,
                                         titre=title)

    def plot_user_response(self, xn, nbegin=-2, title='User response'):
        """Plot user-defined response
Return inputs, outputs

>>> f = DigitalFilter(a=[1], b=[0.25, 0.25])
>>> f.plot_user_response([1, 1, 1, 0, 0, 0], -1)
-1 0 0.0
0 1 0.25
1 1 0.5
2 1 0.5
3 0 0.25
4 0 0.0
5 0 0.0
([1, 1, 1, 0, 0, 0], [0.25, 0.5, 0.5, 0.25, 0.0, 0.0])
"""
        return self.tracer_reponse_personnalisee(xn=xn, ndebut=nbegin,
                                                 titre=title)

    def print_stability_results(self):
        """  TODO : english translation """
        self.afficher_bilan_stabilite()

    def print_z_transfer_function(self):
        """Print Z-transfer function (negative z power)

>>> f = DigitalFilter(a=[1], b=[0.5, 0.5])
>>> f.print_z_transfer_function()
H(z) = 0.5 +0.5z⁻¹
>>> f = DigitalFilter(a=[2, -0.2, 0.01], b=[1, 0.5])
>>> f.print_z_transfer_function()
        0.5 +0.25z⁻¹
H(z) =  -------------------
        1 -0.1z⁻¹ +0.005z⁻²
"""
        self.afficher_transmittance_z()

    def print_z_transfer_function_poles_zeros(self):
        """  TODO : english translation

>>> f = DigitalFilter(a=[2, -0.2, 0.01], b=[1, 0.5])
>>> f.print_z_transfer_function_poles_zeros()
        0.5(z+0.5).z
H(z) =  ----------------------------
        (z-0.05+0.05j)(z-0.05-0.05j)
"""
        self.afficher_transmittance_z_poles_zeros()

    def print_z_transfer_function_positive_power(self):
        """Print Z-transfer function (positive z power)

>>> f = DigitalFilter(a=[1], b=[0.5, 0.5])
>>> f.print_z_transfer_function_positive_power()
        0.5z +0.5
H(z) =  ---------
        z
>>> f = DigitalFilter(a=[2, -0.2, 0.01], b=[1, 0.5])
>>> f.print_z_transfer_function_positive_power()
        0.5z² +0.25z
H(z) =  ---------------
        z² -0.1z +0.005
"""
        self.afficher_transmittance_z_puissance_positive()

    def print_z_transform(self):
        """Print Z-transform

>>> f = DigitalFilter(a=[2], b=[0.5, 0.25])
>>> f.print_z_transform()
2*Y(z) = 0.5*X(z) +0.25*X(z)z⁻¹
>>> f = DigitalFilter(a=[1, -0.1], b=[0.5, 0.25])
>>> f.print_z_transform()
Y(z) = 0.5*X(z) +0.25*X(z)z⁻¹
       +0.1*Y(z)z⁻¹
"""
        self.afficher_transformee_en_z()

    def print_z_transform_normalized(self):
        """Print Z-transform (normalized with a0=1)

>>> f = DigitalFilter(a=[2], b=[0.5, 0.25])
>>> f.print_z_transform_normalized()
Y(z) = 0.25*X(z) +0.125*X(z)z⁻¹
>>> f = DigitalFilter(a=[1, -0.1], b=[0.5, 0.25])
>>> f.print_z_transform_normalized()
Y(z) = 0.5*X(z) +0.25*X(z)z⁻¹
       +0.1*Y(z)z⁻¹
"""
        self.afficher_transformee_en_z_normalisee()

    def print_equation(self):
        """Print difference equation
a0*y(n) = b0*x(n) + b1*x(n-1) + b2*x(n-2) + ...
          -a1*y(n-1) -a2*y(n-2) -a3*y(n-3) + ...

>>> f = DigitalFilter(a=[2], b=[0.5, 0.25])
>>> f.print_equation()
2*y(n) = 0.5*x(n) +0.25*x(n-1)
>>> f = DigitalFilter(a=[1, -0.1], b=[0.5, 0.25])
>>> f.print_equation()
y(n) = 0.5*x(n) +0.25*x(n-1)
       +0.1*y(n-1)
"""
        self.afficher_equation_recurrence()

    def print_equation_normalized(self):
        """Print difference equation (normalized with a0=1)
y(n) = b0*x(n) + b1*x(n-1) + b2*x(n-2) + ...
       -a1*y(n-1) -a2*y(n-2) -a3*y(n-3) + ...

>>> f = DigitalFilter(a=[2], b=[0.5, 0.25])
>>> f.print_equation_normalized()
y(n) = 0.25*x(n) +0.125*x(n-1)
>>> f = DigitalFilter(a=[1, -0.1], b=[0.5, 0.25])
>>> f.print_equation_normalized()
y(n) = 0.5*x(n) +0.25*x(n-1)
       +0.1*y(n-1)
"""
        self.afficher_equation_recurrence_normalisee()

    def order(self):
        """Return the order of the digital filter

>>> f = DigitalFilter(a=[2, -0.2, 0.01], b=[1, 0.5])
>>> f.order()
2
"""
        return self.ordre()

    def recursive_filter(self):
        """
Return True if the filter is recursive (IIR Infinite Impulse Response)
Return False if the filter is non-recursive (FIR Finite Impulse Response)

>>> f = DigitalFilter(a=[2, -0.2], b=[1, 0.5])
>>> f.recursive_filter()
True
>>> f = DigitalFilter(a=[1], b=[0.5, 0.5])
>>> f.recursive_filter()
False
"""
        return self.filtre_recursif()

    def normalized_coeffs(self):
        """Return True if the output coefficient a0 is 1
False otherwise

>>> f = DigitalFilter(a=[2, -0.2], b=[1, 0.5])
>>> f.normalized_coeffs()
False
"""
        return self.coeffs_normalises()

    def poles_zeros_common(self):
        """ TODO : english translation

>>> f = DigitalFilter(a=[1, -1], b=[0.25, 0, 0, 0, -0.25])
>>> f.poles_zeros_common()
[1.0]
"""
        return self.poles_zeros_commun()


def _arrondi_pz(val):
    """Formatage et arrondi à 1e-9 près
val : float ou complex
retourne str

Exemple :
>>> _arrondi_pz(1e-16-1e-16j)
'0'
>>> _arrondi_pz(1+2j)
'1+2j'
>>> _arrondi_pz(-2j)
'-0-2j'
>>> _arrondi_pz(-2000-1e-7j)
'-2000'
"""
    # précision 1e-9 relatif
    tol = 1e-9
    # on supprime les parties réel et imag négligeable
    if abs(val) < tol:
        val = 0.0
    else:
        if abs(val.real) < tol:
            val = 1j*val.imag
        if abs(val.imag) < tol:
            val = val.real

    if val.real == 0 and val.imag == 0:
        res = 0.0  # float
    elif val.real != 0 and val.imag == 0:
        # réel pur
        res = val.real  # float
    elif val.real == 0 and val.imag != 0:
        # imaginaire pur
        res = 1j*val.imag  # complex
    elif val.real != 0 and val.imag != 0:
        if abs(val.real/val.imag) < tol:
            # on annule la partie réelle négligeable
            res = 1j*val.imag  # complex
        elif abs(val.imag/val.real) < tol:
            # on annule la partie imaginaire négligeable
            res = val.real  # float
        else:
            res = val  # complex
    # on transforme en str avec un arrondi
    return "{:.9g}".format(res)


def _arrondi(val):
    """Formatage et arrondi à 1e-9 près
val : float ou complex
retourne un float ou complex

Exemple :
>>> _arrondi(1e-16-1e-16j)
0.0
>>> _arrondi(1+2j)
(1+2j)
>>> _arrondi(-2j)
(-0-2j)
>>> _arrondi(-2000-1e-7j)
-2000.0
"""
    nb = complex(_arrondi_pz(val))
    if nb.imag == 0:
        # réel pur
        return round(nb.real, 9)
    else:
        return round(nb.real, 9)+1j*round(nb.imag, 9)


def _sup(val):
    """ Conversion d'un nombre entier
en une chaîne de caractère en exposant

Exemple :
>>> _sup(0)
'⁰'
>>> _sup(87)
'⁸⁷'
>>> _sup(-1)
'⁻¹'
"""
    if isinstance(val, int) is False:
        raise TypeError("int number expected")

    str_superscript = "\N{SUPERSCRIPT ZERO}\
\N{SUPERSCRIPT ONE}\N{SUPERSCRIPT TWO}\N{SUPERSCRIPT THREE}\
\N{SUPERSCRIPT FOUR}\N{SUPERSCRIPT FIVE}\N{SUPERSCRIPT SIX}\
\N{SUPERSCRIPT SEVEN}\N{SUPERSCRIPT EIGHT}\N{SUPERSCRIPT NINE}"

    res = '' if val >= 0 else "\N{SUPERSCRIPT MINUS}"
    val = str(abs(val))
    for char in val:
        res += str_superscript[int(char)]
    return res


if __name__ == '__main__':
    help(__name__)
    # doctest
    import doctest
    doctest.testmod(verbose=False,
                    optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
