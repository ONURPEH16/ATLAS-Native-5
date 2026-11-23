# NautilusTrader 2.0 branch needs Python 3.13+. Install a compatible wheel.
FROM python:3.13-slim
WORKDIR /worker
RUN pip install --no-cache-dir 'nautilus_trader>=2.0,<3'
COPY worker.py .
CMD ["python", "worker.py"]
COPY synthetic_data_pnl_test_UNCHANGED.py .
