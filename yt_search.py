import googleapiclient.discovery
import os
from dotenv import load_dotenv

load_dotenv()

def search(name):

    API_KEY = os.getenv('GOOGLE_API')
    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = API_KEY)
    
    request = youtube.search().list(
        part='id',
        maxResults=25,
        q=name
    )
    response = request.execute()

    vid_to_play = response["items"][0]['id']['videoId']

    return vid_to_play


if __name__ == '__main__':
    search("hello")