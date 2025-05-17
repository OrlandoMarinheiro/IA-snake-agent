import time
import asyncio
import getpass
import json
import os
import websockets
import copy
import math
import random


from game import MAP_SIZE




def achatar_u(u):
        coordenadas_achatadas = []

        for bloco in u:
            for componente in bloco:  
                for coordenada in componente: 
                    if coordenada not in coordenadas_achatadas: 
                        coordenadas_achatadas.append(coordenada)
        
        return coordenadas_achatadas


    # verificar se as coordenadas são seguidas na linha
def verificar_linhas(tipo, linhas):

        if tipo == "linhas":
            indicador = 0
        elif tipo == "colunas":
            indicador = 1

        linhas_verificadas = []  
        for linha in linhas:
            linha_seguida = []  

            for i in range(len(linha)):
                if i == 0:
                    linha_seguida.append(linha[i])
                elif abs(linha[i][indicador] - linha[i-1][indicador]) == 1:
                    linha_seguida.append(linha[i])
                else:
                    if len(linha_seguida) > 1:  
                        if linha_seguida not in linhas_verificadas:
                            linhas_verificadas.append(linha_seguida)  

                    linha_seguida = [linha[i]]

            if len(linha_seguida) > 1 and linha_seguida not in linhas_verificadas:
                linhas_verificadas.append(linha_seguida)

        return linhas_verificadas
    

def detetar_colunas(walls_coords):
        colunas = []
        for coord in walls_coords:
            parede_coluna = [] 
            for i in range(len(walls_coords)):
                if coord[0] == walls_coords[i][0]:
                    parede_coluna.append(walls_coords[i])

            if len(parede_coluna) > 1:
                colunas.append(parede_coluna)
        return colunas
    

def detetar_linhas(walls_coords):
        linhas = []
        for coord in walls_coords:
            parede_linha = [] # evita coordenadas repetidas
            for i in range(len(walls_coords)):
                if coord[1] == walls_coords[i][1]:
                    parede_linha.append(walls_coords[i])

            if len(parede_linha) > 1:
                linhas.append(parede_linha)
        return linhas

    
