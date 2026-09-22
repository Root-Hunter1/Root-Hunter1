FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY 7.py ./7.py
COPY database.py ./database.py

EXPOSE 9999/udp

CMD ["python", "7.py", "--host", "0.0.0.0", "--port", "9999"]
                                                                       ENV PYTHONDONT                                                     
