# Hummingbot native connector: separate paper test only

The user-supplied `hummingbot-master.zip` includes `scripts/simple_pmm.py` and
`hummingbot/strategy_v2/executors/position_executor/position_executor.py`.
Its `TripleBarrierConfig` allows *optional* stop loss, take profit, time limit,
and trailing stop. The exact native source files have NOT been edited.

Run `docker compose --profile hummingbot up -d hummingbot` to prepare its official
image. Then use the project's native `hbot` commands (examples in the supplied
upstream README), e.g.:

```bash
docker compose exec hummingbot hbot create simple_pmm --name bybit_paper.yml --set exchange=bybit_paper_trade --set trading_pair=BTC-USDT
docker compose exec hummingbot hbot start bybit_paper.yml
```

The trading pair is an example **required by Hummingbot's one-pair strategy**,
not a hidden global 12-coin limit. Substitute another available connector pair.
This Hummingbot test is separate from the Freqtrade 100 USDT paper wallet.
Do not aggregate two different test-wallet balances as though they were one.
Hummingbot bybit_paper_trade is a *spot* paper connector, not the Bybit perp
executor; for perpetual futures use the separate Bybit testnet connector/keys
as documented upstream, never a real account in this experimental package.

This repository deliberately does not preconfigure Hummingbot real exchange
credentials or start another execution process automatically.
