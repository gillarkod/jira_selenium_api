"""
Move an issue to a new project
"""
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotVisibleException,
)
from xvfbwrapper import Xvfb
from pyyamlconfig import load_config


class MoveIssueError(Exception):
    """
    Generic MoveIssue Error
    """
    pass


class MoveIssue:
    """
    Move an issue to a new project
    """
    def __init__(self, issue, project, username, password):
        self.config = load_config('config.yaml')
        self.issue = issue
        self.project = project
        self.xvfb = Xvfb(width=1280, height=720)
        self.username = username
        self.password = password

        self.xvfb.start()
        chrome_options = Options()
        for argument in self.config.get('arguments', []):
            chrome_options.add_argument(argument)
        self.browser = webdriver.Chrome(
            chrome_options=chrome_options,
        )
        self.login()
        self.move(self.get_issue_id())
        self.verify()
        self.clean()

    def clean(self):
        """
        Clean up on exit
        """
        self.xvfb.stop()
        self.browser.quit()

    def login(self):
        """
        Log in to Jira
        """
        self.browser.get(
            '{}/login.jsp'.format(
                self.config.get('url')
            )
        )
        try:
            username = self.browser.find_element_by_id('login-form-username')
            username.send_keys(self.username)
            password = self.browser.find_element_by_id('login-form-password')
            password.send_keys(self.password)
            password.send_keys(Keys.ENTER)
            if 'login.jsp' in self.browser.current_url:
                raise MoveIssueError('Could not login')
        except (NoSuchElementException, ElementNotVisibleException):
            raise MoveIssueError('Could not login')

    def get_issue_id(self):
        """
        Fetch issue id that is required for the move issue dialog
        """
        self.browser.get('{}/browse/{}'.format(
            self.config.get('url'),
            self.issue,
        ))
        try:
            issue_id = self.browser.find_element_by_id('key-val').get_attribute('rel')
        except NoSuchElementException:
            raise MoveIssueError('Could not find issue')
        return issue_id

    def move(self, issue_id):
        """
        Go through the move issue wizard
        """
        self.browser.get('{}/secure/MoveIssue!default.jspa?id={}'.format(
            self.config.get('url'),
            issue_id,
        ))
        dropdown = self.browser.find_element_by_id('project-options')
        suggestions = json.loads(
            dropdown.get_attribute('data-suggestions')
        )
        for item in suggestions:
            if item.get('label') == 'All Projects':
                for project in item.get('items'):
                    if '({})'.format(self.project) in project.get('label'):
                        inputfield = self.browser.find_element_by_id('project-field')
                        inputfield.send_keys(self.project)
                        inputfield.send_keys(Keys.ENTER)
                        self.browser.find_element_by_id('next_submit').click()
                        break
                else:
                    continue
                break
        else:
            raise MoveIssueError('Could not find project')

        try:
            self.browser.find_element_by_id('next_submit').click()
            self.browser.find_element_by_id('move_submit').click()
        except NoSuchElementException:
            raise MoveIssueError('Could not submit move request')

    def verify(self):
        """
        Verify that the issue has been moved
        """
        if self.project not in self.browser.current_url:
            raise MoveIssueError('Issue move failed')
