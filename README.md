# Play Store Review Trend Analysis System

An AI-powered system for analyzing Google Play Store reviews and generating trend analysis reports. The system processes daily batches of reviews, extracts topics using AI agents, and creates comprehensive trend reports showing topic frequency over a rolling 30-day window.

## Features

- **Daily Batch Processing**: Processes reviews day-by-day as batches
- **AI-Powered Topic Extraction**: Uses semantic similarity and embeddings to identify topics
- **Topic Deduplication**: Automatically consolidates similar topics (e.g., "Delivery guy was rude" → "Delivery partner rude")
- **Trend Analysis**: Generates reports showing topic frequency trends over 30-day rolling windows
- **Automatic Topic Discovery**: Discovers new topics beyond seed topics as reviews are processed

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Set up OpenAI API key for enhanced topic extraction:
```bash
export OPENAI_API_KEY='your-api-key-here'
```
Or create a `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

## Usage

### Basic Usage

Generate a trend report for a specific date:

```bash
python main.py --app swiggy --date 2024-06-30 --fetch
```

### Arguments

- `--app`: App name (`swiggy`, `zomato`) or Play Store package name
- `--date`: Target date (T) in YYYY-MM-DD format. Report will show trends from T-30 to T
- `--fetch`: Fetch reviews from Play Store if not found locally
- `--process-all`: Process all dates from June 1, 2024 to target date
- `--format`: Output format (`csv`, `excel`, `json`) - default: `csv`

### Examples

1. **Generate report for Swiggy on June 30, 2024**:
```bash
python main.py --app swiggy --date 2024-06-30 --fetch
```

2. **Process all dates and generate report**:
```bash
python main.py --app swiggy --date 2024-06-30 --process-all --fetch
```

3. **Generate report in Excel format**:
```bash
python main.py --app zomato --date 2024-07-15 --format excel
```

4. **Use custom app (provide package name)**:
```bash
python main.py --app com.example.app --date 2024-06-30 --fetch
```

### Testing with Sample Data

To test the system without fetching real reviews, you can generate sample data:

```bash
# Generate sample reviews for June 2024
python generate_sample_data.py --start-date 2024-06-01 --end-date 2024-06-30 --reviews-per-day 50

# Then process the sample data
python main.py --app swiggy --date 2024-06-30
```

### Testing Topic Extraction

Test the topic extraction and deduplication system:

```bash
python test_system.py
```

## Output

The system generates a trend analysis report table where:
- **Rows**: Topics (issues, requests, feedback)
- **Columns**: Dates from T-30 to T
- **Cells**: Frequency of topic occurrence on that date

Example output structure:
```
Topic                   2024-06-01  2024-06-02  2024-06-03  ...  2024-06-30
Delivery issue          12          8           15          ...  23
Food stale              5           7           3           ...  11
Delivery partner rude   8           12          6           ...  9
Maps not working        2           4           7           ...  5
...
```

Reports are saved in the `reports/` directory.

## Architecture

### Components

1. **ReviewFetcher** (`review_fetcher.py`): Fetches reviews from Google Play Store
2. **TopicExtractor** (`topic_extractor.py`): AI agent for topic extraction and deduplication
3. **BatchProcessor** (`batch_processor.py`): Processes daily batches of reviews
4. **ReportGenerator** (`report_generator.py`): Generates trend analysis reports

### Topic Deduplication

The system uses semantic similarity (cosine similarity on embeddings) to consolidate similar topics:
- "Delivery guy was rude" → "Delivery partner rude"
- "Delivery person behaved badly" → "Delivery partner rude"
- "Delivery partner was impolite" → "Delivery partner rude"

Similarity threshold: 0.75 (configurable in `config.py`)

### Data Storage

- **Raw Reviews**: `data/reviews/reviews_YYYY-MM-DD.json`
- **Processed Reviews with Topics**: `data/topics/topics_YYYY-MM-DD.json`
- **Topic Registry**: `data/topics/topic_registry_{app_name}.json`
- **Reports**: `reports/trend_report_YYYY-MM-DD.{csv,excel,json}`

## Configuration

Edit `config.py` to customize:
- Seed topics for initial categorization
- Similarity threshold for topic deduplication
- Maximum number of topics to track
- Date ranges and window sizes
- Embedding model selection

## Technical Approach

### AI Agent Strategy

1. **Keyword-Based Extraction**: Fast initial topic detection using keyword matching
2. **Semantic Embeddings**: Uses sentence transformers for semantic similarity
3. **Topic Registry**: Maintains a registry of canonical topics with embeddings
4. **Deduplication**: Compares new topics against registry using cosine similarity
5. **Optional OpenAI Enhancement**: Can use GPT-3.5 for additional topic discovery

### Why Agentic AI?

- **High Recall**: Captures variations in how users express the same issue
- **Adaptive**: Discovers new topics as they emerge
- **Semantic Understanding**: Understands context and meaning, not just keywords
- **Deduplication**: Prevents topic fragmentation through semantic similarity

## Limitations & Notes

- Google Play Store API rate limits may apply when fetching reviews
- Review fetching may take time for large date ranges
- Topic extraction accuracy depends on review quality and language
- Some reviews may not match any topics (noise filtering)

## Future Enhancements

- Support for multiple languages
- Sentiment analysis integration
- Topic clustering visualization
- Real-time processing pipeline
- Web dashboard for report visualization

## License

MIT License

