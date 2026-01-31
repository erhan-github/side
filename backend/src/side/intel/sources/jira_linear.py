"""
Enterprise Intent Sources.
Wraps Jira and Linear APIs to treat tickets as 'Tasks'.
"""

from typing import List, Dict

class LinearSource:
    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def fetch_my_issues(self) -> List[Dict]:
        """Mocks fetching assigned issues from Linear."""
        return [
            {
                "id": "LIN-101",
                "title": "Fix Race Condition in PulseEngine",
                "priority": "HIGH",
                "url": "https://linear.app/sidelith/issue/LIN-101"
            }
        ]

class JiraSource:
    def __init__(self, host: str = None, token: str = None):
        self.host = host

    def fetch_sprint_tickets(self) -> List[Dict]:
        """Mocks fetching JQL query for current sprint."""
        return [
            {
                "key": "SIDE-404",
                "summary": "Deployment failing on Railway",
                "status": "In Progress"
            }
        ]