def detetar_U(linhas_verificadas, colunas_verificadas):
    u_blocks = []

    def verificar_tentativa_U(tentativa_U, u_blocks):
        if len(tentativa_U) == 3 or len(tentativa_U) == 4:
            if tentativa_U not in u_blocks:
                u_blocks.append(tentativa_U)

    #linhas/colunas perpendiculares às bordas
    def verificar_perpendicularidade(tentativa_U, coord, linhas_verificadas, colunas_verificadas, u_blocks, tipo):
        adjacente_encontrado = False
        if tipo == "linha":
            for coluna in colunas_verificadas:
                if coord in coluna:
                    if coord[0] > 0 and coord[0] < MAP_SIZE[0] - 1: 
                        tentativa_U.append(coluna)
                        adjacente_encontrado = True
                        break
        elif tipo == "coluna":
            for linha in linhas_verificadas:
                if coord in linha:
                    if coord[1] > 0 and coord[1] < MAP_SIZE[1] - 1:
                        tentativa_U.append(linha)
                        adjacente_encontrado = True
                        break

        if adjacente_encontrado:
            if tentativa_U not in u_blocks:
                u_blocks.append(tentativa_U)
        elif not adjacente_encontrado and len(tentativa_U) == 1:
            if tentativa_U not in u_blocks:
                u_blocks.append(tentativa_U)


    def verificar_direcao_e_distancia(lado1, lado2):
   
        if lado1[0][0] == lado2[0][0]:  # Mesma coluna
         
            return abs(lado1[0][1] - lado2[0][1]) >= 2
        elif lado1[0][1] == lado2[0][1]:  # Mesma linha
        
            return abs(lado1[0][0] - lado2[0][0]) >= 2
 
        return False



    for coluna in colunas_verificadas:

                tentativa_U = [coluna]
                intersecoes = []

                for linha in linhas_verificadas:
                    intersecao = [coord for coord in linha if coord in tentativa_U[0]]
                    if len(intersecao) == 1:
                        tentativa_U.append(linha)
                        intersecoes.append(intersecao[0])

                if len(tentativa_U) == 3 and verificar_direcao_e_distancia(tentativa_U[1], tentativa_U[2]):
                    verificar_tentativa_U(tentativa_U, u_blocks)


    for linha in linhas_verificadas:

                tentativa_U = [linha]
                intersecoes = []

                for coluna in colunas_verificadas:
                    intersecao = [coord for coord in coluna if coord in tentativa_U[0]]
                    if len(intersecao) == 1:
                        tentativa_U.append(coluna)
                        intersecoes.append(intersecao[0])

                if len(tentativa_U) == 3 and verificar_direcao_e_distancia(tentativa_U[1], tentativa_U[2]):
                    verificar_tentativa_U(tentativa_U, u_blocks)


    # verificar U quase perfeitos em pé
    for linha in linhas_verificadas:
        tentativa_U_corrpd = [linha]
        for coluna in colunas_verificadas:
            for i in range(len(coluna) - 1):

                if [coluna[i][0] + 1, coluna[i][1] - 1] in linha or \
                    [coluna[i][0] - 1, coluna[i][1] - 1] in linha:

                    if coluna not in tentativa_U_corrpd:
                        tentativa_U_corrpd.append(coluna)
                if coluna[i] in linha:
                    if coluna not in tentativa_U_corrpd:
                        tentativa_U_corrpd.append(coluna)
                if len(tentativa_U_corrpd) == 4:
                    break

        verificar_tentativa_U(tentativa_U_corrpd, u_blocks)
    
    # verificar U quase perfeitos deitados
    for coluna in colunas_verificadas:
        tentativa_U_corrpd = [coluna]
        for linha in linhas_verificadas:
            for i in range(len(linha) - 1):

                if [linha[i][0] - 1, linha[i][1] + 1] in coluna or \
                    [linha[i][0] - 1, linha[i][1] - 1] in coluna:
                    
                    if linha not in tentativa_U_corrpd:
                        tentativa_U_corrpd.append(linha)
                if linha[i] in coluna:
                    if linha not in tentativa_U_corrpd:
                        tentativa_U_corrpd.append(linha)
                if len(tentativa_U_corrpd) == 4:
                    break

        verificar_tentativa_U(tentativa_U_corrpd, u_blocks)

    # verificar linha perpendicular à parede até 7 casas dos cantos do mapa
    for linha in linhas_verificadas:
        for coord in linha:
            if coord[0] == MAP_SIZE[0] - 1 or coord[0] == 0:
                    tentativa_U = [linha]
                    verificar_perpendicularidade(tentativa_U, coord, linhas_verificadas, colunas_verificadas, u_blocks, "linha")

    # verificar coluna perpendicular à parede até 10 casas dos cantos do mapa
    for coluna in colunas_verificadas:
        for coord in coluna:
            if coord[1] == MAP_SIZE[1] - 1 or coord[1] == 0:
                    tentativa_U = [coluna]
                    verificar_perpendicularidade(tentativa_U, coord, linhas_verificadas, colunas_verificadas, u_blocks, "coluna")

    return u_blocks


