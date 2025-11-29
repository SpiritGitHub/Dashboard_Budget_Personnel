import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from PIL import Image
import io

# =============== CONFIGURATION ================
st.set_page_config(
    page_title="💰 Budget Personnel",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============== CSS PERSONNALISÉ ================
st.markdown("""
<style>
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .success { color: #10b981; }
    .warning { color: #f59e0b; }
    .danger { color: #ef4444; }
    .alert-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .quick-add-form {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .fcfa-badge {
        background-color: #1a73e8;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-left: 5px;
    }
    .quick-action-btn {
        margin: 5px 0;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# =============== BASE DE DONNÉES ================

def init_db():
    """Initialise la base de données SQLite."""
    conn = sqlite3.connect('budget.db')
    c = conn.cursor()
    
    # Table transactions
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        description TEXT NOT NULL,
        categorie TEXT NOT NULL,
        montant INTEGER NOT NULL,
        type TEXT NOT NULL,
        notes TEXT
    )''')
    
    # Table budget
    c.execute('''CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categorie TEXT UNIQUE NOT NULL,
        limite INTEGER NOT NULL,
        mois TEXT NOT NULL
    )''')
    
    conn.commit()
    return conn

def add_transaction(date, description, categorie, montant, type_trans, notes=""):
    """Ajoute une transaction à la base de données."""
    conn = sqlite3.connect('budget.db')
    c = conn.cursor()
    c.execute('''INSERT INTO transactions (date, description, categorie, montant, type, notes)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (date, description, categorie, int(montant), type_trans, notes))
    conn.commit()
    conn.close()

def get_transactions(start_date=None, end_date=None, categorie=None):
    """Récupère les transactions avec filtres optionnels."""
    conn = sqlite3.connect('budget.db')
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []
    
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    if categorie:
        query += " AND categorie = ?"
        params.append(categorie)
    
    query += " ORDER BY date DESC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df['montant'] = df['montant'].astype(int)
    return df

def set_budget(categorie, limite, mois):
    """Définit ou met à jour le budget d'une catégorie."""
    conn = sqlite3.connect('budget.db')
    c = conn.cursor()
    
    try:
        c.execute('''INSERT INTO budgets (categorie, limite, mois)
                     VALUES (?, ?, ?)''', (categorie, int(limite), mois))
    except sqlite3.IntegrityError:
        c.execute('''UPDATE budgets SET limite = ?, mois = ?
                     WHERE categorie = ? AND mois = ?''',
                  (int(limite), mois, categorie, mois))
    
    conn.commit()
    conn.close()

def get_budgets(mois):
    """Récupère les budgets pour un mois donné."""
    conn = sqlite3.connect('budget.db')
    df = pd.read_sql_query("SELECT * FROM budgets WHERE mois = ?", conn, params=[mois])
    conn.close()
    
    if not df.empty:
        df['limite'] = df['limite'].astype(int)
    return df

def get_monthly_stats(year, month):
    """Calcule les statistiques mensuelles."""
    conn = sqlite3.connect('budget.db')
    month_str = f"{year}-{month:02d}"
    
    df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE date LIKE ? ORDER BY date",
        conn, params=[f"{month_str}%"]
    )
    conn.close()
    
    if df.empty:
        return None
    
    df['date'] = pd.to_datetime(df['date'])
    df['montant'] = df['montant'].astype(int)
    
    revenus = df[df['type'] == 'Revenu']['montant'].sum()
    depenses = df[df['type'] == 'Dépense']['montant'].sum()
    
    return {
        'revenus': int(revenus),
        'depenses': int(depenses),
        'solde': int(revenus - depenses),
        'transactions': df
    }

def format_fcfa(montant):
    """Formate un montant en FCFA avec séparateurs de milliers."""
    return f"{int(montant):,} FCFA".replace(",", " ")

def check_alerts(df_transactions, budgets_df):
    """Vérifie les alertes intelligentes."""
    alerts = []
    
    # Solde négatif
    solde_mensuel = get_monthly_stats(datetime.now().year, datetime.now().month)
    if solde_mensuel and solde_mensuel['solde'] < 0:
        alerts.append({
            'type': 'danger',
            'message': f"⚠️ Solde négatif: {format_fcfa(solde_mensuel['solde'])}"
        })
    
    # Grosses dépenses (supérieures à 50 000 FCFA)
    grosses_depenses = df_transactions[
        (df_transactions['type'] == 'Dépense') & 
        (df_transactions['montant'] > 50000)
    ]
    if not grosses_depenses.empty:
        for _, depense in grosses_depenses.head(3).iterrows():
            alerts.append({
                'type': 'warning',
                'message': f"💰 Grosse dépense: {depense['description']} - {format_fcfa(depense['montant'])}"
            })
    
    # Dépassement de budget
    if not budgets_df.empty:
        for _, budget in budgets_df.iterrows():
            depenses_categorie = df_transactions[
                (df_transactions['categorie'] == budget['categorie']) & 
                (df_transactions['type'] == 'Dépense')
            ]['montant'].sum()
            
            if depenses_categorie > budget['limite']:
                alerts.append({
                    'type': 'warning',
                    'message': f"📊 Budget dépassé {budget['categorie']}: {format_fcfa(depenses_categorie)}/{format_fcfa(budget['limite'])}"
                })
    
    return alerts

def export_to_csv(df):
    """Exporte les données en CSV."""
    csv = df.to_csv(index=False).encode()
    return csv

def export_to_excel(df):
    """Exporte les données en Excel."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Transactions')
    buffer.seek(0)
    return buffer.getvalue()

# =============== INTERFACE PRINCIPALE ================

# Initialiser la BD
init_db()

# Sidebar
with st.sidebar:
    st.header("💰 Budget Personnel")
    st.markdown("Gérez vos finances en **Franc CFA**")
    
    st.markdown("---")
    st.header("⚙️ Navigation")
    page = st.radio(
        "Sélectionnez une page:",
        ["📊 Tableau de bord", "➕ Transactions rapides", "📈 Analyse financière", "💼 Gestion budgets", "📥 Export données"]
    )
    
    st.markdown("---")
    st.subheader("📅 Filtres avancés")
    
    # Période
    period_options = ["Ce mois", "3 derniers mois", "6 derniers mois", "Cette année", "Personnalisé"]
    selected_period = st.selectbox("Période", period_options)
    
    if selected_period == "Personnalisé":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Date début", value=datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("Date fin", value=datetime.now())
    else:
        end_date = datetime.now()
        if selected_period == "Ce mois":
            start_date = datetime(end_date.year, end_date.month, 1)
        elif selected_period == "3 derniers mois":
            start_date = end_date - timedelta(days=90)
        elif selected_period == "6 derniers mois":
            start_date = end_date - timedelta(days=180)
        else:  # Cette année
            start_date = datetime(end_date.year, 1, 1)
    
    # Filtre par catégorie
    categories = st.multiselect(
        "Catégories",
        ["Toutes", "Alimentation", "Transport", "Loisirs", "Santé", "Éducation", "Logement", "Utilities", "Autre", "Salaire", "Bonus"],
        default=["Toutes"]
    )
    
    # Filtre par type
    type_filter = st.multiselect(
        "Type de transaction",
        ["Tous", "Revenu", "Dépense"],
        default=["Tous"]
    )

# =============== PAGE 1 : TABLEAU DE BORD ================
if page == "📊 Tableau de bord":
    st.title("💰 Dashboard Budget Personnel")
    st.markdown(f"<span class='fcfа-badge'>Devise: Franc CFA (FCFA)</span>", unsafe_allow_html=True)
    
    # Transactions pour les alertes
    df_alerts = get_transactions(start_date=start_date.isoformat(), end_date=end_date.isoformat())
    budgets = get_budgets(f"{datetime.now().year}-{datetime.now().month:02d}")
    
    # Alertes intelligentes
    alerts = check_alerts(df_alerts, budgets)
    if alerts:
        st.subheader("🔔 Alertes intelligentes")
        for alert in alerts:
            st.markdown(f"""
            <div class="alert-box">
                <strong>{alert['message']}</strong>
            </div>
            """, unsafe_allow_html=True)
    
    stats = get_monthly_stats(datetime.now().year, datetime.now().month)
    
    if stats:
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">💵 Revenus</div>
                <div class="metric-value">{format_fcfa(stats['revenus'])}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">💸 Dépenses</div>
                <div class="metric-value">{format_fcfa(stats['depenses'])}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            solde_color = "success" if stats['solde'] >= 0 else "danger"
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">💲 Solde</div>
                <div class="metric-value {solde_color}">{format_fcfa(stats['solde'])}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            taux_epargne = (stats['solde'] / stats['revenus'] * 100) if stats['revenus'] > 0 else 0
            epargne_color = "success" if taux_epargne >= 20 else "warning" if taux_epargne >= 10 else "danger"
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">🎯 Taux d'épargne</div>
                <div class="metric-value {epargne_color}">{taux_epargne:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Graphiques financiers avancés
        col1, col2 = st.columns(2)
        
        with col1:
            # Dépenses par catégorie (camembert)
            cat_depenses = stats['transactions'][stats['transactions']['type'] == 'Dépense'].groupby('categorie')['montant'].sum()
            
            fig_pie = px.pie(
                values=cat_depenses.values,
                names=cat_depenses.index,
                title="💰 Répartition des dépenses par catégorie",
                template="plotly_dark"
            )
            fig_pie.update_traces(textinfo='percent+label+value', 
                                texttemplate='%{label}<br>%{value:,} FCFA<br>(%{percent})',
                                hovertemplate='<b>%{label}</b><br>%{value:,} FCFA<br>%{percent}')
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # Graphique en barres horizontales - Top dépenses
            top_depenses = stats['transactions'][stats['transactions']['type'] == 'Dépense'].nlargest(10, 'montant')
            fig_bar_h = px.bar(
                top_depenses,
                y='description',
                x='montant',
                title="📊 Top 10 des plus grosses dépenses",
                orientation='h',
                template="plotly_dark",
                labels={'montant': 'Montant (FCFA)'}
            )
            fig_bar_h.update_traces(hovertemplate='<b>%{y}</b><br>%{x:,} FCFA')
            st.plotly_chart(fig_bar_h, use_container_width=True)
        
        with col2:
            # Évolution temporelle (courbes)
            df_daily = stats['transactions'].groupby(['date', 'type'])['montant'].sum().reset_index()
            
            fig_line = px.line(
                df_daily,
                x='date',
                y='montant',
                color='type',
                title="📈 Évolution quotidienne des revenus et dépenses",
                labels={'montant': 'Montant (FCFA)', 'date': 'Date'},
                template="plotly_dark"
            )
            fig_line.update_traces(hovertemplate='<b>%{x}</b><br>%{y:,} FCFA')
            st.plotly_chart(fig_line, use_container_width=True)
            
            # Graphique à zones empilées
            df_stacked = stats['transactions'][stats['transactions']['type'] == 'Dépense']
            df_stacked = df_stacked.groupby(['date', 'categorie'])['montant'].sum().reset_index()
            
            fig_area = px.area(
                df_stacked,
                x='date',
                y='montant',
                color='categorie',
                title="📊 Évolution des dépenses par catégorie",
                template="plotly_dark",
                labels={'montant': 'Montant (FCFA)'}
            )
            fig_area.update_traces(hovertemplate='<b>%{x}</b><br>%{y:,} FCFA')
            st.plotly_chart(fig_area, use_container_width=True)
        
        # Transactions récentes
        st.subheader("🔄 Transactions récentes")
        transactions_display = stats['transactions'].head(10).copy()
        transactions_display['montant'] = transactions_display['montant'].apply(format_fcfa)
        st.dataframe(
            transactions_display[['date', 'description', 'categorie', 'montant', 'type']],
            width='stretch',
            hide_index=True
        )
    
    else:
        st.info(f"📭 Aucune transaction pour ce mois")

# =============== PAGE 2 : TRANSACTIONS RAPIDES ================
elif page == "➕ Transactions rapides":
    st.title("➕ Gestion des Transactions")
    st.markdown(f"<span class='fcfа-badge'>Tous les montants en Franc CFA (entiers)</span>", unsafe_allow_html=True)
    
    # Section d'ajout rapide avec montants personnalisés
    st.markdown('<div class="quick-add-form">', unsafe_allow_html=True)
    st.subheader("⚡ Actions rapides avec montant personnalisé")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**💵 Revenus rapides**")
        
        # Formulaire rapide pour Salaire
        with st.form(key='salaire_form'):
            salaire_montant = st.number_input("💰 Montant du salaire (FCFA)", min_value=0, step=1000, value=250000, format="%d", key="salaire_montant")
            if st.form_submit_button("💼 Ajouter Salaire", use_container_width=True):
                add_transaction(
                    date=datetime.now().isoformat(),
                    description="Salaire mensuel",
                    categorie="Salaire",
                    montant=salaire_montant,
                    type_trans="Revenu"
                )
                st.success(f"Salaire de {format_fcfa(salaire_montant)} ajouté!")
        
        # Formulaire rapide pour Bonus
        with st.form(key='bonus_form'):
            bonus_montant = st.number_input("🎁 Montant du bonus (FCFA)", min_value=0, step=1000, value=50000, format="%d", key="bonus_montant")
            if st.form_submit_button("💰 Ajouter Bonus", use_container_width=True):
                add_transaction(
                    date=datetime.now().isoformat(),
                    description="Bonus",
                    categorie="Bonus",
                    montant=bonus_montant,
                    type_trans="Revenu"
                )
                st.success(f"Bonus de {format_fcfa(bonus_montant)} ajouté!")
    
    with col2:
        st.write("**💸 Dépenses courantes**")
        
        # Formulaire rapide pour Courses
        with st.form(key='courses_form'):
            courses_montant = st.number_input("🛒 Montant courses (FCFA)", min_value=0, step=1000, value=45000, format="%d", key="courses_montant")
            if st.form_submit_button("🛒 Ajouter Courses", use_container_width=True):
                add_transaction(
                    date=datetime.now().isoformat(),
                    description="Courses alimentaires",
                    categorie="Alimentation",
                    montant=courses_montant,
                    type_trans="Dépense"
                )
                st.success(f"Courses de {format_fcfa(courses_montant)} ajoutées!")
        
        # Formulaire rapide pour Transport
        with st.form(key='transport_form'):
            transport_montant = st.number_input("⛽ Montant transport (FCFA)", min_value=0, step=1000, value=25000, format="%d", key="transport_montant")
            if st.form_submit_button("🚗 Ajouter Transport", use_container_width=True):
                add_transaction(
                    date=datetime.now().isoformat(),
                    description="Frais de transport",
                    categorie="Transport",
                    montant=transport_montant,
                    type_trans="Dépense"
                )
                st.success(f"Transport de {format_fcfa(transport_montant)} ajouté!")
    
    with col3:
        st.write("**🎯 Autres dépenses**")
        
        # Formulaire rapide pour Restaurant
        with st.form(key='restaurant_form'):
            restaurant_montant = st.number_input("🍽️ Montant restaurant (FCFA)", min_value=0, step=1000, value=15000, format="%d", key="restaurant_montant")
            if st.form_submit_button("🍽️ Ajouter Restaurant", use_container_width=True):
                add_transaction(
                    date=datetime.now().isoformat(),
                    description="Repas au restaurant",
                    categorie="Loisirs",
                    montant=restaurant_montant,
                    type_trans="Dépense"
                )
                st.success(f"Restaurant de {format_fcfa(restaurant_montant)} ajouté!")
        
        # Formulaire rapide pour Abonnement
        with st.form(key='abonnement_form'):
            abonnement_montant = st.number_input("📱 Montant abonnement (FCFA)", min_value=0, step=1000, value=10000, format="%d", key="abonnement_montant")
            if st.form_submit_button("📱 Ajouter Abonnement", use_container_width=True):
                add_transaction(
                    date=datetime.now().isoformat(),
                    description="Abonnement mensuel",
                    categorie="Utilities",
                    montant=abonnement_montant,
                    type_trans="Dépense"
                )
                st.success(f"Abonnement de {format_fcfa(abonnement_montant)} ajouté!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Formulaire d'ajout manuel complet
    st.subheader("✏️ Ajout manuel personnalisé")
    
    col1, col2 = st.columns(2)
    
    with col1:
        date = st.date_input("📅 Date", value=datetime.now())
        description = st.text_input("📝 Description")
        type_trans = st.selectbox("Type", ["Dépense", "Revenu"])
    
    with col2:
        montant = st.number_input("💰 Montant (FCFA)", min_value=0, step=100, value=1000, format="%d")
        categorie = st.selectbox(
            "📂 Catégorie",
            ["Alimentation", "Transport", "Loisirs", "Santé", "Éducation", 
             "Logement", "Utilities", "Autre", "Salaire", "Bonus"]
        )
    
    notes = st.text_area("📌 Notes (optionnel)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Ajouter transaction", type="primary", use_container_width=True):
            if description and montant > 0:
                add_transaction(
                    date=date.isoformat(),
                    description=description,
                    categorie=categorie,
                    montant=montant,
                    type_trans=type_trans,
                    notes=notes
                )
                st.success(f"✅ {description} ({format_fcfa(montant)}) ajoutée!")
                st.rerun()
            else:
                st.error("❌ Veuillez remplir tous les champs obligatoires")
    
    with col2:
        if st.button("🔄 Réinitialiser", use_container_width=True):
            st.rerun()

# =============== PAGE 3 : ANALYSE FINANCIÈRE ================
elif page == "📈 Analyse financière":
    st.title("📈 Analyse Financière Avancée")
    st.markdown(f"<span class='fcfа-badge'>Analyse en Franc CFA</span>", unsafe_allow_html=True)
    
    # Récupérer les données filtrées
    query_conditions = []
    params = []
    
    query_conditions.append("date >= ? AND date <= ?")
    params.extend([start_date.isoformat(), end_date.isoformat()])
    
    if "Toutes" not in categories:
        placeholders = ','.join(['?'] * len(categories))
        query_conditions.append(f"categorie IN ({placeholders})")
        params.extend(categories)
    
    if "Tous" not in type_filter:
        placeholders = ','.join(['?'] * len(type_filter))
        query_conditions.append(f"type IN ({placeholders})")
        params.extend(type_filter)
    
    where_clause = " AND ".join(query_conditions)
    
    conn = sqlite3.connect('budget.db')
    df_analysis = pd.read_sql_query(
        f"SELECT * FROM transactions WHERE {where_clause} ORDER BY date",
        conn, params=params
    )
    conn.close()
    
    if not df_analysis.empty:
        df_analysis['date'] = pd.to_datetime(df_analysis['date'])
        df_analysis['month'] = df_analysis['date'].dt.to_period('M')
        df_analysis['montant'] = df_analysis['montant'].astype(int)
        
        # Statistiques détaillées
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total = df_analysis['montant'].sum()
            st.metric("📊 Total", format_fcfa(total))
        
        with col2:
            moyenne = df_analysis['montant'].mean()
            st.metric("📈 Moyenne", format_fcfa(int(moyenne)))
        
        with col3:
            max_trans = df_analysis['montant'].max()
            st.metric("🔝 Maximum", format_fcfa(max_trans))
        
        with col4:
            count_trans = len(df_analysis)
            st.metric("🔢 Nombre", f"{count_trans}")
        
        st.markdown("---")
        
        # Graphiques avancés
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenus vs Dépenses par mois
            monthly_data = df_analysis.groupby(['month', 'type'])['montant'].sum().reset_index()
            monthly_data['month'] = monthly_data['month'].astype(str)
            
            fig_monthly = px.bar(
                monthly_data,
                x='month',
                y='montant',
                color='type',
                title="📊 Revenus et dépenses par mois",
                barmode='group',
                template="plotly_dark",
                labels={'montant': 'Montant (FCFA)', 'month': 'Mois'}
            )
            fig_monthly.update_traces(hovertemplate='<b>%{x}</b><br>%{y:,} FCFA')
            st.plotly_chart(fig_monthly, use_container_width=True)
            
            # Graphique en cascade (waterfall) - Évolution du solde
            monthly_balance = df_analysis.groupby('month').apply(
                lambda x: x[x['type']=='Revenu']['montant'].sum() - x[x['type']=='Dépense']['montant'].sum()
            ).reset_index()
            monthly_balance.columns = ['month', 'solde']
            monthly_balance['month'] = monthly_balance['month'].astype(str)
            
            fig_waterfall = go.Figure(go.Waterfall(
                name="Solde",
                orientation="v",
                measure=["relative"] * len(monthly_balance),
                x=monthly_balance['month'],
                y=monthly_balance['solde'],
                connector={"line":{"color":"rgb(63, 63, 63)"}},
            ))
            
            fig_waterfall.update_layout(
                title="💧 Évolution du solde mensuel (FCFA)",
                showlegend=True,
                template="plotly_dark"
            )
            fig_waterfall.update_traces(hovertemplate='<b>%{x}</b><br>%{y:,} FCFA')
            st.plotly_chart(fig_waterfall, use_container_width=True)
        
        with col2:
            # Top catégories
            top_cat = df_analysis.groupby('categorie')['montant'].sum().nlargest(8)
            fig_top = px.bar(
                x=top_cat.values,
                y=top_cat.index,
                orientation='h',
                title="🏆 Top catégories par montant (FCFA)",
                template="plotly_dark",
                labels={'x': 'Montant (FCFA)', 'y': 'Catégorie'}
            )
            fig_top.update_traces(hovertemplate='<b>%{y}</b><br>%{x:,} FCFA')
            st.plotly_chart(fig_top, use_container_width=True)
            
            # Distribution des montants
            fig_dist = px.histogram(
                df_analysis,
                x='montant',
                nbins=20,
                title="📊 Distribution des montants (FCFA)",
                template="plotly_dark",
                labels={'montant': 'Montant (FCFA)'}
            )
            fig_dist.update_traces(hovertemplate='<b>%{x:,} FCFA</b><br>Count: %{y}')
            st.plotly_chart(fig_dist, use_container_width=True)
        
        # Analyse de tendance
        st.subheader("📈 Analyse de tendance")
        
        # Préparation des données pour l'analyse de tendance
        df_trend = df_analysis.copy()
        df_trend['week'] = df_trend['date'].dt.isocalendar().week
        df_trend['year_week'] = df_trend['date'].dt.year.astype(str) + '-W' + df_trend['week'].astype(str)
        
        weekly_trend = df_trend.groupby(['year_week', 'type'])['montant'].sum().reset_index()
        
        fig_trend = px.line(
            weekly_trend,
            x='year_week',
            y='montant',
            color='type',
            title="📈 Tendances hebdomadaires (FCFA)",
            template="plotly_dark",
            labels={'montant': 'Montant (FCFA)', 'year_week': 'Semaine'}
        )
        fig_trend.update_traces(hovertemplate='<b>%{x}</b><br>%{y:,} FCFA')
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Tableau détaillé
        st.subheader("📋 Détail des transactions")
        display_df = df_analysis[['date', 'description', 'categorie', 'montant', 'type']].copy()
        display_df['montant'] = display_df['montant'].apply(format_fcfa)
        st.dataframe(
            display_df.sort_values('date', ascending=False),
            width='stretch',
            hide_index=True
        )
    
    else:
        st.info("📭 Aucune transaction pour cette période avec les filtres sélectionnés")

# =============== PAGE 4 : GESTION BUDGETS ================
elif page == "💼 Gestion budgets":
    st.title("💼 Gestion des Budgets")
    st.markdown(f"<span class='fcfа-badge'>Budgets en Franc CFA</span>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("➕ Définir un budget")
        
        categorie_budget = st.selectbox(
            "Catégorie",
            ["Alimentation", "Transport", "Loisirs", "Santé", "Éducation", "Logement", "Utilities", "Autre"]
        )
        
        limite_budget = st.number_input("Limite mensuelle (FCFA)", min_value=0, step=1000, value=50000, format="%d")
        
        mois_budget = st.selectbox(
            "Mois",
            [f"{datetime.now().year}-{datetime.now().month:02d}"] + 
            [f"{datetime.now().year}-{(datetime.now().month + i) % 12 or 12:02d}" for i in range(1, 6)]
        )
        
        if st.button("✅ Définir le budget", type="primary", use_container_width=True):
            set_budget(categorie_budget, limite_budget, mois_budget)
            st.success(f"✅ Budget de {format_fcfa(limite_budget)} défini pour {categorie_budget} ({mois_budget})")
            st.rerun()
    
    with col2:
        st.subheader("📊 Tableau des budgets")
        
        budgets = get_budgets(f"{datetime.now().year}-{datetime.now().month:02d}")
        
        if not budgets.empty:
            # Récupérer les dépenses actuelles
            transactions = get_transactions(
                start_date=f"{datetime.now().year}-{datetime.now().month:02d}-01",
                end_date=f"{datetime.now().year}-{datetime.now().month:02d}-31"
            )
            
            budget_data = []
            
            for _, budget in budgets.iterrows():
                cat = budget['categorie']
                limite = budget['limite']
                
                dépenses = transactions[
                    (transactions['categorie'] == cat) & 
                    (transactions['type'] == 'Dépense')
                ]['montant'].sum()
                
                utilisation = (dépenses / limite * 100) if limite > 0 else 0
                reste = limite - dépenses
                
                budget_data.append({
                    'Catégorie': cat,
                    'Limite': format_fcfa(limite),
                    'Dépenses': format_fcfa(dépenses),
                    'Reste': format_fcfa(reste),
                    'Utilisation': f"{utilisation:.1f}%"
                })
            
            df_budget = pd.DataFrame(budget_data)
            st.dataframe(df_budget, width='stretch', hide_index=True)
            
            # Graphique d'utilisation des budgets
            utilisation_values = [float(x.split('%')[0]) for x in df_budget['Utilisation']]
            fig_budget = px.bar(
                df_budget,
                x='Catégorie',
                y=utilisation_values,
                title="📊 Utilisation des budgets (%)",
                template="plotly_dark",
                labels={'y': 'Pourcentage d\'utilisation'}
            )
            fig_budget.update_traces(hovertemplate='<b>%{x}</b><br>%{y:.1f}%')
            st.plotly_chart(fig_budget, use_container_width=True)
        else:
            st.info("📭 Aucun budget défini pour ce mois")

# =============== PAGE 5 : EXPORT DONNÉES ================
elif page == "📥 Export données":
    st.title("📥 Import / Export des données")
    st.markdown(f"<span class='fcfа-badge'>Données en Franc CFA</span>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📤 Exporter les données")
        
        format_export = st.radio("Format d'export", ["CSV", "Excel"])
        
        # Appliquer les filtres pour l'export
        transactions_export = get_transactions(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        if not transactions_export.empty:
            if format_export == "CSV":
                csv_data = export_to_csv(transactions_export)
                st.download_button(
                    label="📥 Télécharger en CSV",
                    data=csv_data,
                    file_name=f"budget_{start_date}_{end_date}.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
            else:
                excel_data = export_to_excel(transactions_export)
                st.download_button(
                    label="📥 Télécharger en Excel",
                    data=excel_data,
                    file_name=f"budget_{start_date}_{end_date}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True
                )
            
            # Statistiques d'export
            total_export = transactions_export['montant'].sum()
            st.info(f"""
            **Résumé de l'export:**
            - Période: {start_date} à {end_date}
            - Nombre de transactions: {len(transactions_export)}
            - Total: {format_fcfa(total_export)}
            """)
        else:
            st.info("📭 Aucune donnée à exporter pour cette période")
    
    with col2:
        st.subheader("📥 Importer des données")
        
        uploaded_file = st.file_uploader("Choisissez un fichier CSV", type=["csv"])
        
        if uploaded_file is not None:
            try:
                df_import = pd.read_csv(uploaded_file)
                
                st.write("Aperçu des données à importer:")
                st.dataframe(df_import.head(), width='stretch')
                
                # Vérification des colonnes requises
                required_columns = ['date', 'description', 'categorie', 'montant', 'type']
                missing_columns = [col for col in required_columns if col not in df_import.columns]
                
                if missing_columns:
                    st.error(f"❌ Colonnes manquantes: {', '.join(missing_columns)}")
                else:
                    if st.button("✅ Importer les données", type="primary", use_container_width=True):
                        for _, row in df_import.iterrows():
                            add_transaction(
                                date=row['date'],
                                description=row['description'],
                                categorie=row['categorie'],
                                montant=int(row['montant']),
                                type_trans=row['type'],
                                notes=row.get('notes', '')
                            )
                        st.success(f"✅ {len(df_import)} transactions importées avec succès!")
                        st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur lors de l'import: {e}")
    
    st.markdown("---")
    st.subheader("📊 Historique complet")
    
    # Appliquer les filtres pour l'historique
    all_transactions = get_transactions(
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )
    
    if not all_transactions.empty:
        # Filtres supplémentaires pour l'historique
        col1, col2 = st.columns(2)
        with col1:
            sort_by = st.selectbox("Trier par", ["Date récente", "Date ancienne", "Montant croissant", "Montant décroissant"])
        with col2:
            show_columns = st.multiselect(
                "Colonnes à afficher",
                ['date', 'description', 'categorie', 'montant', 'type', 'notes'],
                default=['date', 'description', 'categorie', 'montant', 'type']
            )
        
        # Appliquer le tri
        if sort_by == "Date récente":
            all_transactions = all_transactions.sort_values('date', ascending=False)
        elif sort_by == "Date ancienne":
            all_transactions = all_transactions.sort_values('date', ascending=True)
        elif sort_by == "Montant croissant":
            all_transactions = all_transactions.sort_values('montant', ascending=True)
        else:  # Montant décroissant
            all_transactions = all_transactions.sort_values('montant', ascending=False)
        
        # Formater l'affichage
        display_hist = all_transactions[show_columns].copy()
        if 'montant' in display_hist.columns:
            display_hist['montant'] = display_hist['montant'].apply(format_fcfa)
        
        st.dataframe(
            display_hist,
            width='stretch',
            hide_index=True,
            height=500
        )
    else:
        st.info("📭 Aucune transaction enregistrée pour cette période")