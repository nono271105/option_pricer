# data_fetcher.py
import yfinance as yf
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()
import numpy as np

class DataFetcher:
    def __init__(self):
        # Clé API pour FRED (Secured Overnight Financing Rate)
        self.fred_api_key = os.getenv("FRED_API_KEY")

    def get_live_price(self, ticker_symbol):
        try:
            ticker = yf.Ticker(ticker_symbol)
            todays_data = ticker.history(period='1d')
            if not todays_data.empty:
                return todays_data['Close'].iloc[-1]
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération du prix en direct pour {ticker_symbol}: {e}")
            return None

    def get_historical_volatility(self, ticker_symbol, period="1y"):
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period=period)
            if hist.empty:
                return None
            
            # Calcul de la volatilité annuelle
            returns = hist['Close'].pct_change().dropna()
            if len(returns) < 2: # Nécessite au moins 2 retours pour calculer un écart-type
                return None
            
            annual_volatility = returns.std() * np.sqrt(252) # 252 jours de trading par an
            return annual_volatility
        except Exception as e:
            print(f"Erreur lors de la récupération de la volatilité historique pour {ticker_symbol}: {e}")
            return None

    def get_sofr_rate(self):
        """
        Récupère le taux SOFR (Secured Overnight Financing Rate) le plus récent
        depuis l'API de FRED.
        """
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id=SOFR&api_key={self.fred_api_key}&file_type=json"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Lève une exception pour les codes d'état HTTP d'erreur
            data = response.json()
            
            observations = data.get('observations', [])
            if observations:
                # Les observations sont généralement triées par date. Le dernier élément est le plus récent.
                latest_observation = observations[-1]
                sofr_value = float(latest_observation['value'])
                # L'API renvoie le taux en pourcentage (ex: 5.33 pour 5.33%).
                # Nous devons le convertir en décimal pour le modèle Black-Scholes.
                return sofr_value / 100.0
            else:
                print("Aucune observation SOFR trouvée dans la réponse de l'API.")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête HTTP lors de la récupération du SOFR : {e}")
            return None
        except ValueError as e:
            print(f"Erreur de parsing JSON ou de conversion de valeur pour le SOFR : {e}")
            return None
        except Exception as e:
            print(f"Une erreur inattendue est survenue lors de la récupération du SOFR : {e}")
            return None

    def get_dividend_yield(self, ticker_symbol):
        """
        Récupère le rendement de dividende annuel pour un ticker donné.
        Utilise le rendement de dividende le plus récent du rapport YFinance.
        """
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            dividend_yield = info.get("dividendYield")
            
            if dividend_yield is not None:
                return float(dividend_yield) / 100.0 
            else:
                return 0.0 # Si non disponible, retourne 0.0
        except Exception as e:
            print(f"Erreur lors de la récupération du rendement de dividende pour {ticker_symbol}: {e}")
            return 0.0 # Retourne 0 si erreur ou non trouvé
