from binance import Client
from datetime import datetime, timedelta
import time
import os

class CoinTracker:
    def __init__(self):
        print("Binance bağlantısı kuruluyor...")
        self.client = Client()
        self.current_prices = {}
        self.previous_prices = {}
        print("Bağlantı başarılı!")

    def clear_terminal(self):
        # Terminal ekranını temizle (Windows ve Unix sistemleri için)
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_current_prices(self):
        try:
            # Önce BTC ile test et
            btc = self.client.get_symbol_ticker(symbol="BTCUSDT")
            if not btc:
                raise Exception("BTC verisi alınamadı")
                
            # Tüm verileri al
            tickers = self.client.get_ticker()
            prices = {}
            
            for item in tickers:
                if item['symbol'].endswith('USDT'):
                    try:
                        price = float(item['lastPrice'])
                        if price > 0:  # Sıfır fiyatları filtrele
                            prices[item['symbol']] = price
                    except:
                        continue
            
            if not prices:
                raise Exception("Hiç veri alınamadı")
                
            print(f"Toplam {len(prices)} coin verisi alındı")
            return prices
            
        except Exception as e:
            print(f"Veri alma hatası: {e}")
            return {}

    def calculate_5min_change(self):
        if not self.previous_prices:
            self.previous_prices = self.current_prices.copy()
            return []

        changes = []
        for symbol, current_price in self.current_prices.items():
            if symbol in self.previous_prices:
                prev_price = self.previous_prices[symbol]
                # Sıfıra bölme hatasını önle
                if prev_price != 0:
                    percent_change = ((current_price - prev_price) / prev_price) * 100
                    changes.append({
                        'symbol': symbol,
                        'percent_change': percent_change,
                        'price': current_price
                    })

        self.previous_prices = self.current_prices.copy()
        return changes

    def get_next_update_time(self):
        now = datetime.now()
        minutes = now.minute
        next_5min = 5 * ((minutes // 5) + 1)
        
        if next_5min == 60:
            next_time = now.replace(hour=now.hour + 1, minute=0, second=0, microsecond=0)
        else:
            next_time = now.replace(minute=next_5min, second=0, microsecond=0)
            
        return next_time

    def display_results(self, changes, wait_seconds):
        self.clear_terminal()
        current_time = datetime.now()
        next_update = self.get_next_update_time()
        
        print(f"\n{'='*50}")
        print(f"Kripto Para Takip Programı - {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        
        # Geri sayım bilgisi
        minutes = int(wait_seconds // 60)
        seconds = int(wait_seconds % 60)
        print(f"Bir sonraki güncelleme: {minutes:02d}:{seconds:02d}")
        print(f"Hedef zaman: {next_update.strftime('%H:%M:00')}")
        print(f"Takip edilen coin sayısı: {len(self.current_prices)}")
        print(f"{'='*50}\n")
        
        if changes:
            # En yüksek 5 değişimi al ve göster
            top_changes = sorted(changes, key=lambda x: x['percent_change'], reverse=True)[:5]
            
            print("Son 5 Dakikada En Çok Yükselenler:")
            print(f"{'Symbol':<10} {'Değişim (%)':<12} {'Fiyat (USDT)':<15}")
            print("-" * 37)
            
            for coin in top_changes:
                symbol = coin['symbol']
                change = coin['percent_change']
                price = coin['price']
                
                # Pozitif değişimleri yeşil, negatifleri kırmızı yap
                color = '\033[92m' if change > 0 else '\033[91m'
                reset_color = '\033[0m'
                
                print(f"{symbol:<10} {color}{change:>+8.2f}%{reset_color}     ${price:<10.4f}")
        else:
            print("İlk veriler toplanıyor, bir sonraki güncellemeyi bekleyin...")
        
        print(f"\n{'='*50}")

    def run(self):
        print("\nProgram başlatılıyor...")
        
        try:
            # İlk verileri al
            print("İlk veriler toplanıyor...")
            self.current_prices = self.get_current_prices()
            
            if not self.current_prices:
                print("Veri alınamıyor! Tekrar deneniyor...")
                time.sleep(2)
                self.current_prices = self.get_current_prices()
            
            while True:
                now = datetime.now()
                next_update = self.get_next_update_time()
                wait_seconds = (next_update - now).total_seconds()
                
                # Yeni fiyatları al ve değişimi hesapla
                self.current_prices = self.get_current_prices()
                changes = self.calculate_5min_change()
                
                # Geri sayım göster
                while wait_seconds > 0:
                    self.display_results(changes, wait_seconds)
                    time.sleep(1)
                    wait_seconds -= 1
                    now = datetime.now()
                    next_update = self.get_next_update_time()
                    wait_seconds = (next_update - now).total_seconds()
                
        except Exception as e:
            print(f"Hata oluştu: {e}")
            print("Program sonlandırılıyor...")

if __name__ == "__main__":
    tracker = CoinTracker()
    tracker.run() 