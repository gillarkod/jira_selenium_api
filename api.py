#!/bin/env python3
"""
API for interacting with Jira
Some features of Jira don't have an endpoint and are too complex
to implement with scriptrunner. Instead, we use selenium.
"""
from flask import (
    Flask,
    request,
)
from jira_selenium import (
    MoveIssue,
    MoveIssueError,
)
from pyyamlconfig import load_config

APP = Flask(__name__)


@APP.route('/move/<issue>/<project>')
def move_issue(issue, project):
    """
    Move an issue to a new project
    """
    try:
        auth = request.authorization
        if auth is None:
            return 'You need to authenticate', 401
        MoveIssue(issue, project, auth.username, auth.password)
        return 'success'
    except MoveIssueError as err:
        return str(err), 400

if __name__ == '__main__':
    config = load_config('config.yaml')
    ssl = config.get('ssl')
    if ssl is None:
        context = None
    else:
        context = (ssl.get('crt'), ssl.get('key'))
    APP.run(
        host=config.get('host', '0.0.0.0'),
        port=config.get('port', 5000),
        debug=config.get('debug', False),
        ssl_context=context,
    )
