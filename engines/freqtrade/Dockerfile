# Railway service for original ATLAS Native 5 Freqtrade engine.
# Uses official Freqtrade execution engine and the unchanged uploaded SampleStrategy.
FROM freqtradeorg/freqtrade:stable

USER root
RUN mkdir -p /data /freqtrade/user_data/strategies
COPY user_data/config.json /freqtrade/user_data/config.json
COPY user_data/strategies/SampleStrategy.py /freqtrade/user_data/strategies/SampleStrategy.py
RUN chown -R ftuser:ftuser /data /freqtrade/user_data
USER ftuser

EXPOSE 8081

ENTRYPOINT ["/bin/sh", "-c", "sudo /bin/chown -R ftuser:ftuser /data && exec freqtrade \"$@\"", "--"]

CMD ["trade", "--config", "/freqtrade/user_data/config.json", "--strategy", "SampleStrategy", "--strategy-path", "/freqtrade/user_data/strategies", "--db-url", "sqlite:////data/atlas_paper.sqlite"]
