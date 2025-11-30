"""
Onglet pour la visualisation 3D de la surface de volatilité implicite avec Plotly.
"""

from typing import Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QGroupBox, QMessageBox, QDateEdit, QProgressBar
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QDate, QThread, pyqtSignal
from PyQt5.QtGui import QDoubleValidator
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime

from implied_volatility_surface import ImpliedVolatilitySurface


class SurfaceCalculationThread(QThread):
    """Thread pour calculer la surface IV sans bloquer l'UI."""
    
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, ticker_symbol: str, current_price: Optional[float] = None):
        super().__init__()
        self.ticker_symbol = ticker_symbol
        self.current_price = current_price
        self.surface_calculator = ImpliedVolatilitySurface()
        self.raw_data = None
        self.grid_data = None
    
    def run(self):
        """Exécute le calcul en arrière-plan."""
        try:
            self.progress.emit(25)
            self.raw_data, self.grid_data = self.surface_calculator.get_surface_for_ticker(
                self.ticker_symbol,
                self.current_price
            )
            self.progress.emit(100)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class VolatilitySurfaceTab(QWidget):
    """
    Onglet pour la visualisation 3D de la surface de volatilité implicite.
    
    Axes:
        X: Strike (prix d'exercice)
        Y: Time to Maturity (jours jusqu'à expiration)
        Z: Implied Volatility (volatilité implicite)
    """
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.surface_calculator = ImpliedVolatilitySurface()
        self.current_price: Optional[float] = None
        self.raw_data = None
        self.grid_data = None
        self.calculation_thread: Optional[SurfaceCalculationThread] = None
        
        self.init_ui()
    
    def init_ui(self) -> None:
        """Initialise l'interface utilisateur."""
        main_layout = QVBoxLayout(self)
        
        # =============== PANNEAU CONTRÔLE ===============
        control_group = QGroupBox("Paramètres de la Surface IV")
        control_layout = QFormLayout()
        
        self.ticker_input = QLineEdit()
        self.ticker_input.setPlaceholderText("Ex: AAPL, MSFT, TSLA")
        self.ticker_input.setText("AAPL")
        control_layout.addRow("Ticker Symbole:", self.ticker_input)
        
        self.price_input = QLineEdit()
        self.price_input.setValidator(QDoubleValidator(0.01, 100000.0, 2))
        self.price_input.setPlaceholderText("Optionnel: laisser vide pour récupérer automatiquement")
        control_layout.addRow("Prix Actuel (optionnel):", self.price_input)
        
        button_layout = QHBoxLayout()
        
        self.calculate_button = QPushButton("Calculer la Surface IV")
        self.calculate_button.clicked.connect(self.calculate_surface)
        button_layout.addWidget(self.calculate_button)
        
        self.save_button = QPushButton("Exporter (HTML)")
        self.save_button.clicked.connect(self.export_html)
        self.save_button.setEnabled(False)
        button_layout.addWidget(self.save_button)
        
        control_layout.addRow(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        control_layout.addRow("Progression:", self.progress_bar)
        
        # Status label
        self.status_label = QLabel("En attente de calcul...")
        self.status_label.setStyleSheet("color: gray;")
        control_layout.addRow(self.status_label)
        
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)
        
        # =============== ZONE GRAPHIQUE ===============
        # Pour plotly, on va créer un widget HTML
        self.graph_container = QWidget()
        self.graph_layout = QVBoxLayout(self.graph_container)
        self.info_label = QLabel("Cliquez sur 'Calculer la Surface IV' pour démarrer")
        self.info_label.setStyleSheet("color: #666; font-size: 12px;")
        self.graph_layout.addWidget(self.info_label)
        
        main_layout.addWidget(self.graph_container, 1)
    
    def calculate_surface(self) -> None:
        """Lance le calcul de la surface IV en thread."""
        ticker = self.ticker_input.text().strip().upper()
        if not ticker:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un ticker.")
            return
        
        # Récupérer le prix optionnel
        current_price = None
        if self.price_input.text().strip():
            try:
                current_price = float(self.price_input.text())
            except ValueError:
                QMessageBox.warning(self, "Erreur", "Prix invalide.")
                return
        
        # Désactiver le bouton et afficher la progression
        self.calculate_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("⏳ Récupération des données de marché...")
        self.status_label.setStyleSheet("color: orange;")
        
        # Créer et lancer le thread
        self.calculation_thread = SurfaceCalculationThread(ticker, current_price)
        self.calculation_thread.progress.connect(self.on_progress)
        self.calculation_thread.finished.connect(self.on_calculation_finished)
        self.calculation_thread.error.connect(self.on_calculation_error)
        self.calculation_thread.start()
    
    def on_progress(self, value: int) -> None:
        """Met à jour la barre de progression."""
        self.progress_bar.setValue(value)
    
    def on_calculation_finished(self) -> None:
        """Appelé quand le calcul est terminé."""
        if self.calculation_thread:
            self.raw_data = self.calculation_thread.raw_data
            self.grid_data = self.calculation_thread.grid_data
        
        if self.raw_data is not None and not self.raw_data.empty:
            self.plot_surface()
            self.status_label.setText(
                f"✓ Surface IV calculée ({len(self.raw_data)} points)"
            )
            self.status_label.setStyleSheet("color: green;")
            self.save_button.setEnabled(True)
        else:
            self.status_label.setText("✗ Erreur: Aucune donnée valide")
            self.status_label.setStyleSheet("color: red;")
        
        self.calculate_button.setEnabled(True)
        self.progress_bar.setVisible(False)
    
    def on_calculation_error(self, error_msg: str) -> None:
        """Gère les erreurs lors du calcul."""
        QMessageBox.critical(self, "Erreur de Calcul", error_msg)
        self.status_label.setText(f"✗ Erreur: {error_msg}")
        self.status_label.setStyleSheet("color: red;")
        self.calculate_button.setEnabled(True)
        self.progress_bar.setVisible(False)
    
    def plot_surface(self) -> None:
        """Crée et affiche le graphique 3D Plotly."""
        if self.raw_data is None or self.raw_data.empty:
            QMessageBox.warning(self, "Erreur", "Pas de données à tracer.")
            return
        
        # Proportions intelligentes des axes
        # Simplifiées pour une meilleure visibilité: Y est toujours agrandi
        x_scale = 1.0
        y_scale = 2.0  # L'axe Y (Jours) est toujours bien visible
        z_scale = 1.0
        
        # Créer la figure
        fig = go.Figure()
        
        # Ajouter les points bruts (initialement cachés)
        # On stocke les données mais on les cache pour ne pas surcharger le graphique
        fig.add_trace(go.Scatter3d(
            x=self.raw_data['Strike'],
            y=self.raw_data['Days_to_Maturity'],
            z=self.raw_data['IV'] * 100,  # Convertir en pourcentage pour l'affichage
            mode='markers',
            marker=dict(
                size=2,
                color=self.raw_data['IV'] * 100,
                colorscale='Plasma',
                showscale=False,
                opacity=0.3
            ),
            name='Données de marché',
            visible='legendonly',  # Caché par défaut, visible si clic sur légende
            hovertemplate='<b>Strike:</b> $%{x:.2f}<br>' +
                         '<b>Maturité:</b> %{y} jours<br>' +
                         '<b>IV:</b> %{z:.2f}%<br>' +
                         '<extra></extra>'
        ))
        
        # Ajouter la surface interpolée si disponible
        if self.grid_data is not None:
            X_grid, Y_grid, Z_grid = self.grid_data
            fig.add_trace(go.Surface(
                x=X_grid[0],
                y=Y_grid[:, 0],
                z=Z_grid * 100,  # Convertir en pourcentage pour l'affichage
                colorscale='Plasma',
                name='Surface interpolée',
                opacity=0.85,
                showscale=True,
                colorbar=dict(
                    title="IV (%)",
                    thickness=15,
                    len=0.7
                ),
                hovertemplate='<b>Strike:</b> %{x:.2f}<br>' +
                             '<b>Maturité:</b> %{y} jours<br>' +
                             '<b>IV:</b> %{z:.2f}%<br>' +
                             '<extra></extra>'
            ))
        
        # Configuration de la mise en page avec scaling intelligent
        fig.update_layout(
            title=dict(
                text=f"Surface de Volatilité Implicite - {self.ticker_input.text().upper()}",
                font=dict(size=16)
            ),
            scene=dict(
                xaxis=dict(
                    title='Strike (K)',
                    backgroundcolor="rgb(230, 230,230)",
                    gridcolor="white",
                    showbackground=True,
                ),
                yaxis=dict(
                    title='Jours jusqu\'à expiration',
                    backgroundcolor="rgb(230, 230,230)",
                    gridcolor="white",
                    showbackground=True,
                ),
                zaxis=dict(
                    title='Volatilité Implicite (%) - σ',
                    backgroundcolor="rgb(230, 230,230)",
                    gridcolor="white",
                    showbackground=True,
                ),
                camera=dict(
                    eye=dict(x=1.5, y=-1.5, z=1.3),
                    center=dict(x=0, y=0, z=0),
                    up=dict(x=0, y=0, z=1)
                ),
                aspectratio=dict(
                    x=x_scale,
                    y=y_scale,
                    z=z_scale
                )
            ),
            width=1200,
            height=700,
            hovermode='closest',
            showlegend=True
        )
        
        # Sauvegarder en HTML temporaire et afficher
        try:
            html_str = pio.to_html(fig, include_plotlyjs='cdn', div_id="volatility_surface")
            
            # Nettoyer l'ancienne vue si elle existe
            while self.graph_layout.count() > 0:
                item = self.graph_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Créer la nouvelle vue
            web_view = QWebEngineView()
            web_view.setHtml(html_str)
            self.graph_layout.addWidget(web_view)
        
        except Exception as e:
            QMessageBox.critical(self, "Erreur d'affichage", f"Impossible d'afficher le graphique: {e}")
    
    def export_html(self) -> None:
        """Exporte la surface en fichier HTML."""
        if self.raw_data is None or self.raw_data.empty:
            QMessageBox.warning(self, "Erreur", "Pas de surface à exporter.")
            return
        
        try:
            ticker = self.ticker_input.text().upper()
            filename = f"iv_surface_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            
            # Calculer les proportions intelligentes des axes
            strike_range = self.raw_data['Strike'].max() - self.raw_data['Strike'].min()
            days_range = self.raw_data['Days_to_Maturity'].max() - self.raw_data['Days_to_Maturity'].min()
            iv_range = (self.raw_data['IV'].max() - self.raw_data['IV'].min()) * 100  # En pourcentage
            
            # Calcul des scaling factors pour equilibrer visuellement les axes
            min_range = min(strike_range, days_range, iv_range)
            
            # Scaling factors (ajustent la "longueur visuelle" de chaque axe)
            x_scale = strike_range / min_range if min_range > 0 else 1.0
            y_scale = days_range / min_range if min_range > 0 else 1.5  # Légèrement agrandi
            z_scale = iv_range / min_range if min_range > 0 else 1.0
            
            # Recréer la figure pour l'export
            fig = go.Figure()
            
            # Ajouter les points bruts (cachés par défaut)
            fig.add_trace(go.Scatter3d(
                x=self.raw_data['Strike'],
                y=self.raw_data['Days_to_Maturity'],
                z=self.raw_data['IV'] * 100,  # Convertir en pourcentage
                mode='markers',
                marker=dict(
                    size=2,
                    color=self.raw_data['IV'] * 100,
                    colorscale='Viridis',
                    showscale=False,
                    opacity=0.3
                ),
                name='Données de marché',
                visible='legendonly',
                hovertemplate='<b>Strike:</b> $%{x:.2f}<br>' +
                             '<b>Maturité:</b> %{y} jours<br>' +
                             '<b>IV:</b> %{z:.2f}%<br>' +
                             '<extra></extra>'
            ))
            
            # Ajouter la surface interpolée
            if self.grid_data is not None:
                X_grid, Y_grid, Z_grid = self.grid_data
                fig.add_trace(go.Surface(
                    x=X_grid[0],
                    y=Y_grid[:, 0],
                    z=Z_grid * 100,  # Convertir en pourcentage
                    colorscale='Viridis',
                    opacity=0.85,
                    name='Surface interpolée',
                    showscale=True,
                    colorbar=dict(
                        title="IV (%)"
                    ),
                    hovertemplate='<b>Strike:</b> %{x:.2f}<br>' +
                                 '<b>Maturité:</b> %{y} jours<br>' +
                                 '<b>IV:</b> %{z:.2f}%<br>' +
                                 '<extra></extra>'
                ))
            
            # Appliquer le scaling intelligent
            fig.update_layout(
                title=f"Surface de Volatilité Implicite - {ticker}",
                scene=dict(
                    xaxis=dict(title='Strike (K)'),
                    yaxis=dict(title='Jours jusqu\'à expiration'),
                    zaxis=dict(title='Volatilité Implicite (%) - σ'),
                    aspectratio=dict(
                        x=x_scale,
                        y=y_scale,
                        z=z_scale
                    )
                )
            )
            
            fig.write_html(filename)
            QMessageBox.information(self, "Succès", f"Fichier exporté: {filename}")
        
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export: {e}")
    
    def update_financial_params(self, ticker: str, S: float) -> None:
        """Met à jour le ticker et le prix (appelé depuis l'app principale)."""
        self.ticker_input.setText(ticker)
        if S is not None:
            self.price_input.setText(f"{S:.2f}")
