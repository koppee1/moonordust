from binance import Client
import time

def test_connection():
    print("Binance API Testi Başlıyor...")
    
    try:
        # API bağlantısı
        client = Client()
        print("API bağlantısı başarılı!")
        
        # Fiyat verilerini al
        print("\nFiyat verileri alınıyor...")
        tickers = client.get_ticker()
        
        # USDT çiftlerini filtrele
        usdt_pairs = [t for t in tickers if t['symbol'].endswith('USDT')]
        
        print(f"\nToplam {len(usdt_pairs)} USDT çifti bulundu.")
        print("\nÖrnek veriler (ilk 5 çift):")
        
        for ticker in usdt_pairs[:5]:
            symbol = ticker['symbol']
            price = float(ticker['lastPrice'])
            print(f"{symbol}: ${price:,.2f}")
            
    except Exception as e:
        print(f"\nHATA: {str(e)}")
        print("\nOlası çözümler:")
        print("1. İnternet bağlantınızı kontrol edin")
        print("2. VPN kullanıyorsanız kapatın")
        print("3. Binance'in ülkenizde erişilebilir olduğundan emin olun")

if __name__ == "__main__":
    test_connection()
    input("\nÇıkmak için Enter'a basın...") 