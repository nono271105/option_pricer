import numpy as np
from scipy.stats import norm
# from scipy.optimize import brentq # Supprimé car implied_volatility n'est plus utilisée

class OptionModels:
    def __init__(self):
        pass

    def black_scholes_price(self, S, K, T, r, sigma, q, option_type='call'):
        """
        Calcule le prix d'une option européenne en utilisant le modèle Black-Scholes.

        Paramètres:
        S (float): Prix actuel de l'actif sous-jacent
        K (float): Prix d'exercice (strike) de l'option
        T (float): Temps jusqu'à l'échéance en années (ex: 0.5 pour 6 mois)
        r (float): Taux sans risque annuel (taux continu)
        sigma (float): Volatilité annualisée de l'actif sous-jacent
        q (float): Rendement du dividende continu annualisé
        option_type (str): 'call' pour une option d'achat, 'put' pour une option de vente

        Retourne:
        float: Le prix Black-Scholes de l'option
        """
        if T <= 0:
            if option_type == 'call':
                return max(0, S - K)
            elif option_type == 'put':
                return max(0, K - S)

        # Empêcher les erreurs si sigma est trop petit ou négatif
        if sigma <= 1e-6: # Un sigma très proche de zéro peut causer des problèmes
            if option_type == 'call':
                return max(0, S * np.exp(-q * T) - K * np.exp(-r * T))
            else: # put
                return max(0, K * np.exp(-r * T) - S * np.exp(-q * T))


        d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        if option_type == 'call':
            price = S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        elif option_type == 'put':
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)
        else:
            raise ValueError("option_type doit être 'call' ou 'put'")
        return price


    def calculate_greeks(self, S, K, T, r, sigma, q, option_type='call'):
        """
        Calcule les Grecs (Delta, Gamma, Theta, Rho, Vega) pour une option européenne.

        Paramètres:
        S (float): Prix actuel de l'actif sous-jacent
        K (float): Prix d'exercice (strike) de l'option
        T (float): Temps jusqu'à l'échéance en années
        r (float): Taux sans risque annuel
        sigma (float): Volatilité annualisée
        q (float): Rendement du dividende continu annualisé
        option_type (str): 'call' ou 'put'

        Retourne:
        dict: Un dictionnaire contenant les valeurs des Grecs
        """
        if T <= 0 or sigma <= 1e-6: # Gérer les cas où T=0 ou sigma est très faible
            # Retourner des valeurs par défaut pour les Grecs à maturité ou avec vol nulle
            return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'rho': 0}

        d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        greeks = {}

        # Delta
        if option_type == 'call':
            greeks['delta'] = np.exp(-q * T) * norm.cdf(d1)
        elif option_type == 'put':
            greeks['delta'] = np.exp(-q * T) * (norm.cdf(d1) - 1)

        # Gamma (identique pour call et put)
        greeks['gamma'] = np.exp(-q * T) * norm.pdf(d1) / (S * sigma * np.sqrt(T))

        # Vega (identique pour call et put)
        greeks['vega'] = S * np.exp(-q * T) * norm.pdf(d1) * np.sqrt(T) # Non divisé par 100 ici, le fera dans GUI

        # Theta (par jour)
        if option_type == 'call':
            theta_annual = - (S * np.exp(-q * T) * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) \
                           + q * S * np.exp(-q * T) * norm.cdf(d1) \
                           - r * K * np.exp(-r * T) * norm.cdf(d2)
        elif option_type == 'put':
            theta_annual = - (S * np.exp(-q * T) * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) \
                           - q * S * np.exp(-q * T) * norm.cdf(-d1) \
                           + r * K * np.exp(-r * T) * norm.cdf(-d2)
        greeks['theta'] = theta_annual / 365.0

        # Rho (pour 1% de changement dans le taux sans risque)
        if option_type == 'call':
            greeks['rho'] = K * T * np.exp(-r * T) * norm.cdf(d2) / 100.0
        elif option_type == 'put':
            greeks['rho'] = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100.0

        return greeks

# Test de la classe (peut être supprimé en production)
if __name__ == "__main__":
    models = OptionModels()

    # Paramètres de test
    S_test = 100    # Prix de l'actif sous-jacent
    K_test = 100    # Prix d'exercice
    T_test = 0.5    # Temps jusqu'à l'échéance (0.5 an = 6 mois)
    r_test = 0.05   # Taux sans risque (5%)
    sigma_test = 0.20 # Volatilité (20%) - maintenant HISTORIQUE
    q_test = 0.01   # Rendement du dividende (1%)
    option_type_test = 'call'

    # 1. Calcul du prix Black-Scholes avec volatilité historique
    bs_price = models.black_scholes_price(S_test, K_test, T_test, r_test, sigma_test, q_test, option_type_test)
    print(f"Prix Black-Scholes ({option_type_test}) avec volatilité historique: {bs_price:.4f}")

    # 2. Calcul des Grecs
    greeks = models.calculate_greeks(S_test, K_test, T_test, r_test, sigma_test, q_test, option_type_test)
    print("\nGrecs:")
    for greek_name, value in greeks.items():
        print(f"  {greek_name.capitalize()}: {value:.4f}")

    # Test avec une put
    option_type_test_put = 'put'
    bs_price_put = models.black_scholes_price(S_test, K_test, T_test, r_test, sigma_test, q_test, option_type_test_put)
    print(f"\nPrix Black-Scholes ({option_type_test_put}) avec volatilité historique: {bs_price_put:.4f}")
    greeks_put = models.calculate_greeks(S_test, K_test, T_test, r_test, sigma_test, q_test, option_type_test_put)
    print("Grecs (Put):")
    for greek_name, value in greeks_put.items():
        print(f"  {greek_name.capitalize()}: {value:.4f}")