# 💰 Application de Gestion de Budget Personnel

Bienvenue sur l’application web de gestion du budget personnel en **Franc CFA (FCFA)**, conçue pour faciliter le suivi de vos finances quotidiennes grâce à une interface moderne, des visualisations interactives, et des alertes intelligentes.

<div align="center">
    <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white"/>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
    <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white"/>
    <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/>
</div>

---

## 🚀 À propos

Cette application interactive construite avec **Streamlit** vous permet de :
- Suivre vos **revenus**, **dépenses**, et leur évolution dans le temps.
- Gérer vos **budgets par catégorie** avec des alertes de dépassement.
- Analyser vos habitudes de consommation grâce à des graphiques interactifs.
- Exporter/importer vos transactions pour une gestion complète.
- Le tout, en **Franc CFA** et adapté aux réalités locales.

<img width="1261" height="615" alt="image" src="https://github.com/user-attachments/assets/f14d78f7-025d-423f-a9a3-51ddde40ab3a" />

---

## ✨ Fonctionnalités Clés

- **Tableau de bord** dynamique : métriques principales, solde, taux d’épargne, alertes.
- **Ajout rapide ou manuel** de transactions (dépenses / revenus).
- **Analyse détaillée** : Statistiques, tendances, distribution, classements par catégorie.
- **Gestion mensuelle des budgets par catégorie**.
- **Visualisations** : camemberts, courbes, barres horizontales, histogrammes, waterfall charts.
- **Filtres avancés** par période, catégorie ou type.
- **Import/Export** des données en CSV ou Excel.
- Gestion des données avec une **base SQLite** locale robuste.

---

## 🛠️ Installation

### Prérequis

- Python 3.7 ou supérieur
- pip (`python -m ensurepip`)

### Installation des dépendances

```bash
pip install streamlit pandas plotly numpy pillow openpyxl
```

### (Optionnel) Fichier `requirements.txt`

```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.0.0
numpy>=1.24.0
Pillow>=10.0.0
openpyxl>=3.1.0
```

---

## ⚡ Démarrage Rapide

```bash
streamlit run app.py
```
Puis ouvrez [http://localhost:8501](http://localhost:8501) dans votre navigateur.

---

## 🗂️ Structure de la Base de Données

```sql
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

---

## 📝 Mode d'emploi

### 1️⃣ Premiers Pas

1. Lancez l’application
2. Ajoutez vos premières transactions (dépense ou revenu)
3. Consulter le tableau de bord
4. Définissez vos budgets mensuels

### 2️⃣ Ajouter une Transaction

- Rendez-vous sur **Transactions rapides**
- Choisissez le type (Revenu / Dépense)
- Remplissez le montant et validez

### 3️⃣ Exemple de transactions

| Type      | Catégorie      | Montant      | Description        |
|-----------|---------------|--------------|--------------------|
| 💵 Revenu | Salaire        | 250 000 FCFA | Salaire mensuel    |
| 💵 Revenu | Bonus          | 50 000 FCFA  | Prime ponctuelle   |
| 💸 Dépense| Alimentation   | 45 000 FCFA  | Courses            |
| 💸 Dépense| Transport      | 25 000 FCFA  | Carburant          |
| 💸 Dépense| Loisirs        | 15 000 FCFA  | Sortie             |

---

## 📊 Visualisations et Analyses

- **Camemberts** : répartition des dépenses
- **Courbes** : évolution quotidienne et hebdomadaire
- **Barres** : top catégories et plus grosses dépenses
- **Histogrammes** : distribution des montants
- **Waterfall chart** : évolution du solde global
- **Alertes** : solde négatif, grosses dépenses, dépassement de budget

---

## 🎯 Gestion des Budgets

- Budgets mensuels personnalisés par catégorie
- Visualisation en pourcentage d’utilisation
- Alertes automatiques en cas de dépassement

---

## 📥 Import / Export de Données

- **Exporter** : tout ou partie des transactions en CSV ou Excel.
- **Importer** : ajoutez des transactions à partir d’un fichier CSV
- **Historique détaillé** avec possibilités de tri et de filtrage

---

## 💾 Personnalisation et Développement

- Gestion des montants en Franc CFA, format adapté : `X XXX FCFA`
- Interface moderne et responsive (Streamlit + CSS customisé)
- Codé en Python, base de données locale SQLite
- Fonctions clés : `init_db`, `add_transaction`, `get_monthly_stats`, `check_alerts`, `format_fcfa`

---

## 🤝 Contribution

1. **Forkez** ce dépôt
2. **Créez** une branche :  
   ```bash
   git checkout -b feature/nom-feature
   ```
3. **Commitez** vos modifications :  
   ```bash
   git commit -am "Ajout/Modif : message clair"
   ```
4. **Pushez** la branche :  
   ```bash
   git push origin feature/nom-feature
   ```
5. **Ouvrez une Pull Request** pour examen

---

## 📞 Support

- Problème de dépendance ? → `pip install package_manquant`
- Port déjà utilisé ? → `streamlit run app.py --server.port 8502`
- Graphiques vides ? → Ajoutez des transactions !
- Pour des suggestions ou des bugs, ouvrez une **issue**.

---

## 📄 Licence

Ce projet est sous licence **MIT**.

---

<div align="center">
Développé avec ❤️ pour simplifier la gestion financière au quotidien.<br>
Prenez le contrôle de vos finances en Franc CFA !
</div>
