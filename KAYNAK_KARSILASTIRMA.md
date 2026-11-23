# Kaynak incelemesi (gönderilen ZIP dosyalarının içinden)

## 1. freqtrade-develop.zip
- `freqtrade/templates/sample_strategy.py`: `class SampleStrategy(IStrategy)`, `can_short=False`, `minimal_roi`, `stoploss=-0.10`, `trailing_stop=False`, `timeframe=5m` ve `populate_entry_trend`/`populate_exit_trend`.
- `freqtrade/plugins/pairlist/VolumePairList.py`: `number_assets` parametresi zorunlu, `quoteVolume` ile sıralama; sahte 12 coin listesi yok.
- `pyproject.toml`: `requires-python >=3.12`, `ccxt>=4.5.76`.
- Çalıştırma: resmi Freqtrade imajı; ZIP'ten `SampleStrategy.py` aynen kopyalandı.

## 2. ccxt-master.zip
- `README.md` ve `python/README.md`: Unified API, `load_markets()`, order/ticker/ohlcv çağrıları ve Bybit dahil 100+ borsa.
- Coin sayısı sabit değildir. `load_markets` dönüşü filtrelenir. `hub/main.py` gerçek CCXT çağrısı yapar; sayı yalnız yanıt geldiğinde görüntülenir.

## 3. polars-main.zip
- `README.md` ve `py-polars/pyproject.toml`: Polars Rust-native DataFrame. Yerel Python paketi `polars` rapor gruplama için kullanıldı.
- Strateji veya emir gönderme katmanı yoktur.

## 4. hummingbot-master.zip
- `hummingbot/strategy_v2/executors/position_executor/data_types.py`: `TripleBarrierConfig` içinde `stop_loss`, `take_profit`, `time_limit`, `trailing_stop` isteğe bağlı. `PositionExecutorConfig` giriş side, amount, leverage içerir.
- `hummingbot/strategy_v2/executors/position_executor/position_executor.py`: bariyer kontrolü, TP, SL, trailing ve emir yaşam döngüsü.
- `scripts/simple_pmm.py`: native paper market making örneği. Değiştirilmeden `reference_sources` içinde bulunur.
- `docker-compose.yml` resmi `hummingbot/hummingbot:latest` görüntüsüyle konteyner kullanır; başlatma için `hbot` komutları gerekir.

## 5. nautilus_trader-develop.zip
- `python/pyproject.toml`: versiyon 2.0.0, `requires-python >=3.13,<3.16`; Rust-native modüller.
- `examples/backtest/synthetic_data_pnl_test.py`: orijinal örnek; aynen kopyalandı.
- Kendi `BacktestEngine` ve olay tabanlı emir takibi mevcut. Bu pakette araştırma servisinde gerçek modül import edilir, ancak tarihi veri/instrument/strategy kurulmadan çalışmış gibi sonuç gösterilmez.
- Resmi Bybit adaptör kısıtları: https://nautilustrader.io/docs/latest/integrations/bybit/

## Farklı kütüphaneler neden tek algoritma değil?
Freqtrade algoritması native IStrategy, Hummingbot stratejileri PMM/PositionExecutor, NautilusTrader stratejileri event-driven strategy/execution API kullanır. CCXT borsa arayüzü, Polars analitik aracıdır. Dolayısıyla bu ZIP'ler aynı BUY/SELL sinyalini üretmez; bunları tek strateji koduna "birebir" bağlamak kaynak davranışlarını korumaz.

Resmi belgeler:
- https://github.com/freqtrade/freqtrade/tree/develop
- https://github.com/ccxt/ccxt/tree/master
- https://github.com/pola-rs/polars/tree/main
- https://github.com/hummingbot/hummingbot/tree/master
- https://github.com/nautechsystems/nautilus_trader/tree/develop
- https://www.freqtrade.io/en/latest/plugins/
- https://www.freqtrade.io/en/latest/exchanges/
- https://hummingbot.org/installation/hummingbot-client/
