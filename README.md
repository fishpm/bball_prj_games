Baseball Game Predictions
=========================

ETL
---
The purpose of ETL (Extract-Transform-Load) is to take the raw sources of data and, in code, define each step to the point it becomes a feature in the model or data that can be directly presented via the UI.

All data should be stored as tables and use Postgres as the relational database. To install and run the app should only require the ability to download the data sets and the relevant software including postgres running locally.

Model
-----
The model(s) takes prepared data from the database and creates a machine learning model that can be serialized to permanently save it and easily load it into memory for use. 

App
---
The purpose of the app is to provide a friendly interface to the data and the model. The app consists of a web framework that serves the frontend (probably some combination of HTML, CSS, and javascript) and talks to an API that, for example, can in turn talk to the database or score a model.

To run the app go to app/ and run

```
python app.py
```

And go to localhost:5000 in your browser.

Requirements
------------
Software required to run the application:
- Postgres 9.3

Python packages
- sklearn
- flask
- psycopg2
