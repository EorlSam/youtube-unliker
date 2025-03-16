# YouTube Liked Videos Cleaner

A Python script that helps you clean up your "Liked videos" playlist on YouTube by removing videos under a specified duration (e.g., short clips, TikToks, etc.).

## Features

- Connect to your YouTube account using OAuth 2.0
- Automatically fetch all your liked videos
- Filter videos based on their duration
- Remove short videos from your "Liked videos" playlist
- Resume capability after quota limits are reached
- Dry run mode to preview which videos would be unliked

## Requirements

- Python 3.6+
- Google account with YouTube data
- Google Cloud Project with YouTube Data API v3 enabled

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/youtube-unliker.git
   cd youtube-unliker
   ```

2. Install dependencies:
   ```
   pip install google-api-python-client google-auth-oauthlib google-auth isodate
   ```

## Setup Google Cloud Project

Before using this script, you need to set up a Google Cloud project and enable the YouTube Data API:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the YouTube Data API v3:
   - In the left sidebar, go to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: "Desktop application"
   - Name: "YouTube Likes Cleaner" (or any name you prefer)
   - Click "Create"
5. Download the credentials JSON file
6. Rename the downloaded file to `client-secret.json` and place it in the same directory as the script

## Usage

Basic usage:
```
python youtube_likes_cleaner.py
```

This will remove all liked videos under 5 minutes (the default threshold).

### Command-line options:

- `--min-duration X`: Set the minimum duration threshold in minutes (default: 5)
- `--client-secret PATH`: Path to your OAuth client secret file (default: client-secret.json)
- `--dry-run`: Preview which videos would be unliked without actually removing them
- `--batch-size N`: Number of videos to unlike in one batch (lower for quota issues)
- `--start-index N`: Start processing from this index (useful for resuming after quota exceeded)

### Examples:

Remove videos under 10 minutes:
```
python youtube_likes_cleaner.py --min-duration 10
```

Preview which videos would be unliked:
```
python youtube_likes_cleaner.py --dry-run
```

Resume after hitting quota limits:
```
python youtube_likes_cleaner.py --start-index 42
```

## Quota Limits

The YouTube Data API has daily quota limits. If you hit these limits, the script will automatically stop and provide you with the command to resume where you left off. The default quota for a new project is 10,000 units per day.

To check your quota usage:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to your project
3. Go to "APIs & Services" > "Dashboard"
4. See the "Quotas" section

## Privacy and Security

This script requires access to your YouTube account through OAuth 2.0. The script only accesses your liked videos and removes videos from your liked playlist. It does not access any other data or perform any other actions on your account.

Your OAuth credentials are stored locally in `client-secret.json` and `token.json`. Keep these files secure and do not share them.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## License

[MIT License](LICENSE)