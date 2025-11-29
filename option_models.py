import numpy as np
from scipy.stats import norm
from typing import Dict, Literal, Optional

class OptionModels:
    def black_scholes_price(
        self, 
        S: float, 
        K: float, 
        T: float, 
        r: float, 
        sigma: float, 
        q: float, 
        option_type: Literal['call', 'put'] = 'call'
    ) -> float:
        """
        Calcule le prix d'une option européenne en utilisant le modèle Black-Scholes.
        
        Args:
            S: Prix actuel de l'actif sous-jacent
            K: Prix d'exercice (strike)
            T: Temps jusqu'à expiration (en années)
            r: Taux sans risque annualisé
            sigma: Volatilité annualisée
            q: Rendement de dividende annualisé
            option_type: 'call' ou 'put'
            
        Returns:
            float: Prix théorique de l'option
        """
        if T <= 0:
            if option_type == 'call':
                return max(0, S - K)
            elif option_type == 'put':
                return max(0, K - S)

        # Empêcher les erreurs si sigma est trop petit ou négatif
        if sigma <= 1e-6:
            if option_type == 'call':
                return max(0, S * np.exp(-q * T) - K * np.exp(-r * T))
            elif option_type == 'put':
                return max(0, K * np.exp(-r * T) - S * np.exp(-q * T))
            
        d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        if option_type == 'call':
            price = S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        elif option_type == 'put':
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)
        else:
            raise ValueError("option_type doit être 'call' ou 'put'")

        return price

    def calculate_greeks(
        self, 
        S: float, 
        K: float, 
        T: float, 
        r: float, 
        sigma: float, 
        q: float, 
        option_type: Literal['call', 'put'] = 'call'
    ) -> Dict[str, float]:
        """
        Calcule les Grecs (Delta, Gamma, Theta, Vega, Rho) pour le modèle Black-Scholes.
        
        Args:
            S: Prix actuel de l'actif sous-jacent
            K: Prix d'exercice
            T: Temps jusqu'à expiration (en années)
            r: Taux sans risque annualisé
            sigma: Volatilité annualisée
            q: Rendement de dividende annualisé
            option_type: 'call' ou 'put'
            
        Returns:
            Dict[str, float]: Dictionnaire avec clés 'delta', 'gamma', 'theta', 'vega', 'rho'
        """
        if T <= 0 or sigma <= 1e-6:
            return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'rho': 0}
            
        d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        Nd1 = norm.cdf(d1)
        n_d1 = norm.pdf(d1)

        # Delta
        if option_type == 'call':
            delta = np.exp(-q * T) * Nd1
        else: # put
            delta = -np.exp(-q * T) * norm.cdf(-d1)

        # Gamma
        gamma = np.exp(-q * T) * n_d1 / (S * sigma * np.sqrt(T))

        # Vega
        vega = S * np.exp(-q * T) * n_d1 * np.sqrt(T)

        # Theta (annualisé)
        theta_part1 = -(S * np.exp(-q * T) * n_d1 * sigma) / (2 * np.sqrt(T))
        
        if option_type == 'call':
            theta_part2 = -r * K * np.exp(-r * T) * norm.cdf(d2)
            theta_part3 = q * S * np.exp(-q * T) * Nd1
        else: # put
            theta_part2 = r * K * np.exp(-r * T) * norm.cdf(-d2)
            theta_part3 = -q * S * np.exp(-q * T) * norm.cdf(-d1)
            
        theta = theta_part1 + theta_part2 + theta_part3
        theta_daily = theta / 365.0

        # Rho
        if option_type == 'call':
            rho = K * T * np.exp(-r * T) * norm.cdf(d2)
        else: # put
            rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)
        
        return {
            'delta': delta,
            'gamma': gamma,
            'theta': theta_daily,
            'vega': vega,
            'rho': rho
        }

    def cox_ross_rubinstein_price(
        self, 
        S: float, 
        K: float, 
        T: float, 
        r: float, 
        q: float, 
        sigma: float, 
        N: int, 
        option_type: Literal['call', 'put']
    ) -> float:
        """
        Calcule le prix d'une option Américaine en utilisant le modèle binomial CRR.
        
        Args:
            S: Prix actuel de l'actif sous-jacent
            K: Prix d'exercice
            T: Temps jusqu'à expiration (en années)
            r: Taux sans risque annualisé
            q: Rendement de dividende annualisé
            sigma: Volatilité annualisée
            N: Nombre de pas dans l'arbre binomial
            option_type: 'call' ou 'put'
            
        Returns:
            float: Prix théorique de l'option américaine
        """
        if T <= 0 or N <= 0:
            if option_type == 'call':
                return max(0, S - K)
            elif option_type == 'put':
                return max(0, K - S)

        dt = T / N
        df = np.exp(-r * dt)
        df_q = np.exp(-(r - q) * dt)

        u = np.exp(sigma * np.sqrt(dt))
        d = 1.0 / u
        p = (df_q - d) / (u - d)

        # 1. Initialiser le prix de l'actif aux nœuds à l'échéance (t=N)
        stock_prices = np.zeros(N + 1)
        for j in range(N + 1):
            stock_prices[j] = S * (u**j) * (d**(N - j))

        # 2. Calculer la valeur de l'option à l'échéance (t=N)
        option_values = np.zeros(N + 1)
        if option_type == 'call':
            option_values = np.maximum(stock_prices - K, 0)
        elif option_type == 'put':
            option_values = np.maximum(K - stock_prices, 0)
        
        # 3. Rétropropagation (Backward Induction)
        for i in range(N - 1, -1, -1):
            for j in range(i + 1):
                # Valeur de continuation (Prix de l'option européenne actualisé d'un pas)
                continuation_value = df * (p * option_values[j + 1] + (1 - p) * option_values[j])
                
                # Prix de l'actif à ce noeud
                S_node = S * (u**j) * (d**(i - j))
                
                # Valeur d'exercice immédiat
                if option_type == 'call':
                    exercise_value = max(0, S_node - K)
                elif option_type == 'put':
                    exercise_value = max(0, K - S_node)
                
                # Option Américaine: Max(Continuation, Exercice)
                option_values[j] = max(continuation_value, exercise_value)

        return option_values[0]

    def calculate_greeks_crr(
        self, 
        S: float, 
        K: float, 
        T: float, 
        r: float, 
        q: float, 
        sigma: float, 
        N: int, 
        option_type: Literal['call', 'put'], 
        epsilon: float = 1e-4
    ) -> Dict[str, float]:
        """
        Calcule les Grecs du modèle CRR par différences finies.
        
        Args:
            S: Prix actuel de l'actif sous-jacent
            K: Prix d'exercice
            T: Temps jusqu'à expiration (en années)
            r: Taux sans risque annualisé
            q: Rendement de dividende annualisé
            sigma: Volatilité annualisée
            N: Nombre de pas dans l'arbre binomial
            option_type: 'call' ou 'put'
            epsilon: Pas pour les différences finies (par défaut 1e-4)
            
        Returns:
            Dict[str, float]: Dictionnaire avec clés 'delta', 'gamma', 'theta', 'vega', 'rho'
        """
        
        # Fonction utilitaire pour le prix CRR
        def crr_price(S_local, sigma_local, r_local):
            return self.cox_ross_rubinstein_price(S_local, K, T, r_local, q, sigma_local, N, option_type)
            
        # Delta (dérivée par rapport à S)
        S_plus = S + epsilon
        S_minus = S - epsilon
        C_plus = crr_price(S_plus, sigma, r)
        C_minus = crr_price(S_minus, sigma, r)
        delta = (C_plus - C_minus) / (2 * epsilon)

        # Gamma (dérivée seconde par rapport à S)
        C_center = crr_price(S, sigma, r)
        gamma = (C_plus - 2 * C_center + C_minus) / (epsilon**2)
        
        # Theta (dérivée par rapport à T, divisée par 365 pour "par jour")
        T_epsilon_minus = T - epsilon
        if T_epsilon_minus <= 0: T_epsilon_minus = 1e-6 
        
        C_t_minus_epsilon = self.cox_ross_rubinstein_price(S, K, T_epsilon_minus, r, q, sigma, N, option_type)
        theta = (C_t_minus_epsilon - C_center) / epsilon
        theta_daily = theta / 365.0 
        

        # Vega (dérivée par rapport à sigma)
        sigma_plus = sigma + epsilon
        sigma_minus = sigma - epsilon
        C_sigma_plus = crr_price(S, sigma_plus, r)
        C_sigma_minus = crr_price(S, sigma_minus, r)
        vega = (C_sigma_plus - C_sigma_minus) / (2 * epsilon)
        
        # Rho (dérivée par rapport à r)
        r_plus = r + epsilon
        r_minus = r - epsilon
        C_r_plus = crr_price(S, sigma, r_plus)
        C_r_minus = crr_price(S, sigma, r_minus)
        rho = (C_r_plus - C_r_minus) / (2 * epsilon)
        
        return {
            'delta': delta,
            'gamma': gamma,
            'theta': theta_daily,
            'vega': vega,
            'rho': rho
        }

