"""
TEMPLATE GENERAL POUR UN PROGRAMME MILP AVEC GUROBI

Structure :
1. Importation
2. Donnees / Parametres
3. Modele
4. Variables de decision
5. Contraintes
6. Fonction objectif
7. Optimisation
8. Extraction des resultats
9. Export (optionnel)
"""

# ----------------------------------------
# 1. IMPORTATION
# ----------------------------------------
import gurobipy as gp
from gurobipy import GRB


# ----------------------------------------
# 2. DONNEES ET PARAMETRES
# ----------------------------------------
# Definir ici tous les ensembles, parametres, donnees

# Exemple de sets
P = ["prod_1","prod_2","prod_3","prod_4","prod_5"] #P=5
U = ["usine_1","usine_2"]                          #U=2
M = ["mp_1","mp_2","mp_3","mp_4"]                  #M=4
F = ["four_1","four_2","four_3"]                   #F=3

#Paramètres de coût
# Cout de production par Usine
Cost_prod={("prod_1","usine_1"):2, ("prod_2","usine_1"):6, ("prod_3","usine_1"):3, ("prod_4","usine_1"):7, ("prod_5","usine_1"):5,
          ("prod_1","usine_2"):5, ("prod_2","usine_2"):3, ("prod_3","usine_2"):8, ("prod_4","usine_2"):2, ("prod_5","usine_2"):6}
# Cout de la matiere premiere par fournisseur
Cost_MPremiere={("four_1","mp_1"):1, ("four_1","mp_2"):4, ("four_1","mp_3"):3, ("four_1","mp_4"):5,
                ("four_2","mp_1"):3, ("four_2","mp_2"):2, ("four_2","mp_3"):7, ("four_2","mp_4"):6,
                ("four_3","mp_1"):2, ("four_3","mp_2"):4, ("four_3","mp_3"):3, ("four_3","mp_4"):2}
#Cout d'installation
Cost_install_usines={"usine_1": 10,"usine_2": 11}
Cost_select_fournisseurs={"four_1": 10,"four_2": 11,"four_3": 13}

#Ratio Matieres premiere par produit
ratio_produit_MP_kg = {("prod_1","mp_1"):5,("prod_1","mp_2"):0,("prod_1","mp_3"):1,("prod_1","mp_4"):19,
                      ("prod_2","mp_1"):7,("prod_2","mp_2"):0,("prod_2","mp_3"):15,("prod_2","mp_4"):13,
                      ("prod_3","mp_1"):0,("prod_3","mp_2"):11,("prod_3","mp_3"):12,("prod_3","mp_4"):1,
                      ("prod_4","mp_1"):2,("prod_4","mp_2"):9,("prod_4","mp_3"):0,("prod_4","mp_4"):1,
                      ("prod_5","mp_1"):6,("prod_5","mp_2"):2,("prod_5","mp_3"):1,("prod_5","mp_4"):0}

#Definition des capacités
#Capacité maximal de prodcution par site
capa_prod_usine = {("usine_1","prod_1"):546,("usine_1","prod_2"):0,("usine_1","prod_3"):162,("usine_1","prod_4"):321,("usine_1","prod_5"):120,
                   ("usine_2","prod_1"):406,("usine_2","prod_2"):95,("usine_2","prod_3"):432,("usine_2","prod_4"):0,("usine_2","prod_5"):540}

#Capacité Matière première par fournisseurs
capa_appro_fourn = {("four_1","mp_1"):0,("four_1","mp_2"):112,("four_1","mp_3"):62,("four_1","mp_4"):210,
                  ("four_2","mp_1"):352,("four_2","mp_2"):0,("four_2","mp_3"):65,("four_2","mp_4"):113,
                  ("four_3","mp_1"):221,("four_3","mp_2"):872,("four_3","mp_3"):0,("four_3","mp_4"):110}

# ----------------------------------------
# 3. CRÉATION DU MODÈLE
# ----------------------------------------
model = gp.Model("modele_optimisation_V0")
#Le commit est fait


# ----------------------------------------
# 4. VARIABLES DE DÉCISION
# ----------------------------------------
# CONTINUOUS, INTEGER, BINARY, SEMI-CONTINUOUS, SEMI-INTEGER, etc.

# Exemple : quantité expédiée
x = model.addVars(I, J, vtype=GRB.CONTINUOUS, name="x")

# Exemple : centre ouvert ou non
y = model.addVars(I, vtype=GRB.BINARY, name="y")


# ----------------------------------------
# 5. CONTRAINTES DU MODÈLE
# ----------------------------------------

# 5.1 Contraintes de capacité
for i in I:
    model.addConstr(
        gp.quicksum(x[i, j] for j in J) <= capacity[i] * y[i],
        name=f"cap[{i}]"
    )

# 5.2 Satisfaction de la demande
for j in J:
    model.addConstr(
        gp.quicksum(x[i, j] for i in I) >= demand[j],
        name=f"demand[{j}]"
    )

# 5.3 Toute autre contrainte spécifique
# Exemple :
# model.addConstr(x["A","X"] <= 10, name="example_limit")


# ----------------------------------------
# 6. FONCTION OBJECTIF
# ----------------------------------------
# Minimiser le coût total

model.setObjective(
    gp.quicksum(cost[i, j] * x[i, j] for i in I for j in J),
    GRB.MINIMIZE
)


# ----------------------------------------
# 7. OPTIMISATION
# ----------------------------------------
model.optimize()


# ----------------------------------------
# 8. EXTRACTION DES RÉSULTATS
# ----------------------------------------
if model.status == GRB.OPTIMAL:

    print("\n=== SOLUTION OPTIMALE ===\n")

    print("--- Variables x[i,j] ---")
    for i, j in x:
        if x[i, j].X > 1e-6:  # éviter les +0.0
            print(f"x[{i},{j}] = {x[i,j].X}")

    print("\n--- Variables y[i] ---")
    for i in y:
        print(f"y[{i}] = {y[i].X}")

else:
    print("Aucune solution optimale trouvée.")


# ----------------------------------------
# 9. EXPORT DU MODÈLE (OPTIONNEL)
# ----------------------------------------
# Pour exporter le modèle sous forme LP ou MPS :
# model.write("modele.lp")
# model.write("modele.mps")
