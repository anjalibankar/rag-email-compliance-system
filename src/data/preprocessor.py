import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class CSVProcessor:
    """Process and validate CSV files for email compliance system"""
    
    @staticmethod
    def validate_columns(df: pd.DataFrame, required_columns: List[str]) -> bool:
        """
        Validate that DataFrame contains required columns
        
        Args:
            df: DataFrame to validate
            required_columns: List of required column names
            
        Returns:
            bool: True if all columns present
            
        Raises:
            ValueError: If columns are missing
        """
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
        return True
    
    @staticmethod
    def load_sample_data(file_path: str) -> pd.DataFrame:
        """
        Load and validate sample training data
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            pd.DataFrame: Validated DataFrame
        """
        required_columns = ['Date', 'From', 'To', 'Subject', 'Body', 'Classification', 'Category']
        
        try:
            df = pd.read_csv(file_path)
            CSVProcessor.validate_columns(df, required_columns)
            
            logger.info(f"Loaded {len(df)} sample emails from {file_path}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading sample data: {e}")
            raise
    
    @staticmethod
    def load_test_data(file_path: str) -> pd.DataFrame:
        """
        Load and validate test data
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            pd.DataFrame: Validated DataFrame
        """
        required_columns = ['Date', 'From', 'To', 'Subject', 'Body']
        
        try:
            df = pd.read_csv(file_path)
            CSVProcessor.validate_columns(df, required_columns)
            
            logger.info(f"Loaded {len(df)} test emails from {file_path}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading test data: {e}")
            raise
    
    @staticmethod
    def clean_email_body(text: str) -> str:
        """
        Clean email body text
        
        Args:
            text: Raw email body
            
        Returns:
            str: Cleaned text
        """
        if pd.isna(text):
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters that might cause issues
        text = text.replace('\r\n', ' ').replace('\n', ' ').replace('\t', ' ')
        
        return text.strip()
    
    @staticmethod
    def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess DataFrame (clean text, handle missing values, etc.)
        
        Args:
            df: Input DataFrame
            
        Returns:
            pd.DataFrame: Preprocessed DataFrame
        """
        df = df.copy()
        
        # Clean email bodies
        if 'Body' in df.columns:
            df['Body'] = df['Body'].apply(CSVProcessor.clean_email_body)
        
        # Clean subjects
        if 'Subject' in df.columns:
            df['Subject'] = df['Subject'].fillna('No Subject')
            df['Subject'] = df['Subject'].apply(lambda x: ' '.join(str(x).split()))
        
        # Ensure dates are valid
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Handle missing classifications
        if 'Classification' in df.columns:
            df['Classification'] = df['Classification'].fillna('Compliant')
        
        if 'Category' in df.columns:
            df['Category'] = df['Category'].fillna('Compliant')
        
        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates(subset=['From', 'To', 'Subject', 'Body'], keep='first')
        removed_count = initial_count - len(df)
        
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate emails")
        
        return df
    
    @staticmethod
    def save_results(df: pd.DataFrame, output_path: str) -> None:
        """
        Save results to CSV
        
        Args:
            df: DataFrame to save
            output_path: Output file path
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_csv(output_path, index=False)
            logger.info(f"Results saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            raise
    
    @staticmethod
    def get_data_statistics(df: pd.DataFrame) -> Dict:
        """
        Get statistics about the dataset
        
        Args:
            df: Input DataFrame
            
        Returns:
            dict: Statistics dictionary
        """
        stats = {
            'total_emails': len(df),
            'unique_senders': df['From'].nunique() if 'From' in df.columns else 0,
            'unique_receivers': df['To'].nunique() if 'To' in df.columns else 0,
            'date_range': None,
        }
        
        if 'Date' in df.columns:
            try:
                dates = pd.to_datetime(df['Date'], errors='coerce')
                stats['date_range'] = {
                    'start': dates.min(),
                    'end': dates.max()
                }
            except:
                pass
        
        if 'Classification' in df.columns:
            stats['compliant'] = len(df[df['Classification'] == 'compliant'])
            stats['non_compliant'] = len(df[df['Classification'] == 'non-compliant'])
            stats['compliance_ratio'] = stats['compliant'] / stats['total_emails'] if stats['total_emails'] > 0 else 0
        
        if 'Category' in df.columns:
            stats['categories'] = df[df['Classification'] == 'non-compliant']['Category'].value_counts().to_dict()
        
        return stats
    
    @staticmethod
    def merge_datasets(dfs: List[pd.DataFrame], output_path: Optional[str] = None) -> pd.DataFrame:
        """
        Merge multiple datasets
        
        Args:
            dfs: List of DataFrames to merge
            output_path: Optional path to save merged data
            
        Returns:
            pd.DataFrame: Merged DataFrame
        """
        if not dfs:
            raise ValueError("No DataFrames provided for merging")
        
        merged = pd.concat(dfs, ignore_index=True)
        merged = merged.drop_duplicates(subset=['From', 'To', 'Subject', 'Body'], keep='first')
        
        logger.info(f"Merged {len(dfs)} datasets into {len(merged)} unique emails")
        
        if output_path:
            CSVProcessor.save_results(merged, output_path)
        
        return merged


class DataValidator:
    """Validate email data quality"""
    
    @staticmethod
    def validate_email_format(email: str) -> bool:
        """Check if email has valid format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, str(email)))
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Dict[str, List]:
        """
        Validate entire DataFrame and return issues
        
        Args:
            df: DataFrame to validate
            
        Returns:
            dict: Dictionary of validation issues
        """
        issues = {
            'invalid_emails': [],
            'missing_bodies': [],
            'invalid_dates': [],
            'invalid_classifications': []
        }
        
        for idx, row in df.iterrows():
            # Check email formats
            if 'From' in df.columns and not DataValidator.validate_email_format(row['From']):
                issues['invalid_emails'].append(f"Row {idx}: Invalid 'From' email: {row['From']}")
            
            if 'To' in df.columns and not DataValidator.validate_email_format(row['To']):
                issues['invalid_emails'].append(f"Row {idx}: Invalid 'To' email: {row['To']}")
            
            # Check for empty bodies
            if 'Body' in df.columns and (pd.isna(row['Body']) or str(row['Body']).strip() == ''):
                issues['missing_bodies'].append(f"Row {idx}: Empty email body")
            
            # Check date format
            if 'Date' in df.columns:
                try:
                    pd.to_datetime(row['Date'])
                except:
                    issues['invalid_dates'].append(f"Row {idx}: Invalid date: {row['Date']}")
            
            # Check classification values
            if 'Classification' in df.columns:
                valid_classifications = ['compliant', 'non-compliant', 'Compliant', 'Non-Compliant']
                if row['Classification'] not in valid_classifications:
                    issues['invalid_classifications'].append(
                        f"Row {idx}: Invalid classification: {row['Classification']}"
                    )
        
        return issues