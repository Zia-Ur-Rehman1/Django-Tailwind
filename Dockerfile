# Builder Image
FROM python:3.11-slim-buster

WORKDIR /app

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD python manage.py runserver 0.0.0.0:80

# CMD ["gunicorn", "app.wsgi:application", "--bind", "0.0.0.0:8000"]