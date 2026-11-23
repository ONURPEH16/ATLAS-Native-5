# ATLAS NATIVE 5 — Orijinal motorlarla sıfırdan araştırma ve sanal işlem paketi

**UYARI:** Bu kurulum, önceki Profesör Bot ve NOVA V1 kodlarını taşımaz. Eski 12 coin, sabit 20x, %5 teminat, TP'siz trailing ve özel EMA stratejisi **kullanılmaz**. Birincil motor için kullanıcının yüklediği `freqtrade-develop.zip` dosyasındaki `freqtrade/templates/sample_strategy.py` **bayt bayt değiştirilmeden** kopyalanmıştır. Bu strateji Freqtrade'in EĞİTİM amaçlı örneğidir; kârlılık kanıtı değildir. Varsayılan olarak `can_short=False` (sadece LONG), kendi `minimal_roi`, `stoploss=-0.10` ve `trailing_stop=False` değerlerine sahiptir. Böylece "kendi orijinal SL/TP'sini kullan" isteğine uyar, fakat her koşulda LONG ve SHORT açmaz.

## 5 kaynağın gerçek rolleri

| Kaynak | Gerçekte kullanılan kısım | Orijinal işleyiş |
|---|---|---|
| Freqtrade (`freqtrade-develop.zip`) | Resmi Freqtrade konteyneri, **ZIP'ten değiştirilmeden kopyalanmış SampleStrategy** | 100 USDT **dry-run** cüzdan, motorun kendi market order / stop / ROI akışı |
| CCXT (`ccxt-master.zip`) | Hub'da `ccxt.bybit().load_markets()`; Freqtrade de dahili CCXT kullanır | Bybit'teki aktif USDT lineer perp enstrümanlarının listesini **o anda** keşfeder |
| Polars (`polars-main.zip`) | `polars.DataFrame.group_by` ile gerçek Freqtrade API işlemlerinden günlük rapor | Veri/rapor hesabı, asla broker değildir |
| Hummingbot (`hummingbot-master.zip`) | Ayrı resmi Hummingbot konteyneri, ZIP'teki `simple_pmm.py` örneği dokümana kondu | Native paper connector ve stratejiler; özel seçilen piyasada ayrı test hesabı |
| NautilusTrader (`nautilus_trader-develop.zip`) | Ayrı Python 3.13 araştırma servisinde gerçek NautilusTrader importu ve ZIP'teki değişmemiş backtest örneği | Olay tabanlı backtest; **Bybit gerçek emirleri kapalı** |

**Önemli dürüstlük notu:** Docker servisleri, yüklenen beş ZIP'in her satırını kaynak koddan derlemez. Freqtrade/Hummingbot'un resmi dağıtım görüntüleri; CCXT, Polars ve NautilusTrader'ın sürümlü Python dağıtımları kullanılır. Kaynak ZIP'lerinden seçilen örnekler aynı dosya içerikleriyle saklanır. Resmi dağıtım sürümü, ZIP'in `develop/master` anlık görüntüsünden farklı olabilir. Yerelde Docker çalıştırıp üçünün tümünde uçtan uca emir testi doğrulanmadı. Bu bir **native entegrasyon başlangıç paketi**, "üçü aynı anda aynı kasada işlem açıyor" iddiası değildir.

## Coin sayısı — 12 yok

Freqtrade'in `VolumePairList` bileşeni kullanılır; üst sınır `100000` seçildiği için **12/20 gibi yapay bir coin sınırı yok**. Gerçekte kaç aktif piyasa olduğunu CCXT borsa verisinden bulur, Freqtrade ise kendi piyasa-uygunluk ve hacim kontrollerinden geçirir. Her aktif piyasa otomatik işlem açılabilir demek değildir; bazı kontratların asgari emir miktarı 100 USDT için uygun olmayabilir. Binlerce enstrümanın 5 dakikalık mumlarının indirilmesi sunucu kaynakları ve Bybit hız sınırları nedeniyle ağır olabilir. Çok fazla istek hatası alınırsa `config.json > pairlists[0].number_assets` değerini kendin teknik ihtiyaçlarına göre azaltmak gerekebilir; bu kâr/zararı değiştirebilir.

Hummingbot'ta native `simple_pmm` **bir yapılandırmada bir pair** ile çalışır; bütün coinleri otomatik taradığı iddia edilemez. NautilusTrader'da hangi araçlar ve veriler yüklenecekse onları ayrıca belirtmek gerekir. Üç kaynak projede evrensel, ortak "x adet coin" bilgisi yoktur.

## SL / TP — platformların orijinal kuralları

- **Freqtrade:** `SampleStrategy.py` içindeki `minimal_roi` zaman tablosu, `stoploss=-0.10` ve `trailing_stop=False`. Bu dosya değişmedi. Buradaki **-10% fiyat getirisi/yük kaldıracı mantığını gerçek stop garantisi sanma**: Freqtrade futures stop yorumunu kendi hesaplar. Kullanıcıdan 20x istenmediği için 20x zorlanmaz; mevcut native strateji callback ile kaldıraç artırmaz ve varsayılan kaldıraç 1x'dir.
- **Hummingbot:** `PositionExecutor` içindeki `TripleBarrierConfig`: isteğe bağlı `stop_loss`, `take_profit`, `time_limit`, `trailing_stop`. Hangi strategynin nasıl girdiği yapılandırmaya bağlı; `simple_pmm` bir piyasa yapıcılığı örneğidir ve Freqtrade ile aynı stop düzenini kullanmaz.
- **NautilusTrader:** Stop, TP ve takip eden emirler ayrı Native OrderType / strategy emirleri olarak tanımlanır. Bybit adaptöründe **pozisyon TP/SL ve bazı trailing stop gönderimleri** desteklenmediği için gerçek borsayla yürütülebileceği varsayılmaz.

