"""
PySHS - Faciliter le traitement de données en SHS
Langue : Français
Dernière modification : 22/02/2022
Auteur : Émilien Schultz
Contributeurs :
- Matthias Bussonnier
- Léo Mignot


Pour le moment le module PySHS comprend :

- une fonction de description du tableau
- une fonction de comparaison de deux colonnes pour voir le recodage
- une fonction pour le tri à plat (pondéré)
- une fonction pour les tableaux croisés (pondérés)
- une fonction pour des tableaux croisés multiples (pondérés) afin de voir le lien variable dépendante/indépendantes
- une fonction pour un tableau croisé à trois variables pour en contrôler une lors de l'analyse
- une fonction de mise en forme des résultats de la régression logistique de Statsmodel pour avoir un tableau avec les références
- une fonction pour produire la régression logistique binomiale

Temporairement :
- une fonction de mise en forme différente de la régression logistique, incluant les effets d'interaction (beta)
- une fonction de test du ratio de vraissemblance de deux régressions

À faire :
- cercle de corrélation pour l'ACP
- vérifier la régression logistique pour des variables quantitatives & effets d'interaction


"""


import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

from scipy.stats import chi2_contingency
from scipy.stats.distributions import chi2

import statsmodels.api as sm
import statsmodels.formula.api as smf

import plotly.graph_objects as go
import plotly.express as pex



__version__ = "0.2.1"


def description(df):
    """
    Description d'un tableau de données

    Parameters
    ----------
    df : DataFrame

    Returns
    -------
    DataFrame
        Description des variables du tableau

    """
    tableau = []
    for i in df.columns:
        if is_numeric_dtype(df[i]):
            l = [i,"Numérique",None,None,round(df[i].mean(),2),round(df[i].std(),2),pd.isnull(df[i]).sum()]
        else:
            l = [i,"Catégorielle",len(df[i].unique()),df[i].mode().iloc[0],None,None,pd.isnull(df[i]).sum()]
        tableau.append(l)
    tableau = pd.DataFrame(tableau,
            columns=["Variable","Type","Modalités","Mode",
                     "Moyenne","Écart-type","Valeurs manquantes"]).set_index("Variable")
    return tableau.fillna(" ")


def tri_a_plat(df, variable, weight=False, ro=1):
    """
    Tri à plat pour une variable qualitative pondérée ou non.

    Parameters
    ----------
    df : DataFrame
    variable : string
        column name
    weight : string (optionnal)
        column name for the weigthing
    ro: int (optionnal)
        number of digits to round

    Returns
    -------
    DataFrame
        Tri à plat mis en forme

    Comments
    --------
    Pas de gestion des valeurs manquantes actuellement

    """
    # Tester le format de l'entrée
    if not isinstance(df, pd.DataFrame):
        print("Attention, ce n'est pas un tableau Pandas")
        return None
    if variable not in df.columns:
        print("Attention, la variable n'est pas dans le tableau")
        return None

    # Cas de données non pondérées
    if not weight:
        effectif = df[variable].value_counts()
        pourcentage = round(100 * df[variable].value_counts(normalize=True), ro)
        tableau = pd.DataFrame([effectif, pourcentage]).T
        tableau.columns = ["Effectif", "Pourcentage (%)"]

    # Cas des données pondérées
    else:
        effectif = round(df.groupby(variable)[weight].sum(), ro)
        total = effectif.sum()
        pourcentage = round(100 * effectif / total, ro)
        tableau = pd.DataFrame([effectif, pourcentage]).T
        tableau.columns = ["Effectif redressé", "Pourcentage (%)"]

    # Retourner le tableau ordonné en forçant l'index en texte
    tableau.index = [str(i) for i in tableau.index]
    tableau = tableau.sort_index()

    # Ajout de la ligne total
    tableau.loc["Total"] = [effectif.sum(),round(pourcentage.sum(),ro)]

    return tableau


