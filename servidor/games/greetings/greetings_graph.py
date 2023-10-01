import networkx as nx
from pyvis.network import Network
import string
#import pandas as pd
from servidor.games.greetings.greetings_graph_node import Node
from typing import List

N = 12 # Number of nodes
NUM_INPUTS = 8 # Input edges on each node
NUM_OUTPUTS = NUM_INPUTS # Output edges on each node
NUM_BIDIRECTIONAL = 4 # Num of bidirectional edges between nodes

def create_nodes(n: int, NUM_INPUTS, NUM_OUTPUTS, NUM_BIDIRECTIONAL) -> List[Node]:
    """
        Creates a list n nodes with the alphabet letters names
    """
    alphabet = string.ascii_lowercase
    nodes = []
    for i in range(n):
        nodes.append(Node(alphabet[i], NUM_INPUTS, NUM_OUTPUTS, NUM_BIDIRECTIONAL))
    return nodes

def get_new_node(requestor, edge_type, all_nodes):
    """
        Requestor: Node that is requesting a new edge
        Edge_type: Type of edge that is requested from requestor to the new node
        All_nodes: All nodes in the network

        Returns the less connected avaliable node that is compatible to join with the requestor (using the edge_type)
    """
    min_connected_node = None
    
    if edge_type == 'input':
        reverse_edge_type = 'output'
    elif edge_type == 'output':
        reverse_edge_type = 'input'
    else:
        reverse_edge_type = 'bidirectional'
    
    for new_node in all_nodes:
        if requestor.can_connect(new_node, edge_type, reverse_edge_type):
            if min_connected_node == None: # Initialize the min connected node to a valid node
                min_connected_node = new_node
            # If they can teorically connect, save it as the min connected node if it is better than the previosly found one
            if new_node.get_num_edges_of_type(reverse_edge_type) < min_connected_node.get_num_edges_of_type(reverse_edge_type):
                min_connected_node = new_node

    return min_connected_node

def is_correct_graph(players, NUM_INPUTS, NUM_OUTPUTS, NUM_BIDIRECTIONAL):
    """
        Checks if the graph is correct (all nodes have the correct number of edges)
    """
    for player in players:
        if player.get_num_inputs() != NUM_INPUTS:
            return False
        if player.get_num_outputs() != NUM_OUTPUTS:
            return False
        if player.get_num_bidirectional_edges() != NUM_BIDIRECTIONAL:
            return False
    return True

def create_networkx_graph(players):
    """
        Creates a networkx digraph from the given nodes
    """
    G = nx.DiGraph()

    for player in players:
        G.add_node(player.get_name())

    for player in players:
        for output_edge_player in player.get_outputs():
            G.add_edge(player.get_name(), output_edge_player.get_name())

    return G

def create_salu2(players, NUM_INPUTS, NUM_OUTPUTS, NUM_BIDIRECTIONAL):
    """
        Creates a salu2 network with the given nodes
    """
    for player in players:

        #print(f"BEFORE: Node {player.get_name()} has {player.get_num_inputs()} input edges, {player.get_num_outputs()} output edges and {player.get_num_bidirectional_edges()} bidireccional edges")
        #player.print_edges()

        num_bidirectional = player.get_num_bidirectional_edges()

        if num_bidirectional < NUM_BIDIRECTIONAL:
            for i in range(NUM_BIDIRECTIONAL - num_bidirectional):
                new_node = get_new_node(player, 'bidirectional', players)
                if(new_node != None):
                    player.add_bidirectional_edge(new_node)
                else:
                    #print("No hay nodos disponibles para bidireccionales")
                    return False

        num_inputs = player.get_num_inputs()

        if num_inputs < NUM_INPUTS:
            for i in range(NUM_INPUTS - num_inputs):
                new_node = get_new_node(player, 'input', players)
                if(new_node != None):
                    player.add_input_edge(new_node, False)
                else:
                    #print("No hay nodos disponibles para input")
                    return False

        num_outputs = player.get_num_outputs()

        if num_outputs < NUM_OUTPUTS:
            for i in range(NUM_OUTPUTS - num_outputs):
                new_node = get_new_node(player, 'output', players)
                if(new_node != None):
                    player.add_output_edge(new_node, False)
                else:
                    #print("No hay nodos disponibles para output")
                    return False

        #print(f"AFTER: Node {player.get_name()} has {player.get_num_inputs()} input edges, {player.get_num_outputs()} output edges and {player.get_num_bidirectional_edges()} bidireccional edges")
        #player.print_edges()    

    for player in players:
        pass
        #print(f"FINAL: Node {player.get_name()} has {player.get_num_inputs()} input edges, {player.get_num_outputs()} output edges and {player.get_num_bidirectional_edges()} bidireccional edges")
    
    # Always correct if it reaches this point
    if is_correct_graph(players, NUM_INPUTS, NUM_OUTPUTS, NUM_BIDIRECTIONAL):
        return True
    else:
        return False
    
