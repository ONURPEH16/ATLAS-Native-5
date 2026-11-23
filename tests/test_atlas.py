import importlib.util
import json
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('atlas_hub',ROOT/'hub'/'main.py')
appmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(appmod)


def test_uploaded_sample_is_unmodified():
    import hashlib,zipfile
    z=zipfile.ZipFile('/mnt/data/freqtrade-develop.zip')
    original=z.read('freqtrade-develop/freqtrade/templates/sample_strategy.py')
    actual=(ROOT/'engines/freqtrade/user_data/strategies/SampleStrategy.py').read_bytes()
    assert hashlib.sha256(original).digest()==hashlib.sha256(actual).digest()


def test_config_dry_run_all_universe():
    cfg=json.loads((ROOT/'engines/freqtrade/user_data/config.json').read_text())
    assert cfg['dry_run'] is True and cfg['dry_run_wallet']==100
    assert cfg['exchange']['key']==cfg['exchange']['secret']==''
    assert len(cfg['exchange']['pair_whitelist'])==1
    assert cfg['pairlists'][0]['method']=='VolumePairList'
    assert cfg['pairlists'][0]['number_assets']>=10000


def test_native_market_discovery_does_not_fake_unavailable():
    class Ex:
        def load_markets(self):return {'A':dict(symbol='BTC/USDT:USDT',active=True,swap=True,linear=True,settle='USDT',quote='USDT'),
                 'B':dict(symbol='ETH/USDT:USDT',active=False,swap=True,linear=True,settle='USDT',quote='USDT'),
                 'C':dict(symbol='BTC/USDT:USDT',active=True,swap=True,linear=True,settle='USDT',quote='USDT'),
                 'D':dict(symbol='DOGE/USDT',active=True,swap=False,linear=False,settle=None,quote='USDT')}
    assert appmod.native_markets(lambda:Ex())==['BTC/USDT:USDT']


def test_auth_and_guard(monkeypatch):
    monkeypatch.setenv('DASH_PASSWORD','a-very-long-passphrase')
    c=TestClient(appmod.app)
    assert c.get('/api/status').status_code==401
    import base64
    cred=base64.b64encode(b'admin:a-very-long-passphrase').decode()
    headers={'Authorization':'Basic '+cred}
    assert c.get('/').status_code==401
    assert c.post('/api/action',headers=headers,json={'command':'start'}).status_code==403
    with patch.object(appmod,'ft_call',return_value={'dry_run':False}):
        assert c.post('/api/action',headers={**headers,'x-atlas-action':'1'},json={'command':'start'}).status_code==503


def test_paper_trade_rejects_live(monkeypatch):
    monkeypatch.setenv('DASH_PASSWORD','a-very-long-passphrase')
    with patch.object(appmod,'ft_call',return_value={'dry_run':False}):
        try:appmod.actual_is_dry_run()
        except Exception as ex:assert ex.status_code==503
        else:assert False


def test_native_example_files_match_upstream():
    import zipfile
    for n,p,out in [('hummingbot-master','hummingbot-master/scripts/simple_pmm.py','hummingbot_simple_pmm_UNCHANGED.py'),
                    ('nautilus_trader-develop','nautilus_trader-develop/examples/backtest/synthetic_data_pnl_test.py','nautilus_synthetic_backtest_UNCHANGED.py')]:
        with zipfile.ZipFile('/mnt/data/'+n+'.zip') as z:
            assert z.read(p)==(ROOT/'reference_sources'/out).read_bytes()