def preencher_U(u_coords):

    def preencher_figura(coordinates):
        if not coordinates:
            return []

        min_x = min(coord[0] for coord in coordinates)
        max_x = max(coord[0] for coord in coordinates)
        min_y = min(coord[1] for coord in coordinates)
        max_y = max(coord[1] for coord in coordinates)
        bordasY = [0, MAP_SIZE[1] - 1]
        bordasX = [0, MAP_SIZE[0] - 1]

        filled_coordinates = []

        # Colunas
        if min_y in bordasY or max_y in bordasY:


            if min_x <= 10:
                canto = 0

                for x in range(canto, max_x + 1):
                    for y in range(min_y, max_y + 1):
                        filled_coordinates.append([x, y])

            elif min_x >= MAP_SIZE[0] - 10:
                canto = MAP_SIZE[0] - 1

                for x in range(min_x, canto + 1):
                    for y in range(min_y, max_y + 1):
                        filled_coordinates.append([x, y])

        # Linhas
        if min_x in bordasX or max_x in bordasX:

            if min_y <= 7:
                canto = 0
                for y in range(canto, max_y + 1):
                    for x in range(min_x, max_x + 1):
                        filled_coordinates.append([x, y])

            elif min_y >= MAP_SIZE[1] - 7:
                canto = MAP_SIZE[1] - 1
                for y in range(min_y, canto + 1):
                    for x in range(min_x, max_x + 1):
                        filled_coordinates.append([x, y])

        # Preenchimento interno
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                filled_coordinates.append([x, y])

        return filled_coordinates
    
    

    def refinar_fig(coords):
        fig_refinadas = []
        for u in coords:
            u_set = set(tuple(tuple(coord) for coord in bloco) for bloco in u)
            already_included = False
            for refined in fig_refinadas:
                refined_set = set(tuple(tuple(coord) for coord in bloco) for bloco in refined)
                if u_set.issubset(refined_set):
                    already_included = True
                    break
            if not already_included:
                fig_refinadas.append(u)
        return fig_refinadas

    u_coords = refinar_fig(u_coords)
    prenchimento = []   
    for u in u_coords:
        coords = achatar_u([u])
        prenchimento.append(preencher_figura(coords))


    return prenchimento


def juntar_coords(u_blocks, mapa_coords):
    paredes_coords = [coord for coord in mapa_coords]
    for u in u_blocks:
        paredes_coords.append(u)
    return paredes_coords


# função de deteção de becos
def detecao(walls_coords):
    # Otimização: Evitar cálculos redundantes
    linhas = verificar_linhas('linhas', detetar_linhas(walls_coords))
    colunas = verificar_linhas('colunas', detetar_colunas(walls_coords))
    detecoes = detetar_U(linhas, colunas)
    return achatar_u([preencher_U(detecoes)])


# ----------------



#### variaveis globais ####
ponto_referencia = []
cantos = []
vez_do_canto = 0
ultimo_canto = []

comida_inicial = []
flag_comida_inicial = True
coord_comida = []
superFoods = []

paredes = []
livres = []
zonas_visitadas = {} 
zonas_por_visitar = []
fps = 0

enemy_body = []


timer = 300

# ------------------- #



def ir_superfood(range_sight, traverse, step, head):
    # Otimização: Simplificação da lógica
    if step >= 2500 or (step >= 1700 and step <= 2000):
        return True
    if range_sight >= 3 and traverse:
        return False
    return True
    



def calcular_cantos(range_sight):
    global ultimo_canto

    cantos = [[range_sight - 1,range_sight - 1], [range_sight - 1, MAP_SIZE[1] - range_sight - 1], [MAP_SIZE[0] - range_sight - 1, range_sight -1], [MAP_SIZE[0] - range_sight - 1 , MAP_SIZE[1] - range_sight - 1]]

    for canto in cantos:
        if canto in paredes:
            for i in range(range_sight):
                if [canto[0] + i, canto[1]] not in paredes:
                    cantos[cantos.index(canto)] = [canto[0] + i, canto[1]]
                    break   
                elif [canto[0], canto[1] + i] not in paredes:
                    cantos[cantos.index(canto)] = [canto[0], canto[1] + i]
                    break   
    
    ultimo_canto = cantos[-1]
    return cantos
                        
          
        

def get_tails(mapa):
    livres =  []
    comida_inicial = []
    paredes = []
    if mapa:
        for i in range(len(mapa)):
            for j in range(len(mapa[i])):
                if mapa[i][j] == 0:   #### ver se é necessário adicionar 3
                    livres.append([i,j])
                elif mapa[i][j] == 2:
                    comida_inicial.append([i,j])
                    livres.append([i,j])
                elif mapa[i][j] == 1:
                    paredes.append([i,j])
    paredes += juntar_coords(detecao(paredes), paredes)
    return comida_inicial, paredes, livres


## distancia de manhattan
def distancia(ponto1, ponto2):
    return abs(ponto1[0] - ponto2[0]) + abs(ponto1[1] - ponto2[1])



