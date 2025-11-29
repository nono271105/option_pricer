import numpy as np
import matplotlib.pyplot as plt
from typing import Literal, Optional

class StrategyManager:
    def __init__(self) -> None:
        pass

    def calculate_single_option_payoff(
        self, 
        S_range: np.ndarray, 
        K: float, 
        premium: float, 
        option_type: Literal['call', 'put'], 
        position: Literal['long', 'short']
    ) -> np.ndarray:
        """
        Calcule le payoff net à maturité pour une seule option.

        Args:
            S_range: Gamme de prix de l'actif sous-jacent à l'échéance
            K: Prix d'exercice
            premium: Prime payée (long) ou reçue (short)
            option_type: 'call' ou 'put'
            position: 'long' (achat) ou 'short' (vente)

        Returns:
            np.ndarray: Le payoff net pour chaque prix dans S_range
        """
        if option_type == 'call':
            gross_payoff = np.maximum(S_range - K, 0)
        elif option_type == 'put':
            gross_payoff = np.maximum(K - S_range, 0)
        else:
            raise ValueError("option_type doit être 'call' ou 'put'")

        if position == 'long':
            net_payoff = gross_payoff - premium
        elif position == 'short':
            net_payoff = -gross_payoff + premium
        else:
            raise ValueError("position doit être 'long' ou 'short'")
        return net_payoff

    def plot_payoff(
        self, 
        K: float, 
        premium: float, 
        option_type: Literal['call', 'put'], 
        position: Literal['long', 'short'], 
        title: str = "", 
        ax: Optional[object] = None
    ) -> None:
        """
        Trace le payoff à maturité pour une seule option.

        Args:
            K: Prix d'exercice
            premium: Prime de l'option
            option_type: 'call' ou 'put'
            position: 'long' (achat) ou 'short' (vente)
            title: Titre du graphique
            ax: Axe Matplotlib optionnel (crée un nouvel axe si None)
        """
        # Définir une plage de prix de l'actif sous-jacent pour le tracé
        # Étendre la plage autour du strike pour bien voir le payoff
        S_min = max(0, K * 0.7)
        S_max = K * 1.3
        S_range = np.linspace(S_min, S_max, 200)

        payoff = self.calculate_single_option_payoff(S_range, K, premium, option_type, position)

        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))

        ax.plot(S_range, payoff, label=f'{position.capitalize()} {option_type.capitalize()} (K={K})')
        ax.axhline(0, color='grey', linestyle='--', linewidth=0.8) # Ligne du zéro payoff
        ax.axvline(K, color='grey', linestyle=':', linewidth=0.8, label=f'Strike K={K}') # Ligne du strike
        ax.set_xlabel("Prix de l'actif sous-jacent à l'échéance (S)")
        ax.set_ylabel("Profit/Perte")
        ax.set_title(title or f"Payoff - {position.capitalize()} {option_type.capitalize()} (K={K}, Premium={premium:.2f})")
        ax.grid(True)
        ax.legend()

