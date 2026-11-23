"""Native NautilusTrader presence/compatibility diagnostic, not a trading engine.
The input ZIP's unmodified full example is in reference_sources/. Users can
run native backtests with sourced market feeds without enabling real orders.
"""
import json
import time
from pathlib import Path
from datetime import datetime, timezone
p=Path('/research/nautilus_status.json')
while True:
    try:
        import nautilus_trader
        from nautilus_trader.backtest import BacktestEngine
        message={'service':'nautilus_trader','installed':True,
                 'native_engine_imported':BacktestEngine.__name__,
                 'trading':False,'paper_wallet_connected':False,
                 'state':'ready_for_native_historical_backtest',
                 'note':'Data/instrument/strategy not configured. Never count this as an executed backtest.'}
    except Exception as ex:
        message={'service':'nautilus_trader','installed':False,'trading':False,
                 'state':'import_error','error':type(ex).__name__+': '+str(ex)[:200]}
    message['checked_utc']=datetime.now(timezone.utc).isoformat()
    p.write_text(json.dumps(message))
    time.sleep(60)
