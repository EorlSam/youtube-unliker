#!/usr/bin/env python3
"""
YouTube Liked Videos Cleaner

This script connects to your YouTube account using OAuth2 authentication
and removes videos from your liked videos playlist that are under a specified duration.

Requirements:
- Google API Python Client: pip install google-api-python-client
- Google Auth OAuthLib: pip install google-auth-oauthlib
- Google Auth: pip install google-auth

Usage:
python youtube_likes_cleaner.py --min-duration 5 --client-secret client-secret.json
"""

import os
import argparse
import isodate
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Set up the YouTube API scopes required for this application
# We need the ability to read liked videos and manage likes
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def get_authenticated_service(client_secret_file):
    """Authenticate with the YouTube API using OAuth2."""
    credentials = None
    # Token file stores the user's credentials between runs
    token_file = 'token.json'
    
    # Check if we have previously saved credentials
    if os.path.exists(token_file):
        credentials = Credentials.from_authorized_user_info(
            info=eval(open(token_file).read()), scopes=SCOPES)
    
    # If there are no valid credentials, let the user log in
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_file, SCOPES)
            credentials = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(str(credentials.to_json()))
    
    # Build the YouTube service
    return build('youtube', 'v3', credentials=credentials)

def get_liked_videos(youtube):
    """Retrieve all videos from the user's 'Liked videos' playlist."""
    # First, get the liked videos playlist ID
    channels_response = youtube.channels().list(
        part='contentDetails',
        mine=True
    ).execute()
    
    # The liked videos playlist is a special playlist 
    liked_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['likes']
    
    liked_videos = []
    next_page_token = None
    
    # Get all videos from the liked videos playlist
    while True:
        playlist_items_response = youtube.playlistItems().list(
            part='snippet,contentDetails',
            playlistId=liked_playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()
        
        # Add each video's ID and other required details
        for item in playlist_items_response.get('items', []):
            video_id = item['contentDetails']['videoId']
            liked_videos.append({
                'id': video_id,
                'playlist_item_id': item['id'],
                'title': item['snippet']['title']
            })
        
        # Check if there are more pages of results
        next_page_token = playlist_items_response.get('nextPageToken')
        if not next_page_token:
            break
    
    return liked_videos, liked_playlist_id

def get_video_durations(youtube, video_ids):
    """Get the duration of each video in ISO 8601 format and convert to minutes."""
    video_durations = {}
    
    # Process video IDs in batches of 50 (API limit)
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        videos_response = youtube.videos().list(
            part='contentDetails',
            id=','.join(batch)
        ).execute()
        
        for item in videos_response.get('items', []):
            # Parse ISO 8601 duration to seconds
            duration_str = item['contentDetails']['duration']
            duration = isodate.parse_duration(duration_str)
            duration_minutes = duration.total_seconds() / 60
            
            video_durations[item['id']] = duration_minutes
    
    return video_durations

def unlike_videos(youtube, videos_to_unlike, liked_playlist_id):
    """Remove videos from the liked videos playlist."""
    for video in videos_to_unlike:
        print(f"Unliking: {video['title']} (Duration: {video['duration_minutes']:.2f} minutes)")
        
        # Method 1: Remove from liked videos playlist
        youtube.playlistItems().delete(
            id=video['playlist_item_id']
        ).execute()
        
        # Method 2: Use videos.rate with 'none' rating 
        # (This is a backup method in case the first one doesn't work)
        youtube.videos().rate(
            id=video['id'],
            rating='none'
        ).execute()
        
    return len(videos_to_unlike)

def main():
    parser = argparse.ArgumentParser(description='Remove videos from your liked videos that are under a specified duration.')
    parser.add_argument('--min-duration', type=float, default=5,
                        help='Minimum duration in minutes (videos shorter than this will be unliked)')
    parser.add_argument('--client-secret', type=str, default='client-secret.json',
                        help='Path to the OAuth client secret JSON file')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be unliked without actually unliking')
    
    args = parser.parse_args()
    
    print(f"YouTube Liked Videos Cleaner")
    print(f"Minimum video duration: {args.min_duration} minutes")
    
    # Authenticate and build the service
    youtube = get_authenticated_service(args.client_secret)
    
    # Get all liked videos
    print("Retrieving your liked videos...")
    liked_videos, liked_playlist_id = get_liked_videos(youtube)
    print(f"Found {len(liked_videos)} liked videos.")
    
    if not liked_videos:
        print("No liked videos found. Exiting.")
        return
    
    # Get durations for all videos
    print("Retrieving video durations...")
    video_durations = get_video_durations(youtube, [video['id'] for video in liked_videos])
    
    # Find videos to unlike based on duration
    videos_to_unlike = []
    for video in liked_videos:
        duration = video_durations.get(video['id'])
        if duration is None:
            print(f"Warning: Couldn't get duration for {video['title']}")
            continue
            
        video['duration_minutes'] = duration
        if duration < args.min_duration:
            videos_to_unlike.append(video)
    
    # Display summary
    print(f"\nFound {len(videos_to_unlike)} videos under {args.min_duration} minutes:")
    for video in videos_to_unlike:
        print(f"- {video['title']} ({video['duration_minutes']:.2f} minutes)")
    
    # Unlike videos if not a dry run
    if videos_to_unlike:
        if args.dry_run:
            print("\nDRY RUN: No videos were unliked.")
        else:
            print("\nUnliking videos...")
            unliked_count = unlike_videos(youtube, videos_to_unlike, liked_playlist_id)
            print(f"\nSuccessfully unliked {unliked_count} videos.")
    else:
        print("\nNo videos under the specified duration were found.")

if __name__ == '__main__':
    main()