import json
import requests

class FreelancerScraper(object):
    def __init__(self, oauth_token: str) -> None:
        self.headers = {'freelancer-oauth-v1': oauth_token}
        url = "https://www.freelancer.com/api/users/0.1/self/"

        # Start session and verify user
        self.session = requests.Session()
        self.session.get(self.url, headers=self.headers)
        self.job_list = [129,55,2320,95,13,39]
        
    def get_projects(self):
        # We create the project request url and save it to a json
        projects_url = 'https://www.freelancer.com/api/projects/0.1/projects/active/?compat=&limit=10'

        for job in self.job_list:
            projects_url += f'&jobs%5B%5D={job}'

        r = self.session.get(projects_url)
        data = r.json()
        projects = data['result']['projects']

        return projects
