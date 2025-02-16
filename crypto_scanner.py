from binance.client import Client
from datetime import datetime, timedelta
import time
import pandas as pd
import sys

class CoinTracker:
    def __init__(self):
        self.client = Client()
        self.previous_prices = {}
        self.start_time = datetime.now()
        self.run_duration = timedelta(hours=24)
        self.update_interval = 300  # 5 dakika (saniye cinsinden)

    def get_current_prices(self):
        prices = self.client.get_ticker()
        return {item['symbol']: float(item['lastPrice']) for item in prices if item['symbol'].endswith('USDT')}

    def calculate_5min_change(self, current_prices):
        if not self.previous_prices:
            self.previous_prices = current_prices
            return pd.DataFrame()

        changes = []
        for symbol, current_price in current_prices.items():
            if symbol in self.previous_prices:
                prev_price = self.previous_prices[symbol]
                percent_change = ((current_price - prev_price) / prev_price) * 100
                changes.append({
                    'symbol': symbol,
                    'priceChangePercent': percent_change,
                    'lastPrice': current_price
                })

        self.previous_prices = current_prices
        return pd.DataFrame(changes)

    def get_top_performers(self):
        current_prices = self.get_current_prices()
        df = self.calculate_5min_change(current_prices)
        
        if df.empty:
            return df

        # En yüksek değişime göre sırala
        top_coins = df.nlargest(5, 'priceChangePercent')
        return top_coins[['symbol', 'priceChangePercent', 'lastPrice']]

    def should_continue(self):
        elapsed_time = datetime.now() - self.start_time
        return elapsed_time < self.run_duration

    def countdown(self, seconds):
        for remaining in range(seconds, 0, -1):
            sys.stdout.write(f"\rBir sonraki güncelleme: {remaining} saniye ")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write('\r' + ' ' * 50 + '\r')  # Satırı temizle

    def run(self):
        print(f"Program başlatıldı - Bitiş zamanı: {self.start_time + self.run_duration}")
        
        while self.should_continue():
            current_time = datetime.now()
            print(f"\n{current_time.strftime('%Y-%m-%d %H:%M:%S')} - Son 5 Dakikada En İyi Performans Gösterenler:")
            
            try:
                top_performers = self.get_top_performers()
                
                if not top_performers.empty:
                    for _, coin in top_performers.iterrows():
                        print(f"Sembol: {coin['symbol']:<12} "
                              f"5dk Değişim: %{coin['priceChangePercent']:>6.2f} "
                              f"Fiyat: ${float(coin['lastPrice']):>10.4f}")
                else:
                    print("İlk veri toplanıyor, bir sonraki güncellemeyi bekleyin...")
            
            except Exception as e:
                print(f"Hata oluştu: {e}")
            
            print("\n" + "="*50)  # Ayırıcı çizgi
            self.countdown(self.update_interval)

        print("\nProgram 24 saatlik çalışma süresini tamamladı.")

if __name__ == "__main__":
    tracker = CoinTracker()
    tracker.run() 