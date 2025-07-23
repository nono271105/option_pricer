# Option Pricer
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Une application Python pour l'évaluation d'options financières utilisant le modèle Black-Scholes et l'analyse des stratégies d'options.

## Fonctionnalités

- Calcul du prix des options selon le modèle Black-Scholes (incluant les dividendes)
- Calcul des Grecs (Delta, Gamma, Theta, Vega, Rho)
- Récupération des données financières en temps réel via Yahoo Finance
- Visualisation des payoffs d'options
- Simulation de prix d'options avec différentes volatilités et prix sous-jacents
- Interface graphique intuitive avec PyQt5

## Installation

1. Clonez le dépôt :
```sh
git clone https://github.com/nono271105/option_pricer
cd documents
```

2. Créez un environnement virtuel (recommandé) :
```sh
python -m venv venv
source venv/bin/activate  # Sur Unix/macOS
venv\Scripts\activate     # Sur Windows
```

3. Installez les dépendances :
```sh
pip install -r requirements.txt
```

## Utilisation

1. Lancez l'application :
```sh
python main.py
```

2. Dans l'onglet "Calculateur d'Option" :
   - Entrez un symbole boursier (ex: AAPL)
   - Cliquez sur "Récupérer les Données" pour obtenir les données de marché
   - Configurez les paramètres de l'option (type, strike, échéance)
   - Utilisez les boutons pour calculer le prix et visualiser le payoff

3. Dans l'onglet "Simulation Call Price" :
   - Utilisez la matrice de simulation pour voir l'impact de la volatilité et du prix sous-jacent
   - Les résultats sont présentés avec un code couleur pour une meilleure visualisation

## Structure du Projet

- `main.py` : Point d'entrée de l'application
- `gui_app.py` : Interface utilisateur principale
- `option_models.py` : Implémentation du modèle Black-Scholes
- `data_fetcher.py` : Récupération des données financières
- `strategy_manager.py` : Gestion des stratégies et calculs de payoff
- `simulation_tab.py` : Interface de simulation de prix d'options

## Dépendances Principales

- PyQt5 : Interface graphique
- yfinance : Données financières
- numpy : Calculs numériques
- matplotlib : Visualisation
- scipy : Fonctions statistiques

## Remarques

- Les données financières sont récupérées en temps réel via Yahoo Finance
- La volatilité historique est calculée sur une période d'un an (52 sem)
- Le taux sans risque est basé sur le rendement du bon du Trésor (^TNX)