def verification_recodage(corpus,c1,c2):
    """
    Comparer une variable recodée qualitatives avec la variable initiale
    

    Parameters
    ----------
    corpus : DataFrame
    c1 : str
        column name
    c2 : str
        column name

    Returns
    -------
    None

    Comments
    --------
    Pour le moment uniquement de l'affichage

    """
    
    # Vérifier que les deux colonnes sont distinctes
    if c1==c2:
        print("Ce sont les mêmes colonnes")
        return None
    
    # Vérifier que les deux variables sont bien dans le corpus
    if c1 not in corpus.columns:
        print("La variable %s n'est pas dans le tableau" % c1)
        return None
    if c2 not in corpus.columns:
        print("La variable %s n'est pas dans le tableau" % c2)
        return None
    
    # Vérification s'il y a des valeurs manquantes dans la colonne d'arrivée
    s = pd.isnull(corpus[c2]).sum()
    if s>0:
        print("Il y a %d valeurs nulles dans la colonne recodée"%s)
    
    # renommer et modifier les labels pour éviter les homonymies
    df = corpus[[c1,c2]].copy()
    df[c1] = df[c1].fillna("None").apply(lambda x : str(x)+"(1)")
    df[c2] = df[c2].fillna("None").apply(lambda x : str(x)+"(2)")
    
    # tableau croisé des deux variables
    t = pd.crosstab(df[c2],df[c1])
    
    # création des relations
    t_flat = t.unstack() #Déplier le tableau croisé
    links = []
    for i,j in zip(t_flat.index,t_flat):
        links.append([i[0],i[1],j])

    # éléments pour définir le diagramme de Sankey avec plotly
    all_nodes = list(t.index) + list(t.columns)
    source_indices = [all_nodes.index(i[0]) for i in links]
    target_indices = [all_nodes.index(i[1]) for i in links]
    values = [i[2] for i in links]
    node_colors = ["orange"]*len(t.index) + ["blue"]*len(t.columns)

    # Création de la figure
    fig = go.Figure(data=[go.Sankey(
        # Define nodes
        node = dict(
          label =  all_nodes,
          color =  node_colors
        ),

        # Add links
        link = dict(
          source =  source_indices,
          target =  target_indices,
          value =  values,
          #color = edge_colors,
    ))])

    fig.update_layout(title_text="Colonne %s à colonne %s" % (c1,c2),
                      font_size=10,height=500,width=600)
    fig.show()
    return None



def tableau_croise(df, c1, c2, weight=False, p=False, debug=False, ro=1):
    """
    Tableau croisé pour deux variables qualitatives, avec
    présentation des pourcentages par ligne.

    Parameters
    ----------
    df : DataFrame
    c1,c2 : string
        column names
    weight : string (optionnel),
        column name for weights
    p : bool (optionnel)
        calculate the chi2 test for the table
    debug : bool (optionnel)
        return intermediate tables (raw)
    ro: int (optionnal)
        number of digits to round

    Returns
    -------
    crosstab : DataFrame
        Tableau croisé mis en forme

    Comments
    --------
    Pas de gestion des valeurs manquantes actuellement, qui ne sont donc pas comptées

    """

    # Tester le format de l'entrée
    if not isinstance(df, pd.DataFrame):
        print("Attention, ce n'est pas un tableau Pandas")
        return None
    if c1 not in df.columns or c2 not in df.columns:
        print("Attention, une des variables n'est pas dans le tableau")
        return None

    # Si les données ne sont pas pondérées, création d'une pondération unitaire
    if not weight:
        df = df.copy()  # Pour ne pas modifier l'objet
        df["weight"] = 1
        weight = "weight"

    # Tableau effectif avec distribution marginales
    t_absolu = round(
        pd.crosstab(df[c1], df[c2], df[weight], aggfunc=sum, margins=True), ro
    ).fillna(0)
    # Tableau pourcentages par ligne (enlever la colonne totale)
    t_pourcentage = t_absolu.drop("All",axis=1).apply(lambda x: round(100 * x / sum(x),ro), axis=1)

    # Mise en forme du tableau avec les pourcentages
    t = t_absolu.copy()
    for i in range(0, t_pourcentage.shape[0]):
        for j in range(0, t_pourcentage.shape[1]):
            t.iloc[i, j] = (
                str(t_absolu.iloc[i, j])
                + " ("
                + str(round(t_pourcentage.iloc[i, j], ro))
                + "%)"
            )

    # Ajout des 100% pour la ligne colonne
    t["All"] = t["All"].apply(lambda x : "{} (100%)".format(x))

    # Traduire All par Total
    t.columns = list(t.columns)[:-1]+["Total"]
    t.index = list(t.index)[:-1]+["Total"]
            
    # Retour des tableaux non mis en forme
    if debug:
        return t, t_absolu, t_pourcentage

    # Retour du tableau avec la p-value
    if p:
        return t, chi2_contingency(t_absolu.drop("All").drop("All",axis=1))[1]

    # Retour du tableau mis en forme
    return t

