#!/usr/bin/env python3
"""
YouTube Channel RAG Tool
Scrapes YouTube channel videos and enables chat with transcripts using Gemini API
"""

import os
import time
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from apify_client import ApifyClient
from google import genai
from google.genai import types
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

# Load environment variables
load_dotenv()

class YouTubeRAG:
    def __init__(self):
        """Initialize the YouTube RAG tool with API clients"""
        self.apify_token = os.getenv('APIFY_API_TOKEN')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')

        if not self.apify_token:
            raise ValueError("APIFY_API_TOKEN not found in environment variables")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        self.apify_client = ApifyClient(self.apify_token)
        self.gemini_client = genai.Client(api_key=self.gemini_api_key)

        self.transcripts_dir = Path("transcripts")
        self.transcripts_dir.mkdir(exist_ok=True)

        self.file_search_store = None
        self.channel_name = None

    def _normalize_url(self, url):
        """Normalize URL to use HTTPS and proper format"""
        url = url.strip()
        if url.startswith('http://'):
            url = url.replace('http://', 'https://')
        elif not url.startswith('https://'):
            url = 'https://' + url
        return url

    def scrape_youtube_channel(self, channel_url, max_videos):
        """
        Scrape YouTube channel videos using Apify

        Args:
            channel_url: YouTube channel URL
            max_videos: Maximum number of videos to scrape (from newest to oldest)

        Returns:
            List of video data with titles and transcripts
        """
        # Normalize URL to HTTPS
        channel_url = self._normalize_url(channel_url)

        print(f"\n🔍 Scraping {max_videos} videos from channel: {channel_url}")
        print("This may take a few minutes...\n")

        # First, try to get channel videos with the main scraper
        # We'll use streamers/youtube-scraper for video metadata
        # and streamers/youtube-video-to-transcript for transcripts

        try:
            # Step 1: Get video URLs from the channel
            print("📹 Fetching video list from channel...")

            channel_run_input = {
                "startUrls": [{"url": channel_url}],
                "maxResults": max_videos,
                "maxResultsShorts": 0,
                "maxResultStreams": 0,
            }

            # Run the YouTube scraper
            channel_run = self.apify_client.actor("streamers/youtube-scraper").call(
                run_input=channel_run_input
            )

            # Fetch results from the dataset
            videos_data = []
            for item in self.apify_client.dataset(channel_run["defaultDatasetId"]).iterate_items():
                videos_data.append(item)

            print(f"✓ Found {len(videos_data)} videos")

            # Step 2: Get transcripts for each video
            videos_with_transcripts = []

            for idx, video in enumerate(videos_data[:max_videos], 1):
                video_url = video.get('url') or f"https://www.youtube.com/watch?v={video.get('id')}"
                video_title = video.get('title', 'Untitled Video')

                print(f"\n📝 [{idx}/{min(len(videos_data), max_videos)}] Processing: {video_title}")
                print(f"   URL: {video_url}")

                # Try to get transcript
                transcript = self._get_video_transcript(video_url)

                if transcript:
                    videos_with_transcripts.append({
                        'title': video_title,
                        'url': video_url,
                        'transcript': transcript,
                        'description': video.get('description', ''),
                        'published_at': video.get('date', ''),
                        'views': video.get('viewCount', 0),
                        'duration': video.get('duration', ''),
                    })
                    print(f"   ✓ Transcript retrieved ({len(transcript)} characters)")
                else:
                    print(f"   ⚠ No transcript available for this video")

            print(f"\n✓ Successfully processed {len(videos_with_transcripts)} videos with transcripts")
            return videos_with_transcripts

        except Exception as e:
            print(f"\n❌ Error scraping YouTube channel: {str(e)}")
            print("\nTrying alternative approach with transcript scraper...")
            return self._scrape_with_transcript_actor(channel_url, max_videos)

    def _extract_video_id(self, video_url):
        """Extract video ID from YouTube URL"""
        # Handle different URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
            r'youtube\.com\/embed\/([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                return match.group(1)
        return None

    def _get_video_transcript(self, video_url):
        """Get transcript for a single video using YouTube Transcript API"""
        try:
            # Extract video ID from URL
            video_id = self._extract_video_id(video_url)

            if not video_id:
                return None

            # Try to get transcript (prefer English, but accept any language)
            try:
                # Try to get English transcript first
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            except NoTranscriptFound:
                # If no English transcript, get whatever is available
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

            # Combine all transcript segments into one text
            transcript_text = ' '.join([segment['text'] for segment in transcript_list])

            return transcript_text if transcript_text else None

        except TranscriptsDisabled:
            # Video has transcripts disabled
            return None
        except NoTranscriptFound:
            # No transcript available in any language
            return None
        except Exception as e:
            # Other errors
            return None

    def _scrape_with_transcript_actor(self, channel_url, max_videos):
        """Alternative method using different Apify actors"""
        print("Using alternative scraping method...")

        # This is a fallback - we'll create dummy data for now
        # In production, you might want to use different actor combinations
        print("⚠ Could not retrieve transcripts with available actors.")
        print("Please ensure the videos have captions/subtitles enabled.")
        return []

    def create_transcript_files(self, videos_data):
        """
        Create individual text files for each video transcript

        Args:
            videos_data: List of video dictionaries with transcript data

        Returns:
            List of file paths created
        """
        print(f"\n📄 Creating transcript files...")

        file_paths = []

        for idx, video in enumerate(videos_data, 1):
            # Create a safe filename from video title
            safe_title = "".join(c for c in video['title'] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title[:100]  # Limit filename length
            filename = f"{idx:03d}_{safe_title}.txt"
            file_path = self.transcripts_dir / filename

            # Create file content with metadata and transcript
            content = f"""Title: {video['title']}
URL: {video['url']}
Published: {video.get('published_at', 'N/A')}
Views: {video.get('views', 'N/A')}
Duration: {video.get('duration', 'N/A')}

Description:
{video.get('description', 'N/A')}

{'='*80}
TRANSCRIPT:
{'='*80}

{video['transcript']}
"""

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            file_paths.append(file_path)
            print(f"  ✓ Created: {filename}")

        print(f"\n✓ Created {len(file_paths)} transcript files in '{self.transcripts_dir}' directory")
        return file_paths

    def upload_to_gemini(self, file_paths):
        """
        Upload transcript files to Gemini File Search

        Args:
            file_paths: List of file paths to upload

        Returns:
            File search store name
        """
        print(f"\n☁️  Uploading files to Gemini File Search...")

        # Create a file search store
        store_name = f"youtube-rag-{int(time.time())}"
        print(f"  Creating file search store: {store_name}")

        self.file_search_store = self.gemini_client.file_search_stores.create(
            config={'display_name': store_name}
        )

        print(f"  ✓ Store created: {self.file_search_store.name}")

        # Upload each file to the store
        for idx, file_path in enumerate(file_paths, 1):
            print(f"\n  [{idx}/{len(file_paths)}] Uploading: {file_path.name}")

            operation = self.gemini_client.file_search_stores.upload_to_file_search_store(
                file=str(file_path),
                file_search_store_name=self.file_search_store.name,
                config={'display_name': file_path.name}
            )

            # Wait for upload to complete
            wait_count = 0
            while not operation.done:
                time.sleep(2)
                operation = self.gemini_client.operations.get(operation)
                wait_count += 1
                if wait_count % 5 == 0:
                    print(f"    Still uploading... ({wait_count * 2}s)")

            print(f"    ✓ Upload complete")

        print(f"\n✓ All files uploaded to Gemini File Search!")
        return self.file_search_store.name

    def chat_with_transcripts(self):
        """Interactive chat interface for querying video transcripts"""
        print("\n" + "="*80)
        print("💬 YOUTUBE TRANSCRIPT CHAT")
        print("="*80)
        print("\nYou can now ask questions about the video transcripts!")
        print("Type 'quit', 'exit', or 'q' to end the chat.\n")
        print("="*80 + "\n")

        while True:
            try:
                # Get user input
                user_question = input("You: ").strip()

                if user_question.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!\n")
                    break

                if not user_question:
                    continue

                # Query Gemini with File Search
                print("\n🤔 Thinking...\n")

                response = self.gemini_client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=user_question,
                    config=types.GenerateContentConfig(
                        tools=[
                            types.Tool(
                                file_search=types.FileSearch(
                                    file_search_store_names=[self.file_search_store.name]
                                )
                            )
                        ]
                    )
                )

                # Display response
                print("Assistant:", response.text)
                print("\n" + "-"*80 + "\n")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")
                continue


