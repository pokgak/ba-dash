# Demo Dashboard for RIOT-OS Benchmarking Results

The dashboard is separated into two parts a) the server b) the dashboard. The server holds all the results for past benchmarks. It might be replaceable by a DB. The dashboard fetches the results from the server and, based on the type of metric chosen, decide how to parse and plot the results.

## Dependencies

- setup a virtualenv and install dependencies
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Run server and dashboard

```
# server
cd test-server
python3 server.py

# dashboard
python3 app.py
```

The server is hosted on `0.0.0.0:5000` and the dashboard is accesible on `127.0.0.1:8050`.
