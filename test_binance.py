from binance.client import Client
import time

client = Client()

try:
    prices = client.get_ticker()
    print("Bağlantı başarılı!")
    print(f"Toplam {len(prices)} coin verisi alındı")
    print("\nÖrnek veri:")
    print(prices[0])
except Exception as e:
    print(f"Hata: {e}") 