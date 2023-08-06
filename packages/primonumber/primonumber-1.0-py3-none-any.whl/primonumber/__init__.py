#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu March 2 17:00:24 2022

@author: jesus
"""
def primo(n):
	if n < 2:
		return False
	for i in range(2, n):
		es_primo = True
		for j in range(2, i):
			if(i%j == 0):
				es_primo = False
		if(es_primo):
			print(f"{i} es primo")
