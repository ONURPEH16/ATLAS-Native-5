"""ATLAS native engine dashboard: CCXT market discovery, Polars reports,
read-only-by-default Freqtrade API integration. No simulated fills invented.
"""
from __future__ import annotations
import base64
import hmac
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel

app = FastAPI(title='ATLAS · Five Native Sources', docs_url=None, redoc_url=None, openapi_url=None)
IST = ZoneInfo('Europe/Istanbul')
FT_URL = os.getenv('FT_URL','http://freqtrade:8081/api/v1').rstrip('/')
PUBLIC = Path(__file__).parent/'static'/'index.html'
MARKET_CACHE={'time':0,'symbols':[],'error':None,'all_count':0}


def good_auth(value):
    if not value.startswith('Basic '): return False
    try:
        d=base64.b64decode(value[6:],validate=True).decode('utf-8')
        u,p=d.split(':',1)
    except (ValueError, UnicodeError): return False
    expected=os.getenv('DASH_PASSWORD','')
    return (len(expected)>=12 and not expected.startswith('REPLACE_') and hmac.compare_digest(u,os.getenv('DASH_USER','admin'))
            and hmac.compare_digest(p,expected))


@app.middleware('http')
async def security(request:Request, nxt):
    if request.url.path=='/health': return PlainTextResponse('ATLAS hub healthy')
    if not good_auth(request.headers.get('Authorization','')):
        return Response('Authentication required',status_code=401,
                        headers={'WWW-Authenticate':'Basic realm="ATLAS NATIVE"'})
    if request.method not in ('GET','HEAD'):
        if request.headers.get('x-atlas-action')!='1':
            return JSONResponse({'error':'missing action header'},status_code=403)
        origin=request.headers.get('origin')
        if origin and origin.split('://',1)[-1].rstrip('/')!=request.headers.get('host'):
            return JSONResponse({'error':'cross-origin denied'},status_code=403)
    response=await nxt(request)
    response.headers['Cache-Control']='no-store'
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['X-Frame-Options']='DENY'
    response.headers['Content-Security-Policy']="default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none'; object-src 'none'"
    return response


def ft_call(method,route,payload=None):
    try:
        r=httpx.request(method,FT_URL+route,json=payload,timeout=9.0,
             auth=(os.getenv('FT_USER','native_internal'),os.getenv('FT_PASSWORD','')))
        r.raise_for_status()
        return r.json()
    except (httpx.HTTPError,ValueError) as ex:
        raise HTTPException(503,detail='Freqtrade API baglanamadi: '+type(ex).__name__) from ex


def actual_is_dry_run():
    cfg=ft_call('GET','/show_config')
    if cfg.get('dry_run') is not True:
        raise HTTPException(503,detail='SAFE GUARD: Freqtrade dry_run etkin degil; islemler devre disi')
    return cfg


def native_markets(loader=None):
    if loader is None:
        import ccxt
        loader=lambda:ccxt.bybit({'enableRateLimit':True,'options':{'defaultType':'swap'}})
    ex=loader()
    try:
        markets=ex.load_markets()
    finally:
        close=getattr(ex,'close',None)
        if callable(close):close()
    symbols=sorted([m['symbol'] for m in markets.values()
       if m.get('active') is not False and m.get('swap') and m.get('linear')
       and m.get('settle')=='USDT' and m.get('quote')=='USDT' and m.get('symbol')])
    return sorted(set(symbols))


@app.get('/')
def index():return FileResponse(PUBLIC,media_type='text/html')


@app.get('/api/status')
def status():
    ans={'system':'ATLAS NATIVE LAB','mode':'PAPER','owner_engine':'Freqtrade',
         'secondary_engines':{'Hummingbot':'opt-in separate paper setup',
                              'NautilusTrader':'native backtest research service'},
         'paper_wallet_start_usdt':100,'source_project_count':5,
         'now_istanbul':datetime.now(IST).isoformat(),'freqtrade_connected':False}
    try:
        cfg=actual_is_dry_run()
        ans['freqtrade_connected']=True
        ans['freqtrade_config']={'dry_run':cfg.get('dry_run'),
             'strategy':cfg.get('strategy'),'state':cfg.get('state'),
             'trading_mode':cfg.get('trading_mode'),'stake_currency':cfg.get('stake_currency'),
             'max_open_trades':cfg.get('max_open_trades'),'stake_amount':cfg.get('stake_amount')}
        for field,route in [('balance','/balance'),('profit','/profit'),('positions','/status')]:
            try:ans[field]=ft_call('GET',route)
            except HTTPException:ans[field]=None
    except HTTPException as ex:
        ans['error']=ex.detail
    p=Path(os.getenv('RESEARCH_STATUS_DIR','/research'))/'nautilus_status.json'
    if p.exists():
        try: ans['nautilus']=json.loads(p.read_text())
        except (ValueError,OSError):pass
    return ans


