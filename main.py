"""
Main execution script for Play Store Review Trend Analysis
"""
import argparse
import sys
from datetime import datetime, timedelta
from config import APP_CONFIGS, START_DATE
from batch_processor import BatchProcessor
from report_generator import ReportGenerator


def parse_app_name(app_input: str) -> tuple:
    """Parse app name from input (supports name or package)"""
    app_input_lower = app_input.lower()
    
    # Check if it's a known app name
    for app_key, config in APP_CONFIGS.items():
        if app_key in app_input_lower or config['app_name'].lower() in app_input_lower:
            return app_key, config['package_name'], config['app_name']
    
    # If not found, assume it's a package name
    return 'custom', app_input, app_input


def main():
    parser = argparse.ArgumentParser(
        description='Generate trend analysis report for Play Store reviews'
    )
    parser.add_argument(
        '--app',
        type=str,
        required=True,
        help='App name (swiggy/zomato) or Play Store package name'
    )
    parser.add_argument(
        '--date',
        type=str,
        required=True,
        help='Target date (T) in YYYY-MM-DD format'
    )
    parser.add_argument(
        '--fetch',
        action='store_true',
        help='Fetch reviews from Play Store if not found locally'
    )
    parser.add_argument(
        '--process-all',
        action='store_true',
        help='Process all dates from START_DATE to target date'
    )
    parser.add_argument(
        '--format',
        type=str,
        default='csv',
        choices=['csv', 'excel', 'json'],
        help='Output format for the report'
    )
    
    args = parser.parse_args()
    
    # Parse target date
    try:
        target_date = datetime.strptime(args.date, '%Y-%m-%d')
    except ValueError:
        print(f"Error: Invalid date format. Use YYYY-MM-DD")
        sys.exit(1)
    
    # Parse app name
    app_key, package_name, app_name = parse_app_name(args.app)
    print(f"App: {app_name} ({package_name})")
    print(f"Target date: {target_date.date()}")
    
    # Initialize processor
    batch_processor = BatchProcessor(app_name, package_name)
    
    # Process batches
    if args.process_all:
        # Process all dates from START_DATE to target_date
        current_date = START_DATE
        while current_date <= target_date:
            batch_processor.process_daily_batch(current_date, fetch_if_missing=args.fetch)
            current_date += timedelta(days=1)
    else:
        # Process only the target date and required historical dates
        window_start = max(target_date - timedelta(days=30), START_DATE)
        current_date = window_start
        
        while current_date <= target_date:
            batch_processor.process_daily_batch(current_date, fetch_if_missing=args.fetch)
            current_date += timedelta(days=1)
    
    # Generate report
    report_generator = ReportGenerator(batch_processor)
    report_df = report_generator.generate_trend_report(target_date)
    
    # Print summary
    report_generator.print_report_summary(report_df)
    
    # Save report
    report_path = report_generator.save_report(report_df, target_date, format=args.format)
    
    # Display report preview
    print(f"\n{'='*60}")
    print("REPORT PREVIEW (first 10 rows, first 5 dates)")
    print(f"{'='*60}")
    date_columns = [col for col in report_df.columns if col != 'Topic']
    preview_columns = ['Topic'] + date_columns[:5]
    print(report_df[preview_columns].head(10).to_string(index=False))
    
    print(f"\n✓ Report generation complete!")
    print(f"  Full report saved to: {report_path}")


if __name__ == '__main__':
    main()

