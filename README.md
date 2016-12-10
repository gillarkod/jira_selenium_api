jira_selenium_api
=================
An api that provides functions in Jira that are not available from the REST api and are too complicated to write in Script Runner.

Usage
-----
Install requirements

`pip install -r requirements.txt`

Run app

`python api.py`

Set up config file

`echo 'url: https://jira.example.com' > config.yaml`

Move an issue

`curl -u <user>:<password> 'http://localhost:5000/move/ISSUE-1/PROJECT'`

You can also use [this python module](https://github.com/gillarkod/jira_extended)