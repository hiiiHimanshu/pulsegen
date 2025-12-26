# Quick Start Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Test with Sample Data (Recommended for First Run)

Generate sample review data to test the system:

```bash
python generate_sample_data.py --start-date 2024-06-01 --end-date 2024-06-30 --reviews-per-day 50
```

## Step 3: Process Reviews and Generate Report

Process the sample data and generate a trend report:

```bash
python main.py --app swiggy --date 2024-06-30
```

This will:
1. Load reviews from `data/reviews/`
2. Extract topics from each review
3. Deduplicate similar topics
4. Generate a trend report showing topic frequencies from June 1-30, 2024
5. Save the report to `reports/trend_report_2024-06-30.csv`

## Step 4: View the Report

Open the generated CSV file in Excel or any spreadsheet application to view the trend analysis.

## Using Real Play Store Data

To fetch real reviews from Google Play Store:

```bash
python main.py --app swiggy --date 2024-06-30 --fetch
```

**Note**: Fetching real reviews may take time and is subject to rate limits.

## Understanding the Output

The report shows:
- **Rows**: Each topic/issue identified in reviews
- **Columns**: Dates from T-30 to T (30-day rolling window)
- **Cells**: Number of times that topic appeared in reviews on that date

Example:
- If "Delivery issue" appears 12 times on June 1st, the cell at row "Delivery issue" and column "2024-06-01" will show 12
- This allows you to see trends: Is this issue increasing or decreasing over time?

## Customization

Edit `config.py` to:
- Add seed topics for your app
- Adjust similarity threshold for topic deduplication
- Change the rolling window size
- Configure other parameters

## Troubleshooting

1. **No reviews found**: Make sure you've generated sample data or fetched reviews with `--fetch` flag
2. **Import errors**: Ensure all dependencies are installed: `pip install -r requirements.txt`
3. **OpenAI errors**: The system works without OpenAI API key. It's optional for enhanced topic extraction.


