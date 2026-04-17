# User microserice

## Requirements
- Python 3.13
- Docker & Docker Compose

## Set up
1. Copy the .env.example into .env
2. Start the dependencies
```bash
docker compose up -d
```
3. Install python dependencies
```bash
pip install -r requirements.txt
```
4. Run migrations
```bash
flask --app src.app db upgrade
```
5. Start the app
```bash
python .\run.py
```
