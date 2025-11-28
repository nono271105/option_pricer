import sys
import yfinance as yf
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFormLayout, QGroupBox, QGridLayout,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit,
    QTabWidget, QDialog 
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QDoubleValidator, QIntValidator

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from datetime import date, datetime

from data_fetcher import DataFetcher
from option_models import OptionModels
from strategy_manager import StrategyManager
from simulation_tab import CallPriceSimulationTab

# Nouvelle classe pour la fenêtre de dialogue des graphiques
class PlottingDialog(QDialog):
    """
    Une petite fenêtre de dialogue pour afficher les graphiques Matplotlib.
    """
    def __init__(self, parent=None, title="Graphique"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(150, 150, 700, 500) # Taille par défaut

        layout = QVBoxLayout(self)
        self.fig = Figure(figsize=(7, 5))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

class OptionPricingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Option Pricer") # Titre de la fenêtre principale
        self.setGeometry(100, 100, 1200, 800)

        self.data_fetcher = DataFetcher()
        self.option_models = OptionModels()
        self.strategy_manager = StrategyManager()

        self.S = None
        self.r = None
        self.q = None
        self.historical_vol = None
        self.current_ticker = None
        
        # Ajout des attributs pour stocker les paramètres de l'option calculés
        # Ces attributs seront utilisés par les fonctions de tracé des Grecs
        self.K = None 
        self.T = None 
        self.option_type = None 
        self.current_sigma = None # Volatilité utilisée pour le dernier calcul des Grecs

        self.init_ui()

    def init_ui(self):
        self.tab_widget = QTabWidget()

        option_calculator_widget = QWidget()
        option_calculator_layout = QHBoxLayout(option_calculator_widget)

        # --- Panneau de contrôle à gauche (du premier onglet) ---
        control_panel_layout = QVBoxLayout()
        control_panel_group = QGroupBox("Paramètres de l'option")
        control_form_layout = QFormLayout()

        self.ticker_input = QLineEdit("AAPL")
        self.ticker_input.setPlaceholderText("Ex: AAPL")
        control_form_layout.addRow("Ticker Symbole:", self.ticker_input)

        self.option_type_combo = QComboBox()
        self.option_type_combo.addItems(["call", "put"])
        control_form_layout.addRow("Type d'option:", self.option_type_combo)

        self.strike_input = QLineEdit("150.00")
        self.strike_input.setValidator(QDoubleValidator(0.0, 100000.0, 2))
        control_form_layout.addRow("Prix d'exercice (K):", self.strike_input)

        self.maturity_date_input = QDateEdit(QDate.currentDate().addMonths(3))
        self.maturity_date_input.setCalendarPopup(True)
        self.maturity_date_input.setDisplayFormat("dd/MM/yyyy")
        control_form_layout.addRow("Date d'échéance:", self.maturity_date_input)

        self.position_combo = QComboBox()
        self.position_combo.addItems(["long", "short"])
        control_form_layout.addRow("Position:", self.position_combo)

        self.fetch_data_button = QPushButton("Récupérer les Données")
        self.fetch_data_button.clicked.connect(self.fetch_data)
        control_form_layout.addRow(self.fetch_data_button)

        self.calculate_button = QPushButton("Calculer Prix et Grecs")
        self.calculate_button.clicked.connect(self.calculate_option_metrics)
        control_form_layout.addRow(self.calculate_button)

        self.plot_payoff_button = QPushButton("Tracer le Payoff")
        self.plot_payoff_button.clicked.connect(self.plot_option_payoff)
        control_form_layout.addRow(self.plot_payoff_button)

        control_panel_group.setLayout(control_form_layout)
        control_panel_layout.addWidget(control_panel_group)
        control_panel_layout.addStretch(1)

        option_calculator_layout.addLayout(control_panel_layout, 1)

        # --- Panneau d'affichage à droite (du premier onglet) ---
        display_panel_layout = QVBoxLayout()

        current_data_group = QGroupBox("Données Actuelles")
        current_data_layout = QFormLayout()
        self.live_price_label = QLabel("N/A")
        self.risk_free_rate_label = QLabel("N/A")
        self.dividend_yield_label = QLabel("N/A")
        self.historical_vol_label = QLabel("N/A")
        self.bs_price_label = QLabel("N/A")

        current_data_layout.addRow("Prix Actuel (S):", self.live_price_label)
        current_data_layout.addRow("Taux Sans Risque SOFR (r):", self.risk_free_rate_label)
        current_data_layout.addRow("Rendement Dividende (q):", self.dividend_yield_label)
        current_data_layout.addRow("Volatilité Utilisée (σ):", self.historical_vol_label) # Mise à jour du libellé
        current_data_layout.addRow("Prix de l'option:", self.bs_price_label)
        current_data_group.setLayout(current_data_layout)
        display_panel_layout.addWidget(current_data_group)

        greeks_group = QGroupBox("Grecs")
        greeks_table_layout = QGridLayout()
        self.greeks_table = QTableWidget(1, 5)
        self.greeks_table.setHorizontalHeaderLabels(["Delta", "Gamma", "Theta (par jour)", "Vega", "Rho"])
        self.greeks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.greeks_table.setEditTriggers(QTableWidget.NoEditTriggers)
        # Connecter le signal cellClicked pour gérer les clics sur les Grecs
        self.greeks_table.cellClicked.connect(self.handle_greek_click)

        for col in range(5):
            self.greeks_table.setItem(0, col, QTableWidgetItem("N/A"))

        greeks_table_layout.addWidget(self.greeks_table, 0, 0)
        greeks_group.setLayout(greeks_table_layout)
        display_panel_layout.addWidget(greeks_group)

        payoff_plot_group = QGroupBox("Payoff de l'option")
        payoff_plot_layout = QVBoxLayout()

        self.fig = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.fig)
        payoff_plot_layout.addWidget(self.canvas)
        payoff_plot_group.setLayout(payoff_plot_layout)
        display_panel_layout.addWidget(payoff_plot_group)

        option_calculator_layout.addLayout(display_panel_layout, 2)

        self.tab_widget.addTab(option_calculator_widget, "Calculateur d'Option")

        self.simulation_tab = CallPriceSimulationTab()
        self.tab_widget.addTab(self.simulation_tab, "Simulation Call Price")

        main_window_layout = QVBoxLayout()
        main_window_layout.addWidget(self.tab_widget)
        self.setLayout(main_window_layout)

        self.fetch_data() # Appel initial pour peupler les données au démarrage de l'app

        self.tab_widget.currentChanged.connect(self.on_tab_changed)

    def fetch_data(self):
        ticker_symbol = self.ticker_input.text().strip().upper()
        if not ticker_symbol:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un symbole de ticker.")
            self.current_ticker = "N/A"
            self.S = None
            self.r = None
            self.q = None
            self.historical_vol = None
            self.simulation_tab.update_financial_data(self.current_ticker, self.S, self.r, self.q, self.historical_vol)
            return
        
        self.current_ticker = ticker_symbol

        live_price = self.data_fetcher.get_live_price(ticker_symbol)
        if live_price is not None:
            self.live_price_label.setText(f"{live_price:.2f}")
            self.S = live_price
        else:
            self.live_price_label.setText("Erreur / N/A")
            self.S = None
            QMessageBox.warning(self, "Données Manquantes",
                                 f"Impossible de récupérer le prix de {ticker_symbol}. Les calculs suivants pourraient être inexacts.")
            self.simulation_tab.update_financial_data(self.current_ticker, self.S, self.r, self.q, self.historical_vol)
            return

        # --- REMPLACEMENT DU TAUX SANS RISQUE PAR LE SOFR ---
        sofr_rate = self.data_fetcher.get_sofr_rate()
        if sofr_rate is not None:
            self.risk_free_rate_label.setText(f"{sofr_rate*100:.2f}%")
            self.r = sofr_rate
        else:
            self.risk_free_rate_label.setText("Erreur / N/A")
            self.r = None
            QMessageBox.warning(self, "Taux SOFR Manquant",
                                 "Impossible de récupérer le taux SOFR. Le calcul des options utilisera un taux par défaut (1%).")
            # Utiliser une valeur par défaut raisonnable si le SOFR n'est pas disponible
            self.r = 0.04 # 4% par défaut si SOFR non récupérable

        dividend_yield_for_calculation = self.data_fetcher.get_dividend_yield(ticker_symbol)
        
        # Pour l'affichage, on prend le rendement YFinance direct
        dividend_yield_for_display = 0.0 
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            temp_dividend = info.get("dividendYield")
            if temp_dividend is not None:
                dividend_yield_for_display = float(temp_dividend) # Afficher en %
        except Exception:
            pass

        self.dividend_yield_label.setText(f"{dividend_yield_for_display:.2f}%")
        self.q = dividend_yield_for_calculation


        historical_vol = self.data_fetcher.get_historical_volatility(ticker_symbol, period="1y")
        if historical_vol is not None:
            # L'affichage de la volatilité historique est conservé pour information
            self.historical_vol_label.setText(f"Historique: {historical_vol*100:.2f}%")
            self.historical_vol = historical_vol
        else:
            self.historical_vol_label.setText("Erreur / N/A")
            self.historical_vol = None
            QMessageBox.warning(self, "Volatilité Historique Manquante",
                                 f"Impossible de calculer la volatilité historique pour {ticker_symbol}. "
                                 "Les calculs du prix BSM et des Grecs utiliseront une volatilité par défaut (20%).")
        
        # On passe la vol historique à la simulation tab initialement, elle sera mise à jour dans calculate_option_metrics
        self.simulation_tab.update_financial_data(self.current_ticker, self.S, self.r, self.q, self.historical_vol)

    def calculate_option_metrics(self):
        try:
            # Récupération des inputs de l'interface
            self.K = float(self.strike_input.text())
            self.option_type = self.option_type_combo.currentText() # 'call' ou 'put'

            # Conversion de la date de l'interface en objet datetime pour yfinance
            maturity_qdate = self.maturity_date_input.date()
            maturity_datetime = datetime(maturity_qdate.year(), maturity_qdate.month(), maturity_qdate.day()) 
            
            # --- Vérifications préalables ---
            if self.S is None or self.r is None or self.q is None or self.current_ticker is None:
                QMessageBox.warning(self, "Données Manquantes", "Veuillez d'abord récupérer toutes les données de l'actif sous-jacent (S, r, q).")
                return
            if self.K <= 0:
                QMessageBox.warning(self, "Erreur de Strike", "Le prix d'exercice doit être supérieur à 0.")
                return
            
            # Appel de la nouvelle fonction qui retourne l'IV, le Prix Marché et la date réelle
            fetched_iv, market_price, closest_date = self.data_fetcher.get_implied_volatility_and_price(
                self.current_ticker, self.K, maturity_datetime, self.option_type 
            )
            
            # Mise à jour du temps jusqu'à l'échéance (T) en utilisant la date d'expiration réelle
            if closest_date:
                # La date d'expiration réelle (closest_date) est un string 'YYYY-MM-DD'
                closest_date_obj = datetime.strptime(closest_date, '%Y-%m-%d').date()
                today = date.today()
                time_difference = closest_date_obj - today
                self.T = time_difference.days / 365.0
                if self.T < 0: 
                    self.T = 1e-6 # Petite valeur positive si date est passée
                    QMessageBox.information(self, "Avertissement Date", "La date d'expiration la plus proche est déjà passée. Le temps à l'échéance (T) est forcé à une valeur minimale.")
            else:
                # Fallback sur la date de l'utilisateur si la chaîne d'options n'a pas pu être récupérée
                today = date.today()
                time_difference = maturity_datetime.date() - today
                self.T = time_difference.days / 365.0
                if self.T <= 0:
                    QMessageBox.warning(self, "Erreur de Maturité", "La date d'échéance doit être dans le futur.")
                    return

            # --- Logique de choix de la Volatilité (IV vs Historique) ---
            if fetched_iv is not None and fetched_iv > 0.001 and market_price is not None:
                # Utilisation de l'IV du marché
                sigma = fetched_iv
                pricing_method = "IV Marché"
                bs_price = market_price # Le prix BSM est le prix marché si on utilise l'IV
                
            else:
                # Fallback sur la volatilité historique (ou par défaut 20%)
                sigma = self.historical_vol if self.historical_vol is not None and self.historical_vol > 0 else 0.20
                pricing_method = "Vol Historique (Fallback)"
                market_price = None 
                
                # Calcul du prix Black-Scholes avec le fallback sigma
                bs_price = self.option_models.black_scholes_price(self.S, self.K, self.T, self.r, sigma, self.q, self.option_type)
                
                if self.historical_vol is None or self.historical_vol <= 0 or fetched_iv is None:
                     QMessageBox.information(self, "Volatilité",
                                         f"L'IV du marché n'est pas disponible. "
                                         f"Utilisation d'une volatilité ({sigma*100:.2f}%) pour les calculs.")

            self.current_sigma = sigma # Stocker la sigma utilisée pour les tracés de Grecs
            
            # --- Mise à jour de l'affichage ---
            
            self.historical_vol_label.setText(f"Volatilité Utilisée ({pricing_method}): {self.current_sigma*100:.2f}%")
            self.bs_price_label.setText(f"{bs_price:.4f} $")

            # Calcul des Grecs (en utilisant la sigma choisie)
            greeks = self.option_models.calculate_greeks(
                self.S, self.K, self.T, self.r, self.current_sigma, self.q, self.option_type
            )

            # Mise à jour de la table des Grecs
            self.greeks_table.setItem(0, 0, QTableWidgetItem(f"{greeks.get('delta', 0):.4f}"))
            self.greeks_table.setItem(0, 1, QTableWidgetItem(f"{greeks.get('gamma', 0):.4f}"))
            self.greeks_table.setItem(0, 2, QTableWidgetItem(f"{greeks.get('theta', 0):.4f}"))
            self.greeks_table.setItem(0, 3, QTableWidgetItem(f"{greeks.get('vega', 0)/100:.4f}")) 
            self.greeks_table.setItem(0, 4, QTableWidgetItem(f"{greeks.get('rho', 0):.4f}"))

            # Mettre à jour les données pour l'onglet de simulation
            self.simulation_tab.update_financial_data(self.current_ticker, self.S, self.r, self.q, self.current_sigma)


        except ValueError:
            QMessageBox.warning(self, "Erreur de Saisie", "Veuillez entrer des valeurs numériques valides pour K.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur de Calcul", f"Une erreur inattendue est survenue: {e}")

    #Gérer le clic sur un Grec
    def handle_greek_click(self, row, column):
        """
        Gère les clics sur les cellules de la table des Grecs et affiche un graphique.
        """
        greek_names = ["Delta", "Gamma", "Theta", "Vega", "Rho"]
        if column < len(greek_names):
            greek_name = greek_names[column]
            self.plot_greek_evolution(greek_name)
    
    #Tracer l'évolution d'un Grec
    def plot_greek_evolution(self, greek_name):
        """
        Calcule et trace l'évolution d'un Grec donné en fonction du prix du sous-jacent.
        """
        # Vérifiez que toutes les données nécessaires sont disponibles
        if self.S is None or self.K is None or self.T is None or \
           self.r is None or self.q is None or self.current_sigma is None or \
           self.option_type is None:
            QMessageBox.warning(self, "Données Manquantes",
                                 f"Veuillez d'abord calculer les métriques de l'option (Prix, Grecs) pour pouvoir tracer l'évolution du {greek_name}.")
            return

        # Définir une plage de prix du sous-jacent pour le tracé
        # Environ +/- 30% du prix actuel pour une bonne visualisation
        S_range = np.linspace(self.S * 0.7, self.S * 1.3, 100)
        
        greek_values = []
        for s_val in S_range:
            greeks = self.option_models.calculate_greeks(
                S=float(s_val), K=self.K, T=self.T, r=self.r, sigma=self.current_sigma, q=self.q, option_type=self.option_type
            )
            
            # Gérer les noms spécifiques des Grecs
            if greek_name == "Delta":
                value = greeks.get('delta', 0)
            elif greek_name == "Gamma":
                value = greeks.get('gamma', 0)
            elif greek_name == "Theta":
                value = greeks.get('theta', 0)
            elif greek_name == "Vega":
                value = greeks.get('vega', 0) / 100 # Ajuster pour le % de vol
            elif greek_name == "Rho":
                value = greeks.get('rho', 0)
            else:
                value = 0
            
            greek_values.append(value)

        # Créer et afficher la fenêtre de dialogue pour le graphique
        dialog = PlottingDialog(self, title=f"Évolution du {greek_name}")
        ax = dialog.fig.add_subplot(111)
        ax.plot(S_range, greek_values)
        ax.axvline(self.S, color='r', linestyle='--', label=f'S₀ Actuel: {self.S:.2f}')
        ax.set_title(f'Évolution du {greek_name} en fonction du prix du sous-jacent S₀')
        ax.set_xlabel('Prix du Sous-jacent (S₀)')
        ax.set_ylabel(greek_name)
        ax.grid(True)
        ax.legend()
        dialog.canvas.draw()
        dialog.exec_() # Affiche la boîte de dialogue de manière modale


    def plot_option_payoff(self):
        try:
            # Récupérer les valeurs de K et option_type directement des inputs
            K = float(self.strike_input.text())
            option_type = self.option_type_combo.currentText()
            position = self.position_combo.currentText()

            bs_price_str = self.bs_price_label.text()
            if bs_price_str == "N/A":
                QMessageBox.warning(self, "Prix BSM Manquant",
                                    "Veuillez d'abord calculer le prix Black-Scholes avant de tracer le payoff. "
                                    "Le payoff utilisera ce prix comme prime.")
                return

            # On retire le '$' pour la conversion en float
            premium = float(bs_price_str.replace('$', '').strip())

            if premium <= 0 and position == 'long':
                 QMessageBox.information(self, "Premium Nul/Négatif",
                                     "Le prix Black-Scholes calculé (premium) est nul ou négatif pour un achat. "
                                     "Le tracé ne sera pas représentatif d'une prime positive normale.")

            if K <= 0:
                QMessageBox.warning(self, "Erreur de Strike", "Le prix d'exercice doit être supérieur à 0.")
                return

            # --- Calcul du Breakeven ---
            breakeven = 0.0
            if option_type == "call":
                if position == "long":
                    breakeven = K + premium
                elif position == "short":
                    # Pour un short call, le breakeven est le strike + prime, 
                    # mais le profit est limité à premium si le prix de l'actif reste sous K.
                    # On affiche le point où la perte commence (au-dessus de K+premium, le profit devient négatif).
                    breakeven = K + premium 
            elif option_type == "put":
                if position == "long":
                    breakeven = K - premium
                elif position == "short":
                    # Pour un short put, le breakeven est le strike - prime.
                    breakeven = K - premium 
            
            self.fig.clear()
            ax = self.fig.add_subplot(111)

            self.strategy_manager.plot_payoff(
                K, premium, option_type, position, ax=ax
            )

            # --- Mise à jour du titre du graphique avec le Breakeven ---
            title_text = f"Payoff de l'Option {position.capitalize()} {option_type.capitalize()} (K={K:.2f}, Premium={premium:.4f})"
            if breakeven is not None:
                title_text += f"\nBreakeven = {breakeven:.2f}"
            
            ax.set_title(title_text)

            self.canvas.draw()

        except ValueError:
            QMessageBox.warning(self, "Erreur de Saisie", "Veuillez entrer des valeurs numériques valides pour K.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur de Tracé", f"Une erreur est survenue lors du tracé du payoff: {e}. Détails: {e.__class__.__name__}: {e}")

    def on_tab_changed(self, index):
        if index == self.tab_widget.indexOf(self.simulation_tab):
            # Utilisez les attributs de la classe si les données sont déjà chargées
            if self.current_ticker is not None and self.S is not None and self.r is not None and self.q is not None and self.historical_vol is not None:
                # La simulation tab est mise à jour avec le self.current_sigma qui est l'IV ou le fallback
                self.simulation_tab.update_financial_data(self.current_ticker, self.S, self.r, self.q, self.current_sigma) 
            else:
                QMessageBox.information(self, "Données Manquantes",
                                        "Veuillez récupérer les données financières (Ticker, Prix Actuel, Taux Sans Risque, Dividende, Volatilité) dans l'onglet 'Calculateur d'Option' d'abord.")