@app.get('/api/markets')
def markets():
    now=time.monotonic()
    if now-MARKET_CACHE['time']>1800 or (not MARKET_CACHE['time']):
        try:
            symbols=native_markets()
            MARKET_CACHE.update(time=now,symbols=symbols,error=None,all_count=len(symbols))
        except Exception as ex:
            MARKET_CACHE.update(time=now,error=type(ex).__name__+': '+str(ex)[:120])
    return {'source':'ccxt_bybit.load_markets()','type':'active_USDT_linear_swaps',
            'count':MARKET_CACHE['all_count'],'symbols':MARKET_CACHE['symbols'],
            'error':MARKET_CACHE['error'],
            'note':'Discoverable markets are not guaranteed tradeable for 100 USDT; Freqtrade also applies its own whitelist/filters.'}


def summarize_closed(rows, day):
    import polars as pl
    closed=[]
    for item in rows:
        if item.get('is_open'):continue
        d=item.get('close_date') or item.get('close_date_utc')
        try:
            stamp=datetime.fromisoformat(str(d).replace('Z','+00:00'))
            if stamp.tzinfo is None:stamp=stamp.replace(tzinfo=timezone.utc)
            if stamp.astimezone(IST).date().isoformat()!=day:continue
        except (ValueError,TypeError,AttributeError):continue
        closed.append({'id':item.get('trade_id',item.get('id')),
                       'pair':item.get('pair'),'short':bool(item.get('is_short')),
                       'entry_tag':item.get('enter_tag') or '',
                       'exit_reason':item.get('exit_reason') or '',
                       'pnl':float(item.get('close_profit_abs') or 0),
                       'open_date':item.get('open_date'),'close_date':d})
    if not closed:return {'trades':[], 'count':0, 'winners':0,'pnl_usdt':0,'win_rate_pct':None,'by_pair':[]}
    df=pl.DataFrame(closed)
    pairs=df.group_by('pair').agg([pl.col('pnl').sum().round(5).alias('net_pnl'),pl.len().alias('trades')]).sort('net_pnl')
    pnl=round(float(df['pnl'].sum()),5)
    wins=int(df.filter(pl.col('pnl')>0).height)
    return {'trades':closed,'count':len(closed),'winners':wins,'pnl_usdt':pnl,
             'win_rate_pct':round(100*wins/len(closed),2), 'by_pair':pairs.to_dicts()}


@app.get('/api/daily')
def daily(day:str|None=None):
    day=day or datetime.now(IST).date().isoformat()
    try:datetime.strptime(day,'%Y-%m-%d')
    except ValueError:raise HTTPException(400,'Tarih YYYY-MM-DD olmali')
    actual_is_dry_run()
    # Freqtrade native API; no imagined trade rows. These rows may be paginated.
    payload=ft_call('GET','/trades?limit=500&offset=0')
    rows=payload.get('trades',[]) if isinstance(payload,dict) else []
    result=summarize_closed(rows,day)
    result.update({'schema':'ATLAS_NATIVE_DAILY_1','day_istanbul':day,
         'source':'Freqtrade native /trades API + Polars','mode':'paper',
         'pagination_note':'Latest 500 rows; if larger, older rows are excluded.',
         'warning':'Different engines use independent simulation accounts; only Freqtrade PnL counted.'})
    return result


@app.get('/api/daily/download')
def download(day:str|None=None):
    data=daily(day)
    filename=f'ATLAS_Gunluk_{data["day_istanbul"]}.json'
    return Response(json.dumps(data,ensure_ascii=False,indent=2),media_type='application/json',
                    headers={'Content-Disposition':f'attachment; filename="{filename}"'})


class Action(BaseModel):
    command:str
    trade_id:int|None=None


@app.post('/api/action')
def action(data:Action):
    actual_is_dry_run()
    if data.command in ('start','pause'):
        return ft_call('POST','/'+data.command,{})
    if data.command=='close_paper_trade' and data.trade_id and data.trade_id>0:
        positions=ft_call('GET','/status')
        if not any(int(t.get('trade_id',t.get('id',0)))==data.trade_id for t in positions):
            raise HTTPException(404,'Acik sanal pozisyon bulunamadi')
        return ft_call('POST','/forceexit',{'tradeid':str(data.trade_id)})
    raise HTTPException(400,'Sadece start/pause/close_paper_trade desteklenir')
