# data_fetcher.py
import yfinance as yf
import os
import requests
from datetime import datetime, timedelta, date
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

    def get_option_data_chain(self, ticker_symbol, maturity_datetime):
        """
        Récupère la chaîne d'options yfinance pour la date d'expiration la plus proche
        de la date choisie (maturity_datetime).
        Retourne l'objet option_chain (calls et puts) et la date d'expiration réelle (string YYYY-MM-DD).
        """
        try:
            ticker = yf.Ticker(ticker_symbol)
            expirations = ticker.options
            
            if not expirations:
                print("Aucune date d'expiration trouvée.")
                return None, None

            # Trouver la date d'expiration disponible la plus proche
            # On compare la date cible (maturity_datetime.date()) avec les dates d'expiration disponibles (converties en date)
            closest_date = min(expirations, 
                               key=lambda x: abs(datetime.strptime(x, '%Y-%m-%d').date() - maturity_datetime.date()))
            
            # Récupérer la chaîne d'options pour cette date
            opt_chain = ticker.option_chain(closest_date)
            
            return opt_chain, closest_date

        except Exception as e:
            print(f"Erreur lors de la récupération de la chaîne d'options: {e}")
            return None, None
            
    def get_implied_volatility_and_price(self, ticker_symbol, strike, maturity_datetime, option_type):
        """
        Récupère l'IV et le prix du marché (Last Price) pour un strike donné.
        """
        opt_chain, closest_date = self.get_option_data_chain(ticker_symbol, maturity_datetime)

        if opt_chain is None or closest_date is None:
            return None, None, None # IV, Prix, Date réelle

        option_type = option_type.lower()
        
        # 1. Sélectionner les Calls ou les Puts
        if option_type == 'call':
            data = opt_chain.calls
        elif option_type == 'put':
            data = opt_chain.puts
        else:
            print(f"Type d'option non reconnu: {option_type}")
            return None, None, None
        
        # 2. Trouver le strike le plus proche dans la liste
        if data.empty:
            print("Aucune donnée d'option pour cette expiration.")
            return None, None, closest_date
            
        # Assurer que 'strike' est une colonne numérique et calculer la différence absolue
        data['abs_diff'] = abs(data['strike'] - strike)
        closest_row = data.sort_values('abs_diff').iloc[0]
        
        iv = closest_row['impliedVolatility']
        price = closest_row['lastPrice']
        
        # Vérification de sécurité et s'assurer que l'IV et le prix sont valides
        if iv is None or iv <= 0.001 or price is None or price <= 0:
            print(f"IV ({iv}) ou Prix ({price}) non valide ou nul pour K={strike} et type={option_type}.")
            return None, None, closest_date
            
        return iv, price, closest_date