def get_all_correct_graphs():
    correct_graphs = []
    for num_inputs in range(N):
        for num_bidirectionals in range(num_inputs):
            players = create_nodes(N, num_inputs, num_inputs, num_bidirectionals)
            correct = create_salu2(players, num_inputs, num_inputs, num_bidirectionals)
            if correct:
                correct_graphs.append((num_inputs, num_bidirectionals))
    
    return correct_graphs

def get_best_correct_graph(correct_graphs):
    """
        It is desirable to have high input edges and medium bidirectional edges
        So the product of the sum and the difference of the two values is the score
    """

    best_score = 0
    best_graph = None

    for graph in correct_graphs:
        sum = graph[0] + graph[1]
        difference = graph[0] - graph[1]
        prod = sum * difference
        if prod > best_score:
            best_score = prod
            best_graph = graph 

    return best_score, best_graph


            
if __name__ == "__main__":

    correct_graphs_configs = get_all_correct_graphs()

    print(correct_graphs_configs)

    best_score, best_graph_config = get_best_correct_graph(correct_graphs_configs)

    print(f"Best graph is {best_graph_config} with score {best_score}")

    players = create_nodes(N, best_graph_config[0], best_graph_config[0], best_graph_config[1])

    create_salu2(players, best_graph_config[0], best_graph_config[0], best_graph_config[1])

    G = create_networkx_graph(players)
    
    # Dibuja el grafo utilizando pyvis
    nt = Network(directed=True)
    nt.from_nx(G)
    # Disable physics to make it look better
    nt.write_html('salu2_graph.html')

    """

    in_degree = G.in_degree()
    out_degree = G.out_degree()

    for node, in_degree_value in in_degree:
        #print(f"El nodo {node} tiene un grado de entrada de {in_degree_value}")

    for node, out_degree_value in out_degree:
        #print(f"El nodo {node} tiene un grado de salida de {out_degree_value}")

    # Contar el número de aristas bidireccionales
    num_aristas_bidireccionales = 0
    for u, v in G.edges():
        if G.has_edge(v, u):
            num_aristas_bidireccionales += 1

    num_aristas_bidireccionales = num_aristas_bidireccionales/2 # Cada arista bidireccional se cuenta dos veces

    # Contar el número de aristas unidireccionales
    num_aristas_unidireccionales = G.number_of_edges() - num_aristas_bidireccionales * 2

    # Imprime el número de aristas bidireccionales y unidireccionales
    #print(f"El número de aristas es {G.number_of_edges()}, debe ser {N * (NUM_INPUTS + NUM_OUTPUTS) / 2}")
    #print(f"El número de aristas bidireccionales es {num_aristas_bidireccionales}, debe ser {N * NUM_BIDIRECTIONAL / 2}")
    #print(f"El número de aristas unidireccionales es {num_aristas_unidireccionales}, debe ser {N * (NUM_INPUTS + NUM_OUTPUTS - (2 * NUM_BIDIRECTIONAL)) / 2}")

    # Obtener la matriz de adyacencia
    matriz_adyacencia = nx.adjacency_matrix(G)

    # Imprimir la matriz de adyacencia
    #print(matriz_adyacencia.todense())
    """