def comida_proxima_e_marcar_zona_como_vista(body, sight, traverse, sight_range, step): # para cada sight retorna a comida mais próxima   IMPLEMENTAR O MORE CLOSE FOOD   ##### AJUSTAR PONTOS DE REFERÊNCIA EM VEZ DE METER ROTA
    global zonas_visitadas
    global zonas_por_visitar
    global paredes
    global superFoods
    global enemy_body

    food_coords = []

    head = body[0]
    enemy = []

    for x in sight:
        for y in sight[x]:
            if sight[x][y] == 2:  
                if traverse:
                    if [int(x), int(y)] not in food_coords:
                        food_coords.append([int(x), int(y)])                                                                                                                                                                  
                else:
                    if [int(x), int(y)] not in food_coords and distancia(head, [int(x), int(y)]) <= sight_range and [int(x), int(y)] not in paredes: 
                        food_coords.append([int(x), int(y)])

            if sight[x][y] == 3:
                if ir_superfood(sight_range, traverse,step,head) == False: ## true
 
                    if [int(x), int(y)] not in superFoods:
                        superFoods.append([int(x), int(y)])
                elif ir_superfood(sight_range, traverse,step,head) == True:
                    if [int(x), int(y)] not in superFoods:
                        superFoods.append([int(x), int(y)])
               
                
            # remover a zona que a cobra já viu
            if [int(x), int(y)] not in zonas_visitadas.values() and [int(x), int(y)] in zonas_por_visitar:
    
                    if step in zonas_visitadas:
                        zonas_visitadas[step] += [[int(x), int(y)]]
                    else:
                        zonas_visitadas[step] = [[int(x), int(y)]]
                    zonas_por_visitar.remove([int(x), int(y)])
            
            # detetar inimigos
            if sight.get(str(x)) is not None:
                if sight.get(str(x)).get(str(y)) == 4 and [int(x), int(y)] not in body:
                    enemy.append([int(x), int(y)])
 
    enemy_body = enemy

    return food_coords



def verificar_proximo_passo(body): 
    global cantos
    global vez_do_canto
    global ultimo_canto
    cabeca = body[0]
 
    max_randoms = 4
    while max_randoms != 0:

        if vez_do_canto == 4:
            vez_do_canto = 0
            break
        
        vez_do_canto += 1

        ponto = random.choice(zonas_por_visitar)
        #print("Procurando...")
        if ponto in paredes or ponto in body :
            #print("Ponto é parede")
            continue

        if distancia(cabeca, ponto) >= 10: 
            return ponto
    
    ### canto 
    
        max_randoms -= 1
    
    ponto = cantos[0]
    cantos = cantos[1:] + [ponto]


    return ponto



