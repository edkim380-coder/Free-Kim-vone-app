import os
import google_auth_oauthlib.flow
from googleapiclient.discovery import build

# Define the required OAuth scope for uploading videos to YouTube
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def authenticate_youtube():
    """Authenticates the user with YouTube via OAuth2 and returns the API client."""
    client_secrets_file = "client_secret.json"
    
    # Verify that the credentials file exists in the current directory
    if not os.path.exists(client_secrets_file):
        print(f"Error: '{client_secrets_file}' not found in this folder!")
        print("Please make sure your JSON credentials file is placed here.")
        return None

    try:
        # Initialize the OAuth Flow from the downloaded credentials file
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, SCOPES
        )
        
        # Run local server with open_browser=False for Termux CLI compatibility
        print("Starting authentication flow...")
        creds = flow.run_local_server(
            port=8080, 
            prompt='consent', 
            open_browser=False
        )
        
        # Build and return the authenticated YouTube service client
        youtube = build("youtube", "v3", credentials=creds)
        print("Successfully authenticated with YouTube!")
        return youtube

    except Exception as e:
        print(f"Authentication failed due to an error: {e}")
        return None

if __name__ == "__main__":
    authenticate_youtube()
