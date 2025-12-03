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
from gurobipy import GRB, quicksum

# ----------------------------------------
# 2. DONNEES ET PARAMETRES
# ----------------------------------------
# Definir ici tous les ensembles, parametres, donnees

# Exemple de sets
PRODUITS = ["prod_1","prod_2","prod_3","prod_4","prod_5"] #P=5
USINES = ["usine_1","usine_2"]                          #U=2
MATIERES_PREMIERES = ["mp_1","mp_2","mp_3","mp_4"]                  #M=4
FOURNISSEURS = ["four_1","four_2","four_3"]                   #F=3
BigM = 1000

#Parametres de cout
# Cout de production par Usine  #cost_prod(U?P)
cost_prod={("usine_1","prod_1"):2, ("usine_1","prod_2"):6, ("usine_1","prod_3"):3, ("usine_1""prod_4"):7, ("usine_1""prod_5"):5,
          ("usine_2","prod_1"):5, ("usine_2","prod_2"):3, ("usine_2","prod_3"):8, ("usine_2","prod_4"):2, ("usine_2","prod_5"):6}
# Cout de la matiere premiere par fournisseur  ###cosMP(f,r)
cost_MPremiere={("four_1","mp_1"):1, ("four_1","mp_2"):4, ("four_1","mp_3"):3, ("four_1","mp_4"):5,
                ("four_2","mp_1"):3, ("four_2","mp_2"):2, ("four_2","mp_3"):7, ("four_2","mp_4"):6,
                ("four_3","mp_1"):2, ("four_3","mp_2"):4, ("four_3","mp_3"):3, ("four_3","mp_4"):2}
#Cout d installation ###costinstal(u)
cost_install_usines={"usine_1": 10,"usine_2": 11}
cost_select_fournisseurs={"four_1": 10,"four_2": 11,"four_3": 13}

#Ratio Matieres premiere par produit ###ratio_pro_mp(p,r)
ratio_pro_mp = {("prod_1","mp_1"):5,("prod_1","mp_2"):0,("prod_1","mp_3"):1,("prod_1","mp_4"):19,
                      ("prod_2","mp_1"):7,("prod_2","mp_2"):0,("prod_2","mp_3"):15,("prod_2","mp_4"):13,
                      ("prod_3","mp_1"):0,("prod_3","mp_2"):11,("prod_3","mp_3"):12,("prod_3","mp_4"):1,
                      ("prod_4","mp_1"):2,("prod_4","mp_2"):9,("prod_4","mp_3"):0,("prod_4","mp_4"):1,
                      ("prod_5","mp_1"):6,("prod_5","mp_2"):2,("prod_5","mp_3"):1,("prod_5","mp_4"):0}

#Definition des capacites
#Capacite maximal de prodcution par site ###capa_prod(u,p)
capa_prod = {("usine_1","prod_1"):546,("usine_1","prod_2"):0,("usine_1","prod_3"):162,("usine_1","prod_4"):321,("usine_1","prod_5"):120,
                   ("usine_2","prod_1"):406,("usine_2","prod_2"):95,("usine_2","prod_3"):432,("usine_2","prod_4"):0,("usine_2","prod_5"):540}

#Capacite Matiere premiere par fournisseurs ###capa_appro(f,r)
capa_appro = {("four_1","mp_1"):0,("four_1","mp_2"):112,("four_1","mp_3"):62,("four_1","mp_4"):210,
                  ("four_2","mp_1"):352,("four_2","mp_2"):0,("four_2","mp_3"):65,("four_2","mp_4"):113,
                  ("four_3","mp_1"):221,("four_3","mp_2"):872,("four_3","mp_3"):0,("four_3","mp_4"):110}


#DEMANDE DE PRODUCTION 
Dmde = {"prod_1" : 101,
       "prod_2" : 92,
       "prod_3" : 122,
       "prod_4" : 181,
       "prod_5" : 178}

# ----------------------------------------
# 3. CREATION DU MODELE
# ----------------------------------------
model = gp.Model("modele_optimisation_V0")
#Le commit est fait


# ----------------------------------------
# 4. VARIABLES DE DECISION
# ----------------------------------------
# CONTINUOUS, INTEGER, BINARY, SEMI-CONTINUOUS, SEMI-INTEGER, etc.

#Variable binaire // choix des usines a ouvrir ou a fermer // fournisseurs a selectionner. U(u)
U_SELECT = {u: model.addVar(vtype=GRB.BINARY, name=f"U_SELECT{u}") for u in USINES}

#Selection de fournisseurs  F_SELECT(f)
F_SELECT = {f: model.addVar(vtype=GRB.BINARY, name=f"F_CHOOSE{f}") for f in FOURNISSEURS}

