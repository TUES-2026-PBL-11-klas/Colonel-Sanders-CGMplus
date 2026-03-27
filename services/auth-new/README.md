# User microserice

## Requirements
- Python 3.13
- Docker & Docker Compose

## Set up
1. Start the dependencies
```bash
docker compose up -d
```
2. Install python dependencies
```bash
pip install -r requirements.txt
```
3. Run migrations
```bash
flask --app src.app db upgrade
```
4. Start the app
```bash
python .\run.py
```
