"""Stop accidental deployment with published example passwords."""
from pathlib import Path
import sys
p=Path(__file__).parents[1]/'.env'
if not p.exists():
    sys.exit('HATA: .env bulunamadi. .env.example kopyalayip doldurun.')
values={}
for line in p.read_text().splitlines():
    if '=' in line and not line.lstrip().startswith('#'):
        a,b=line.split('=',1); values[a.strip()]=b.strip()
keys=('DASH_PASSWORD','FT_API_PASSWORD','FT_JWT_SECRET','FT_WS_TOKEN')
for k in keys:
    val=values.get(k,'')
    if len(val)<16 or val.startswith('REPLACE_'):
        sys.exit(f'HATA: {k} icin en az 16 karakterlik benzersiz sifre olusturun.')
if len(set(values[k] for k in keys))<len(keys):
    sys.exit('HATA: Farkli anahtarlarda ayni sifre kullanmayin.')
print('GUVENLIK KONTROLU BASARILI; acik anahtarlar loglanmadi.')
