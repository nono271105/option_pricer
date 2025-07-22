import numpy as np
import matplotlib.pyplot as plt

class StrategyManager:
    def __init__(self):
        pass

    def calculate_single_option_payoff(self, S_range, K, premium, option_type, position):
        """
        Calcule le payoff à maturité pour une seule option.

        Paramètres:
        S_range (np.array): Gamme de prix de l'actif sous-jacent à l'échéance.
        K (float): Prix d'exercice.
        premium (float): Prime payée (pour achat) ou reçue (pour vente).
        option_type (str): 'call' ou 'put'.
        position (str): 'long' (achat) ou 'short' (vente).

        Retourne:
        np.array: Le payoff net pour chaque prix dans S_range.
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

    def plot_payoff(self, K, premium, option_type, position, title="", ax=None):
        """
        Trace le payoff à maturité pour une seule option.

        Paramètres:
        K (float): Prix d'exercice.
        premium (float): Prime de l'option.
        option_type (str): 'call' ou 'put'.
        position (str): 'long' (achat) ou 'short' (vente).
        title (str): Titre du graphique.
        ax (matplotlib.axes._axes.Axes, optional): Axe Matplotlib sur lequel tracer.
                                                  Crée un nouvel axe si None.
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

# Test de la classe (peut être supprimé en production)
if __name__ == "__main__":
    manager = StrategyManager()

    # Exemple d'achat de Call
    K_call = 100
    premium_call = 5
    manager.plot_payoff(K_call, premium_call, 'call', 'long', "Payoff Achat Call")
    plt.show()

    # Exemple de vente de Put
    K_put = 95
    premium_put = 3
    manager.plot_payoff(K_put, premium_put, 'put', 'short', "Payoff Vente Put")
    plt.show()

    # Pour montrer comment combiner des stratégies (future extension)
    # def plot_strategy(options, S_range):
    #     total_payoff = np.zeros_like(S_range, dtype=float)
    #     for opt in options:
    #         K, premium, option_type, position = opt['K'], opt['premium'], opt['option_type'], opt['position']
    #         total_payoff += manager.calculate_single_option_payoff(S_range, K, premium, option_type, position)
    #     plt.figure(figsize=(10, 6))
    #     plt.plot(S_range, total_payoff, label="Stratégie Combinée")
    #     plt.axhline(0, color='grey', linestyle='--')
    #     plt.xlabel("Prix de l'actif sous-jacent à l'échéance (S)")
    #     plt.ylabel("Profit/Perte")
    #     plt.title("Payoff - Stratégie Combinée")
    #     plt.grid(True)
    #     plt.legend()
    #     plt.show()

    # S_range_combined = np.linspace(80, 120, 200)
    # options_example = [
    #     {'K': 100, 'premium': 5, 'option_type': 'call', 'position': 'long'},
    #     {'K': 105, 'premium': 2, 'option_type': 'call', 'position': 'short'}
    # ]
    # plot_strategy(options_example, S_range_combined)