def main_AIagent(state):
    global ponto_referencia
    global comida_inicial
    global flag_comida_inicial
    global coord_comida
    global superFoods
    global zonas_visitadas
    global zonas_por_visitar
    global paredes
    global livres
    global fps


    
    sight = state.get('sight')
    body = state.get('body')
    traverse = state.get('traverse')    
    cabeca = body[0]
    step = state.get('step')
    sight_range = state.get('range')


    if step > 1:

        
        if sight_range == 2:
           
            timer_add = 400
            if step - timer_add in zonas_visitadas:
                
                for zona in zonas_visitadas[step - timer_add]:
                    zonas_por_visitar.append(zona)
                zonas_visitadas.pop(step - timer_add)

            
        elif sight_range == 3:
            timer_add = 300
            if step - timer_add in zonas_visitadas:
                
                for zona in zonas_visitadas[step - timer_add]:
                    zonas_por_visitar.append(zona)
                zonas_visitadas.pop(step - timer_add)

            
        else:
            timer_add = 200
            if step - timer_add in zonas_visitadas:
                
                for zona in zonas_visitadas[step - timer_add]:
                    zonas_por_visitar.append(zona)
                zonas_visitadas.pop(step - timer_add)

            
        coord_comida = comida_proxima_e_marcar_zona_como_vista(body, sight, traverse, sight_range, step)

        
        if comida_inicial:

            if coord_comida != []:
                goal = coord_comida
            else:
                goal = comida_inicial
            
            if cabeca in comida_inicial:
                comida_inicial.remove(cabeca)

        elif coord_comida:
            
            goal = coord_comida

            if cabeca in coord_comida:
                coord_comida.remove(cabeca)
        
            
        else:
            if ponto_referencia == [] or ponto_referencia not in zonas_por_visitar:
                ponto_referencia = verificar_proximo_passo(body)
            goal = [ponto_referencia]

        if ir_superfood(sight_range, traverse, step, cabeca) == True:
            if coord_comida != []:
                goal = coord_comida 
            elif superFoods != []:
                superFoods = sorted(superFoods, key=lambda point: math.dist(point, cabeca))
                goal = superFoods
            
            if cabeca in superFoods:
                superFoods.remove(cabeca)
        
        if len(goal) > 3:
            goal = goal[:3]
        


        goal_mask = [False for _ in range(len(goal))]

        newstate = {'body': copy.deepcopy(body), 
                    'traverse': traverse, 
                    'walls': paredes, 
                    'map_size': MAP_SIZE, 
                    'adversial_snake': enemy_body, 
                    'goal': goal, 
                    'goal_mask': copy.deepcopy(goal_mask), 
                    'superFoods': superFoods, 
                    'step' : step,
                    'range_sight': sight_range}

        domain = SearchDomain()
        problem = SearchProblem(domain, newstate)
        searchTree = SearchTree(problem, (1/fps) * 0.8, 'A*')

        path = searchTree.search()
       
        if path != None and len(path) > 1:
            next_move = path[1]['key']
            return next_move


    return 'n'




#search tree
#domínio para abordar o inimigo que se quer
class SearchDomain:

    # construtor
    def __init__(self):
        pass



    # lista de accoes possiveis num estado
    def actions(self, state):
        snake_positions = state.get('body')
        walls_coords = state.get('walls')
        map_size = state.get('map_size')
        adversial_snake = state.get('adversial_snake')
        traverse = state.get('traverse')
        step = state.get('step')
        superFoods = state.get('superFoods')
        sight_range = state.get('range_sight')
        if ir_superfood(sight_range, traverse, step, snake_positions[0]) == True: 
                snake_positions_dummy = copy.deepcopy(snake_positions)
        else:
            snake_positions_dummy = snake_positions + superFoods
        
               

        x, y = snake_positions[0]
       
        a, b = map_size

        set_actions = set()

        if not traverse:
            if (x > 0) and [x - 1, y] not in snake_positions and [x - 1, y] not in walls_coords and [x - 1, y] not in adversial_snake:
                set_actions.add(('a', (-1, 0)))
            if (x < a - 1) and [x + 1, y] not in snake_positions and [x + 1, y] not in walls_coords and [x + 1, y] not in adversial_snake:
                set_actions.add(('d', (1, 0)))
            if (y > 0) and [x, y - 1] not in snake_positions and [x, y - 1] not in walls_coords and [x, y - 1] not in adversial_snake:
                set_actions.add(('w', (0, -1)))
            if (y < b - 1) and [x, y + 1] not in snake_positions and [x, y + 1] not in walls_coords and [x, y + 1] not in adversial_snake:
                set_actions.add(('s', (0, 1)))
        else:
            if [x - 1, y] not in snake_positions_dummy and [x - 1, y] not in adversial_snake:
                set_actions.add(('a', (-1, 0)))
            if [x + 1, y] not in snake_positions_dummy and [x + 1, y] not in adversial_snake:
                set_actions.add(('d', (1, 0)))
            if [x, y - 1] not in snake_positions_dummy and [x, y - 1] not in adversial_snake:
                set_actions.add(('w', (0, -1)))
            if [x, y + 1] not in snake_positions_dummy and [x, y + 1] not in adversial_snake:
                set_actions.add(('s', (0, 1)))

        return set_actions
    
    
    # resultado de uma accao num estado, ou seja, o estado seguinte
    def result(self, state, action):
        snake_positions = copy.deepcopy(state['body'])
        goal_mask = copy.deepcopy(state['goal_mask'])
        goal = state['goal']
        map_size = state['map_size']
        traverse = state['traverse']

        x, y = snake_positions[0]
        a, b = map_size
        new_head = [x + action[1][0], y + action[1][1]]

        # Handle wrap-around if traverse is active
        if traverse:
            if new_head[0] < 0:
                new_head[0] = a - 1
            elif new_head[0] >= a:
                new_head[0] = 0
            if new_head[1] < 0:
                new_head[1] = b - 1
            elif new_head[1] >= b:
                new_head[1] = 0

        # Check for collision with the snake's body
        if new_head in snake_positions or new_head in state['adversial_snake']:
            return state  # Return the current state if there's a collision

        # Update snake positions
        snake_positions.insert(0, new_head)
        snake_positions.pop(-1)

        # Check if the new head is on a goal
        for i in range(len(goal)):
            if new_head == goal[i]:
                goal_mask[i] = True
                snake_positions.append([a, b])  # Add new segment to the snake

        # Create new state
        new_state = copy.deepcopy(state)
        new_state['body'] = snake_positions
        new_state['goal_mask'] = goal_mask
        new_state['key'] = action[0]

        return new_state
   

    # test if the given "goal" is satisfied in "state"
    def satisfies(self, state):
        return all(state['goal_mask'])

    # custo de uma accao num estado
    def cost(self):
        return 1
    
    # custo estimado de chegar de um estado a outro
    def heuristic(self, state):
        x, y = state['body'][0]       # cabeça da cobra
        distance = 0
       
        for i in range(len(state['goal'])):
            if not state['goal_mask'][i]:
                distance += calculate_distance_with_portals([x, y], state['goal'][i], state['map_size'][0], state['map_size'][1], state['traverse'],state['range_sight'], state['step'], state['body'])
                x, y = state['goal'][i]

            
        return distance