def main():
    """Main application entry point"""
    print("\n" + "="*80)
    print("🎥 YOUTUBE CHANNEL RAG TOOL")
    print("="*80)
    print("\nThis tool scrapes YouTube channel videos and lets you chat with transcripts")
    print("using Gemini AI's File Search capability.\n")

    try:
        # Initialize RAG tool
        rag = YouTubeRAG()

        # Get user input
        print("="*80)
        channel_url = input("\n📺 Enter YouTube channel URL: ").strip()

        if not channel_url:
            print("❌ Channel URL is required!")
            return

        try:
            max_videos = int(input("📊 How many videos to process (newest first)? ").strip())
            if max_videos <= 0:
                print("❌ Number of videos must be positive!")
                return
        except ValueError:
            print("❌ Please enter a valid number!")
            return

        print("\n" + "="*80)

        # Step 1: Scrape YouTube channel
        videos_data = rag.scrape_youtube_channel(channel_url, max_videos)

        if not videos_data:
            print("\n❌ No videos with transcripts found. Please ensure:")
            print("   1. The channel URL is correct")
            print("   2. Videos have captions/subtitles enabled")
            print("   3. The videos are public")
            return

        # Step 2: Create transcript files
        file_paths = rag.create_transcript_files(videos_data)

        # Step 3: Upload to Gemini File Search
        store_name = rag.upload_to_gemini(file_paths)

        # Step 4: Start chat interface
        rag.chat_with_transcripts()

    except ValueError as e:
        print(f"\n❌ Configuration Error: {str(e)}")
        print("\nPlease ensure you have:")
        print("1. Created a .env file (copy from .env.example)")
        print("2. Added your APIFY_API_TOKEN")
        print("3. Added your GEMINI_API_KEY")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
