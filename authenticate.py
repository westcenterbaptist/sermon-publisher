import os
import requests
import base64
import json
from datetime import datetime, timedelta
from config_manager import ConfigManager

class Authenticator:
    def __init__(self, config):
        self.config = config
        self.config_manager = ConfigManager()

    def authenticate(self):
        if self.token_exists():
            if self.check_valid_token():
               return True 

        # Get API key and secret from configuration
        api_key = self.config['api_key']
        api_secret = self.config['api_secret']

        # Create the credentials string
        credentials = f"{api_key}:{api_secret}"
    
        # Base64 encode the credentials
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

        oauth_token_url = f"{self.config['base_url']}oauth/token"

        # Set the headers with the Authorization header
        headers = {
            'Authorization': f"Basic {encoded_credentials}"
        }

        # Set the request payload
        data = {
            'grant_type': 'client_credentials'
        }

        # Make a request to obtain the access token
        response = requests.post(oauth_token_url, headers=headers, data=data)

        # Handle the response
        if response.status_code == 200:
            access_token = response.json()['access_token']
            expires_in = response.json()['expires_in']
        
            # Save the access token and expiration time
            self.save_token(access_token, expires_in)
        
            return True
        else:
            print(f"Failed to authenticate. Status code: {response.status_code}")
            return False

    def token_exists(self):
        if os.path.exists(self.config['token_path']):
            token_data = self.get_token_data()
            return token_data is not None
        
        return False

    def read_token(self):
        token_data = self.get_token_data()
        return token_data['access_token']

    def save_token(self, access_token, expires_in):
        expiration_time = datetime.now() + timedelta(seconds=expires_in)
        token_data = {
            'access_token': access_token,
            'expiration_time': expiration_time.isoformat()
        }

        with open(self.config['token_path'], 'w') as token_file:
            json.dump(token_data, token_file)

    def check_valid_token(self):
        token_data = self.get_token_data()
        if token_data:
            expiration_time = datetime.fromisoformat(token_data['expiration_time'])
            return datetime.now() <= expiration_time
        return False

    def get_token_data(self):
        with open(self.config['token_path'], 'r') as token_file:
            return json.load(token_file)