# Problemas concretos a resolver
# dentro de um determinado dominio
class SearchProblem:
    def __init__(self, domain, initial):
        self.domain = domain
        self.initial = initial
    def goal_test(self, state):
        return self.domain.satisfies(state)

# Nos de uma arvore de pesquisa
class SearchNode:
    def __init__(self,state,parent): 
        self.state = state
        self.parent = parent
        self.cost = 0
        self.heuristic = 0
        self.eval = 0
    def __str__(self):
        return "no(" + str(self.state) + ")"
    def __repr__(self):
        return str(self)

# Arvores de pesquisa
class SearchTree:

    # construtor
    def __init__(self,problem, limit, strategy='A*'): 
        self.problem = problem
        root = SearchNode(problem.initial, None)
        self.open_nodes = [root]
        self.strategy = strategy
        self.solution = None
        self.non_terminals = 0
        self.expanded_nodes = 0
        self.limit = limit

    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self,node):
        if node.parent == None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return(path)

    # procurar a solucao
    def search(self):

        inicio = time.time()
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            self.expanded_nodes += 1
            fim = time.time()

            
            if self.problem.goal_test(node.state) or (fim-inicio) >= self.limit:
                self.solution = node
                self.terminals = len(self.open_nodes)+1
                return self.get_path(node)
            self.non_terminals += 1
            lnewnodes = []
            for a in self.problem.domain.actions(node.state):
                newstate = self.problem.domain.result(node.state,a)
                if newstate not in self.get_path(node):
                    newnode = SearchNode(newstate,node)
                    newnode.cost = node.cost + self.problem.domain.cost( )    
                    newnode.heuristic = self.problem.domain.heuristic ( newnode.state )                          
                    newnode.eval = newnode.cost + newnode.heuristic
                    lnewnodes.append(newnode)
            self.add_to_open(lnewnodes)
            
        return None
    


    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def add_to_open(self,lnewnodes):
        if self.strategy == 'breadth':
            self.open_nodes.extend(lnewnodes)
        elif self.strategy == 'depth':
            self.open_nodes[:0] = lnewnodes
        elif self.strategy == 'A*':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes = sorted(self.open_nodes, key=lambda node : node.eval) 
        elif self.strategy == 'gulosa':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes = sorted(self.open_nodes, key=lambda node : node.heuristic) 
        elif self.strategy == 'uniforme':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes = sorted(self.open_nodes, key=lambda node : node.cost)



