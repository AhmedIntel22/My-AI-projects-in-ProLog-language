import copy
import heapq
import time
import tkinter as tk

# ========== INITIAL STATES ==========
etat_depart = [
    [1, 2, 7],
    [8, 6, 0],
    [3, 5, 4]
]

etat_final = [
    [1, 2, 3],
    [8, 0, 4],
    [7, 6, 5]
]

# ========== BASIC FUNCTIONS ==========
def estEtatFinal(t):
    return t == etat_final

def position_case_vide(t):
    for y in range(3):
        for x in range(3):
            if t[y][x] == 0:
                return (x, y)

def numero(t, x, y):
    return t[y][x]

def permuter(t, c1, c2):
    nouveau = copy.deepcopy(t)
    x1, y1 = c1
    x2, y2 = c2
    nouveau[y1][x1], nouveau[y2][x2] = nouveau[y2][x2], nouveau[y1][x1]
    return nouveau

def transitions(t):
    voisins = []
    x, y = position_case_vide(t)

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy

        if 0 <= nx < 3 and 0 <= ny < 3:
            voisins.append(permuter(t, (x, y), (nx, ny)))

    return voisins

def afficher_taquin(t):
    for ligne in t:
        print(ligne)
    print()

def transformer_etat(t):
    return tuple(tuple(ligne) for ligne in t)

# ========== DFS ==========
def dfs(etat_depart):
    debut = time.time()
    freeNodes = [(etat_depart, [])]
    closedNodes = set()

    nb_etats_generes = 1
    nb_noeuds_visites = 0

    while freeNodes:
        etat_courant, chemin = freeNodes.pop(0)
        etat_tuple = transformer_etat(etat_courant)

        if etat_tuple in closedNodes:
            continue

        closedNodes.add(etat_tuple)
        nb_noeuds_visites += 1

        if estEtatFinal(etat_courant):
            return {
                "solution": chemin + [etat_courant],
                "nb_etats_generes": nb_etats_generes,
                "nb_noeuds_visites": nb_noeuds_visites,
                "temps": time.time() - debut
            }

        voisins = transitions(etat_courant)
        nouveaux = []

        for voisin in voisins:
            if transformer_etat(voisin) not in closedNodes:
                nouveaux.append((voisin, chemin + [etat_courant]))

        nb_etats_generes += len(nouveaux)
        freeNodes = nouveaux + freeNodes

    return None


# ========== DFS LIMITED ==========
def dfs_limite(etat_depart, limite):
    debut = time.time()
    freeNodes = [(etat_depart, [], 0)]
    closedNodes = set()

    nb_etats_generes = 1
    nb_noeuds_visites = 0

    while freeNodes:
        etat_courant, chemin, profondeur = freeNodes.pop(0)
        etat_tuple = transformer_etat(etat_courant)

        if etat_tuple in closedNodes:
            continue

        closedNodes.add(etat_tuple)
        nb_noeuds_visites += 1

        if estEtatFinal(etat_courant):
            return {
                "solution": chemin + [etat_courant],
                "nb_etats_generes": nb_etats_generes,
                "nb_noeuds_visites": nb_noeuds_visites,
                "temps": time.time() - debut
            }

        if profondeur < limite:
            voisins = transitions(etat_courant)
            nouveaux = []

            for voisin in voisins:
                if transformer_etat(voisin) not in closedNodes:
                    nouveaux.append((voisin, chemin + [etat_courant], profondeur + 1))

            nb_etats_generes += len(nouveaux)
            freeNodes = nouveaux + freeNodes

    return None


# ========== BFS ==========
def bfs(etat_depart):
    debut = time.time()
    freeNodes = [(etat_depart, [])]
    closedNodes = set()

    nb_etats_generes = 1
    nb_noeuds_visites = 0

    while freeNodes:
        etat_courant, chemin = freeNodes.pop(0)
        etat_tuple = transformer_etat(etat_courant)

        if etat_tuple in closedNodes:
            continue

        closedNodes.add(etat_tuple)
        nb_noeuds_visites += 1

        if estEtatFinal(etat_courant):
            return {
                "solution": chemin + [etat_courant],
                "nb_etats_generes": nb_etats_generes,
                "nb_noeuds_visites": nb_noeuds_visites,
                "temps": time.time() - debut
            }

        voisins = transitions(etat_courant)
        nouveaux = []

        for voisin in voisins:
            if transformer_etat(voisin) not in closedNodes:
                nouveaux.append((voisin, chemin + [etat_courant]))

        nb_etats_generes += len(nouveaux)
        freeNodes += nouveaux

    return None


# ========== HEURISTIC + A* ==========
def heuristique(t):
    h = 0
    for y in range(3):
        for x in range(3):
            if t[y][x] != 0 and t[y][x] != etat_final[y][x]:
                h += 1
    return h

def a_etoile(etat_depart):
    debut = time.time()
    open_list = []
    closedNodes = set()

    heapq.heappush(open_list, (heuristique(etat_depart), 0, etat_depart, []))

    nb_etats_generes = 1
    nb_noeuds_visites = 0

    while open_list:
        f, g, etat_courant, chemin = heapq.heappop(open_list)
        etat_tuple = transformer_etat(etat_courant)

        if etat_tuple in closedNodes:
            continue

        closedNodes.add(etat_tuple)
        nb_noeuds_visites += 1

        if estEtatFinal(etat_courant):
            return {
                "solution": chemin + [etat_courant],
                "nb_etats_generes": nb_etats_generes,
                "nb_noeuds_visites": nb_noeuds_visites,
                "temps": time.time() - debut
            }

        for voisin in transitions(etat_courant):
            if transformer_etat(voisin) not in closedNodes:
                g_new = g + 1
                f_new = g_new + heuristique(voisin)

                heapq.heappush(
                    open_list,
                    (f_new, g_new, voisin, chemin + [etat_courant])
                )

                nb_etats_generes += 1

    return None


