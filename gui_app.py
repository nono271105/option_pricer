import sys
import yfinance as yf
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFormLayout, QGroupBox, QGridLayout,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit,
    QTabWidget
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QDoubleValidator, QIntValidator

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from datetime import date

from data_fetcher import DataFetcher
from option_models import OptionModels
from strategy_manager import StrategyManager
from simulation_tab import CallPriceSimulationTab

class OptionPricingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Option Pricer")
        self.setGeometry(100, 100, 1200, 800)

        self.data_fetcher = DataFetcher()
        self.option_models = OptionModels()
        self.strategy_manager = StrategyManager()

        self.S = None
        self.r = None
        self.q = None
        self.historical_vol = None
        self.current_ticker = None

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
        current_data_layout.addRow("Taux Sans Risque (r):", self.risk_free_rate_label)
        current_data_layout.addRow("Rendement Dividende (q):", self.dividend_yield_label)
        current_data_layout.addRow("Volatilité Historique (σ):", self.historical_vol_label)
        current_data_layout.addRow("Prix de l'option:", self.bs_price_label)
        current_data_group.setLayout(current_data_layout)
        display_panel_layout.addWidget(current_data_group)

        greeks_group = QGroupBox("Grecs")
        greeks_table_layout = QGridLayout()
        self.greeks_table = QTableWidget(1, 5)
        self.greeks_table.setHorizontalHeaderLabels(["Delta", "Gamma", "Theta (par jour)", "Vega", "Rho"])
        self.greeks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.greeks_table.setEditTriggers(QTableWidget.NoEditTriggers)

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

        self.fetch_data()

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

        risk_free_rate = self.data_fetcher.get_risk_free_rate()
        self.risk_free_rate_label.setText(f"{risk_free_rate*100:.2f}%")
        self.r = risk_free_rate

        dividend_yield_for_calculation = self.data_fetcher.get_dividend_yield(ticker_symbol)
        
        dividend_yield_for_display = 0.0
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            temp_dividend = info.get("dividendYield")
            if temp_dividend is not None:
                dividend_yield_for_display = float(temp_dividend)
        except Exception:
            pass

        self.dividend_yield_label.setText(f"{dividend_yield_for_display:.2f}%")
        self.q = dividend_yield_for_calculation

        historical_vol = self.data_fetcher.get_historical_volatility(ticker_symbol, period="1y")
        if historical_vol is not None:
            self.historical_vol_label.setText(f"{historical_vol*100:.2f}%")
            self.historical_vol = historical_vol
        else:
            self.historical_vol_label.setText("Erreur / N/A")
            self.historical_vol = None
            QMessageBox.warning(self, "Volatilité Historique Manquante",
                                 f"Impossible de calculer la volatilité historique pour {ticker_symbol}. "
                                 "Les calculs du prix BSM et des Grecs utiliseront une volatilité par défaut (20%).")
        
        self.simulation_tab.update_financial_data(self.current_ticker, self.S, self.r, self.q, self.historical_vol)

    def calculate_option_metrics(self):
        if self.S is None or self.r is None or self.q is None:
            QMessageBox.warning(self, "Données Manquantes", "Veuillez d'abord récupérer toutes les données de l'actif sous-jacent.")
            return

        try:
            K = float(self.strike_input.text())
            option_type = self.option_type_combo.currentText()

            today = date.today()
            maturity_qdate = self.maturity_date_input.date()
            maturity_date = date(maturity_qdate.year(), maturity_qdate.month(), maturity_qdate.day())
            time_difference = maturity_date - today
            T_days = time_difference.days
            T = T_days / 365.0

            if T <= 0:
                QMessageBox.warning(self, "Erreur de Maturité", "La date d'échéance doit être dans le futur.")
                return
            if K <= 0:
                QMessageBox.warning(self, "Erreur de Strike", "Le prix d'exercice doit être supérieur à 0.")
                return

            sigma = self.historical_vol if self.historical_vol is not None and self.historical_vol > 0 else 0.20
            if self.historical_vol is None or self.historical_vol <= 0:
                 QMessageBox.information(self, "Volatilité",
                                         f"La volatilité historique n'est pas disponible ou est nulle. "
                                         f"Utilisation d'une volatilité par défaut ({sigma*100:.0f}%) pour les calculs.")

            bs_price = self.option_models.black_scholes_price(
                self.S, K, T, self.r, sigma, self.q, option_type
            )
            self.bs_price_label.setText(f"{bs_price:.4f}")

            greeks = self.option_models.calculate_greeks(
                self.S, K, T, self.r, sigma, self.q, option_type
            )

            self.greeks_table.setItem(0, 0, QTableWidgetItem(f"{greeks.get('delta', 0):.4f}"))
            self.greeks_table.setItem(0, 1, QTableWidgetItem(f"{greeks.get('gamma', 0):.4f}"))
            self.greeks_table.setItem(0, 2, QTableWidgetItem(f"{greeks.get('theta', 0):.4f}"))
            self.greeks_table.setItem(0, 3, QTableWidgetItem(f"{greeks.get('vega', 0)/100:.4f}"))
            self.greeks_table.setItem(0, 4, QTableWidgetItem(f"{greeks.get('rho', 0):.4f}"))

        except ValueError:
            QMessageBox.warning(self, "Erreur de Saisie", "Veuillez entrer des valeurs numériques valides pour K.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur de Calcul", f"Une erreur inattendue est survenue: {e}")

    def plot_option_payoff(self):
        try:
            K = float(self.strike_input.text())
            option_type = self.option_type_combo.currentText()
            position = self.position_combo.currentText()

            bs_price_str = self.bs_price_label.text()
            if bs_price_str == "N/A":
                QMessageBox.warning(self, "Prix BSM Manquant",
                                    "Veuillez d'abord calculer le prix Black-Scholes avant de tracer le payoff. "
                                    "Le payoff utilisera ce prix comme prime.")
                return

            premium = float(bs_price_str)

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
                    breakeven = K + premium # En cas de short call, le breakeven est K + prime (ce qui est une perte pour le vendeur)
            elif option_type == "put":
                if position == "long":
                    breakeven = K - premium
                elif position == "short":
                    breakeven = K - premium # En cas de short put, le breakeven est K - prime (ce qui est une perte pour le vendeur)
            
            # Ajustement pour la symétrie du short :
            # Pour un Short Call, le breakeven est le prix de l'actif sous-jacent au-dessus duquel le vendeur perd de l'argent.
            # Pour un Short Put, le breakeven est le prix de l'actif sous-jacent en dessous duquel le vendeur perd de l'argent.
            # La formule K + Premium pour Short Call et K - Premium pour Short Put reste correcte pour définir le seuil.
            
            self.fig.clear()
            ax = self.fig.add_subplot(111)

            self.strategy_manager.plot_payoff(
                K, premium, option_type, position, ax=ax
            )

            # --- Mise à jour du titre du graphique avec le Breakeven ---
            title_text = f"Payoff de l'Option {position.capitalize()} {option_type.capitalize()} (K={K:.2f}, Premium={premium:.2f})"
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
            if self.current_ticker is not None and self.S is not None and self.r is not None and self.q is not None and self.historical_vol is not None:
                self.simulation_tab.update_financial_data(self.current_ticker, self.S, self.r, self.q, self.historical_vol)
            else:
                QMessageBox.information(self, "Données Manquantes",
                                        "Veuillez récupérer les données financières (Ticker, Prix Actuel, Taux Sans Risque, Dividende, Volatilité) dans l'onglet 'Calculateur d'Option' d'abord.")