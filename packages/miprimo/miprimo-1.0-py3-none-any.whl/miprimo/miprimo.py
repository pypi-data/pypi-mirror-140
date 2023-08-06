#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 1 16:52:31 2022

@author: Fran
"""
def primos2n(n):
    primos = []
    for num in range(2, n + 1):
        fg = False
        for i in range(2, num):
            if num % i == 0:
                fg = True
                break
        if (fg == False):
            primos.append(num)
    return primos
#pip install --user ./dist/miprimo-1.0-py3-none-any.whl
#python C:/Users/Fran/PycharmProjects/FndPyA4/venv/numeros_primos/setup.py bdist_wheel