def tableau_croise_controle(df, cont, c, r, weight=False, chi2=False):
    """
    Tableau croisé avec une variable de contrôle en plus

    Parameters
    ----------
    df : DataFrame
    cont : string
        column name for control variable
    c,r : strings
        column names for crosstable
    weight : string (optionnel),
        column name for weights

    Returns
    -------
    crosstab : DataFrame
        Tableau croisé mis en forme

    Comments
    --------
    Pas de gestion des valeurs manquantes actuellement, qui ne sont donc pas comptées

    """

    # Tester le format de l'entrée
    if not isinstance(df, pd.DataFrame):
        print("Attention, ce n'est pas un tableau Pandas")
        return None
    if cont not in df.columns or c not in df.columns or r not in df.columns:
        print("Attention, une des variables n'est pas dans le tableau")
        return None

    # Si les données ne sont pas pondérées, création d'une pondération unitaire
    if not weight:
        df = df.copy()  # Pour ne pas modifier l'objet
        df["weight"] = 1
        weight = "weight"

    tab = {}
    mod = df[cont].unique() # modalités de contrôle
    for i in mod:
        d = df[df[cont]==i] # sous-ensemble
        t,p = tableau_croise(d, c, r, weight, p=True)
        # Mettre Total plutôt que All dans le tableau
        t.columns = list(t.columns)[:-1]+["Total"]
        t.index = list(t.index)[:-1]+["Total"]

        # Construire le tableau avec ou sans le chi2
        if chi2:
            tab[i + " (p = %.3f)" % p] = t
        else:
            tab[i] = t
        
    # Mise en forme du tableau
    tab = pd.concat(tab)
    tab.index.names = [cont,c]

    # Retour du tableau mis en forme
    return tab


def tableau_croise_multiple(df, dep, indeps, weight=False, chi2=True, axis = 0, ss_total=True):
    """
    Tableau croisé multiple une variable dépendantes/plusieurs indépendantes.

    Parameters
    ----------
    df : DataFrame
    dep : string ou dic {nom:label}
        nom de la variable dépendante en colonne
    indeps : dict ou list
        dictionnaire des variables indépendantes et leur label pour le tableau
    weight : optionnel, colonne de la pondération
    axis : optionnel, orientation des pourcentages, axis = 1 pour les colonnes
    ss_total : optionnel, présence de sous totaux

    Returns
    -------
    DataFrame
        mis en forme du tableau croisé avec pourcentages par ligne et tri croisé
        sur total p-value indicative par un chi2

    Comments
    --------
    Manque une colonne tri à plat

    """

    # Tester le format de l'entrée
    if not isinstance(df, pd.DataFrame):
        print("Attention, ce n'est pas un tableau Pandas")
        return None
    if (type(indeps)!=list) and (type(indeps)!=dict):
        print("Les variables ne sont pas renseignées sous le bon format")
        return None
    if dep not in df.columns:
        print("La variable {} n'est pas dans le tableau".format(dep))
        return None
    for i in indeps:
        if i not in df.columns:
            print("La variable {} n'est pas dans le tableau".format(i))
            return None        

    # Noms des variables
    if type(indeps) == list:
        indeps = {i:i for i in indeps}
        
    t_all = {}

    # Compteur des totaux par croisement
    check_total = []

    # Boucle sur les variables indépendantes
    for i in indeps:
        # Tableau croisé pondéré (deux orientations possibles)
        if axis == 0:
            t, p = tableau_croise(df, i, dep, weight, p=True)
        else:
            t, p = tableau_croise(df, dep, i, weight, p=True)
            t = t.T

        # Enlever les sous-totaux si besoin
        if not ss_total:
            t = t.drop("Total")

        dis = tri_a_plat(df,i,weight = weight)

        check_total.append(t.iloc[-1,-1])
        t["Distribution"] = dis["Pourcentage (%)"].apply(lambda x : "{}%".format(x))
        if chi2:
            t_all[indeps[i] + " (p = %.03f)" % p] = t
        else:
            t_all[indeps[i]] = t
            
    # Création d'un DataFrame
    t_all = pd.concat(t_all)
    t_all.columns.name = ""
    t_all.index.names = ["Variable", "Modalités"]
    t_all.columns.values[-2] = "Total"

    # Alerter sur les totaux différents
    if len(set(check_total))!=1:
        print("Attention, les totaux par tableaux sont différents (valeurs manquantes)")

    return t_all



