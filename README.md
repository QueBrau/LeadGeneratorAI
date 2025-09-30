# LeadGeneratorAI

A Python-based lead generation tool that automatically finds potential clients for home improvement services by searching social media groups and analyzing posts with AI.

## Features

- **Multi-Platform Search**: Searches Facebook groups, Reddit, and Nextdoor for relevant posts
- **AI-Powered Analysis**: Uses OpenAI GPT to analyze posts and determine lead quality
- **Automated Data Collection**: Uses SerpAPI for web scraping and data gathering
- **CSV Export**: Exports qualified leads to a CSV file for easy follow-up
- **Customizable Search Terms**: Easily modify search terms for different services or locations

## Services Targeted

- Painting services
- Home remodeling
- Landscaping
- Drywall repair
- Interior design
- HVAC services
- Electrical work
- Plumbing services
- And more...

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/LeadGeneratorAI.git
cd LeadGeneratorAI
```

2. Create a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
# or
source .venv/bin/activate  # On macOS/Linux
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Configuration

1. Get your API keys:
   - [SerpAPI Key](https://serpapi.com/) - Sign up for free tier
   - [OpenAI API Key](https://platform.openai.com/) - Create account and get API key

2. Create a `.env` file in the project root:
```bash
# Copy the example and add your keys
cp .env.example .env
```

3. Edit `.env` file with your actual API keys:
```env
SERPAPI_API_KEY=your_serpapi_key_here
OPENAI_API_KEY=your_openai_key_here
LOCATION=Your City, State
```

⚠️ **Important**: Never commit your `.env` file to version control. It's already included in `.gitignore`.

4. Customize the search terms in `lead_finder.py` as needed.

## Usage

Run the lead finder:
```bash
python lead_finder.py
```

The tool will:
1. Search for relevant posts across multiple platforms
2. Analyze each post using AI to determine if it's a qualified lead
3. Save qualified leads to `qualified_leads.csv`

## Output

The generated CSV file contains:
- Platform (Facebook, Reddit, Nextdoor)
- Post title/content
- URL (when available)
- AI analysis and reasoning
- Lead quality score

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License.