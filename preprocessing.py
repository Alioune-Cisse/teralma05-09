import numpy as np
import pandas as pd
from pulp import *

def read_data(file, sep=",", header=0) -> pd.DataFrame:
    try:
        data = pd.read_excel(file, header=[header])
    except:
        try:
            data = pd.read_csv(file, encoding="ISO-8859-1", sep=sep)
        except Exception as e:
            print(e)
    return data

def clean_data(df: pd.DataFrame, col) -> pd.DataFrame:
    df = df.drop_duplicates().apply(lambda x: x.astype(str).str.lower())
    df = df[(df[col] != "nan") & (df[col] != "#value!")]
    return df.apply(lambda x: x.str.strip())

def get_palier(df:pd.DataFrame, valeur:float) -> str:
    paliers = df.iloc[-1:,2:].transpose().astype('float')
    try:
        palier = paliers.index[paliers.iloc[:,0]>=valeur][0]
    except Exception as e:
        if(valeur > paliers.iloc[-1,0]):
            palier = paliers.index[-1]
        elif(valeur < paliers.iloc[0,0]):
            palier = paliers.index[0]
        else:
            print(e)
    return palier

def choix_categ(df: pd.DataFrame, choix: list) -> dict:
    all_choice = df.iloc[:,1].unique().tolist()
    choices = [x.lower().strip() for x in choix]
    choix_possibles = list(set(all_choice) & set(choices))
    return {"X"+str(i+1): choix_possibles[i] for i in range(len(choix_possibles))}

def constraints(df: pd.DataFrame, budget: int, choice: list, invites: int) -> dict:
    palier = get_palier(df, budget)
    #print(palier)
    contraintes = {"egalites": [], "inegalites": []}
    choix = choix_categ(df, choice)

    for it, elt in list(choix.items()):
        prix = float(df[df.iloc[:,1] == elt][palier])
        #valeurs.append(prix)
        if list(df[df.iloc[:,1] == elt].iloc[:,0])[0] in ["super marché", "produits beautés"]:
            contraintes["egalites"].append({elt: prix})
        else:
            contraintes["inegalites"].append({elt: prix})


    return contraintes


def pulp_optimize(df: pd.DataFrame, budget: int, choice: list, invites: int) -> dict:
    contraintes = constraints(df, budget, choice, invites)
    choix = choix_categ(df, choice)

    # Initialiser les variables
    variables = [LpVariable(i, lowBound=0, cat=LpInteger) for i in choix.keys()]

    # Initialiser le problème
    probleme = LpProblem(name='Répartition budget', sense=LpMaximize)

    # Ajouter contraintes budgéétaire
    contrainte_budget = LpConstraint(e=sum(variables), sense=LpConstraintEQ, name='contrainte_budgétaire', rhs=budget)
    probleme.add(contrainte_budget)

    for elt in variables:
        # Ajouter contraintes des valeurs non nulles
        # contrainte = LpConstraint(e=elt, sense=LpConstraintGE, name='not null contrainte ' + choix[elt.name], rhs=0)
        # probleme.add(contrainte)

        # Récupérer listes contraintes égalités et inégalités
        contraintes_egalites = set().union(*(d.keys() for d in contraintes["egalites"]))
        contraintes_inegalites = set().union(*(d.keys() for d in contraintes["inegalites"]))

        if choix[elt.name] in contraintes_inegalites:
            for sub in contraintes["inegalites"]:
                try:
                    valeur = sub[choix[elt.name]]
                except:
                    pass

            # Ajouter contrainte d'inégalités
            contrainte = LpConstraint(e=elt, sense=LpConstraintLE, name='contrainte ' + choix[elt.name], rhs=valeur)
            probleme.add(contrainte)

            contrainte_ = LpConstraint(e=elt, sense=LpConstraintGE, name='great contrainte ' + choix[elt.name],
                                       rhs=valeur // 4)
            probleme.add(contrainte_)

        elif choix[elt.name] in contraintes_egalites:
            for sub in contraintes["egalites"]:
                try:
                    valeur = sub[choix[elt.name]]
                except:
                    pass

            # Ajouter contraintes d'égalités
            contrainte = LpConstraint(e=elt, sense=LpConstraintEQ, name='contrainte ' + choix[elt.name], rhs=valeur)
            probleme.add(contrainte)

    # Ajouter la fonction objectif à maximiser au problème
    fonction_objectif = LpAffineExpression(e=sum(variables))
    probleme.setObjective(fonction_objectif)

    # Initialiser le solveur
    solver = PULP_CBC_CMD(timeLimit=20, msg=True)
    probleme.solve(solver=solver)

    # print(probleme)
    repartitions = {}
    for val in variables:
        repartitions[choix[val.name]] = round(val.value())
    repartitions["Autres"] = budget - sum(repartitions.values())
    return repartitions