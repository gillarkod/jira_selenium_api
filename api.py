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
    APP.run(debug=True)
