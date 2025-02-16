from binance import Client
import time

print("Test başlıyor...")
print("1. Client oluşturuluyor...")

client = Client()

print("2. Veri alınmaya çalışılıyor...")
try:
    # Sadece BTC fiyatını al
    btc_price = client.get_symbol_ticker(symbol="BTCUSDT")
    print(f"\nBTC Fiyatı: ${float(btc_price['price']):,.2f}")
    
    print("\n3. Tüm coinler için deneniyor...")
    all_tickers = client.get_ticker()
    usdt_pairs = [t for t in all_tickers if t['symbol'].endswith('USDT')]
    print(f"Toplam {len(usdt_pairs)} USDT çifti bulundu")
    
    print("\nİlk 3 coin:")
    for t in usdt_pairs[:3]:
        print(f"{t['symbol']}: ${float(t['lastPrice']):,.2f}")
        
except Exception as e:
    print(f"\nHATA: {e}")
    print("\nOlası nedenler:")
    print("1. İnternet bağlantısı")
    print("2. Binance API kısıtlaması")
    print("3. VPN/Proxy sorunu")

input("\nÇıkmak için Enter'a basın...") 