# Option Pricer

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Une application Python pour l'évaluation d'options financières utilisant le modèle Black-Scholes.

## Fonctionnalités

### Calcul des Options
- **Modèle Black-Scholes avec dividendes** : Calcul précis du prix des options call/put
- **Grecs complets** : Delta, Gamma, Theta (par jour), Vega, Rho avec visualisation interactive
- **Graphiques des Grecs** : Cliquez sur un Grec pour voir son évolution en fonction du prix du sous-jacent

### Données de Marché en Temps Réel
- **Prix en direct** via Yahoo Finance
- **Taux SOFR** (Secured Overnight Financing Rate) via l'API FRED pour le taux sans risque
- **Rendement de dividende** automatiquement récupéré
- **Volatilité historique** calculée sur 1 an (252 jours de trading)

### Visualisation et Analyse
- **Payoffs d'options** avec breakeven automatiquement calculé
- **Positions long/short** pour calls et puts
- **Simulation matricielle** : Impact de la volatilité et du prix sous-jacent sur le prix d'un call
- **Code couleur** dans les simulations pour une analyse visuelle rapide

### Interface Utilisateur
- **Interface PyQt5** intuitive avec onglets
- **Validation des entrées** avec contrôles automatiques
- **Gestion d'erreurs** complète avec messages informatifs
- **Graphiques intégrés** avec Matplotlib

## Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/nono271105/option_pricer
cd option_pricer
```

2. Créez un environnement virtuel (recommandé) :
```bash
python -m venv venv
source venv/bin/activate  # Sur Unix/macOS
venv\Scripts\activate     # Sur Windows
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Créez un fichier `.env` (optionnel) :
```bash
# Ajoutez vos clés API si nécessaire
FRED_API_KEY=votre_cle_fred_api
```

## Utilisation

### Lancement
```bash
python main.py
```

### Onglet "Calculateur d'Option"

1. **Configuration de base** :
   - Entrez un symbole boursier (ex: AAPL, MSFT, TSLA)
   - Sélectionnez le type d'option (call/put)
   - Définissez le prix d'exercice (K)
   - Choisissez la date d'échéance
   - Sélectionnez la position (long/short)

2. **Récupération des données** :
   - Cliquez sur "Récupérer les Données"
   - Les données de marché se mettent à jour automatiquement

3. **Calculs et visualisation** :
   - "Calculer Prix et Grecs" : Affiche le prix Black-Scholes et tous les Grecs
   - "Cliquez sur une Grec" dans le tableau pour voir son graphique
   - "Tracer le Payoff" : Visualise le profit/perte à l'échéance

### Onglet "Simulation Call Price"

1. **Paramètres automatiques** :
   - Les données du premier onglet sont automatiquement transférées
   - Les plages de simulation sont calculées automatiquement :
     - Volatilité : ±15 points de pourcentage autour de la volatilité historique
     - Prix sous-jacent : ±10% autour du prix actuel

2. **Simulation matricielle** :
   - Ajustez les pas de simulation si nécessaire
   - Lancez la simulation pour voir l'impact croisé
   - Les couleurs vont du vert (prix bas) au rouge (prix élevé)

## Structure du Projet

```
option_pricer/
├── main.py                 # Point d'entrée de l'application
├── gui_app.py             # Interface utilisateur principale avec gestion des graphiques
├── option_models.py       # Modèle Black-Scholes et calcul des Grecs
├── data_fetcher.py        # Récupération des données (yfinance + FRED API)
├── strategy_manager.py    # Calculs de payoff et stratégies
├── simulation_tab.py      # Interface de simulation matricielle
├── requirements.txt       # Dépendances Python
└── README.md             # Documentation
```

## Dépendances Principales

| Package | Usage |
|---------|-------|
| **PyQt5** | Interface graphique moderne |
| **yfinance** | Données financières en temps réel |
| **requests** | Appels API FRED pour le taux SOFR |
| **numpy** | Calculs numériques et matrices |
| **scipy** | Fonctions statistiques (distribution normale) |
| **matplotlib** | Graphiques et visualisations |
| **pandas** | Manipulation de données (via yfinance) |
| **python-dotenv** | Gestion des variables d'environnement |

## Formules et Méthodologies

### Modèle Black-Scholes avec Dividendes
```
C = S₀e^(-qT)N(d₁) - Ke^(-rT)N(d₂)
P = Ke^(-rT)N(-d₂) - S₀e^(-qT)N(-d₁)

où:
d₁ = [ln(S₀/K) + (r - q + σ²/2)T] / (σ√T)
d₂ = d₁ - σ√T
```

### Grecs
- **Delta** : ∂V/∂S (sensibilité au prix du sous-jacent)
- **Gamma** : ∂²V/∂S² (sensibilité du Delta)
- **Theta** : ∂V/∂T (décroissance temporelle, par jour)
- **Vega** : ∂V/∂σ (sensibilité à la volatilité)
- **Rho** : ∂V/∂r (sensibilité au taux d'intérêt)

### Sources de Données
- **Prix et dividendes** : Yahoo Finance API
- **Taux sans risque** : SOFR via FRED API (Federal Reserve Economic Data)
- **Volatilité** : Calculée sur les rendements historiques quotidiens (252 jours)

## Fonctionnalités Avancées

### Graphiques Interactifs des Grecs
- Cliquez sur n'importe quel Grec dans le tableau pour voir son évolution
- Graphiques en fenêtre séparée avec marqueur du prix actuel
- Plage automatique de ±30% autour du prix actuel

### Gestion d'Erreurs
- Validation des données de marché manquantes
- Gestion des cas limites (échéance passée, volatilité nulle)
- Messages d'avertissement informatifs
- Valeurs par défaut raisonnables en cas d'échec d'API

### Calculs de Breakeven
Calcul automatique du point mort pour chaque stratégie :
- **Long Call** : K + Prime
- **Short Call** : K + Prime  
- **Long Put** : K - Prime
- **Short Put** : K - Prime

## Remarques Techniques

- **Précision des calculs** : Utilisation de `scipy.stats.norm` pour les fonctions de distribution
- **Gestion des dividendes** : Modèle Black-Scholes-Merton complet
- **Fréquence des données** : Données en temps réel pendant les heures de marché
- **Volatilité annualisée** : √252 pour l'annualisation (252 jours de trading/an)
- **Convention Theta** : Exprimé par jour pour une utilisation pratique

## Limitations

- Modèle européen uniquement (pas d'exercice anticipé)
- Volatilité constante assumée
- Taux d'intérêt et dividendes constants
- Pas de coûts de transaction inclus

## Licence

Distribué sous la licence MIT. Voir `LICENSE` pour plus d'informations.
