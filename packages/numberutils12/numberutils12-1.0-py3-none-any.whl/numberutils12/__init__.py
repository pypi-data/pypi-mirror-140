#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Created on Thu May 20 19:52:31 2021

@author: Diego Henao

"""


def suma_enteros(a,b):
    return a+b

      
def resta_enteros(a,b):
    return a-b


def producto_enteros(a,b):
    return a*b


# 5! = 1*2*3*4*5
def factorial(n):
    if (n == 0):
        return 1

    resultado = 1
    for i in range(1, n+1):
        resultado = resultado * i

    return resultado


def listar_n_par(n):
    par = []

    i=0
    while(i <= n):
        if i % 2 == 0:
            par.append(i)
        i += 1
    return par
        




