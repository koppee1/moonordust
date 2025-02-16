from binance import Client
import time
from datetime import datetime
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_next_update_time():
    now = datetime.now()
    minutes = now.minute
    next_5min = 5 * ((minutes // 5) + 1)
    
    if next_5min == 60:
        next_time = now.replace(hour=now.hour + 1, minute=0, second=0, microsecond=0)
    else:
        next_time = now.replace(minute=next_5min, second=0, microsecond=0)
    
    return next_time

def get_prices():
    client = Client()
    tickers = client.get_ticker()
    prices = {}
    for t in tickers:
        if t['symbol'].endswith('USDT'):
            try:
                price = float(t['lastPrice'])
                if price > 0:
                    prices[t['symbol']] = price
            except:
                continue
    return prices

def display_results(changes, wait_seconds):
    clear_screen()
    current_time = datetime.now()
    next_update = get_next_update_time()
    
    print(f"\n{'='*50}")
    print(f"Kripto Para Takip Programı - {current_time.strftime('%H:%M:%S')}")
    print(f"{'='*50}")
    
    minutes = int(wait_seconds // 60)
    seconds = int(wait_seconds % 60)
    print(f"Bir sonraki güncelleme: {minutes:02d}:{seconds:02d}")
    print(f"Hedef zaman: {next_update.strftime('%H:%M:00')}")
    print(f"{'='*50}\n")
    
    if changes:
        print("Son 5 Dakikada En Çok Yükselenler:")
        print(f"{'Symbol':<10} {'Değişim (%)':<12} {'Fiyat (USDT)':<15}")
        print("-" * 37)
        
        for coin in sorted(changes, key=lambda x: x['change'], reverse=True)[:5]:
            color = '\033[92m' if coin['change'] > 0 else '\033[91m'
            reset = '\033[0m'
            print(f"{coin['symbol']:<10} {color}{coin['change']:>+6.2f}%{reset}    ${coin['price']:<10.4f}")
    
    print(f"\n{'='*50}")

def main():
    print("Program başlatılıyor...")
    
    try:
        # İlk verileri al
        print("İlk veriler alınıyor...")
        previous_prices = get_prices()
        current_prices = previous_prices
        
        if not previous_prices:
            print("Veri alınamadı! Program sonlandırılıyor...")
            return
            
        print(f"Toplam {len(previous_prices)} coin takip ediliyor")
        time.sleep(2)
        
        changes = []  # İlk değişim listesi boş başlasın
        
        while True:
            now = datetime.now()
            next_update = get_next_update_time()
            wait_seconds = (next_update - now).total_seconds()
            
            # Yeni periyot başladığında verileri güncelle
            if wait_seconds >= 299:  # 5 dakika - 1 saniye
                current_prices = get_prices()
                changes = []
                
                for symbol, current_price in current_prices.items():
                    if symbol in previous_prices:
                        prev_price = previous_prices[symbol]
                        if prev_price > 0:
                            percent_change = ((current_price - prev_price) / prev_price) * 100
                            changes.append({
                                'symbol': symbol,
                                'change': percent_change,
                                'price': current_price
                            })
                
                previous_prices = current_prices
            
            # Sonuçları göster (sadece ekranı güncelle)
            display_results(changes, wait_seconds)
            time.sleep(1)
            
    except Exception as e:
        print(f"\nHata oluştu: {e}")
        print("Program sonlandırılıyor...")
        time.sleep(5)

if __name__ == "__main__":
    main() 