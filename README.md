# 💰 Application de Gestion de Budget Personnel

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

Une application web interactive développée avec **Streamlit** pour gérer
vos finances personnelles en **Franc CFA (FCFA)**.\
Suivez vos revenus et dépenses, analysez vos habitudes de consommation
et contrôlez votre budget facilement.

------------------------------------------------------------------------

## ✨ Fonctionnalités Principales

### 📊 Tableau de Bord Complet

-   **Métriques financières** : Revenus, Dépenses, Solde, Taux
    d'épargne\
-   **Alertes intelligentes** : Solde négatif, grosses dépenses,
    dépassement de budget\
-   **Visualisations interactives** : Camemberts, courbes, barres, aires
    empilées\
-   **Transactions récentes** : Vue des dernières opérations

### ➕ Gestion Simplifiée des Transactions

-   **Actions rapides** : Formulaires pré-remplis\
-   **Montants personnalisables**\
-   **Catégories organisées** : Alimentation, Transport, Loisirs, Santé,
    Éducation, Logement, etc.\
-   **Saisie manuelle avancée**

### 📈 Analyse Financière Avancée

-   **Statistiques détaillées** : Total, moyenne, max, volume\
-   **Graphiques analytiques** :
    -   Revenus vs Dépenses / mois\
    -   Waterfall chart (solde)\
    -   Top catégories\
    -   Distribution des montants\
    -   Tendances hebdomadaires\
-   **Filtres avancés** : période, catégorie, type

### 💼 Gestion des Budgets

-   **Budgets mensuels par catégorie**\
-   **Suivi en temps réel**\
-   **Visualisation en pourcentage**\
-   **Alertes dépassement**

### 📥 Import / Export

-   **Export** : CSV, Excel\
-   **Import CSV**\
-   **Historique complet**\
-   **Sauvegarde SQLite automatique**

------------------------------------------------------------------------

## 🚀 Installation et Démarrage

### Prérequis

-   Python 3.7+\
-   pip

### Installation

``` bash
pip install streamlit pandas plotly numpy pillow openpyxl
```

### Lancer l'application

``` bash
streamlit run app.py
```

Puis ouvrez :\
👉 http://localhost:8501

------------------------------------------------------------------------

## 📁 Fichier `requirements.txt` (optionnel)

    streamlit>=1.28.0
    pandas>=2.0.0
    plotly>=5.0.0
    numpy>=1.24.0
    Pillow>=10.0.0
    openpyxl>=3.1.0

------------------------------------------------------------------------

## 📱 Guide d'Utilisation

### 🔰 Premiers Pas

1.  Lancez l'application\
2.  Ajoutez vos premières transactions\
3.  Consultez les statistiques\
4.  Définissez vos budgets

### ➕ Ajouter une Transaction Rapide

-   Allez dans **Transactions rapides**\
-   Choisissez **Revenu** ou **Dépense**\
-   Entrez le montant\
-   Cliquez sur **Ajouter**

### 🧾 Exemples de Transactions

  Type         Catégorie      Montant        Description
  ------------ -------------- -------------- -----------------
  💵 Revenu    Salaire        250 000 FCFA   Salaire mensuel
  💵 Revenu    Bonus          50 000 FCFA    Prime
  💸 Dépense   Alimentation   45 000 FCFA    Courses
  💸 Dépense   Transport      25 000 FCFA    Carburant
  💸 Dépense   Loisirs        15 000 FCFA    Sorties
  💸 Dépense   Utilities      10 000 FCFA    Abonnements

------------------------------------------------------------------------

## 🎯 Fonctionnalités Détailées

### 🔔 Système d'Alertes Intelligentes

-   Solde négatif\
-   Dépenses \> 50 000 FCFA\
-   Dépassement de budget\
-   Codes couleur (danger / warning / success)

### 📊 Visualisations Interactives

-   Camemberts\
-   Courbes\
-   Barres horizontales\
-   Zones empilées\
-   Waterfall charts\
-   Histogrammes

### ⚙️ Filtres Avancés

-   Périodes prédéfinies : Ce mois, 3 derniers mois, année\
-   Période personnalisée\
-   Catégorie multiple\
-   Type (Revenus, Dépenses)\
-   Tri avancé

### 💾 Base de Données SQLite

#### Structure

``` sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    description TEXT NOT NULL,
    categorie TEXT NOT NULL,
    montant INTEGER NOT NULL,
    type TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE budgets (
    id INTEGER PRIMARY KEY,
    categorie TEXT UNIQUE NOT NULL,
    limite INTEGER NOT NULL,
    mois TEXT NOT NULL
);
```

------------------------------------------------------------------------

## 🎨 Personnalisation

### Franc CFA (FCFA)

-   Montants entiers\
-   Format : `X XXX FCFA`\
-   Seuils adaptés localement

### UI Moderne

-   Cartes métriques\
-   Sidebar organisée\
-   Responsive\
-   Accessibilité renforcée

------------------------------------------------------------------------

## 🔧 Développement

### Structure du Code

    - config & CSS
    - base de données
    - interface utilisateur (5 pages)
    - utils

### Fonctions Clés (exemples)

``` python
init_db()
add_transaction()
get_monthly_stats()
check_alerts()
format_fcfa()
```

### Extensions possibles

``` python
categories.append("Nouvelle Catégorie")
ALERTE_GROSSE_DEPENSE = 75000
```

------------------------------------------------------------------------

## 📞 Support & Dépannage

### Problèmes courants

-   Module manquant → installer via pip\
-   Port utilisé → `streamlit run app.py --server.port 8502`\
-   Graphiques vides → ajouter des transactions

### Performance

-   Limiter les gros CSV\
-   Nettoyer la base si besoin

------------------------------------------------------------------------

## 🤝 Contribution

1.  Forker le projet\

2.  Créer une branche :

    ``` bash
    git checkout -b feature/new-feature
    ```

3.  Commit :

    ``` bash
    git commit -am "Ajout nouvelle fonctionnalité"
    ```

4.  Push :

    ``` bash
    git push origin feature/new-feature
    ```

5.  Ouvrir une Pull Request

------------------------------------------------------------------------

## 📄 Licence

Projet sous licence **MIT**.

------------------------------------------------------------------------

::: {align="center"}
Développé avec ❤️ pour faciliter la gestion financière en Franc CFA.\
Prenez le contrôle de vos finances !
:::
