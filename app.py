import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Analyseur CSV Pro", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============== CSS PERSONNALISÉ ================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .download-link {
        display: inline-block;
        background-color: #1f77b4;
        color: white;
        padding: 0.5rem 1rem;
        text-decoration: none;
        border-radius: 5px;
        margin: 0.2rem;
    }
    .download-link:hover {
        background-color: #155a8a;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# =============== FONCTIONS AMÉLIORÉES =====================

def detect_outliers(series):
    """Détecte les outliers avec la méthode IQR de manière robuste."""
    if len(series.dropna()) == 0:
        return 0
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    if IQR == 0:  # Éviter la division par zéro
        return 0
    return ((series < Q1 - 1.5*IQR) | (series > Q3 + 1.5*IQR)).sum()

def calculate_missing_percentage(df):
    """Calcule le % de valeurs manquantes par colonne avec plus de détails."""
    missing = df.isnull().sum()
    percentage = (missing / len(df)) * 100
    # Convertir les types de données en string pour éviter les problèmes de sérialisation
    dtypes_str = [str(dtype) for dtype in df.dtypes.values]
    missing_info = pd.DataFrame({
        'Colonne': missing.index,
        'Valeurs Manquantes': missing.values,
        'Pourcentage (%)': percentage.values.round(2),
        'Type de Données': dtypes_str
    }).sort_values('Pourcentage (%)', ascending=False)
    
    return missing_info

def generate_advanced_report(df):
    """Génère un rapport Markdown avancé et complet."""
    buffer = io.StringIO()
    
    buffer.write("# 📄 Rapport d'Analyse Détaillé\n\n")
    buffer.write(f"**Date de Génération:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # Informations générales
    buffer.write("## 📊 Informations Générales\n")
    buffer.write(f"- **Nombre Total d'Observations:** {df.shape[0]:,}\n")
    buffer.write(f"- **Nombre de Variables:** {df.shape[1]}\n")
    buffer.write(f"- **Taille Mémoire Utilisée:** {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB\n\n")
    
    # Aperçu des données
    buffer.write("## 👀 Aperçu du Dataset\n")
    buffer.write("### Premières Lignes\n")
    buffer.write(df.head(10).to_markdown() + "\n\n")
    buffer.write("### Dernières Lignes\n")
    buffer.write(df.tail(5).to_markdown() + "\n\n")
    
    # Types de données
    buffer.write("## 🔧 Types de Données\n")
    type_summary = df.dtypes.reset_index()
    type_summary.columns = ['Colonne', 'Type']
    type_summary['Type'] = type_summary['Type'].astype(str)  # Convertir en string
    buffer.write(type_summary.to_markdown(index=False) + "\n\n")
    
    # Analyse des valeurs manquantes
    buffer.write("## ⚠️ Analyse des Valeurs Manquantes\n")
    missing_df = calculate_missing_percentage(df)
    buffer.write(missing_df.to_markdown(index=False) + "\n\n")
    
    # Statistiques descriptives
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        buffer.write("## 📈 Statistiques Descriptives (Numériques)\n")
        buffer.write(df[numeric_cols].describe().round(2).to_markdown() + "\n\n")
    
    # Variables catégorielles
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    if len(categorical_cols) > 0:
        buffer.write("## 📊 Statistiques Descriptives (Catégorielles)\n")
        for col in categorical_cols:
            buffer.write(f"### {col}\n")
            buffer.write(f"- **Valeurs Uniques:** {df[col].nunique()}\n")
            buffer.write(f"- **Valeur la plus Fréquente:** {df[col].mode().iloc[0] if len(df[col].mode()) > 0 else 'N/A'}\n")
            buffer.write(f"- **Fréquence de la Valeur Principale:** {df[col].value_counts().iloc[0] if len(df[col].value_counts()) > 0 else 0}\n\n")
    
    # Détection des outliers
    if len(numeric_cols) > 0:
        buffer.write("## 🔴 Analyse des Outliers (Méthode IQR)\n")
        outliers_detected = False
        for col in numeric_cols:
            count = detect_outliers(df[col])
            if count > 0:
                buffer.write(f"- **{col}:** {count} outliers ({count/len(df)*100:.2f}%)\n")
                outliers_detected = True
        if not outliers_detected:
            buffer.write("Aucun outlier détecté dans les variables numériques.\n")
        buffer.write("\n")
    
    # Matrice de corrélation
    if len(numeric_cols) > 1:
        buffer.write("## 🔗 Matrice de Corrélation\n")
        corr_matrix = df[numeric_cols].corr()
        # Garder seulement la partie supérieure de la matrice
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        corr_upper = corr_matrix.where(mask)
        buffer.write(corr_upper.round(3).to_markdown() + "\n\n")
    
    # Profil des variables
    buffer.write("## 🎯 Profil des Variables\n")
    for col in df.columns:
        buffer.write(f"### {col}\n")
        buffer.write(f"- **Type:** {df[col].dtype}\n")
        buffer.write(f"- **Valeurs Uniques:** {df[col].nunique()}\n")
        if df[col].dtype in ['object', 'category']:
            top_values = df[col].value_counts().head(5)
            buffer.write("- **Top 5 Valeurs:**\n")
            for val, count in top_values.items():
                buffer.write(f"  - {val}: {count} ({count/len(df)*100:.1f}%)\n")
        else:
            buffer.write(f"- **Moyenne:** {df[col].mean():.2f}\n")
            buffer.write(f"- **Médiane:** {df[col].median():.2f}\n")
            buffer.write(f"- **Écart-type:** {df[col].std():.2f}\n")
        buffer.write("\n")
    
    return buffer.getvalue()

def create_download_link(content, filename, text):
    """Crée un lien de téléchargement pour le contenu textuel."""
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}" class="download-link">{text}</a>'
    return href

def create_data_download_link(df, filename, text, format_type='csv'):
    """Crée un lien de téléchargement pour les données."""
    if format_type == 'csv':
        data = df.to_csv(index=False).encode('utf-8')
        mime_type = "text/csv"
    elif format_type == 'json':
        data = df.to_json(orient='records', indent=2).encode('utf-8')
        mime_type = "application/json"
    elif format_type == 'excel':
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        data = buffer.getvalue()
        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}" class="download-link">{text}</a>'
    return href