# ========== CONSOLE TEST ==========
print("===== DFS =====")
resultat = dfs(etat_depart)

if resultat:
    print("Number of states generated :", resultat["nb_etats_generes"])
    print("Number of nodes visited :", resultat["nb_noeuds_visites"])
    print("Execution time :", resultat["temps"])
    print()


print("===== BFS =====")
resultat = bfs(etat_depart)

if resultat:
    print("Number of states generated :", resultat["nb_etats_generes"])
    print("Number of nodes visited :", resultat["nb_noeuds_visites"])
    print("Execution time :", resultat["temps"])
    print()


print("===== DFS Limited =====")
L = 3

while True:
    resultat = dfs_limite(etat_depart, L)

    if resultat:
        print("Solution found with L =", L)
        print("Number of states generated :", resultat["nb_etats_generes"])
        print("Number of nodes visited :", resultat["nb_noeuds_visites"])
        print("Execution time :", resultat["temps"])
        print()
        break

    L += 1


print("===== A* =====")
resultat = a_etoile(etat_depart)

if resultat:
    print("Number of states generated :", resultat["nb_etats_generes"])
    print("Number of nodes visited :", resultat["nb_noeuds_visites"])
    print("Execution time :", resultat["temps"])
    print()


# ========== GRAPHICAL INTERFACE (GUI) ==========
root = tk.Tk()
root.title("Taquin Solver")
root.geometry("600x600")

frame_taquin = tk.Frame(root)
frame_taquin.pack(pady=10)

buttons = []

for y in range(3):
    row = []

    for x in range(3):
        val = etat_depart[y][x]
        text = "" if val == 0 else str(val)

        btn = tk.Button(
            frame_taquin,
            text=text,
            width=6,
            height=3,
            font=("Cascadia Mono SemiBold", 14),
            bg="#4a73b5",
            fg="white"
        )

        btn.grid(row=y, column=x, padx=2, pady=2)
        row.append(btn)

    buttons.append(row)


btn_init = tk.Button(
    root,
    text="Initialisation",
    bg="#4a73b5",
    fg="white",
    width=20,
    height=2
)
btn_init.pack(pady=10)

frame_algos = tk.Frame(root)
frame_algos.pack(pady=10)

btn_dfs = tk.Button(frame_algos, text="DFS", width=10, bg="#4a73b5", fg="white")
btn_bfs = tk.Button(frame_algos, text="BFS", width=10, bg="#4a73b5", fg="white")
btn_dfs_l = tk.Button(frame_algos, text="DFS Limited", width=12, bg="#4a73b5", fg="white")
btn_astar = tk.Button(frame_algos, text="A*", width=10, bg="#4a73b5", fg="white")

btn_dfs.grid(row=0, column=0, padx=5)
btn_bfs.grid(row=0, column=1, padx=5)
btn_dfs_l.grid(row=0, column=2, padx=5)
btn_astar.grid(row=0, column=3, padx=5)

frame_results = tk.Frame(root)
frame_results.pack(pady=20)

labels = ["visited nodes", "generated states", "Execution time"]
algos = ["DFS", "BFS", "DFS Limited", "A*"]

entries = {}

for i, label in enumerate(labels):
    tk.Label(
        frame_results,
        text=label,
        width=15,
        bg="#4a73b5",
        fg="white"
    ).grid(row=i, column=0, padx=5, pady=5)

    for j, algo in enumerate(algos):
        entry = tk.Label(
            frame_results,
            text="---",
            width=12,
            bg="lightgray"
        )

        entry.grid(row=i, column=j + 1, padx=5, pady=5)

        entries[(label, algo)] = entry

# ========== BUTTON ACTIONS ==========
def run_dfs():
    resultat = dfs(etat_depart)

    entries[("visited nodes", "DFS")].config(
        text=resultat["nb_noeuds_visites"]
    )
    entries[("generated states", "DFS")].config(
        text=resultat["nb_etats_generes"]
    )
    entries[("Execution time", "DFS")].config(
        text=round(resultat["temps"], 4)
    )

def run_bfs():
    resultat = bfs(etat_depart)

    entries[("visited nodes", "BFS")].config(
        text=resultat["nb_noeuds_visites"]
    )
    entries[("generated states", "BFS")].config(
        text=resultat["nb_etats_generes"]
    )
    entries[("Execution time", "BFS")].config(
        text=round(resultat["temps"], 4)
    )

def run_dfs_limite():
    L = 3

    while True:
        resultat = dfs_limite(etat_depart, L)

        if resultat:
            break

        L += 1

    entries[("visited nodes", "DFS Limited")].config(
        text=resultat["nb_noeuds_visites"]
    )
    entries[("generated states", "DFS Limited")].config(
        text=resultat["nb_etats_generes"]
    )
    entries[("Execution time", "DFS Limited")].config(
        text=round(resultat["temps"], 4)
    )

def run_astar():
    resultat = a_etoile(etat_depart)

    entries[("visited nodes", "A*")].config(
        text=resultat["nb_noeuds_visites"]
    )
    entries[("generated states", "A*")].config(
        text=resultat["nb_etats_generes"]
    )
    entries[("Execution time", "A*")].config(
        text=round(resultat["temps"], 4)
    )

btn_dfs.config(command=run_dfs)
btn_bfs.config(command=run_bfs)
btn_dfs_l.config(command=run_dfs_limite)
btn_astar.config(command=run_astar)

# ========== LAUNCHING ==========
root.mainloop()