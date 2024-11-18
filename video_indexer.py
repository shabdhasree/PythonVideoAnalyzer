import json
import os
import requests
from time import sleep

class VideoIndexer:
    subscription_key = "YOUR_PRIMARY_KEY"
    account_id = "YOUR_ACCOUNT_ID"
    location = "trial"  # Update if necessary or your current location

    @classmethod
    def get_access_token(cls):
        url = f"https://api.videoindexer.ai/Auth/{cls.location}/Accounts/{cls.account_id}/AccessToken?allowEdit=true"
        headers = {"Ocp-Apim-Subscription-Key": cls.subscription_key}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            access_token = response.json()
            return access_token
        else:
            print("[*] Error when calling video indexer API.")
            print(f"[*] Response : {response.status_code} {response.reason}")

    @classmethod
    def send_to_video_indexer(cls, local_file_path, video_name, video_description, privacy_setting, access_token):
        headers = {
            "Ocp-Apim-Subscription-Key": cls.subscription_key,
        }
        
        # Construct the URL with additional video details
        video_indexer_url = (
            f"https://api.videoindexer.ai/{cls.location}/Accounts/{cls.account_id}/Videos"
            f"?name={video_name}&description={video_description}&privacy={privacy_setting}"
            f"&indexingPreset=AdvancedVideo&accessToken={access_token}&sendSuccessEmail=True"
            f"&streamingPreset=NoStreaming"
        )

        # Open the local video file and send it as a binary file in the request
        with open(local_file_path, "rb") as video_file:
            files = {
                "file": (local_file_path, video_file, "video/mp4"),  # Adjust MIME type if needed
            }
            response = requests.post(url=video_indexer_url, headers=headers, files=files)
        
        if response.status_code == 200:
            video_indexer_id = response.json()["id"]
            return video_indexer_id
        elif response.status_code == 401:
            print("[*] Access token has expired, retrying with new token.")
            access_token = cls.get_access_token()
            return cls.send_to_video_indexer(local_file_path, video_name, video_description, privacy_setting, access_token)
        else:
            print("[*] Error when calling video indexer API.")
            print(f"[*] Response : {response.status_code} {response.reason}")
            print("[*] Response Content:", response.json())

    @classmethod
    def get_indexed_video_data(cls, video_id, access_token):
        headers = {
            "Ocp-Apim-Subscription-Key": cls.subscription_key,
        }
        url = f"https://api.videoindexer.ai/{cls.location}/Accounts/{cls.account_id}/Videos/{video_id}/Index?accessToken={access_token}"

        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            video_indexer_json_output = response.json()
            return video_indexer_json_output
        elif response.status_code == 401:
            print("[*] Access token has expired, retrying with new token.")
            access_token = cls.get_access_token()
            return cls.get_indexed_video_data(video_id, access_token)
        else:
            print("[*] Error when calling video indexer API.")
            print(f"[*] Response : {response.status_code} {response.reason}")


if __name__ == "__main__":
    vi = VideoIndexer()

    # Local video path (adjust to your local video file path)
    local_video_path = r"YOUR_LOCAL_VIDEO_PATH"

    # Video details
    video_name = "MyLocalVideo"
    video_description = "This is a sample video uploaded directly from local storage."
    privacy_setting = "Public"  # Options: Private, Public, etc.

    # Get an access token
    my_access_token = vi.get_access_token()

    # Send video to Video Indexer with details
    response_id = vi.send_to_video_indexer(local_file_path=local_video_path, video_name=video_name, video_description=video_description, privacy_setting=privacy_setting, access_token=my_access_token)

    # Retrieve indexed video data
    if response_id:
        indexer_response = vi.get_indexed_video_data(video_id=response_id, access_token=my_access_token)
        if indexer_response["state"] == "Processed":
            with open("video_indexer_response.json", "w") as f:
                json.dump(indexer_response, f)
        else:
            print("[*] Video has not finished processing")
