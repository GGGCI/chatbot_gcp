FROM python:3.11-slim

WORKDIR /chatbot

ENV API_KEY ""
ENV PROJECT_BASE_PATH ""

RUN python3 -m venv .venv
RUN . .venv/bin/activate

COPY requirements.txt  app.py  /chatbot/
COPY tools /chatbot/tools/
COPY static /chatbot/static
COPY templates /chatbot/templates
COPY src /chatbot/src/

RUN pip3 install -r requirements.txt

CMD ["python3", "app.py"]