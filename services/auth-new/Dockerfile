FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

# CMD ["gunicorn", "src:app"]
CMD [ "gunicorn -w 4 -b 0.0.0.0:8000", "src.app:create_app()" ]
