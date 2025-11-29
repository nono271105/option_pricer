<h1 align="center">
  <img src="https://github.com/user-attachments/assets/8145acf4-0b8c-47e1-afa7-fd7d1b56da96" alt="logo" width="100" style="vertical-align: middle; margin-right: 1px;">
  Option Pricer
</h1>

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/) 
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Une application Python pour l'évaluation d'options financières utilisant les modèles **Black-Scholes** (Européen) et **Cox-Ross-Rubinstein (CRR)** (Américain).

## Fonctionnalités

### Calcul des Options
- **Modèles de Tarification** :
    - **Black-Scholes-Merton** (BSM) pour les options européennes avec dividendes.
    - **Cox-Ross-Rubinstein** (CRR) pour les options américaines (arbre binomial).
- **Grecs complets** : Delta, Gamma, Theta (par jour), Vega, Rho avec visualisation interactive.
- **Volatilité Implicite (IV)** : Automatiquement récupérée pour une tarification plus précise.

### Données de Marché en Temps Réel
- **Prix en direct** via Yahoo Finance.
- **Taux SOFR** (Secured Overnight Financing Rate) via l'API FRED pour le taux sans risque.
- **Rendement de dividende** automatiquement récupéré.

### Visualisation et Analyse
- **Payoffs d'options** avec breakeven automatiquement calculé.
- **Positions long/short** pour calls et puts.
- **Simulation matricielle** : Impact de la volatilité et du prix sous-jacent sur le prix d'un call.
- **Sourire de Volatilité (Volatility Smile)** :
    - Tracé de l'IV en fonction du Strike pour une échéance donnée.
    - **Lissage par Spline Cubique** pour une courbe claire et continue, facilitant l'analyse du Skew et du Kurtosis. 

### Interface Utilisateur
- **Interface PyQt5** intuitive avec onglets.
- **Validation des entrées** avec contrôles automatiques.
- **Gestion d'erreurs** complète avec messages informatifs.
- **Graphiques intégrés** avec Matplotlib.

## Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/nono271105/option_pricer
cd option_pricer
````

2.  Créez un environnement virtuel (recommandé) :

<!-- end list -->

```bash
python -m venv venv
source venv/bin/activate  # Sur Unix/macOS
venv\Scripts\activate     # Sur Windows
```

3.  Installez les dépendances :

<!-- end list -->

```bash
pip install -r requirements.txt
```

4.  Créez un fichier `.env` :

<!-- end list -->

```bash
# Nécessaire pour le taux sans risque (SOFR)
FRED_API_KEY=votre_cle_fred_api
```

## Utilisation

### Lancement

```bash
python main.py
```

### Onglet "Calculateur BSM"

1.  **Configuration de base** :
      - Entrez un symbole boursier (ex: AAPL, MSFT, TSLA).
      - Définissez le prix d'exercice (K) et la date d'échéance.
2.  **Calculs et visualisation** :
      - "Récupérer les Données" : Synchronise le prix, r, q, et la volatilité historique.
      - "Calculer Prix et Grecs (BSM)" : Utilise l'IV de marché (si disponible) ou la Volatilité Historique pour la tarification et les Grecs.
-----

### Onglet "Modèle CRR (Américain)"

  - Calcule le prix des **options américaines** pour un exercice anticipé potentiel.
  - Utilisez le paramètre **"Nombre de pas (N)"** pour ajuster la précision de l'arbre binomial.
  - Affiche le prix et les Grecs spécifiques au modèle CRR.

-----

### Onglet "Sourire de Volatilité"

  - **Sélectionnez un Ticker et une Date d'Échéance.**
  - Cliquez sur **"Afficher le Sourire de Volatilité"** pour :
    1.  Récupérer la chaîne d'options complète pour cette échéance.
    2.  Nettoyer et filtrer les données IV non valides.
    3.  Tracer l'ensemble des points (Calls et Puts) et la **courbe lissée par Spline Cubique**.
    4.  Visualiser le prix actuel de l'actif (ligne pointillée rouge) par rapport aux Strikes.

-----

### Onglet "Simulation Call Price"

1.  **Paramètres automatiques** :

      - Les données (S, K, T, $\sigma$, r, q) du calculateur BSM sont automatiquement transférées.
      - Les plages de simulation sont calculées autour de ces valeurs.

2.  **Simulation matricielle** :

      - Lancez la simulation pour voir l'impact croisé de la volatilité et du prix sous-jacent sur le prix du Call.
      - **Code couleur** : du vert (prix bas) au rouge (prix élevé) pour une analyse rapide.

## Structure du Projet

```
option_pricer/
├── main.py                 # Point d'entrée de l'application
├── gui_app.py             # Interface utilisateur principale, gestion des onglets CRR et Smile
├── option_models.py       # Modèles Black-Scholes et CRR, calcul des Grecs
├── data_fetcher.py        # Récupération des données (yfinance + FRED API)
├── strategy_manager.py    # Calculs de payoff et stratégies
├── simulation_tab.py      # Interface de simulation matricielle
├── requirements.txt       # Dépendances Python
└── README.md             # Documentation
```

## Licence

Distribué sous la licence MIT. Voir `LICENSE` pour plus d'informations.
