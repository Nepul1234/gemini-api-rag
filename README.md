# 🎥 YouTube Channel RAG Tool

A Retrieval Augmented Generation (RAG) tool that scrapes YouTube channel videos and enables intelligent chat with video transcripts using Google's Gemini AI.

## ✨ Features

- 📺 **Channel Scraping**: Automatically fetch videos from any YouTube channel
- 📝 **Transcript Extraction**: Get subtitles/captions from videos using Apify
- 💾 **Local Storage**: Save each video transcript as a separate file
- ☁️ **Gemini File Search**: Upload transcripts to Gemini's vector database
- 💬 **Interactive Chat**: Ask questions about video content and get AI-powered answers
- 🔍 **Semantic Search**: Find relevant information across all video transcripts

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Apify API token ([Get one here](https://console.apify.com/account/integrations))
- Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd gemini-api-rag
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys:
   ```env
   APIFY_API_TOKEN=your_apify_api_token_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

### Usage

Run the tool:
```bash
python youtube_rag.py
```

Follow the prompts:
1. **Enter YouTube channel URL** (e.g., `https://www.youtube.com/@channelname`)
2. **Specify number of videos** to process (e.g., `10`)
3. **Wait for processing** (scraping, file creation, uploading)
4. **Start chatting** with the video transcripts!

### Example Session

```
🎥 YOUTUBE CHANNEL RAG TOOL
================================================================================

📺 Enter YouTube channel URL: https://www.youtube.com/@TechChannel
📊 How many videos to process (newest first)? 5

🔍 Scraping 5 videos from channel...
✓ Found 5 videos

📝 [1/5] Processing: Introduction to AI
   ✓ Transcript retrieved (15,234 characters)

📄 Creating transcript files...
  ✓ Created: 001_Introduction_to_AI.txt

☁️  Uploading files to Gemini File Search...
✓ All files uploaded!

💬 YOUTUBE TRANSCRIPT CHAT
================================================================================

You: What topics are covered in the videos?
Assistant: The videos cover several key topics including...

You: Tell me about the AI introduction video
Assistant: The "Introduction to AI" video discusses...
```

## 📁 Project Structure

```
gemini-api-rag/
├── youtube_rag.py          # Main application
├── requirements.txt        # Python dependencies
├── .env                    # Your API keys (create this)
├── .env.example           # Template for API keys
├── README.md              # This file
└── transcripts/           # Auto-generated transcript files
    ├── 001_video_title.txt
    ├── 002_video_title.txt
    └── ...
```

## 🔧 How It Works

1. **Scraping**: Uses Apify's YouTube scrapers to fetch video metadata and transcripts
2. **File Generation**: Creates individual text files for each video with:
   - Video title and metadata
   - Full transcript/captions
3. **Vector Database**: Uploads files to Gemini's File Search (vector store)
4. **RAG Chat**: Uses Gemini 2.0 Flash with File Search to answer questions

## 📚 API Documentation

- **Apify Platform**: [https://docs.apify.com/](https://docs.apify.com/)
- **Gemini File Search**: [https://ai.google.dev/gemini-api/docs/file-search](https://ai.google.dev/gemini-api/docs/file-search)
- **YouTube Scraper Actor**: [https://apify.com/streamers/youtube-scraper](https://apify.com/streamers/youtube-scraper)

## ⚠️ Important Notes

### Transcript Availability
- Videos **must have captions/subtitles** (auto-generated or manual)
- Private/unlisted videos cannot be scraped
- Some videos may not have transcripts available

### API Limits
- **Apify**: Check your plan's actor run limits
- **Gemini**: Free tier has 1GB file storage, paid tiers up to 1TB

### Rate Limiting
- Scraping many videos may take time
- Respect YouTube's terms of service
- Consider rate limits on API calls

## 🛠️ Troubleshooting

### "No transcripts found"
- Ensure videos have captions enabled
- Check if the channel URL is correct
- Verify videos are public

### "API Key Error"
- Confirm `.env` file exists with valid keys
- Check API key permissions and quotas
- Ensure no extra spaces in `.env` file

### "Upload Failed"
- Check your internet connection
- Verify Gemini API quota limits
- Try with fewer videos first

## 🔐 Security

- **Never commit `.env`** to version control
- Keep your API keys secret
- Rotate keys if accidentally exposed
- Review Apify and Gemini security best practices

## 📝 License

[Add your license here]

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 💡 Use Cases

- **Content Creators**: Analyze your channel's content themes
- **Researchers**: Search across educational video content
- **Students**: Query lecture transcripts for study material
- **Marketers**: Analyze competitor channel messaging
- **Developers**: Build custom video content applications

## 🎯 Future Enhancements

- [ ] Support for playlists
- [ ] Multiple language support
- [ ] Export chat history
- [ ] Web interface
- [ ] Video timestamp references in answers
- [ ] Batch processing multiple channels
- [ ] Custom metadata filtering

## 📞 Support

For issues or questions:
- Check the [Apify documentation](https://docs.apify.com/)
- Review [Gemini API docs](https://ai.google.dev/gemini-api/docs)
- Open an issue on GitHub

---

Built with ❤️ using [Apify](https://apify.com/) and [Google Gemini](https://ai.google.dev/)
