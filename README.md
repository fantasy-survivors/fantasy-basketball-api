# fantasy-basketball-api

echo "# fantasy-basketball-api" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin git@github.com:fantasy-survivors/fantasy-basketball-api.git
git push -u origin main

## install virtual environment
```python
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip   
```

## install dependencies
```python
pip install -r requirements.txt
source .venv/bin/activate
``` 

## Run player history stats loader with docker
```bash
docker build -t fantasy-survivors:history-data -f Dockerfile.history-data .
docker run -d --name nba-history-data fantasy-survivors:history-data
docker exec -it nba-history-data
docker stop nba-history-data
docker rm nba-history-data
```

docker compose -f docker-compose-local.yaml exec history_stats_loader psql -U postgres_user fantasy_survivors

\dt                     -- List all tables
\d table_name          -- Describe table structure
\du                    -- List users and roles
\l                     -- List databases
\timing                -- Toggle query execution time display
\x                     -- Toggle expanded display
\q                     -- Quit