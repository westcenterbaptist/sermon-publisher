import os
import requests
import base64
import json
from datetime import datetime, timedelta

class PodbeanAuthenticator:
    def __init__(self, key, secret, url):
        self.key = key
        self.secret = secret
        self.url = url
        current_path = os.path.dirname(__file__)
        self.token_path = os.path.join(current_path, './token')
        self.authenticate()

    def authenticate(self):
        # Validate if the token exists and valid
        if self.validate_token():
            return True

        # Create the credentials string and base64 encode
        credentials = f"{self.key}:{self.secret}".encode()
        encoded_credentials = base64.b64encode(credentials).decode()

        # Set up Authorization header and payload
        headers = {'Authorization': f'Basic {encoded_credentials}'}
        data = {'grant_type': 'client_credentials'}

        # Make a request to obtain the access token
        response = requests.post(self.url, headers=headers, data=data)

        if response.status_code == 200:
            access_token = response.json()['access_token']
            expires_in = response.json()['expires_in']
        
            # Save the access token and expiration time
            self.save_token(access_token, expires_in)
        
            return True
        else:
            print(f"Failed to authenticate. Status code: {response.status_code}")
            return False

    def validate_token(self):
        if not os.path.exists(self.token_path):
            token_data = None
            with open(self.token_path, 'w') as f:
                pass
        else:
            token_data = self.get_token()

        if token_data:
            expiration_time = datetime.fromisoformat(token_data['expiration_time'])
            return datetime.now() <= expiration_time
        return False

    def save_token(self, access_token, expires_in):
        expiration_time = datetime.now() + timedelta(seconds=expires_in)
        token_data = {
            'access_token': access_token,
            'expiration_time': expiration_time.isoformat()
        }

        with open(self.token_path, 'w') as f:
            json.dump(token_data, f)

    def get_token(self):
        with open(self.token_path, 'r') as f:
            return json.load(f)

    def remove_token(self):
        if os.path.exists(self.token_path):
            os.remove(self.token_path)