def significativite(x, digits=4):
    """
    Mettre en forme la p-value

    Parameters
    ----------
    x : float, p-value

    Returns
    -------
    string
        p-value with fixed number of decimals and stars
    """

    # Tester le format
    if pd.isnull(x):
        return None

    # Arrondir
    x = round(x, digits)

    # Retourner la valeur avec le nombre d'étoiles associées
    if x < 0.001:
        return str(x) + "***"
    if x < 0.01:
        return str(x) + "**"
    if x < 0.05:
        return str(x) + "*"

    # Retourner la p-value mise en forme
    return str(x)


def tableau_reg_logistique(regression, data, indep_var, sig=True):
    """
    Mise en forme des résultats de la régression logistique issue de Statsmodel
    pour une lecture habituelle en SHS. 

    Prend en compte aussi les effets d'interaction *

    Parameters
    ----------
    regression: statsmodel object from GLM
    df: DataFrame
     Database to extract modalities
    indep_var: dictionnary
     column of the variable / Label to use in the table
    sig: bool (optionnal)

    Returns
    -------
    DataFrame : table for the results

    Comments
    --------
    For the moment, intercept is in the middle of the table ...

    Examples
    --------
    The dictionnary ind_var should be defined as {var:label}

    >>> import statsmodels.api as sm
    >>> modele = smf.glm(formula=f, data=data, family=sm.families.Binomial(),
                 freq_weights=data["weight"])
    >>> reg = modele.fit()
    >>> tableau_reg_logistique(reg,data,ind_var,sig=True)

    """

    # Séparation des variables et des effets d'interaction
    indep_var_unique = {}
    for v in indep_var:
        if "*" in v: #cas d'une interaction
            for e in v.split("*"):
                if not e.strip() in indep_var_unique:
                    indep_var_unique[e.strip()] =  e.strip()
        else:
            indep_var_unique[v] = indep_var[v]


    # Mise en forme du tableau général OR /
    table = np.exp(regression.conf_int())
    table["Odds Ratio"] = round(np.exp(regression.params), 2)
    table["p"] = round(regression.pvalues, 3)
    table["IC 95%"] = table.apply(
        lambda x: "%.2f [%.2f-%.2f]" % (x["Odds Ratio"], x[0], x[1]), axis=1
    )

    # Ajout de la significativité
    if sig:
        table["p"] = table["p"].apply(significativite)
    table = table.drop([0, 1], axis=1)

    # Transformation de l'index pour ajouter les références

    # Gestion à part de l'intercept qui n'a pas de modalité
    temp_intercept = list(table.loc["Intercept"])
    table = table.drop("Intercept")

    # Variables numériques
    var_num = data.select_dtypes(include=np.number).columns

    # Identification des références utilisées par la régression
    # Premier élément des modalités classées pour les variables non numériques
    refs = []
    for v in indep_var_unique:
        if not v in var_num:
            r = sorted(data[v].dropna().unique())[0] #premier élément
            refs.append(str(v) + "[T." + str(r) + "]") #ajout de la référence

    # Ajout des références dans le tableau
    for i in refs:
        table.loc[i] = ["ref", " ", " "]

    # Création d'un MultiIndex Pandas par variable
    new_index = []
    for i in table.index:
        if ":" in i: # cas où c'est une ligne d'interaction
            new_index.append(("var. interaction", i.replace("T.","")))
        else:
            if "[T." in i: # Si c'est une variable catégorielle
                tmp = i.split("[T.")
                new_index.append((indep_var_unique[tmp[0]], tmp[1][0:-1]))  # gérer l'absence dans le dictionnaire
            else:
                new_index.append((indep_var_unique[i], "numérique"))


    # Réintégration de l'Intercept dans le tableau
    new_index.append((".Intercept", ""))
    table.loc[".Intercept"] = temp_intercept

    # Réindexation du tableau
    new_index = pd.MultiIndex.from_tuples(new_index, names=["Variable", "Modalité"])
    table.index = new_index
    table = table.sort_index()

    return table