### Search Tree ###


def calculate_distance_with_portals(snake_head, ponto, map_width, map_height, traverse,sight_range,step,snake_positions):

    x1, y1 = snake_head
    x2, y2 = ponto

    # Direct distance
    direct_distance = abs(x1 - x2) + abs(y1 - y2)

    # Portal distances
    portal_right_left = abs((x1 - map_width) - x2) + abs(y1 - y2)  # Cross through left wall
    portal_left_right = abs((x1 + map_width) - x2) + abs(y1 - y2)  # Cross through right wall
    portal_bottom_top = abs(x1 - x2) + abs((y1 - map_height) - y2)  # Cross through top wall
    portal_top_bottom = abs(x1 - x2) + abs((y1 + map_height) - y2)  # Cross through bottom wall

    # Minimum of all distances

    if traverse or ir_superfood(sight_range, traverse, step, snake_positions) == False:
        
        flag = min(direct_distance, portal_right_left, portal_left_right, portal_bottom_top, portal_top_bottom)
    else :
        flag = direct_distance
    return flag


### safe move snake ###
def safe_move_snake(state):
    snake_positions = state.get('body')
    walls_coords = state.get('walls')
    map_size = state.get('map_size')
    adversial_snake = state.get('adversial_snake')
    traverse = state.get('traverse')

    x, y = snake_positions[0]
    a, b = map_size

    set_actions = set()

    if not traverse:
        if (x > 0) and [x - 1, y] not in snake_positions and [x - 1, y] not in walls_coords and [x - 1, y] not in adversial_snake:
            set_actions.add(('a', (-1, 0)))
        if (x < a - 1) and [x + 1, y] not in snake_positions and [x + 1, y] not in walls_coords and [x + 1, y] not in adversial_snake:
            set_actions.add(('d', (1, 0)))
        if (y > 0) and [x, y - 1] not in snake_positions and [x, y - 1] not in walls_coords and [x, y - 1] not in adversial_snake:
            set_actions.add(('w', (0, -1)))
        if (y < b - 1) and [x, y + 1] not in snake_positions and [x, y + 1] not in walls_coords and [x, y + 1] not in adversial_snake:
            set_actions.add(('s', (0, 1)))
    else:
        if [x - 1, y] not in snake_positions and [x - 1, y] not in adversial_snake:
            set_actions.add(('a', (-1, 0)))
        if [x + 1, y] not in snake_positions and [x + 1, y] not in adversial_snake:
            set_actions.add(('d', (1, 0)))
        if [x, y - 1] not in snake_positions and [x, y - 1] not in adversial_snake:
            set_actions.add(('w', (0, -1)))
        if [x, y + 1] not in snake_positions and [x, y + 1] not in adversial_snake:
            set_actions.add(('s', (0, 1)))

    #print("\n\n\n\nBody: ", snake_positions)
    #print("Safe moves: ", set_actions)
    return random.choice(list(set_actions))
### safe move snake ###




async def agent_loop(server_address="localhost:8000", agent_name="student"):
    global comida_inicial, cantos, paredes, livres, zonas_por_visitar, fps



    """Example client loop."""
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))


        while True:
            key = ""
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server   #100 000 ms
                #print(state)  # print the state, you can use this to further process the game state
                # Next lines are only for the Human Agent, the key values are nonetheless the correct ones!


                if 'map' in state:
                    comida_inicial, paredes, livres = get_tails(state.get('map'))
                    zonas_por_visitar = copy.copy(livres)
                    fps = state.get('fps')

                if 'step' in state and 'body' in state:
                    cantos = calcular_cantos(state.get('range'))
                    if state.get("step") == 1:
                        flag_comida_inicial = True
                        comida_inicial = sorted(comida_inicial, key=lambda point: math.dist(point, state.get('body')[0]))
                    if state.get("step") >= 1:
                        key = main_AIagent(state)

                await websocket.send(json.dumps({"cmd": "key", "key": key}))
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return
            
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())#114060_113602_114947
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))