"""Script para ejecutar Girvan-Newman, guardar la mejor partición y registrar evolución."""
import pickle
import numpy as np
import networkx as nx
import os
import datetime

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
G_air = airUndir.copy()
drop_weights(G_air)
print('C. air (unweighted)')
print(G_air)
print('Es dirigido?:',nx.is_directed(G_air))
print('Es pesado?:',nx.is_weighted(G_air))
print('Es conectado?:',nx.is_connected(G_air))
print('')
# -------------------------------
# Inicializar CSV para evolución
# -------------------------------
csv_file = "modularidad_por_iteracion_air.csv"
with open(csv_file, "w") as f:
    f.write("iteracion,comunidades,modularidad\n")

# -------------------------------
# Ejecutar Girvan-Newman
# -------------------------------
print("Ejecutando algoritmo Girvan-Newman...")
modulos = nx.community.girvan_newman(G_air)

mod_max = -999
com_max = None
mejor_iter = 0

# -------------------------------
# Bucle principal
# -------------------------------
for step, communities in enumerate(modulos, start=1):
    print(f"Iteración {step}: calculando modularidad...")
    n_modularidad = nx.community.modularity(G_air, communities)
    num_comunidades = len(communities)

    print(f"Modularidad = {n_modularidad:.4f} | Comunidades: {num_comunidades}")

    # Guardar evolución en CSV
    with open(csv_file, "a") as f:
        f.write(f"{step},{num_comunidades},{n_modularidad:.6f}\n")

    # Guardar mejor partición
    if n_modularidad > mod_max:
        mod_max = n_modularidad
        com_max = tuple(sorted(c) for c in communities)
        mejor_iter = step

        fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"best_partition_air_{fecha}.pkl"
        with open(filename, "wb") as f:
            pickle.dump({
                "iter": mejor_iter,
                "modularity": mod_max,
                "partition": com_max
            }, f)
        print(f"Partición guardada: iteración {step}, modularidad = {mod_max:.4f}")

# -------------------------------
# Fin del proceso
# -------------------------------
print("\nProceso completado.")
print(f"Mejor partición en la iteración {mejor_iter} con modularidad: {mod_max:.4f}")
print(f"Número de comunidades: {len(com_max)}")
print(f"Histórico guardado en: {csv_file}")
