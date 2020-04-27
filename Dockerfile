FROM python:3.7-slim-buster
WORKDIR /cisco-devnet-sweden-community-webex-bot/
COPY ./ ./
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "run.py"]