# Quantite de MP a commander chez chaque fournisseurs ####Q_APPRO(f,r)
Q_APPRO = {(f,r) : model.addVar(lb=0, vtype=GRB.CONTINUOUS, name=f"Q_MP{f}_{r}") for f in FOURNISSEURS for r in MATIERES_PREMIERES}

# Quantite a produire par site   ####Q_PROD(u,p)
Q_PROD = {(u,p) : model.addVar(lb=0, vtype=GRB.CONTINUOUS, name=f"Q_PROD{u}_{p}") for u in USINES for p in PRODUITS}


# ----------------------------------------
# 5. CONTRAINTES DU MODELE
# ----------------------------------------

# 5.1 Contraintes de capacite production usines Q_PROD(u,p) <=capa_prod(u,p)*U_SELECT(u)
for u in USINES:
    for p in PRODUITS:
        model.addConstr(Q_PROD[u,p] <= capa_prod[u,p]*U_SELECT[u], name=f"cap_prod_{u}_{p}")
#BIG M pour les variables continues
for u in USINES:
    for p in PRODUITS:
        model.addConstr(Q_PROD[u,p] <= BigM*U_SELECT[u], name=f"sup_prod_{p}")

# 5.11 Contraintes de capacite approv fournisseurs Q_APPRO(f,r) <=capa_appro(f,r)*F_SELECT(f)
for f in FOURNISSEURS:
    for r in MATIERES_PREMIERES:
        model.addConstr(Q_APPRO[f,r] <= capa_appro[f,r]*F_SELECT[f], name=f"cap_appro_{f}_{r}")
#BIG M pour les quantite de Matiere premieres
for f in FOURNISSEURS:
    for r in MATIERES_PREMIERES:
        model.addConstr(Q_APPRO[f,r] <= BigM*F_SELECT[f], name=f"sup_appro_{r}")

#Disponibilite de la matiere premiere
for p in PRODUITS:
    for r in MATIERES_PREMIERES:
        qte_total_mp_prod = quicksum(Q_PROD[u,p]*ratio_pro_mp[p,r] for u in USINES)
        qte_total_mp_appro = quicksum(Q_APPRO[f,r] for f in FOURNISSEURS)
        model.addConstr(qte_total_mp_prod <= qte_total_mp_appro, name=f"cap_MP_{p}")

# 5.2 Satisfaction de la demande
for p in PRODUITS:
    prod_total = quicksum(Q_PROD[u,p] for u in USINES)
    model.addConstr(Dmde <= prod_total, name=f"prod_{u}")

# 5.3 Contraintes de non negativites
for u in USINES:
    for p in PRODUITS:
        model.addConstr(Q_PROD[u,p] >=0, name="positif constraint")

for f in FOURNISSEURS:
    model.addConstr(F_SELECT[f] >=0, name="positif constraint")

for u in USINES:
    model.addConstr(U_SELECT[u] >=, name="positif constraint")

for f in FOURNISSEURS:
    for r in MATIERES_PREMIERES:
        model.addConstr(Q_APPRO[f,r] >=0, name="positif constraint")

# 5.3 Toute autre contrainte spécifique
# Exemple :
# model.addConstr(x["A","X"] <= 10, name="example_limit")


# ----------------------------------------
# 6. FONCTION OBJECTIF
# ----------------------------------------

#cout d'achat de la matière première
APPROV_cost = quicksum(Q_APPRO[f,r]*cost_MPremiere[f,r] for f in FOURNISSEURS for r in MATIERES_PREMIERES)

#cout total de production 
PROD_cost = quicksum(Q_PROD[u,p]*cost_prod[u,p] for u in USINES for p in PRODUITS)

TOTAL_cost = APPROV_cost + PROD_cost 

# Minimiser le coût total
model.setObjective(TOTAL_cost,GRB.MINIMIZE)


# ----------------------------------------
# 7. OPTIMISATION
# ----------------------------------------
model.optimize()


# ----------------------------------------
# 8. EXTRACTION DES RESULTATS
# ----------------------------------------
if model.status == GRB.OPTIMAL:

    print("\n=== SOLUTION OPTIMALE ===\n")

    print("--- Variables x[i,j] ---")
    for f, r in Q_APPRO:
        if Q_APPRO[f, r].X > 1e-6:  # eviter les +0.0
            print(f"Q_APPRO[{f},{r}] = {Q_APPRO[f,r].X}")

    print("\n--- Variables F_SELECT[f] ---")
    for f in F_SELECT:
        print(f"F_SELECT[{f}] = {F_SELECT[f].X}")

else:
    print("Aucune solution optimale trouvée.")


# ----------------------------------------
# 9. EXPORT DU MODÈLE (OPTIONNEL)
# ----------------------------------------
# Pour exporter le modèle sous forme LP ou MPS :
# model.write("modele.lp")
# model.write("modele.mps")



