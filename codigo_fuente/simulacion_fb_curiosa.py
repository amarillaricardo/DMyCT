import pandas as pd
import networkx as nx
import numpy as np
import pickle
import random
import os
import datetime
from networkx.algorithms.efficiency_measures import global_efficiency


print("Script iniciado correctamente...")
print("Verificando existencia del archivo 'facebook.txt'...")

# -------------------------------
# Leer grafo desde archivo
# -------------------------------
def read_graph(filename):
    G = nx.Graph()
    array = np.loadtxt(filename, dtype=int)
    G.add_edges_from(array)
    return G

file_path = 'facebook.txt'
if not os.path.isfile(file_path):
    raise FileNotFoundError(f"El archivo '{file_path}' no se encontró.")
print("Archivo encontrado.")

print("Cargando grafo...")
fb = read_graph(file_path)
print(f"Grafo cargado: {fb.number_of_nodes()} nodos, {fb.number_of_edges()} aristas.")


print("Iniciando simulación: Facebook - Estrategia Curiosa")

base_path = '/home/economatica/MCD-DM/'

print("Cargando centralidad de grado de Facebook...")
grado_fb = pd.read_csv(base_path + 'centralidad_grado_facebook.csv', index_col=0)
centralidad_fb = grado_fb['Centralidad_Grado'].to_dict()

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

def estrategia_curiosa(G, centralidad_dict):
    valores = list(centralidad_dict.items())
    valores.sort(key=lambda x: x[1])
    nodos = [x[0] for x in valores]
    pesos = np.linspace(1.0, 0.1, len(nodos))
    pesos /= pesos.sum()
    return random.choices(nodos, weights=pesos, k=len(nodos))

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

print("Calculando orden de nodos con estrategia curiosa...")
nodos = estrategia_curiosa(fb, centralidad_fb)

print("Simulando robustez (Ng/N y eficiencia)...")
fb_ngn_curiosa, fb_eff_curiosa = simular_robustez(fb, nodos, dirigido=False)

output_path = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(output_path, 'fb_curiosa.pkl')

print(f"Guardando resultados en '{output_file}'...")
with open(output_file, 'wb') as f:
    pickle.dump({'ngn': fb_ngn_curiosa, 'eff': fb_eff_curiosa}, f)

print("Simulación completada: Facebook - Curiosa")
