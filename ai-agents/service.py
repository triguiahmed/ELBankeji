import requests
from requests_oauthlib import OAuth1
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Disable debug logging for specific libraries
logging.getLogger("requests_oauthlib").setLevel(logging.INFO)
logging.getLogger("oauthlib").setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.INFO)

class JiraService:
    def __init__(self):
        
        self.jira_url = "https://support.neoxam.com/"
        logger.info(f"JIRA_URL  {self.jira_url}")

    
    def _get_oauth_auth(self, secret_path, mount_point):
        """
        Retrieve OAuth credentials from Vault.

        :param secret_path: The path to the OAuth credentials in Vault.
        :return: OAuth1 authentication object.
        """
        credentials = {}

        return OAuth1(
            credentials["consumer_key"],
            resource_owner_key=credentials["oauth_token"],
            signature_method='RSA-SHA1',
            rsa_key=credentials["private_key"],
            signature_type='auth_header'
        )


    
    def get_issue(self, issue_id):
        """
        Fetch a specific Jira issue by its ID.
        :param issue_id: The Jira issue ID (e.g., 'AP-1234').
        :return: JSON response containing the issue data.
        """
        import json
        auth = self._get_oauth_auth('xray_deploy', 'AP_secrets/')

        # Get issue details to extract assignee and reporter
        url = f'{self.jira_url}rest/api/2/issue/{issue_id}/'
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        logger.info("#################### JIRA RESPONSE  done #################")

        issue_data = response.json()
        assignee_name = issue_data['fields']['assignee']['displayName']
        
        # Get all comments
        url = f'{self.jira_url}rest/api/2/issue/{issue_id}/comment'
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        logger.info("#################### JIRA RESPONSE message done #################")
        
        comments_data = response.json()
        non_assignee_comments = []
        
        for comment in comments_data['comments']:
            if comment['author']['displayName'] != assignee_name:
                non_assignee_comments.append({
                    'author': comment['author']['displayName'],
                    'author_email': comment['author'].get('emailAddress', ''),
                    'created': comment['created'],
                    'updated': comment['updated'],
                    'body': comment['body'],
                    'is_reporter': comment['author']['displayName'] == issue_data['fields']['reporter']['displayName']
                })
        
        # Sort comments by creation date (oldest first)
        non_assignee_comments.sort(key=lambda x: x['created'])
        logger.info("#################### RESPONSE ################# {}".format(json.dumps({
            'issue_key': issue_data['key'],
            'issue_summary': issue_data['fields']['summary'],
            'assignee': assignee_name,
            'non_assignee_comments': non_assignee_comments,
        }, indent=2)))
        # Convert to JSON
        return json.dumps({
            'issue_key': issue_data['key'],
            'issue_summary': issue_data['fields']['summary'],
            'assignee': assignee_name,
            'non_assignee_comments': non_assignee_comments,
        }, indent=2)

#Track customer feedback from support tickets for the NXDH-28959        
#NXDH-29526
#NXDH-29059

