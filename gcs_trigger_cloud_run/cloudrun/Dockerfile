FROM python:3.11-slim

WORKDIR /mnt/

COPY requirements.txt /mnt/

# Install production dependencies.
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /mnt/

CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
