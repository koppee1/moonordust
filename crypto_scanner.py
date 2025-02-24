from binance import Client
import time
from datetime import datetime, timedelta, timezone
import sys
import os
import logging
import requests.exceptions
import asyncio
import json

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CryptoScanner:
    def __init__(self):
        self.client = None
        self.baslangic_fiyatlari = {}
        self.baslangic_hacimleri = {}
        self.son_guncelleme = None
        self.ilk_veri = True
        self.ilk_veriler_alindi = False
        self.hata_sayisi = 0
        self.max_hata = 3
        self.usdt_pairs = []
        self.son_veriler = {}
        
    def api_baglanti_kur(self):
        try:
            print("API bağlantısı kuruluyor...")
            self.client = Client()
            
            # Test API çağrısı
            status = self.client.get_system_status()
            print(f"Sistem durumu: {status['msg']}")
            
            # USDT çiftlerini al
            print("USDT çiftleri alınıyor...")
            exchange_info = self.client.get_exchange_info()
            self.usdt_pairs = [s['symbol'] for s in exchange_info['symbols'] 
                             if s['symbol'].endswith('USDT') and s['status'] == 'TRADING']
            
            if not self.usdt_pairs:
                print("USDT çiftleri alınamadı!")
                return False
                
            print(f"Toplam {len(self.usdt_pairs)} USDT çifti bulundu.")
            return True
            
        except Exception as e:
            print(f"API bağlantı hatası: {e}")
            return False

    def ekrani_temizle(self):
        if os.name == 'nt':
            _ = os.system('cls')
        else:
            _ = os.system('clear')
        sys.stdout.flush()

    def format_sayi(self, sayi):
        if sayi >= 1:
            return f"{sayi:.3f}"
        elif sayi >= 0.00001:
            return f"{sayi:.6f}"
        else:
            return f"{sayi:.8f}"

    def sonraki_guncelleme_zamani(self):
        now = datetime.now(timezone.utc)
        current_minute = now.minute
        current_5min = (current_minute // 5) * 5
        next_5min = current_5min + 5
        
        if next_5min == 60:
            next_time = now.replace(hour=now.hour + 1, minute=0, second=0, microsecond=0)
        else:
            next_time = now.replace(minute=next_5min, second=0, microsecond=0)
        
        wait_seconds = (next_time - now).total_seconds()
        return int(wait_seconds), next_time

    def geri_sayim_goster(self, kalan_sure):
        dakika = kalan_sure // 60
        saniye = kalan_sure % 60
        print(f"\r⏳ Güncellemeye kalan süre: {dakika:02d}:{saniye:02d}", end='', flush=True)

    def coin_verileri_al(self):
        try:
            if not self.client or not self.usdt_pairs:
                if not self.api_baglanti_kur():
                    return [], 0
            
            # Fiyat verilerini al
            tickers = self.client.get_ticker()
            if not tickers:
                return [], 0
                
            # USDT çiftlerini filtrele
            ticker_dict = {t['symbol']: t for t in tickers if t['symbol'] in self.usdt_pairs}
            coin_bilgileri = []
            
            # İlk çalıştırma için başlangıç verilerini topla
            if self.ilk_veri:
                print("\nİlk veriler toplanıyor, lütfen bekleyin...")
                for symbol in self.usdt_pairs:
                    try:
                        ticker = ticker_dict.get(symbol)
                        if not ticker:
                            continue
                            
                        current_price = float(ticker['lastPrice'])
                        current_volume = float(ticker['volume']) * current_price
                        
                        if current_price > 0 and current_volume > 0:
                            self.baslangic_fiyatlari[symbol] = current_price
                            self.baslangic_hacimleri[symbol] = current_volume
                            
                    except (ValueError, KeyError):
                        continue
                
                if len(self.baslangic_fiyatlari) > 0:
                    print(f"İlk veriler başarıyla toplandı: {len(self.baslangic_fiyatlari)} coin")
                    print("5 dakika sonra fiyat değişimleri gösterilecek...")
                    self.ilk_veriler_alindi = True
                    time.sleep(2)
                    
                return [], len(self.usdt_pairs)
            
            # Normal çalışma - değişimleri hesapla
            for symbol in self.usdt_pairs:
                try:
                    ticker = ticker_dict.get(symbol)
                    if not ticker:
                        continue
                        
                    symbol_short = symbol.replace('USDT', '')
                    current_price = float(ticker['lastPrice'])
                    current_volume = float(ticker['volume']) * current_price
                    
                    if current_price <= 0 or current_volume <= 0:
                        continue
                    
                    if symbol in self.baslangic_fiyatlari:
                        fiyat_degisim = ((current_price - self.baslangic_fiyatlari[symbol]) / 
                                       self.baslangic_fiyatlari[symbol] * 100)
                        
                        hacim_degisim = ((current_volume - self.baslangic_hacimleri[symbol]) / 
                                       self.baslangic_hacimleri[symbol] * 100)
                        
                        # Aşırı değişimleri filtrele
                        if abs(fiyat_degisim) > 50 or abs(hacim_degisim) > 500:
                            continue
                        
                        coin_bilgi = {
                            'sembol': symbol_short,
                            'son_fiyat': current_price,
                            'onceki_fiyat': self.baslangic_fiyatlari[symbol],
                            'fiyat_degisim': fiyat_degisim,
                            'hacim_degisim': hacim_degisim,
                            'son_hacim': current_volume
                        }
                        coin_bilgileri.append(coin_bilgi)
                        
                except (ValueError, KeyError):
                    continue
            
            if coin_bilgileri:
                print(f"\nVeriler güncellendi: {len(coin_bilgileri)} coin işlendi")
                time.sleep(1)
                
            return coin_bilgileri, len(self.usdt_pairs)
            
        except Exception as e:
            print(f"Veri alma hatası: {e}")
            return [], 0

    def verileri_goster(self, coin_bilgileri, usdt_sayisi):
        now = datetime.now(timezone.utc)
        self.ekrani_temizle()
        
        print(f"\n=== KRİPTO PARA TAKİP PROGRAMI ===")
        print(f"[{now.strftime('%d-%m-%Y %H:%M')} UTC]")
        print(f"\nToplam {usdt_sayisi} USDT çifti izleniyor")
        
        if not coin_bilgileri:
            if self.ilk_veri:
                if not self.ilk_veriler_alindi:
                    print("\nDurum: İlk veriler toplanıyor...")
                    print("İşlem: Coinlerin mevcut fiyatları kaydediliyor")
                else:
                    print("\nDurum: İlk veriler toplandı!")
                    print("İşlem: 5 dakika bekleniyor...")
                    print("Not: Bu süre sonunda fiyat değişimleri gösterilecek")
                return
            print("\nDurum: Veriler güncelleniyor...")
            return
        
        # Sıralamalar
        yukselenler = sorted(coin_bilgileri, key=lambda x: x['fiyat_degisim'], reverse=True)[:5]
        dusenler = sorted(coin_bilgileri, key=lambda x: x['fiyat_degisim'])[:5]
        hacim_artanlar = sorted(coin_bilgileri, key=lambda x: x['hacim_degisim'], reverse=True)[:5]
        hacim_dusenler = sorted(coin_bilgileri, key=lambda x: x['hacim_degisim'])[:5]
        
        print("\n📈 Son 5 dakikada YÜKSELEN coinler:")
        print("─" * 60)
        for coin in yukselenler:
            print(f"#{coin['sembol']} {self.format_sayi(coin['onceki_fiyat'])} → {self.format_sayi(coin['son_fiyat'])} USDT ({coin['fiyat_degisim']:+.2f}%)")
        
        print("\n📉 Son 5 dakikada DÜŞEN coinler:")
        print("─" * 60)
        for coin in dusenler:
            print(f"#{coin['sembol']} {self.format_sayi(coin['onceki_fiyat'])} → {self.format_sayi(coin['son_fiyat'])} USDT ({coin['fiyat_degisim']:+.2f}%)")
        
        print("\n💹 Son 5 dakikada HACMİ ARTAN coinler:")
        print("─" * 60)
        for coin in hacim_artanlar:
            print(f"#{coin['sembol']} {self.format_sayi(coin['son_fiyat'])} USDT ({coin['hacim_degisim']:+.2f}%)")
        
        print("\n📊 Son 5 dakikada HACMİ DÜŞEN coinler:")
        print("─" * 60)
        for coin in hacim_dusenler:
            print(f"#{coin['sembol']} {self.format_sayi(coin['son_fiyat'])} USDT ({coin['hacim_degisim']:+.2f}%)")

    def calistir(self):
        try:
            print("\n🚀 Program başlatılıyor...")
            if not self.api_baglanti_kur():
                print("❌ API bağlantısı kurulamadı!")
                return
            
            print("\n✅ Program başarıyla başlatıldı!")
            time.sleep(1)
            
            while True:
                try:
                    coin_bilgileri, usdt_sayisi = self.coin_verileri_al()
                    self.verileri_goster(coin_bilgileri, usdt_sayisi)
                    
                    bekleme_suresi, next_update = self.sonraki_guncelleme_zamani()
                    print(f"\n⏰ Bir sonraki güncelleme: {next_update.strftime('%H:%M')} UTC")
                    
                    baslangic = time.time()
                    while True:
                        gecen_sure = int(time.time() - baslangic)
                        kalan = bekleme_suresi - gecen_sure
                        
                        if kalan <= 0:
                            if self.ilk_veriler_alindi and self.ilk_veri:
                                print("\n🔄 5 dakika doldu, değişimler hesaplanıyor...")
                                self.ilk_veri = False
                            else:
                                print("\n📊 Yeni periyot başlıyor...")
                                self.baslangic_fiyatlari.clear()
                                self.baslangic_hacimleri.clear()
                                self.ilk_veri = True
                                self.ilk_veriler_alindi = False
                            time.sleep(1)
                            break
                            
                        self.geri_sayim_goster(kalan)
                        time.sleep(1)
                    
                except Exception as e:
                    print(f"\n⚠️ Döngü hatası: {e}")
                    print("🔄 5 saniye sonra tekrar denenecek...")
                    time.sleep(5)
                    continue
                    
        except KeyboardInterrupt:
            print("\n👋 Program kullanıcı tarafından sonlandırıldı.")
        except Exception as e:
            print(f"\n❌ Kritik hata: {e}")
            print("🔄 Program 3 saniye içinde yeniden başlatılıyor...")
            time.sleep(3)
            self.calistir()

if __name__ == "__main__":
    scanner = CryptoScanner()
    scanner.calistir()