def construction_formule(dep,indep):
    """
    Construit une formule de modèle à partir d'une liste de variables
    """
    return dep + " ~ " + " + ".join([i for i in indep])


def regression_logistique(df,dep_var,indep_var,weight=False,table_only=True):
    """
    Régression logistique binomiale pondérée
    
    Parameters
    ----------
    df: DataFrame
     Database
    dep_var : String
     Name of the binomiale variable
    indep_var: dictionnary or list
     column of the variable / Label to use in the table
    weight: String (optionnal)
     column of the weighting
    table_only: if True, return the model
    
    Returns
    -------
    DataFrame : table for the results, or the model if table_only=Trye

    Comments
    --------
    No space in the names of the variables
    BETA VERSION BE CAREFUL NEED CHECKING

    """
    
    # S'il n'y a pas de pondération définie
    if not weight:
        df["weight"] = 1
        weight = "weight"

    # Vérifier que les variables ne contiennent pas de variables
    if len([i for i in indep_var if " " in i])>0:
        print("Attention, au moins un nom de variable contient un espace. Veuillez l'enlever.")
        print([i for i in indep_var if " " in i])
        return None
        
    # Mettre les variables indépendantes en dictionnaire si nécessaire
    if type(indep_var)==list:
        indep_var = {i:i for i in indep_var}
    
    # Construction de la formule
    f = construction_formule(dep_var,indep_var)
    
    # Création du modèle
    modele = smf.glm(formula=f, data=df, 
                     family=sm.families.Binomial(), 
                     freq_weights=df[weight])
    regression = modele.fit()
        
    # Retourner le tableau de présentation
    if table_only:
        tableau = tableau_reg_logistique(regression,df,indep_var,sig=True)
        return tableau
    else:
        return regression


def likelihood_ratio(mod, mod_r):
    """
    Différence de déviance entre deux modèles logistiques (likelihood ratio)

    Parameters
    ----------
    mod : statsmodel object from GLM
     First model to compare
    mod_r : statsmodel object from GLM
     Second model to compare at
    
    Returns
    -------
    float : p-value of the likelihood ratio

    Comments
    --------
    Source : http://rnowling.github.io/machine/learning/2017/10/07/likelihood-ratio-test.html
    Testé en Rstats avec lmtest
    """
    val = [mod.llf,mod_r.llf]
    LR = 2*(max(val)-min(val)) #rapport de déviance
    
    val = [mod.df_model,mod_r.df_model]
    diff_df = max(val)-min(val) #différence de ddf

    p = chi2.sf(LR,diff_df) #test de la significativité
    return p

# ----------------------------------------------------------------------
# Classes et fonctions temporaires non finalisées



def tableau_reg_logistique_distribution(df, dep_var, indep_var, weight=False):
    
    # Noms des variables
    if type(indep_var) == list:
        indep_var = {i:i for i in indep_var}
        
    # régression logistique
    reg = regression_logistique(df,dep_var,indep_var,weight = weight,table_only=True)
    
    # Distribution
    dis = {}
    for i in indep_var:
        dis[indep_var[i]] = tri_a_plat(df,i,weight=weight)["Pourcentage (%)"].drop("Total")
    dis = pd.concat(dis,axis=0)
    dis.index.names = ['Variable', 'Modalité']

    # garder uniquement l'étoile ...
    reg["s"] = reg["p"].apply(lambda x : "" if pd.isnull(x) else "".join([i for i in x if i=="*"]))

    tab = reg[["IC 95%","s"]].join(dis)

    # ajout étoile
    tab["IC 95%"] = tab.apply(lambda x : str(x["IC 95%"])+" "+x["s"],axis=1)

    return tab[["Pourcentage (%)","IC 95%"]]


def cramers_corrected_stat(confusion_matrix):
    """calculate Cramers V statistic for categorial-categorial association.
    uses correction from Bergsma and Wicher,
    Journal of the Korean Statistical Society 42 (2013): 323-328
    """
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2 / n
    r, k = confusion_matrix.shape

    phi2corr = max(0, phi2 - ((k - 1) * (r - 1)) / (n - 1))
    rcorr = r - ((r - 1) ** 2) / (n - 1)
    kcorr = k - ((k - 1) ** 2) / (n - 1)
    return np.sqrt(phi2corr / min((kcorr - 1), (rcorr - 1)))