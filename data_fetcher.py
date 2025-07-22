import yfinance as yf
import pandas as pd
import numpy as np

class DataFetcher:
    def __init__(self):
        pass

    def get_live_price(self, ticker_symbol):
        """
        Récupère le dernier prix en temps quasi-réel pour un ticker donné.
        """
        try:
            ticker = yf.Ticker(ticker_symbol)
            data = ticker.history(period="1d")
            if not data.empty:
                last_price = data['Close'].iloc[-1]
                return last_price
            else:
                data = ticker.history(period="5m")
                if not data.empty:
                    last_price = data['Close'].iloc[-1]
                    return last_price
                else:
                    return None
        except Exception:
            return None

    def get_dividend_yield(self, ticker_symbol):
        """
        Récupère le rendement du dividende pour un ticker donné.
        Retourne 0.0 si non trouvé.
        Si yfinance retourne 0.49 pour 0.49%, alors la conversion en décimal est nécessaire ici.
        """
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            # Yfinance retourne 0.49 (pour 0.49%). Nous le convertissons en 0.0049 pour le calcul.
            dividend_yield_percent = info.get("dividendYield")
            if dividend_yield_percent is None:
                return 0.0
            # Convertir le pourcentage (ex: 0.49) en décimal (ex: 0.0049) pour les calculs BSM
            return float(dividend_yield_percent) / 100.0
        except Exception:
            return 0.0


    def get_risk_free_rate(self):
        """
        Récupère le taux sans risque en utilisant le rendement du bon du Trésor américain à 10 ans (^TNX).
        """
        try:
            tnx_ticker = yf.Ticker("^TNX")
            data = tnx_ticker.history(period="1d")
            if not data.empty:
                risk_free_rate_percent = data['Close'].iloc[-1]
                return risk_free_rate_percent / 100.0 # Convertir en décimal
            else:
                return 0.02
        except Exception:
            return 0.02

    def get_historical_volatility(self, ticker_symbol, period="1y"):
        """
        Calcule la volatilité historique annualisée sur une période donnée.
        Utilise les retours log-normaux.
        """
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period=period)
            if hist.empty:
                return None
            hist['log_returns'] = np.log(hist['Close'] / hist['Close'].shift(1))
            daily_volatility = hist['log_returns'].std()
            annualized_volatility = daily_volatility * np.sqrt(252)
            return annualized_volatility
        except Exception:
            return None