def plot_advanced_visualizations(df):
    """Crée des visualisations avancées pour le dataset."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    
    figures = []
    
    # Distribution des variables numériques
    if len(numeric_cols) > 0:
        n_cols = min(3, len(numeric_cols))
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
        
        fig1, axes = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4*n_rows))
        if n_rows == 1 and n_cols == 1:
            axes = [axes]
        elif n_rows == 1:
            axes = axes
        else:
            axes = axes.flatten()
        
        for i, col in enumerate(numeric_cols):
            if i < len(axes):
                axes[i].hist(df[col].dropna(), bins=30, alpha=0.7, color='skyblue', edgecolor='black')
                axes[i].set_title(f'Distribution de {col}')
                axes[i].set_xlabel(col)
                axes[i].set_ylabel('Fréquence')
        
        # Masquer les axes vides
        for i in range(len(numeric_cols), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        figures.append(("Distribution des Variables Numériques", fig1))
    
    # Boxplots pour outliers
    if len(numeric_cols) > 0:
        n_cols = min(3, len(numeric_cols))
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
        
        fig2, axes = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4*n_rows))
        if n_rows == 1 and n_cols == 1:
            axes = [axes]
        elif n_rows == 1:
            axes = axes
        else:
            axes = axes.flatten()
        
        for i, col in enumerate(numeric_cols):
            if i < len(axes):
                axes[i].boxplot(df[col].dropna())
                axes[i].set_title(f'Boxplot de {col}')
                axes[i].set_ylabel(col)
        
        for i in range(len(numeric_cols), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        figures.append(("Analyse des Outliers", fig2))
    
    # Top catégories pour variables catégorielles
    if len(categorical_cols) > 0:
        for col in categorical_cols[:3]:  # Limiter aux 3 premières
            fig3, ax = plt.subplots(figsize=(10, 6))
            top_categories = df[col].value_counts().head(10)
            top_categories.plot(kind='bar', ax=ax, color='lightcoral')
            ax.set_title(f'Top 10 Catégories - {col}')
            ax.set_xlabel(col)
            ax.set_ylabel('Fréquence')
            plt.xticks(rotation=45)
            plt.tight_layout()
            figures.append((f"Top Catégories - {col}", fig3))
    
    return figures

# =============== INTERFACE PRINCIPALE ================

st.markdown('<h1 class="main-header">📊 Analyseur Automatique de Fichiers CSV</h1>', unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <p style='font-size: 1.2rem; color: #666;'>
        Chargez un fichier CSV pour obtenir une analyse complète et professionnelle de vos données
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar pour les paramètres
with st.sidebar:
    st.header("⚙️ Paramètres")
    st.markdown("---")
    
    # Options d'analyse
    st.subheader("Options d'Analyse")
    auto_analyze = st.checkbox("Analyse automatique", value=True)
    show_correlations = st.checkbox("Afficher les corrélations", value=True)
    detect_outliers_option = st.checkbox("Détection des outliers", value=True)
    
    st.markdown("---")
    st.subheader("À propos")
    st.info("""
    Cet outil vous permet d'analyser vos données CSV de manière professionnelle :
    - 📊 Statistiques descriptives
    - 🔍 Détection des valeurs manquantes
    - 📈 Visualisations avancées
    - 🧹 Nettoyage des données
    - 📄 Rapports détaillés
    """)

uploaded_file = st.file_uploader("**Choisissez un fichier CSV**", type=["csv"], 
                                help="Sélectionnez un fichier CSV à analyser")

if uploaded_file is not None:
    try:
        # Lecture du fichier avec gestion d'erreurs
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ Fichier chargé avec succès : {uploaded_file.name}")
        
        # Métriques principales dans des cartes
        st.markdown("## 📈 Métriques Principales")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📏 Lignes</h3>
                <h2>{df.shape[0]:,}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📋 Colonnes</h3>
                <h2>{df.shape[1]}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            missing_total = df.isnull().sum().sum()
            st.markdown(f"""
            <div class="metric-card">
                <h3>⚠️ Données Manquantes</h3>
                <h2>{missing_total:,}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            memory_mb = df.memory_usage(deep=True).sum() / 1024**2
            st.markdown(f"""
            <div class="metric-card">
                <h3>💾 Mémoire</h3>
                <h2>{memory_mb:.1f} MB</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Organisation en onglets
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🔍 Aperçu", "📊 Analyse", "📈 Visualisations", 
            "🧹 Nettoyage", "📥 Export", "📄 Rapport"
        ])
        
        # ========== TAB 1 : APERÇU ==========
        with tab1:
            st.subheader("👀 Exploration des Données")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**Aperçu des données :**")
                st.dataframe(df.head(20), width='stretch')
            
            with col2:
                st.write("**Types de données :**")
                dtype_df = df.dtypes.reset_index()
                dtype_df.columns = ['Colonne', 'Type']
                dtype_df['Type'] = dtype_df['Type'].astype(str)  # Convertir en string
                st.dataframe(dtype_df, width='stretch')
                
                st.write("**Résumé des données :**")
                st.json({
                    "Dimensions": f"{df.shape[0]} lignes × {df.shape[1]} colonnes",
                    "Colonnes Numériques": len(df.select_dtypes(include=[np.number]).columns),
                    "Colonnes Catégorielles": len(df.select_dtypes(include=['object']).columns),
                    "Valeurs Dupliquées": df.duplicated().sum()
                })
        
        # ========== TAB 2 : ANALYSE ==========
        with tab2:
            st.subheader("📊 Analyse Statistique")
            
            # Analyse des valeurs manquantes
            st.write("### ⚠️ Analyse des Valeurs Manquantes")
            missing_df = calculate_missing_percentage(df)
            st.dataframe(missing_df, width='stretch')
            
            # Statistiques descriptives
            st.write("### 📈 Statistiques Descriptives")
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                st.dataframe(df[numeric_cols].describe(), width='stretch')
            else:
                st.info("Aucune colonne numérique trouvée pour les statistiques descriptives.")
            
            # Analyse des corrélations
            if show_correlations and len(numeric_cols) > 1:
                st.write("### 🔗 Matrice de Corrélation")
                fig, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(df[numeric_cols].corr(), annot=True, fmt=".2f", cmap="coolwarm", 
                           center=0, cbar_kws={"label": "Coefficient de Corrélation"}, ax=ax)
                st.pyplot(fig)
            
            # Détection des outliers
            if detect_outliers_option and len(numeric_cols) > 0:
                st.write("### 🔴 Détection des Outliers")
                outliers_data = []
                for col in numeric_cols:
                    count = detect_outliers(df[col])
                    if count > 0:
                        outliers_data.append({
                            'Colonne': col,
                            'Outliers': count,
                            'Pourcentage': f"{(count/len(df))*100:.2f}%"
                        })
                
                if outliers_data:
                    outliers_df = pd.DataFrame(outliers_data)
                    st.dataframe(outliers_df, width='stretch')
                else:
                    st.success("Aucun outlier détecté dans les données numériques.")
        
        # ========== TAB 3 : VISUALISATIONS ==========
with tab3:
    st.subheader("📈 Visualisations des Données")

    # --- Visualisations automatiques ---
    if auto_analyze:
        st.write("### 🎨 Visualisations Automatiques")
        figures = plot_advanced_visualizations(df)

        for title, fig in figures:
            st.write(f"**{title}**")
            st.pyplot(fig)
            st.markdown("---")

    # ----------------------------------------------------
    #         VISUALISATIONS PERSONNALISÉES AMÉLIORÉES
    # ----------------------------------------------------
    st.write("### 🎛️ Visualisations Personnalisées")

    # Type de graphique
    chart_type = st.selectbox(
        "📊 Type de graphique :",
        [
            "Scatter Plot (Nuage de points)",
            "Histogramme",
            "Boxplot",
            "Bar Chart",
            "Line Plot",
            "Density Plot (KDE)",
            "Pie Chart",
            "Heatmap d'une colonne"
        ],
        index=0
    )

    # Choix colonnes
    col1, col2 = st.columns(2)

    with col1:
        x_axis = st.selectbox("Axe X :", df.columns, key="x_axis_custom")

    with col2:
        y_options = ['Aucun'] + list(df.columns)
        y_axis = st.selectbox("Axe Y :", y_options, key="y_axis_custom")

    # Récupération des types de données
    x_num = np.issubdtype(df[x_axis].dtype, np.number)
    y_num = y_axis != "Aucun" and np.issubdtype(df[y_axis].dtype, np.number)

    # ----------------------------------------------------
    #               GÉNÉRATION DES GRAPHIQUES
    # ----------------------------------------------------

    # SCATTER PLOT
    if chart_type == "Scatter Plot (Nuage de points)":
        if y_axis == "Aucun":
            st.warning("Veuillez sélectionner une colonne Y pour ce graphique.")
        elif x_num and y_num:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.scatter(df[x_axis], df[y_axis], alpha=0.6)
            ax.set_xlabel(x_axis)
            ax.set_ylabel(y_axis)
            ax.set_title(f"Nuage de points : {x_axis} vs {y_axis}")
            st.pyplot(fig)
        else:
            st.error("❌ Les colonnes X et Y doivent être numériques.")

    # HISTOGRAMME
    elif chart_type == "Histogramme":
        if x_num:
            bins = st.slider("Nombre de bins :", 5, 100, 30)
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(df[x_axis], bins=bins, alpha=0.7)
            ax.set_title(f"Histogramme de {x_axis}")
            st.pyplot(fig)
        else:
            st.error("❌ L'histogramme requiert une colonne numérique.")

    # BOXPLOT
    elif chart_type == "Boxplot":
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(x=df[x_axis], ax=ax)
        ax.set_title(f"Boxplot de {x_axis}")
        st.pyplot(fig)

    # BAR CHART
    elif chart_type == "Bar Chart":
        if not x_num:
            fig, ax = plt.subplots(figsize=(10, 6))
            df[x_axis].value_counts().plot(kind="bar", ax=ax)
            ax.set_title(f"Bar Chart de {x_axis}")
            st.pyplot(fig)
        else:
            st.error("❌ Le Bar Chart est destiné aux colonnes catégorielles.")

    # LINE PLOT
    elif chart_type == "Line Plot":
        if x_num:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(df[x_axis])
            ax.set_title(f"Courbe de {x_axis}")
            st.pyplot(fig)
        else:
            st.error("❌ Le line plot nécessite une colonne numérique.")

    # DENSITY PLOT (KDE)
    elif chart_type == "Density Plot (KDE)":
        if x_num:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.kdeplot(df[x_axis], shade=True, ax=ax)
            ax.set_title(f"Distribution KDE de {x_axis}")
            st.pyplot(fig)
        else:
            st.error("❌ La densité nécessite une colonne numérique.")

    # PIE CHART
    elif chart_type == "Pie Chart":
        if not x_num:
            fig, ax = plt.subplots(figsize=(8, 8))
            df[x_axis].value_counts().plot.pie(autopct="%1.1f%%", ax=ax)
            ax.set_ylabel("")
            ax.set_title(f"Répartition de {x_axis}")
            st.pyplot(fig)
        else:
            st.error("❌ Le Pie chart fonctionne uniquement avec des catégories.")

    # HEATMAP D'UNE COLONNE (distribution)
    elif chart_type == "Heatmap d'une colonne":
        fig, ax = plt.subplots(figsize=(10, 1))
        sns.heatmap([df[x_axis].values], cmap="viridis", ax=ax, cbar=False)
        ax.set_yticks([])
        ax.set_title(f"Heatmap pour {x_axis}")
        st.pyplot(fig)
        # ========== TAB 4 : NETTOYAGE ==========
        with tab4:
            st.subheader("🧹 Outils de Nettoyage des Données")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("### Suppression des Données")
                
                # Suppression des lignes avec valeurs manquantes
                if st.button("🗑️ Supprimer Lignes avec Valeurs Manquantes", use_container_width=True):
                    df_clean = df.dropna()
                    rows_deleted = len(df) - len(df_clean)
                    st.success(f"✅ {rows_deleted} lignes supprimées")
                    st.dataframe(df_clean.head(), width='stretch')
                    
                    # Lien de téléchargement
                    st.markdown(create_data_download_link(
                        df_clean, "data_cleaned_dropna.csv", "📥 Télécharger les Données Nettoyées"
                    ), unsafe_allow_html=True)
                
                # Suppression des colonnes avec trop de valeurs manquantes
                st.write("### Sélection des Colonnes")
                columns_to_keep = st.multiselect(
                    "Choisissez les colonnes à conserver:",
                    df.columns.tolist(),
                    default=df.columns.tolist()
                )
                
                if columns_to_keep:
                    df_filtered = df[columns_to_keep]
                    st.dataframe(df_filtered.head(), width='stretch')
                    
                    st.markdown(create_data_download_link(
                        df_filtered, "data_filtered_columns.csv", "📥 Télécharger avec Colonnes Sélectionnées"
                    ), unsafe_allow_html=True)
            
            with col2:
                st.write("### Transformation des Données")
                
                # Imputation des valeurs manquantes
                if st.button("🔧 Imputer Valeurs Manquantes", use_container_width=True):
                    df_imputed = df.copy()
                    
                    for col in df_imputed.columns:
                        if df_imputed[col].dtype in [np.float64, np.int64]:
                            # Pour les numériques : moyenne ou médiane
                            if df_imputed[col].skew() > 1:  # Distribution asymétrique
                                df_imputed[col] = df_imputed[col].fillna(df_imputed[col].median())
                            else:
                                df_imputed[col] = df_imputed[col].fillna(df_imputed[col].mean())
                        else:
                            # Pour les catégorielles : mode
                            if len(df_imputed[col].mode()) > 0:
                                df_imputed[col] = df_imputed[col].fillna(df_imputed[col].mode()[0])
                            else:
                                df_imputed[col] = df_imputed[col].fillna("Inconnu")
                    
                    st.success("✅ Valeurs manquantes imputées")
                    st.dataframe(df_imputed.head(), width='stretch')
                    
                    st.markdown(create_data_download_link(
                        df_imputed, "data_imputed.csv", "📥 Télécharger les Données Imputées"
                    ), unsafe_allow_html=True)
                
                # Normalisation des données numériques
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    if st.button("📊 Normaliser Données Numériques", use_container_width=True):
                        df_normalized = df.copy()
                        for col in numeric_cols:
                            # Éviter la division par zéro
                            col_min = df[col].min()
                            col_max = df[col].max()
                            if col_max != col_min:
                                df_normalized[col] = (df[col] - col_min) / (col_max - col_min)
                            else:
                                df_normalized[col] = 0.5  # Valeur constante
                        
                        st.success("✅ Données numériques normalisées (0-1)")
                        st.dataframe(df_normalized.head(), width='stretch')
                        
                        st.markdown(create_data_download_link(
                            df_normalized, "data_normalized.csv", "📥 Télécharger les Données Normalisées"
                        ), unsafe_allow_html=True)
        
        # ========== TAB 5 : EXPORT ==========
        with tab5:
            st.subheader("📥 Export des Données")
            
            st.write("### Télécharger dans Différents Formats")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(create_data_download_link(
                    df, "dataset_analyse.csv", "📥 Télécharger en CSV", 'csv'
                ), unsafe_allow_html=True)
            
            with col2:
                st.markdown(create_data_download_link(
                    df, "dataset_analyse.json", "📥 Télécharger en JSON", 'json'
                ), unsafe_allow_html=True)
            
            with col3:
                st.markdown(create_data_download_link(
                    df, "dataset_analyse.xlsx", "📥 Télécharger en Excel", 'excel'
                ), unsafe_allow_html=True)
            
            # Export des données transformées
            st.write("### Données Transformées")
            st.info("Utilisez l'onglet 'Nettoyage' pour appliquer des transformations avant l'export.")
        
        # ========== TAB 6 : RAPPORT ==========
        with tab6:
            st.subheader("📄 Rapport d'Analyse Complet")
            
            if st.button("🔄 Générer le Rapport", type="primary"):
                with st.spinner("Génération du rapport en cours..."):
                    report_content = generate_advanced_report(df)
                
                st.success("✅ Rapport généré avec succès!")
                
                # Aperçu du rapport
                st.write("### Aperçu du Rapport")
                st.markdown(report_content[:1000] + "..." if len(report_content) > 1000 else report_content)
                
                # Téléchargement du rapport
                st.write("### Téléchargement")
                st.markdown(create_download_link(
                    report_content, 
                    f"rapport_analyse_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                    "📥 Télécharger le Rapport Complet (Markdown)"
                ), unsafe_allow_html=True)
                
                # Résumé exécutif
                st.write("### 📋 Résumé Exécutif")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    total_cells = df.shape[0] * df.shape[1]
                    missing_cells = df.isnull().sum().sum()
                    data_quality = ((total_cells - missing_cells) / total_cells * 100) if total_cells > 0 else 100
                    st.metric("Qualité Globale des Données", f"{data_quality:.1f}%")
                    st.metric("Variables Numériques", len(df.select_dtypes(include=[np.number]).columns))
                
                with col2:
                    completeness_rate = (1 - missing_cells / total_cells) * 100 if total_cells > 0 else 100
                    st.metric("Taux de Complétude", f"{completeness_rate:.1f}%")
                    st.metric("Variables Catégorielles", len(df.select_dtypes(include=['object']).columns))
    
    except Exception as e:
        st.error(f"❌ Erreur lors de la lecture du fichier: {str(e)}")
        st.info("""
        **Conseils de dépannage :**
        - Vérifiez que le fichier est un CSV valide
        - Assurez-vous que l'encodage est correct (UTF-8 recommandé)
        - Vérifiez les séparateurs utilisés
        - Contrôlez la cohérence des données
        """)

else:
    # Page d'accueil quand aucun fichier n'est chargé
    st.markdown("""
    <div style='text-align: center; padding: 5rem;'>
        <h2>🚀 Bienvenue dans l'Analyseur CSV Pro</h2>
        <p style='font-size: 1.1rem; color: #666; margin-bottom: 3rem;'>
            Commencez par charger un fichier CSV pour découvrir toutes les fonctionnalités d'analyse
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='text-align: center;'>
            <h3>📊 Analyse Complète</h3>
            <p>Statistiques descriptives, corrélations, détection d'outliers</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='text-align: center;'>
            <h3>🧹 Nettoyage Intelligent</h3>
            <p>Gestion des valeurs manquantes, normalisation, filtrage</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='text-align: center;'>
            <h3>📈 Visualisations Avancées</h3>
            <p>Graphiques interactifs, analyses multidimensionnelles</p>
        </div>
        """, unsafe_allow_html=True)

# Pied de page
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p>Analyseur CSV Pro • Développé avec Streamlit</p>
</div>
""", unsafe_allow_html=True)