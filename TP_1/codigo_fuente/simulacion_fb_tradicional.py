import pandas as pd
import networkx as nx
import numpy as np
import pickle
import random
import os
import datetime
"""Script para ejecutar Girvan-Newman sobre un grafo y guardar la mejor partición + evolución en CSV (sin gráfico)."""

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


print("🚀 Iniciando simulación: Facebook - Estrategia Tradicional")

base_path = '/home/economatica/MCD-DM/'

print("📥 Cargando centralidad de grado de Facebook...")
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
nodos = estrategia_tradicional(fb, centralidad_fb)

print("⚙️ Simulando robustez (Ng/N y eficiencia)...")
fb_ngn_trad, fb_eff_trad = simular_robustez(fb, nodos, dirigido=False)

output_path = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(output_path, 'fb_tradicional.pkl')

print(f"💾 Guardando resultados en '{output_file}'...")
with open(output_file, 'wb') as f:
    pickle.dump({'ngn': fb_ngn_trad, 'eff': fb_eff_trad}, f)

print("✅ Simulación completada: Facebook - Tradicional")
