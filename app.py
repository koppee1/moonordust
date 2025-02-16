from flask import Flask, render_template
from datetime import datetime, timedelta
import time
from binance.client import Client
import pandas as pd
import threading

app = Flask(__name__)

class CoinTracker:
    def __init__(self):
        self.client = Client()
        self.previous_prices = {}
        self.current_data = []
        self.last_update = None
        self.next_update = None
        
    def get_current_prices(self):
        prices = self.client.get_ticker()
        return {item['symbol']: float(item['lastPrice']) for item in prices if item['symbol'].endswith('USDT')}

    def calculate_5min_change(self, current_prices):
        if not self.previous_prices:
            self.previous_prices = current_prices
            return []

        changes = []
        for symbol, current_price in current_prices.items():
            if symbol in self.previous_prices:
                prev_price = self.previous_prices[symbol]
                percent_change = ((current_price - prev_price) / prev_price) * 100
                changes.append({
                    'symbol': symbol,
                    'percent_change': percent_change,
                    'price': current_price
                })

        self.previous_prices = current_prices
        return changes

    def wait_until_next_5min(self):
        """Bir sonraki 5 dakikalık dilimin başlangıcına kadar bekler"""
        now = datetime.now()
        minutes = now.minute
        seconds = now.second
        microseconds = now.microsecond
        
        # Bir sonraki 5 dakikalık dilimi hesapla
        next_5min = 5 * ((minutes // 5) + 1)
        
        # Eğer şu an 55 dakikadan sonraysa, bir sonraki saatin başına geç
        if next_5min == 60:
            next_5min = 0
            
        # Bekleme süresini hesapla
        wait_seconds = ((next_5min - minutes) * 60) - seconds - (microseconds / 1000000)
        if wait_seconds < 0:
            wait_seconds += 3600  # Bir sonraki saate geç
            
        time.sleep(wait_seconds)

    def update_data(self):
        while True:
            try:
                # Önce bir sonraki 5 dakikalık dilimin başlangıcını bekle
                self.wait_until_next_5min()
                
                # Şimdi veriyi güncelle
                current_prices = self.get_current_prices()
                changes = self.calculate_5min_change(current_prices)
                
                if changes:
                    # En yüksek 5 değişimi al
                    sorted_changes = sorted(changes, key=lambda x: x['percent_change'], reverse=True)[:5]
                    self.current_data = sorted_changes
                    self.last_update = datetime.now()
                    # Bir sonraki 5 dakikalık dilimi ayarla
                    self.next_update = self.last_update.replace(
                        minute=(self.last_update.minute // 5 + 1) * 5,
                        second=0,
                        microsecond=0
                    )
                    if self.next_update.minute == 60:
                        self.next_update = self.next_update.replace(
                            hour=self.next_update.hour + 1,
                            minute=0
                        )

            except Exception as e:
                print(f"Hata oluştu: {e}")

tracker = CoinTracker()

# Arka planda veri güncelleme işlemini başlat
update_thread = threading.Thread(target=tracker.update_data)
update_thread.daemon = True
update_thread.start()

@app.route('/')
def home():
    return render_template('index.html', 
                         data=tracker.current_data,
                         last_update=tracker.last_update,
                         next_update=tracker.next_update)

if __name__ == '__main__':
    app.run(debug=True) 