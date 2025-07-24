import pandas as pd
import networkx as nx
import numpy as np
import pickle
import random
import os
import datetime
from networkx.algorithms.efficiency_measures import global_efficiency

print("Script iniciado correctamente...")
print("Verificando existencia del archivo 'airport.txt'...")

# -------------------------------
# Leer grafo desde archivo
# -------------------------------
#Para cargar datos
def read_graph(filename):
    G = nx.Graph()
    array = np.loadtxt(filename, dtype=int)
    G.add_edges_from(array)
    return G

def read_graph_weighted(filename):
    G = nx.Graph()
    array = np.loadtxt(filename, dtype=int)
    G.add_weighted_edges_from(array)
    return G

def read_dir_graph(filename):
    G = nx.DiGraph()
    array = np.loadtxt(filename, dtype=int)
    G.add_edges_from(array)
    return G

def read_dir_graph_weighted(filename):
    G = nx.DiGraph()
    array = np.loadtxt(filename, dtype=int)
    G.add_weighted_edges_from(array)
    return G

def get_graph_pos(filename):
  with open(filename, 'rb') as f:
    posData = pickle.load(f)
  return posData

#Borrarle los pesos a un grafo pesado
def drop_weights(G):
    '''Drop the weights from a networkx weighted graph.'''
    for node, edges in nx.to_dict_of_dicts(G).items():
        for edge, attrs in edges.items():
            attrs.pop('weight', None)


file_path = 'airport.txt'
if not os.path.isfile(file_path):
    raise FileNotFoundError(f"El archivo '{file_path}' no se encontró.")
print("Archivo encontrado.")

air = read_dir_graph_weighted(file_path)
print('Airport')
print(air)
print('Es dirigido?:',nx.is_directed(air))
print('Es pesado?:',nx.is_weighted(air))
print('Es fuertemente conexo?:',nx.is_strongly_connected(air))
print('Es debilmente conexo?:',nx.is_weakly_connected(air))

airStronglyCC = sorted(nx.strongly_connected_components(air), key=len, reverse=True)
airStrongly = air.subgraph(airStronglyCC[0]) # la mas grande en 0 y así en orden
print('Airport componente gigante fuertemente conexa')
print(airStrongly)
print('Es dirigido?:',nx.is_directed(airStrongly))
print('Es pesado?:',nx.is_weighted(airStrongly))
print('Es fuertemente conexo?:',nx.is_strongly_connected(airStrongly))
print('Es debilmente conexo?:',nx.is_weakly_connected(airStrongly))
print('')

airUndir=nx.DiGraph.to_undirected(airStrongly)
airU = airUndir.copy()
drop_weights(airU)
print('C. air (unweighted)')
print(airU)
print('Es dirigido?:',nx.is_directed(airU))
print('Es pesado?:',nx.is_weighted(airU))
print('Es conectado?:',nx.is_connected(airU))
print('')

print("🚀 Iniciando simulación: Aeropuertos - Estrategia Tradicional")

base_path = '/home/economatica/MCD-DM/'

print("📥 Cargando centralidad de grado de Aeropuertos...")
grado_air = pd.read_csv(base_path + 'centralidad_grado_aeropuertos.csv', index_col=0)
centralidad_airU = grado_air['Centralidad_Grado'].to_dict()

def ng_n(G):
    if nx.is_directed(G):
        giant = max(nx.strongly_connected_components(G), key=len)
    else:
        giant = max(nx.connected_components(G), key=len)
    return len(giant) / G.number_of_nodes()

def global_efficiency(G):
    try:
        return nx.global_efficiency(G)
    except:
        return 0

def estrategia_tradicional(G, centralidad_dict):
    return [n for n, _ in sorted(centralidad_dict.items(), key=lambda x: x[1], reverse=True)]

def simular_robustez(G_original, nodos_ordenados, dirigido=False):
    G = G_original.copy()
    fraccion_ngn = []
    eficiencias = []
    visitados = set()

    for i, nodo in enumerate(nodos_ordenados):
        if nodo in G and nodo not in visitados:
            G.remove_node(nodo)
            visitados.add(nodo)
        if G.number_of_nodes() == 0 or G.number_of_edges() == 0:
            fraccion_ngn.append(0)
            eficiencias.append(0)
            break
        fraccion_ngn.append(ng_n(G))
        eficiencias.append(global_efficiency(G))
        if i % 100 == 0:
            print(f"🧩 Iteración {i}/{len(nodos_ordenados)}")

    return fraccion_ngn, eficiencias

print("📊 Calculando orden de nodos con estrategia tradicional...")
nodos = estrategia_tradicional(airU, centralidad_airU)

print("⚙️ Simulando robustez (Ng/N y eficiencia)...")
airU_ngn_trad, airU_eff_trad = simular_robustez(airU, nodos, dirigido=False)

output_path = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(output_path, 'airU_tradicional.pkl')

print(f"💾 Guardando resultados en '{output_file}'...")
with open(output_file, 'wb') as f:
    pickle.dump({'ngn': airU_ngn_trad, 'eff': airU_eff_trad}, f)

print("✅ Simulación completada: Aeropuertos - Tradicional")
