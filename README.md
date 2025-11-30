<h1 align="center">
  <img src="https://github.com/user-attachments/assets/8145acf4-0b8c-47e1-afa7-fd7d1b56da96" alt="logo" width="100" style="vertical-align: middle; margin-right: 1px;">
  Option Pricer
</h1>

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/) 
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Active](https://img.shields.io/badge/status-Active-brightgreen.svg)](#)

Une application Python complète pour l'évaluation d'options financières utilisant les modèles **Black-Scholes-Merton** (Européen) et **Cox-Ross-Rubinstein (CRR)** (Américain). Interface interactive PyQt5 avec visualisations en temps réel et données de marché actualisées.

## Fonctionnalités

### 🎯 Calcul des Options
- **Modèles de Tarification** :
    - **Black-Scholes-Merton** (BSM) pour les options européennes avec rendement de dividende.
    - **Cox-Ross-Rubinstein** (CRR) pour les options américaines avec arbre binomial dynamique.
- **Grecs complets** : 
    - Delta, Gamma, Theta (par jour), Vega, Rho
    - Visualisation interactive dans une tableau dédié
- **Volatilité Implicite (IV)** : Extraction automatique des données de marché via yfinance
- **Support des stratégies** : Positions long/short pour calls et puts

### 📊 Données de Marché en Temps Réel
- **Prix en direct** via Yahoo Finance (yfinance)
- **Taux SOFR** (Secured Overnight Financing Rate) depuis l'API FRED pour le taux sans risque
- **Rendement de dividende** récupéré automatiquement
- **Chaînes d'options complètes** (Options Chains) pour analyse du sourire de volatilité

### 📈 Visualisation et Analyse
- **Payoffs d'options** avec break-even calculé automatiquement
- **Simulation matricielle** : Impact croisé volatilité/prix sous-jacent sur le prix du call
- **Sourire de Volatilité (Volatility Smile)** :
    - Tracé IV vs Strike pour une échéance donnée
    - **Interpolation** par Spline Cubique pour une courbe lisse et continue
    - Analyse du Skew et Kurtosis de la volatilité
    - Support Puts OTM (gauche) et Calls OTM (droite)

### 🎨 Interface Utilisateur
- **Interface PyQt5** avec onglets multiples
- **Validation des entrées** avec contrôles QValidator
- **Gestion d'erreurs** complète avec messages informatifs
- **Graphiques intégrés** Matplotlib
- **Synchronisation des données** entre onglets

## Installation

### Prérequis
- **Python 3.8+** (testé avec Python 3.9, 3.10, 3.11)
- **pip** ou **conda** pour la gestion des dépendances
- **Clé API FRED** (gratuite) pour les taux SOFR

### Étapes d'installation

1. **Clonez le dépôt** :
```bash
git clone https://github.com/nono271105/option_pricer.git
cd option_pricer
```

2. **Créez un environnement virtuel** (fortement recommandé) :

```bash
python -m venv venv
source venv/bin/activate  # Sur Unix/macOS
venv\Scripts\activate     # Sur Windows
```

3. **Installez les dépendances** :

```bash
pip install -r requirements.txt
```

4. **Configurez les variables d'environnement** - Créez un fichier `.env` à la racine du projet :

```env
# Clé API FRED pour les taux SOFR
# Obtenir une clé gratuite sur https://fred.stlouisfed.org/
FRED_API_KEY=votre_cle_fred_ici
```

5. **Vérifiez l'installation** :

```bash
python -c "import PyQt5, yfinance, scipy; print('✓ Dépendances installées')"
```

## Utilisation

### Lancement de l'application

```bash
python main.py
```

L'interface PyQt5 s'ouvrira avec 4 onglets principaux.

### 📑 Onglet 1: "Calculateur BSM" (Black-Scholes-Merton)

**Paramètres d'entrée** :
1. Entrez un symbole boursier (ex: AAPL, MSFT, TSLA, SPY)
2. Définissez le prix d'exercice (K) et la date d'échéance
3. Choisissez le type (Call/Put) et la position (Long/Short)

**Actions** :
- **Récupérer les Données** : Synchronise 
  - Prix actuel (S) via yfinance
  - Taux SOFR (r) via l'API FRED
  - Rendement de dividende (q)
  - Volatilité historique (252 jours)
  - Volatilité implicite (IV) si disponible en marché

- **Calculer Prix et Grecs (BSM)** : 
  - Tarif l'option selon le modèle Black-Scholes-Merton
  - Utilise l'IV de marché si disponible, sinon la volatilité historique
  - Calcule les 5 Grecs : Δ, Γ, Θ, ν, ρ

- **Tracer le Payoff** : 
  - Visualise le P&L à maturité
  - Identifie automatiquement le break-even

**Résultats affichés** :
- Tableau avec les Grecs en temps réel
- Graphique du payoff interactif
- Source de volatilité utilisée (Marché IV vs Historique)
  
<img width="1440" height="900" alt="Onglet 1: Calculateur BSM" src="https://github.com/user-attachments/assets/30ea8f99-96ac-49a9-ba34-484ecb03efb1" />

---

### 🔢 Onglet 2: "Modèle CRR (Cox-Ross-Rubinstein)"

**Particularités** :
- Calcule le prix des **options américaines** (exercice anticipé possible)
- Utilise un **arbre binomial dynamique** (modèle Cox-Ross-Rubinstein)

**Paramètres spécifiques** :
- **Nombre de pas (N)** : Ajustez la précision de l'arbre (50-500 recommandé)
  - N ↑ = Précision ↑ mais calcul plus lent
  - N ↓ = Calcul rapide mais moins précis

**Résultats** :
- Prix CRR vs prix BSM (comparaison)
- Grecs spécifiques au modèle binomial
- Visualisation du payoff américain
  
<img width="1440" height="900" alt="Onglet 2: Modèle CRR" src="https://github.com/user-attachments/assets/ecb446c5-7d08-45c6-8761-847e2fda4c6d" />

---

### 📈 Onglet 3: "Simulation Call Price"

**Synchronisation automatique** :
- Récupère automatiquement les données du calculateur BSM (S, K, T, σ, r, q)
- Pas besoin de re-saisir les paramètres

**Simulation matricielle** :
- **Axes** : 
  - Abscisse : Prix sous-jacent (varié autour de S)
  - Ordonnée : Volatilité (varié autour de σ)
- **Cellules** : Prix théorique du Call pour chaque combinaison

**Code couleur** :
- 🟢 Vert = Prix bas
- 🟡 Jaune = Prix moyen
- 🔴 Rouge = Prix élevé

**Utilité** :
- Comprendre la sensibilité du prix du call
- Identifier les zones de profitabilité
- Analyser l'impact croisé S/σ (Gamma × Vega)
  
<img width="1440" height="900" alt="Onglet 3: Simulation Call Price" src="https://github.com/user-attachments/assets/b9099d90-6d76-47b0-b9b6-904ba023f67c" />

---

### 📊 Onglet 4: "Smile de Volatilité"

**Objectif** : Analyser la structure de la volatilité implicite du marché

**Utilisation** :
1. Sélectionnez un Ticker et une Date d'Échéance
2. Cliquez sur **"Afficher le Smile de Volatilité"**

**Traitement des données** :
- Récupère la chaîne d'options complète (Calls et Puts)
- Filtre les données invalides ou non liquides
- Trace chaque point (IV vs Strike) avec code couleur Calls/Puts
- Applique une **interpolation Spline Cubique** pour une courbe lisse

**Analyse** :
- Identifiez le **Skew** : asymétrie de l'IV par rapport au Strike ATM
- Détectez le **Kurtosis** : bombement ou aplatissement de la courbe
- Analysez l'impact des dividendes et des taux sur la volatilité

**Ligne pointillée rouge** : Prix actuel de l'actif (référence)

<img width="1440" height="900" alt="Onglet 4: Sourire de Volatilité" src="https://github.com/user-attachments/assets/07769499-978b-4687-9b82-67e29c1fcb3b" />

---

### 🌐 Onglet 5: "Surface IV 3D"

**Objectif** : Visualiser la surface 3D complète de la volatilité implicite

**Axes de la Surface** :
- **X-axis** : Strike (K) - Prix d'exercice
- **Y-axis** : Time to Maturity (T) - Jours jusqu'à l'expiration
- **Z-axis** : Implied Volatility (σ) - Volatilité implicite (en %)

**Utilisation** :
1. Entrez un Ticker (ex: AAPL, MSFT, TSLA, SPY)
2. Optionnel : Entrez le prix actuel (sinon récupération automatique)
3. Cliquez sur **"📈 Calculer la Surface IV"**
4. La surface 3D s'affiche avec gradient de couleur Plasma

**Interaction Interactive** :
- **Rotation** : Clic droit + glisse pour tourner la surface
- **Zoom** : Scroll de la souris ou boutons de zoom
- **Hover** : Survolez les points/surface pour voir les détails (Strike, Maturité, IV %)
- **Export** : Cliquez sur **"💾 Exporter (HTML)"** pour sauvegarder en fichier html

**Visualisation** :
- **Gradient Plasma** : Colormap rouge→bleu pour meilleure distinction des niveaux IV
- **Surface lissée** : Interpolation Cubic Griddata pour une surface continue

<img width="1440" height="900" alt="Surface IV 3D" src="https://github.com/user-attachments/assets/33d47407-3f72-4963-8cb5-065126b277c0" />

---

## Structure du Projet

```
option_pricer/
├── main.py                        # Point d'entrée principal
├── gui_app.py                     # Interface PyQt5 (5 onglets)
├── option_models.py               # Moteur de calcul
│   ├── Black-Scholes-Merton (BSM)
│   ├── Cox-Ross-Rubinstein (CRR)
│   └── Calcul des Grecs (Δ, Γ, Θ, ν, ρ)
├── data_fetcher.py                # API Data avec Caching (TTL=3600s)
│   ├── yfinance (prix, IV, options chains, dividendes)
│   ├── FRED API (taux SOFR)
│   └── DataCache (thread-safe, optimisé)
├── strategy_manager.py            # Calculs de payoff et stratégies
├── simulation_tab.py              # Interface onglet simulation matricielle
├── volatility_smile_tab.py        # Interface onglet sourire de volatilité
├── volatility_surface_tab.py      # Interface onglet surface 3D Plotly **NOUVEAU**
├── implied_volatility_surface.py  # Calcul surface 3D **NOUVEAU**
├── cache.py                       # Module caching TTL-based
├── requirements.txt               # Dépendances
└── README.md                      # Documentation
```

### Dépendances principales

| Package | Version | Usage |
|---------|---------|-------|
| `PyQt5` | >=5.15.0 | Interface graphique |
| `PyQtWebEngine` | >=5.15.0 | Affichage Plotly dans PyQt5 |
| `yfinance` | >=0.2.32 | Données de marché (prix, IV, options chains) |
| `matplotlib` | >=3.7.0 | Visualisation 2D |
| `plotly` | >=5.17.0 | Visualisation 3D interactive |
| `scipy` | >=1.9.0 | Calculs statistiques (CDF, interpolation Cubic) |
| `pandas` | >=2.0.0 | Manipulation de données |
| `numpy` | >=1.24.0 | Calculs numériques |
| `requests` | >=2.31.0 | Requêtes HTTP (FRED API) |
| `python-dotenv` | >=1.0.0 | Gestion des variables d'environnement |

---

## Licence

Distribué sous la licence MIT. Voir `LICENSE` pour plus d'informations.

---

**Dernière mise à jour** : 01 Décembre 2025 - Ajout du 5ème onglet Surface IV 3D Plotly
