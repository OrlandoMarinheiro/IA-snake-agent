import numpy as np
import random
from game import MAP_SIZE
# Códigos ANSI para cores
RED = '\033[91m'
GREEN = '\033[92m'
GREY = '\033[90m'
PURPLE = '\033[95m'
RESET = '\033[0m'
BLACK = '\033[30m'


def transpose_matriz(matriz):
    return np.transpose(matriz)

def print_map(state):
    
    mapa = state.get('map')
    if mapa:
        new_mapa = transpose_matriz(mapa)
        
        for linha in new_mapa:
            for char in linha:
                if char == 2:
                    print(f"{RED}{char}{RESET}", end=" ")  # Cor vermelha para o número 2
                elif char == 1:
                    print(f"{GREEN}{char}{RESET}", end=" ")  # Cor verde para o número 1
                else:
                    print(f"{char}", end=" ")  # Sem cor para os outros caracteres
            print()  # Nova linha após imprimir uma linha da matriz


def print_map_from_coords(walls_coords):

    largura_mapa, altura_mapa = MAP_SIZE
    mapa = []

    for i in range(altura_mapa):
        linha = []
        for j in range(largura_mapa):
            linha.append('0')
        mapa.append(linha)

    
    # Preenche as posições de paredes (coordenadas) com 1
    for x, y in walls_coords:
        if int(x) < largura_mapa and int(y) < altura_mapa:
            mapa[int(y)][int(x)] = '1'


    for linha in mapa:
            for char in linha:
                if char == '1':
                    print(f"{GREEN}{char}{RESET}", end=" ")  # Cor verde para o número 1
                else:
                    print(f"{char}", end=" ")  # Sem cor para os outros caracteres
            print()  # Nova linha após imprimir uma linha da matriz



def print_sight(state):

    largura_mapa, altura_mapa = MAP_SIZE
    mapa = []

    for i in range(altura_mapa):
        linha = []
        for j in range(largura_mapa):
            linha.append('-')
        mapa.append(linha)

    sight = state.get('sight')
    if sight:
        for x in sight:
            for y in sight[x]:
                if int(x) < largura_mapa and int(y) < altura_mapa:
                    mapa[int(y)][int(x)] = sight[x][y]
    
    for linha in mapa:
            for char in linha:
                if char == 1:
                    print(f"{BLACK}{char}{RESET}", end=" ")
                elif char == 2:
                    print(f"{RED}{char}{RESET}", end=" ")  # Cor vermelha para o número 2
                elif char == 3:
                    print(f"{PURPLE}{char}{RESET}", end=" ")
                elif char == 4:
                    print(f"{GREEN}{char}{RESET}", end=" ")  # Cor verde para o número 1
                else:
                    print(f"{char}", end=" ")  # Sem cor para os outros caracteres
            print()  # Nova linha após imprimir uma linha da matriz

                
