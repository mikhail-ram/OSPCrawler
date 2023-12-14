import os
import pandas as pd

import googleapiclient.discovery
import googleapiclient.errors

from pathvalidate import sanitize_filename

def getChannelID(youtube, name):
    request = youtube.search().list(
        part="snippet",
        maxResults=1,
        q=name,
        type="channel"
    )

    response = request.execute()
    response = response['items'][0]
    channel_title = response['snippet']['title']
    channel_id = response['id']['channelId']
    print(f"Found channel {channel_title} [channel ID: {channel_id}]")
    return channel_title, channel_id

def getAllCommentsRelatedToChannelID(youtube, channel_id):
    request = youtube.commentThreads().list(
        part="snippet,replies",
        allThreadsRelatedToChannelId=channel_id,
        maxResults = 100
    )
    response = request.execute()

    return response

def exportToCSV(channel_name, response):
    filename = sanitize_filename(f"{channel_name.title()} Comments.csv")
    print(f"Exporting {len(response['items'])} items to {filename}...")
    df = pd.json_normalize(response['items'])
    df.columns = df.columns.str.removeprefix('snippet.topLevelComment.').str.removeprefix('snippet.').str.removesuffix('.value').str.removesuffix('.comments')
    df.to_csv(filename, index=False)

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    api_key = "AIzaSyBuitR1ouBvYCo94LD3a64AB8l6b-wZoGg"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api_key)

    channel_name = input("Please enter the channel name: ")
    channel_name, channel_id = getChannelID(youtube, channel_name)
    response = getAllCommentsRelatedToChannelID(youtube, channel_id)
    exportToCSV(channel_name, response)

    print("Done")

if __name__ == "__main__":
    main()