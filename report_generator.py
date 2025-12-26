"""
Trend analysis report generator
"""
import os
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
from batch_processor import BatchProcessor
from config import ROLLING_WINDOW_DAYS, REPORTS_DIR


class ReportGenerator:
    """Generates trend analysis reports"""
    
    def __init__(self, batch_processor: BatchProcessor):
        self.batch_processor = batch_processor
        os.makedirs(REPORTS_DIR, exist_ok=True)
    
    def generate_trend_report(self, target_date: datetime, window_days: int = ROLLING_WINDOW_DAYS) -> pd.DataFrame:
        """
        Generate trend analysis report for date T showing trends from T-30 to T
        
        Args:
            target_date: Target date (T)
            window_days: Number of days to look back (default 30)
            
        Returns:
            DataFrame with topics as rows and dates as columns
        """
        print(f"\n{'='*60}")
        print(f"Generating trend report for {target_date.date()}")
        print(f"Analyzing trends from {(target_date - timedelta(days=window_days)).date()} to {target_date.date()}")
        print(f"{'='*60}")
        
        # Get all topics
        all_topics = self.batch_processor.get_all_topics()
        
        # Collect topic frequencies for each date in the window
        date_range = []
        current_date = target_date - timedelta(days=window_days)
        
        while current_date <= target_date:
            date_range.append(current_date)
            current_date += timedelta(days=1)
        
        # Build frequency matrix
        topic_frequencies = {}
        
        for date in date_range:
            frequencies = self.batch_processor.get_topic_frequencies_for_date(date)
            date_str = date.date().isoformat()
            
            for topic in all_topics:
                if topic not in topic_frequencies:
                    topic_frequencies[topic] = {}
                topic_frequencies[topic][date_str] = frequencies.get(topic, 0)
        
        # Create DataFrame
        report_data = []
        for topic in all_topics:
            row = {'Topic': topic}
            for date in date_range:
                date_str = date.date().isoformat()
                row[date_str] = topic_frequencies[topic].get(date_str, 0)
            report_data.append(row)
        
        report_df = pd.DataFrame(report_data)
        
        # Sort by total frequency (descending)
        date_columns = [d.date().isoformat() for d in date_range]
        report_df['Total'] = report_df[date_columns].sum(axis=1)
        report_df = report_df.sort_values('Total', ascending=False)
        report_df = report_df.drop('Total', axis=1)
        
        # Reset index
        report_df = report_df.reset_index(drop=True)
        
        return report_df
    
    def save_report(self, report_df: pd.DataFrame, target_date: datetime, format: str = 'csv'):
        """
        Save report to file
        
        Args:
            report_df: Report DataFrame
            target_date: Target date
            format: Output format ('csv', 'excel', 'json')
        """
        date_str = target_date.date().isoformat()
        
        if format == 'csv':
            file_path = os.path.join(REPORTS_DIR, f"trend_report_{date_str}.csv")
            report_df.to_csv(file_path, index=False)
        elif format == 'excel':
            file_path = os.path.join(REPORTS_DIR, f"trend_report_{date_str}.xlsx")
            report_df.to_excel(file_path, index=False)
        elif format == 'json':
            file_path = os.path.join(REPORTS_DIR, f"trend_report_{date_str}.json")
            report_df.to_json(file_path, orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        print(f"\nReport saved to: {file_path}")
        return file_path
    
    def print_report_summary(self, report_df: pd.DataFrame):
        """Print a summary of the report"""
        print(f"\n{'='*60}")
        print("REPORT SUMMARY")
        print(f"{'='*60}")
        print(f"Total topics tracked: {len(report_df)}")
        print(f"Date range: {report_df.columns[1]} to {report_df.columns[-1]}")
        print(f"\nTop 10 topics by total frequency:")
        print("-" * 60)
        
        # Calculate totals for summary
        date_columns = [col for col in report_df.columns if col != 'Topic']
        totals = report_df[date_columns].sum(axis=1)
        top_topics = report_df.copy()
        top_topics['Total'] = totals
        top_topics = top_topics.nlargest(10, 'Total')[['Topic', 'Total']]
        
        for idx, row in top_topics.iterrows():
            print(f"{row['Topic']}: {int(row['Total'])} occurrences")


