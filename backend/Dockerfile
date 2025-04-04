FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY data/ingredients.csv /app/data/ingredients.csv

RUN mkdir -p /app/static /app/media

CMD sh -c "python manage.py migrate --noinput && \
           python manage.py collectstatic --no-input && \
           gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000"
