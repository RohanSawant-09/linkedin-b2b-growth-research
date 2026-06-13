"""
YouTube Transcript Fetcher
==========================

This script downloads a transcript from a YouTube video and saves it
as a Markdown file for research.

HOW TO INSTALL THE REQUIRED PACKAGE
-----------------------------------
Open your terminal and run:

    pip install youtube-transcript-api

HOW TO RUN THIS SCRIPT
----------------------
From the project root folder, run:

    python scripts/youtube_transcript_fetcher.py

Or, if you are already inside the scripts folder:

    python youtube_transcript_fetcher.py
"""

import re
from datetime import datetime
from pathlib import Path

from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
    YouTubeTranscriptApi,
)


def extract_video_id(url):
    """
    Extract the 11-character YouTube video ID from a URL.

    YouTube links come in several formats, so we check a few common patterns.
    Returns the video ID as a string, or None if the URL is not valid.
    """
    patterns = [
        r"(?:youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})",
        r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def build_markdown_content(video_url, video_id, transcript_text):
    """
    Build the Markdown file content using the required structure.
    """
    date_extracted = datetime.now().strftime("%Y-%m-%d")

    return f"""# Video Information

Video URL: {video_url}
Video ID: {video_id}
Date Extracted: {date_extracted}

---

# Transcript

{transcript_text}
"""


def main():
    # Ask the user for a YouTube video URL
    video_url = input("Enter a YouTube video URL: ").strip()

    # Step 1: Extract the video ID from the URL
    video_id = extract_video_id(video_url)

    if video_id is None:
        print("Error: That does not look like a valid YouTube URL.")
        print("Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        return

    # Step 2: Fetch the transcript using youtube-transcript-api
    try:
        transcript = YouTubeTranscriptApi().fetch(video_id)

        # Join each snippet of text into one readable transcript
        transcript_text = "\n".join(snippet.text for snippet in transcript.snippets)

    except (NoTranscriptFound, TranscriptsDisabled):
        print(f"Error: No transcript is available for video ID '{video_id}'.")
        print("The video may not have captions turned on.")
        return

    except VideoUnavailable:
        print(f"Error: The video '{video_id}' is unavailable or does not exist.")
        return

    except Exception as error:
        print(f"Unexpected error: {error}")
        return

    # Step 3: Prepare the output folder (research/youtube-transcripts/)
    script_folder = Path(__file__).parent
    project_root = script_folder.parent
    output_folder = project_root / "research" / "youtube-transcripts"
    output_folder.mkdir(parents=True, exist_ok=True)

    # Step 4: Save the transcript as a Markdown file named after the video ID
    output_file = output_folder / f"{video_id}.md"
    markdown_content = build_markdown_content(video_url, video_id, transcript_text)

    output_file.write_text(markdown_content, encoding="utf-8")

    # Step 5: Tell the user where the file was saved
    print(f"\nSuccess! Transcript saved to:\n{output_file}")


if __name__ == "__main__":
    main()
