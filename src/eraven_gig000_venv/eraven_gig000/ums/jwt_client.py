import requests
from django.conf import settings

UMS_RESTAPI= '/api/v1/ums'

class JWTAuthClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()  # Use session to maintain cookies
        self.session.headers.update({'Content-Type': 'application/json'})

    def sign_in(self, username, password):
        """Sign in and store JWT tokens as cookies in the session."""
        url = f"{self.base_url}/{UMS_RESTAPI}/sign-in/"
        payload = {'username': username, 'password': password}
        response = self.session.post(url, json=payload)
        if response.status_code == 200:
            print("Sign-in successful")
        else:
            print(f"Sign-in failed: {response.json()}")
        return response

    def fetch_user_data(self):
        """Access a protected endpoint using JWT tokens stored as cookies."""
        url = f"{self.base_url}/{UMS_RESTAPI}/users/"
        response = self.session.get(url)
        if response.status_code == 200:
            print("Fetched user data:", response.json())
        elif response.status_code == 401:
            print("Token expired, refreshing...")
            self.refresh_access_token()
            return self.fetch_user_data()  # Retry after refresh
        else:
            print(f"Failed to fetch user data: {response.json()}")
        return response

    def refresh_access_token(self):
        """Refresh the access token and update the session's cookies."""
        url = f"{self.base_url}/{UMS_RESTAPI}/refresh/"
        response = self.session.post(url)
        if response.status_code == 200:
            print("Access token refreshed")
        else:
            print(f"Token refresh failed: {response.json()}")
        return response

    def logout(self):
        """Clear the JWT cookies by logging out."""
        url = f"{self.base_url}/{UMS_RESTAPI}/logout/"
        response = self.session.post(url)
        if response.status_code == 204:
            print("Logged out successfully")
            self.session.cookies.clear()  # Clear session cookies
        else:
            print(f"Logout failed: {response.json()}")
        return response
