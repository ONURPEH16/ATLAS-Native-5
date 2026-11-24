# ATLAS Native 5 — Railway Freqtrade servisi eki

Bu paket ATLAS Native 5'in orijinal içeriğini korur; sadece `engines/freqtrade/Dockerfile` eklenmiştir. Değişiklik işlem stratejisini değiştirmez.

Railway kurulum:
1. Deponun köküne ZIP içeriğini güncelle.
2. Mevcut hub servisini silme; Root Directory `/hub` olarak kalır.
3. Aynı projeye depodan yeni GitHub service ekle, adını `freqtrade` yap, Root Directory `/engines/freqtrade`.
4. Yeni servise `/data` Volume ekle. Eski hub Volume'una dokunma.
5. `FREQTRADE__API_SERVER__PASSWORD` = hub'ın `FT_PASSWORD` değişkenindeki değer.
6. `FREQTRADE__API_SERVER__JWT_SECRET_KEY` ve `FREQTRADE__API_SERVER__WS_TOKEN` = her biri için yeni, güçlü ve birbirinden farklı rastgele değer.
7. Freqtrade servisine public domain üretme. Freqtrade'in internal adresi `freqtrade.railway.internal:8081`.
8. Hub'da `FT_URL=http://freqtrade.railway.internal:8081/api/v1`, `FT_USER=native_internal`, `FT_PASSWORD` aynı kalmalı.

ÖNEMLİ: Freqtrade hâlâ orijinal SampleStrategy'yi çalıştırır (yalnız LONG, varsayılan ROI, stoploss ve trailing kuralları). Bu strateji kârlılık garantisi vermez. Dry-run açık, gerçek para API anahtarları yoktur. Bybit/CloudFront `403 Forbidden` hatası devam ederse Freqtrade veri almaya başlamayabilir; bu sorun Dockerfile eklenerek çözülmez.
