#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOps Foundation - ETL Pipeline
Transform loan data and load into SQL Server data warehouse

Based on ETL-dev (1).py with improvements for production use
"""

import os
import re
import logging
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import urllib.parse
from typing import Tuple, Dict, Any, Optional
from datetime import datetime
import warnings

# Suppress pandas warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataOpsETLPipeline:
    """DataOps ETL Pipeline for loan data processing"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize ETL Pipeline with configuration"""
        self.config = config
        self.engine = None
        self.acceptable_max_null = config.get('acceptable_max_null', 26)
        self.missing_threshold = config.get('missing_threshold', 30.0)
        
        # Initialize database connection
        self._init_database_connection()
        
    def _init_database_connection(self):
        """Initialize database connection"""
        try:
            db_config = self.config['database']
            connection_string = (
                f"mssql+pymssql://{db_config['username']}:{db_config['password']}"
                f"@{db_config['server']}/{db_config['database']}"
            )
            self.engine = create_engine(connection_string)
            logger.info("Database connection initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise
    
    def guess_column_types(self, file_path: str, delimiter: str = ',', 
                          has_headers: bool = True) -> Tuple[bool, Dict[str, str]]:
        """
        Analyze CSV file and infer appropriate data types for each column
        
        Args:
            file_path: Path to CSV file
            delimiter: CSV delimiter
            has_headers: Whether CSV has header row
            
        Returns:
            Tuple of (success, column_types_dict or error_message)
        """
        try:
            logger.info(f"Analyzing column types for file: {file_path}")
            
            # Read CSV file
            df = pd.read_csv(
                file_path, 
                sep=delimiter, 
                low_memory=False, 
                header=0 if has_headers else None
            )
            
            column_types = {}
            
            # Loop through columns and infer data types
            for column in df.columns:
                # Check for datetime format "YYYY-MM-DD HH:MM:SS"
                is_datetime = df[column].dropna().apply(
                    lambda x: bool(re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', str(x)))
                ).all()
                
                # Check for date format "YYYY-MM-DD" 
                is_date = df[column].dropna().apply(
                    lambda x: bool(re.match(r'\d{4}-\d{2}-\d{2}', str(x)))
                ).all()
                
                # Assign data type based on format detection
                if is_datetime:
                    inferred_type = 'datetime64'
                elif is_date:
                    inferred_type = 'date'
                else:
                    inferred_type = pd.api.types.infer_dtype(df[column], skipna=True)
                
                column_types[column] = inferred_type
            
            logger.info(f"Successfully analyzed {len(column_types)} columns")
            return True, column_types
            
        except Exception as e:
            logger.error(f"Error analyzing column types: {e}")
            return False, str(e)
    
    def load_and_clean_data(self, file_path: str) -> pd.DataFrame:
        """
        Load CSV data and perform initial cleaning
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Cleaned DataFrame
        """
        logger.info(f"Loading and cleaning data from: {file_path}")
        
        # Load raw data
        raw_df = pd.read_csv(file_path, low_memory=False)
        logger.info(f"Loaded {raw_df.shape[0]} rows, {raw_df.shape[1]} columns")
        
        # Calculate missing percentage for each column
        missing_percentage = raw_df.isnull().mean() * 100
        logger.info(f"Columns with >30% missing data: {(missing_percentage > self.missing_threshold).sum()}")
        
        # Filter columns with acceptable missing data
        columns_to_keep = missing_percentage[missing_percentage <= self.missing_threshold].index.tolist()
        filtered_df = raw_df[columns_to_keep]
        
        logger.info(f"Kept {len(columns_to_keep)} columns after filtering")
        
        # Filter rows with acceptable null values
        selected_columns = [
            col for col in filtered_df.columns 
            if filtered_df[col].isnull().sum() <= self.acceptable_max_null
        ]
        
        df_selected = filtered_df[selected_columns]
        clean_df = df_selected.dropna()
        
        logger.info(f"Final clean dataset: {clean_df.shape[0]} rows, {clean_df.shape[1]} columns")
        
        return clean_df
    
    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply data transformations
        
        Args:
            df: Input DataFrame
            
        Returns:
            Transformed DataFrame
        """
        logger.info("Applying data transformations")
        
        df_transformed = df.copy()
        
        # Transform issue_d column to datetime
        if 'issue_d' in df_transformed.columns:
            df_transformed['issue_d'] = pd.to_datetime(
                df_transformed['issue_d'], 
                format='%b-%Y',
                errors='coerce'
            )
            logger.info("Converted issue_d to datetime format")
        
        # Transform int_rate column (remove % and convert to float)
        if 'int_rate' in df_transformed.columns:
            if df_transformed['int_rate'].dtype == 'object':
                df_transformed['int_rate'] = (
                    df_transformed['int_rate']
                    .astype(str)
                    .str.rstrip('%')
                    .astype('float') / 100.0
                )
                logger.info("Converted int_rate from percentage to decimal")
        
        # Add derived columns
        if 'issue_d' in df_transformed.columns:
            df_transformed['issue_year'] = df_transformed['issue_d'].dt.year
            df_transformed['issue_month'] = df_transformed['issue_d'].dt.month
            df_transformed['issue_quarter'] = df_transformed['issue_d'].dt.quarter
        
        # Convert data types for SQL Server compatibility
        for col in df_transformed.columns:
            if df_transformed[col].dtype == 'object':
                # Ensure string columns are properly encoded
                df_transformed[col] = df_transformed[col].astype(str)
            elif df_transformed[col].dtype == 'int64':
                # Convert to int32 for SQL Server compatibility
                df_transformed[col] = df_transformed[col].astype('int32')
        
        logger.info("Data transformations completed")
        return df_transformed
    
    def create_dimension_tables(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Create dimension tables for data warehouse
        
        Args:
            df: Source DataFrame
            
        Returns:
            Dictionary of dimension tables
        """
        logger.info("Creating dimension tables")
        
        dimension_tables = {}
        
        # Home Ownership Dimension
        if 'home_ownership' in df.columns:
            home_ownership_dim = (
                df[['home_ownership']]
                .drop_duplicates()
                .reset_index(drop=True)
            )
            home_ownership_dim['home_ownership_id'] = home_ownership_dim.index
            dimension_tables['home_ownership_dim'] = home_ownership_dim
            logger.info(f"Created home_ownership_dim with {len(home_ownership_dim)} records")
        
        # Loan Status Dimension
        if 'loan_status' in df.columns:
            loan_status_dim = (
                df[['loan_status']]
                .drop_duplicates()
                .reset_index(drop=True)
            )
            loan_status_dim['loan_status_id'] = loan_status_dim.index
            dimension_tables['loan_status_dim'] = loan_status_dim
            logger.info(f"Created loan_status_dim with {len(loan_status_dim)} records")
        
        # Date Dimension
        if 'issue_d' in df.columns:
            issue_d_dim = (
                df[['issue_d']]
                .drop_duplicates()
                .reset_index(drop=True)
            )
            issue_d_dim['month'] = issue_d_dim['issue_d'].dt.month
            issue_d_dim['year'] = issue_d_dim['issue_d'].dt.year
            issue_d_dim['quarter'] = issue_d_dim['issue_d'].dt.quarter
            issue_d_dim['month_name'] = issue_d_dim['issue_d'].dt.strftime('%B')
            issue_d_dim['day_of_week'] = issue_d_dim['issue_d'].dt.dayofweek
            issue_d_dim['issue_d_id'] = issue_d_dim.index
            dimension_tables['issue_d_dim'] = issue_d_dim
            logger.info(f"Created issue_d_dim with {len(issue_d_dim)} records")
        
        return dimension_tables
    
    def create_fact_table(self, df: pd.DataFrame, 
                         dimension_tables: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Create fact table with foreign key relationships
        
        Args:
            df: Source DataFrame
            dimension_tables: Dictionary of dimension tables
            
        Returns:
            Fact table DataFrame
        """
        logger.info("Creating fact table")
        
        fact_df = df.copy()
        
        # Create mapping dictionaries for foreign keys
        mappings = {}
        
        if 'home_ownership_dim' in dimension_tables:
            mappings['home_ownership'] = (
                dimension_tables['home_ownership_dim']
                .set_index('home_ownership')['home_ownership_id']
                .to_dict()
            )
        
        if 'loan_status_dim' in dimension_tables:
            mappings['loan_status'] = (
                dimension_tables['loan_status_dim']
                .set_index('loan_status')['loan_status_id']
                .to_dict()
            )
        
        if 'issue_d_dim' in dimension_tables:
            mappings['issue_d'] = (
                dimension_tables['issue_d_dim']
                .set_index('issue_d')['issue_d_id']
                .to_dict()
            )
        
        # Apply mappings to create foreign keys
        for column, mapping in mappings.items():
            if column in fact_df.columns:
                fact_df[f"{column}_id"] = fact_df[column].map(mapping)
                logger.info(f"Created foreign key {column}_id")
        
        # Select fact table columns
        fact_columns = [
            'application_type', 'loan_amnt', 'funded_amnt', 'term', 
            'int_rate', 'installment'
        ]
        
        # Add foreign key columns
        foreign_keys = [col for col in fact_df.columns if col.endswith('_id')]
        fact_columns.extend(foreign_keys)
        
        # Filter to only include available columns
        available_columns = [col for col in fact_columns if col in fact_df.columns]
        
        loans_fact = fact_df[available_columns]
        
        logger.info(f"Created fact table with {len(loans_fact)} records and {len(available_columns)} columns")
        
        return loans_fact
    
    def load_to_database(self, dimension_tables: Dict[str, pd.DataFrame], 
                        fact_table: pd.DataFrame) -> bool:
        """
        Load dimension and fact tables to SQL Server
        
        Args:
            dimension_tables: Dictionary of dimension tables
            fact_table: Fact table DataFrame
            
        Returns:
            Success status
        """
        try:
            logger.info("Loading tables to database")
            
            # Load dimension tables
            for table_name, df in dimension_tables.items():
                df.to_sql(
                    table_name,
                    con=self.engine,
                    if_exists='replace',
                    index=False,
                    method='multi'
                )
                logger.info(f"Loaded {table_name} with {len(df)} records")
            
            # Load fact table
            fact_table.to_sql(
                'loans_fact',
                con=self.engine,
                if_exists='replace',
                index=False,
                method='multi'
            )
            logger.info(f"Loaded loans_fact with {len(fact_table)} records")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading data to database: {e}")
            return False
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform data quality checks
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Data quality report
        """
        logger.info("Performing data quality validation")
        
        report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'data_types': df.dtypes.to_dict(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Check for negative values in amount columns
        amount_columns = ['loan_amnt', 'funded_amnt', 'installment']
        for col in amount_columns:
            if col in df.columns:
                negative_count = (df[col] < 0).sum()
                report[f'{col}_negative_values'] = negative_count
        
        # Check interest rate range
        if 'int_rate' in df.columns:
            report['int_rate_range'] = {
                'min': df['int_rate'].min(),
                'max': df['int_rate'].max(),
                'mean': df['int_rate'].mean()
            }
        
        logger.info(f"Data quality validation completed. Total rows: {report['total_rows']}")
        
        return report
    
    def run_etl_pipeline(self, input_file: str) -> bool:
        """
        Execute the complete ETL pipeline
        
        Args:
            input_file: Path to input CSV file
            
        Returns:
            Success status
        """
        try:
            logger.info("Starting ETL pipeline execution")
            start_time = datetime.now()
            
            # Step 1: Load and clean data
            clean_df = self.load_and_clean_data(input_file)
            
            # Step 2: Transform data
            transformed_df = self.transform_data(clean_df)
            
            # Step 3: Data quality validation
            quality_report = self.validate_data_quality(transformed_df)
            
            # Step 4: Create dimension tables
            dimension_tables = self.create_dimension_tables(transformed_df)
            
            # Step 5: Create fact table
            fact_table = self.create_fact_table(transformed_df, dimension_tables)
            
            # Step 6: Load to database
            success = self.load_to_database(dimension_tables, fact_table)
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            if success:
                logger.info(f"ETL pipeline completed successfully in {duration}")
                logger.info(f"Data quality summary: {quality_report['total_rows']} rows, "
                          f"{quality_report['total_columns']} columns processed")
            else:
                logger.error("ETL pipeline failed during database loading")
            
            return success
            
        except Exception as e:
            logger.error(f"ETL pipeline failed: {e}")
            return False


def main():
    """Main execution function"""
    
    # Configuration
    config = {
        'database': {
            'server': '35.185.131.47',
            'database': 'TestDB',
            'username': 'SA',
            'password': 'Passw0rd123456'
        },
        'acceptable_max_null': 26,
        'missing_threshold': 30.0
    }
    
    # Input file path - update this as needed
    input_file = 'LoanStats_web_14422.csv'
    
    if not os.path.exists(input_file):
        logger.error(f"Input file not found: {input_file}")
        return False
    
    # Initialize and run ETL pipeline
    etl = DataOpsETLPipeline(config)
    success = etl.run_etl_pipeline(input_file)
    
    if success:
        logger.info("DataOps ETL Pipeline completed successfully!")
        return True
    else:
        logger.error("DataOps ETL Pipeline failed!")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