## Neden 3 motoru aynı 100 USDT'ye bağlamadık?

Üç motorun her biri kendi emir, bakiye ve risk durumunu tutar. Aynı 100 sanal doların 3 farklı yazılıma bağımsız 100 dolar gibi verilmesi, aslında 300 dolar simüle edilmesi olur. Bunu **tek kasa** gibi göstermek yanıltıcıdır. Bu yüzden Freqtrade tek paper-broker sahibi, NautilusTrader bağımsız araştırma servisidir. Hummingbot'u etkinleştirirsen *ikinci bir ayrı paper hesabı* olur ve panelde birincil 100 USDT ile toplanmaz. Hummingbot'u ve NautilusTrader'ı da **aynı cüzdanda gerçek işlem yapan alt motorlar** olarak kullanmak için ayrıca merkezi risk brokerı geliştirmek gerekir; böyle bir aracı kurduk diye iddia etmiyoruz.

## Kurulum: Docker Compose / yeni VPS (önerilen)

En sorunsuz yol: **yeni, bağımsız bir VPS** (çok motor için 8 GB+ RAM önerilir; yüklenen piyasa sayısına göre daha fazlası gerekebilir), Docker Engine + Docker Compose. Bu paket **tek Railway servisine** üç motoru gizlice sıkıştırmak için tasarlanmadı. Railway istersen servisler ayrı ayrılmalıdır. GitHub deposuna `atlas_native_5` klasörünün **içindekilerini** yükle.

```bash
cp .env.example .env
# .env içindeki dört şifreyi kendi güçlü, farklı değerlerinle değiştir
python3 scripts/check_env.py
# Freqtrade + CCXT + Polars paneli: 
docker compose up -d --build hub freqtrade
# Durum:
docker compose ps
docker compose logs --tail=100 freqtrade
```

Panel **yalnız `127.0.0.1:8080`** adresinde (VPS'nin kendisi) dinler; dış internetten açmak için HTTPS reverse proxy veya SSH port-forward kur. Panel şifresiz çalışmaz; bilinen REPLACE_ örnek şifrelerini kabul etmez. Freqtrade API'si dışa port yayınlamaz. **Gerçek Bybit API anahtarı GİRME**. Borsaya bağlantı sadece halka açık piyasa verisidir. Railway Volume'u yeni ve eskiden tamamen farklı olsun; burada Docker `freqtrade_data` volume kullanılır.

Paneldeki *Sanal botu başlat* düğmesi Freqtrade'in native `/start`, *Yeni girişleri durdur* `/pause`, *Sanal kapat* `/forceexit` API'sini çalıştırır. `/show_config` içinde `dry_run != true` görülürse panel kontrolü kilitlenir.

Günlük JSON: **Günlük JSON indir**; rapor 500 en yeni native Freqtrade trade satırından hazırlanır. Çok daha büyük veri setleri için API sayfalaması genişletilmeli. CCXT Bybit market keşfi ağ erişimine bağlıdır; hata durumunda panel hata yazar, sahte coin sayısı üretmez.

## Hummingbot native paper modunu ayrıca başlatma

```bash
docker compose --profile hummingbot up -d hummingbot
# Hummingbot's own native commands, using its own paper account:
docker compose exec hummingbot hbot create simple_pmm --name bybit_paper.yml --set exchange=bybit_paper_trade --set trading_pair=BTC-USDT
docker compose exec hummingbot hbot start bybit_paper.yml
```

Bu örnekteki `BTC-USDT`, Hummingbot CLI'nin *örnek bir coin belirtmeyi gerektirmesinden* kaynaklıdır, zorunlu coin havuzu değildir. Bybit paper spot ile Bybit perpetual testnet farklıdır. Perp stratejisi kullanmak istersen Hummingbot'un kendi Bybit perpetual testnet connector kurulumunu uygulaman gerekir. Kendi yerel işlem cüzdanı Freqtrade'den bağımsızdır.

## NautilusTrader native backtest servisini açma

```bash
docker compose --profile nautilus up -d nautilus
docker compose logs nautilus
# Orijinal ZIP içinden değiştirilmeden kopyalanan yerel sentetik backtest örneği:
docker compose run --rm nautilus python /worker/synthetic_data_pnl_test_UNCHANGED.py
```

Bu **sentetik test**, Bybit gerçek mumlarıyla test değildir. Test için dış fiyat verilerinin Nautilus formatına uygun içeri aktarılması gerekir. UI "hazır" yazarsa **kârlılık veya aktif işlem onayı anlamına gelmez.** Nautilus için orijinal ZIP `version.json` 2.0.0 / Python >=3.13 istiyor; resmi dağıtımın kurulumu/sürümü farklı olabilir.

## Hatalar ve doğrulama sınırları

Yerel kontroller: Python sözdizimi, HTML açılması ve hub API/güvenlik testleri. Docker, Hummingbot `hbot`, NautilusTrader 2.0 wheel ve Bybit erişimi bu ortamda çalıştırılamadı; sorunsuz kurulum garantisi yok. Lütfen `docker compose logs` ile doğrudan başarısız servisi kontrol et. *Kârlılık doğrulanmadı*. Freqtrade `SampleStrategy` kendi README'inde bir örnek olduğunu söyler; eğitimseldir.

**Kaynak arşivlerinin tam SHA-256 değerleri:** `SOURCE_SHA256.json`. Orijinal örneklerin nasıl alındığı ve kullanım farkları `KAYNAK_KARSILASTIRMA.md` içinde.
