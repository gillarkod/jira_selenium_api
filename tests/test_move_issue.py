"""
Tests for jira_selenium.move_issue
"""
import unittest
import mock
from jira import JIRA
from jira_selenium import (
    MoveIssue,
    MoveIssueError,
)
from pyyamlconfig import load_config


class TestMoveIssue(unittest.TestCase):
    """
    Tests for jira_selenium.move_issue
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = load_config('config.yaml')
        self.url = config.get('url')
        self.from_project = config.get('from_project')
        self.to_project = config.get('to_project')
        self.username = config.get('username')
        self.password = config.get('password')

        self.assertIsNotNone(
            self.url,
            msg='You need to supply a url to Jira',
        )
        self.assertIsNotNone(
            self.from_project,
            msg='You need to supply a project to create issues in',
        )
        self.assertIsNotNone(
            self.to_project,
            msg='You need to supply a project to move issues to',
        )
        self.assertIsNotNone(
            self.username,
            msg='You need to supply a user that can create issues',
        )
        self.assertIsNotNone(
            self.password,
            msg='You need to supply a password for the user',
        )

        self.jira = JIRA(
            server=self.url,
            basic_auth=(
                self.username,
                self.password,
            )
        )

    def setUp(self):
        self.issue = self.jira.create_issue(
            project={'key': self.from_project},
            issuetype={'name': 'Task'},
            summary='Test issue',
        )

    def tearDown(self):
        self.issue.delete()

    def test_move(self):
        """
        Test that an issue can be moved
        """
        key_before = self.issue.key
        MoveIssue(self.issue.key, self.to_project, self.username, self.password)
        issues = self.jira.search_issues('key={}'.format(key_before))
        self.assertIn(
            self.to_project,
            issues[0].key,
        )

    def test_login_fail(self):
        """
        Test that an exception is raised if login fails
        """
        with mock.patch('jira_selenium.move_issue.load_config') as mock_config:
            mock_config.return_value = {
                'url': self.url,
            }
            with self.assertRaises(MoveIssueError) as err:
                MoveIssue(self.issue.key, self.to_project, self.username, 'wrongpassword')

            self.assertEqual(
                str(err.exception),
                'Could not login',
            )

    def test_wrong_url(self):
        """
        Test that an exception is raised if the login page is faulty
        """
        with mock.patch('jira_selenium.move_issue.load_config') as mock_config:
            mock_config.return_value = {
                'url': '{}/error'.format(self.url),
            }
            with self.assertRaises(MoveIssueError) as err:
                MoveIssue(self.issue.key, self.to_project, self.username, self.password)

            self.assertEqual(
                str(err.exception),
                'Could not login',
            )

    def test_faulty_issue(self):
        """
        Test that an exception is raised if the issue can't be found
        """
        with self.assertRaises(MoveIssueError) as err:
            MoveIssue('NOEXIST-1', self.to_project, self.username, self.password)

        self.assertEqual(
            str(err.exception),
            'Could not find issue',
        )

    def test_faulty_project(self):
        """
        Test that an exception is raised if the project can't be found
        """
        with self.assertRaises(MoveIssueError) as err:
            MoveIssue(self.issue.key, 'NOEXIST', self.username, self.password)

        self.assertEqual(
            str(err.exception),
            'Could not find project',
        )

    def test_faulty_move(self):
        """
        Test that an exception is raised if the issue can't be moved
        """
        with self.assertRaises(MoveIssueError) as err:
            MoveIssue(self.issue.key, self.from_project, self.username, self.password)

        self.assertEqual(
            str(err.exception),
            'Could not submit move request',
        )
