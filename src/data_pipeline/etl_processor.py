#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOps Foundation - Enhanced ETL Processor
ตัวประมวลผล ETL ขั้นสูงที่รวมโค้ดจาก ETL-dev (1).py และปรับปรุงเพิ่มเติม

Features:
- Column type inference and validation
- Data quality checks and filtering
- Dimensional modeling (Star Schema)
- Database integration with error handling
- Monitoring and logging
- Configurable processing parameters
"""

import re
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from sqlalchemy import create_engine
import urllib.parse
import yaml
import os
from dataclasses import dataclass

# Import internal modules
try:
    from ..utils.logger import setup_logger
    from ..utils.config_manager import ConfigManager
    from ..data_quality.quality_checker import DataQualityChecker
    from ..monitoring.metrics_collector import MetricsCollector
except ImportError:
    # Fallback for standalone execution
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class ProcessingResult:
    """ผลลัพธ์การประมวลผล ETL"""
    success: bool
    processed_records: int
    quality_score: float
    processing_time: float
    errors: List[str]
    metadata: Dict[str, Any]


class ETLProcessor:
    """
    Enhanced ETL Processor ที่รวมฟีเจอร์จาก ETL-dev (1).py
    และเพิ่มการจัดการ error, logging, และ monitoring
    """
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """เริ่มต้น ETL Processor"""
        # Setup basic logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize config
        self.config = self._load_config(config_path)
        
        # Data containers
        self.raw_df = None
        self.processed_df = None
        self.column_types = {}
        self.dimension_tables = {}
        self.fact_table = None
        
        # Processing parameters from original ETL-dev (1).py
        self.max_null_percentage = self.config.get('data_quality', {}).get('max_null_percentage', 30.0)
        self.acceptable_max_null = self.config.get('data_quality', {}).get('acceptable_max_null', 26)
        
        self.logger.info("ETL Processor initialized successfully")
    
    def _load_config(self, config_path: str) -> dict:
        """โหลดการตั้งค่าจากไฟล์ YAML"""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as file:
                    return yaml.safe_load(file)
            else:
                self.logger.warning(f"Config file not found: {config_path}. Using defaults.")
                return {}
        except Exception as e:
            self.logger.warning(f"Error loading config: {e}. Using defaults.")
            return {}
    
    def guess_column_types(self, file_path: str, delimiter: str = ',', 
                          has_headers: bool = True) -> Tuple[bool, Dict[str, str]]:
        """
        อนุมานประเภทข้อมูลของคอลัมน์ (จากโค้ดเดิม ETL-dev (1).py)
        """
        try:
            self.logger.info(f"Starting column type inference for: {file_path}")
            
            # Read the CSV file using the specified delimiter and header settings
            df = pd.read_csv(file_path, sep=delimiter, low_memory=False, 
                           header=0 if has_headers else None)
            
            # Initialize a dictionary to store column data types
            column_types = {}
            
            # Loop through columns and infer data types
            for column in df.columns:
                # Check for datetime format "YYYY-MM-DD HH:MM:SS"
                is_datetime = all(
                    re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', str(value)) 
                    for value in df[column].dropna()
                )
                
                # Check for date format "YYYY-MM-DD"
                is_date = all(
                    re.match(r'\d{4}-\d{2}-\d{2}', str(value)) 
                    for value in df[column].dropna()
                )
                
                # Assign data type based on format detection
                if is_datetime:
                    inferred_type = 'datetime64'
                elif is_date:
                    inferred_type = 'date'
                else:
                    inferred_type = pd.api.types.infer_dtype(df[column], skipna=True)
                
                column_types[column] = inferred_type
            
            self.column_types = column_types
            self.logger.info(f"Column type inference completed. Found {len(column_types)} columns")
            
            return True, column_types
            
        except Exception as e:
            error_msg = f"Error in column type inference: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def load_data(self, file_path: str, **kwargs) -> ProcessingResult:
        """โหลดข้อมูลและทำการประมวลผลเบื้องต้น"""
        start_time = datetime.now()
        errors = []
        
        try:
            self.logger.info(f"Loading data from: {file_path}")
            
            # อ่านข้อมูล (จากโค้ดเดิม)
            self.raw_df = pd.read_csv(file_path, low_memory=False, **kwargs)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = ProcessingResult(
                success=True,
                processed_records=len(self.raw_df),
                quality_score=0.0,  # จะคำนวณในขั้นตอนถัดไป
                processing_time=processing_time,
                errors=errors,
                metadata={
                    'file_path': file_path,
                    'columns': list(self.raw_df.columns),
                    'shape': self.raw_df.shape
                }
            )
            
            self.logger.info(f"Data loaded successfully: {self.raw_df.shape}")
            return result
            
        except Exception as e:
            error_msg = f"Error loading data: {str(e)}"
            self.logger.error(error_msg)
            errors.append(error_msg)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                success=False,
                processed_records=0,
                quality_score=0.0,
                processing_time=processing_time,
                errors=errors,
                metadata={}
            )
    
    def filter_by_null_percentage(self, max_null_percentage: float = None) -> ProcessingResult:
        """
        กรองคอลัมน์ที่มี null values เกินกว่าเกณฑ์ที่กำหนด
        (จากโค้ดเดิม ETL-dev (1).py)
        """
        if self.raw_df is None:
            raise ValueError("No data loaded. Please call load_data() first.")
        
        if max_null_percentage is None:
            max_null_percentage = self.max_null_percentage
        
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Filtering columns with null percentage > {max_null_percentage}%")
            
            # คำนวน percentage ของ missing values ของแต่ละ col. ใน dataframe (raw_df)
            missing_percentage = self.raw_df.isnull().mean() * 100
            
            # กรอง columns ที่มี null เกินกว่า threshold ออกไป
            columns_to_keep = missing_percentage[missing_percentage <= max_null_percentage].index.tolist()
            filtered_df = self.raw_df[columns_to_keep]
            
            self.processed_df = filtered_df
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Log results
            removed_columns = len(self.raw_df.columns) - len(columns_to_keep)
            self.logger.info(f"Filtered {removed_columns} columns. Remaining: {len(columns_to_keep)}")
            
            return ProcessingResult(
                success=True,
                processed_records=len(filtered_df),
                quality_score=0.0,
                processing_time=processing_time,
                errors=[],
                metadata={
                    'removed_columns': removed_columns,
                    'remaining_columns': len(columns_to_keep),
                    'columns_kept': columns_to_keep
                }
            )
            
        except Exception as e:
            error_msg = f"Error in filtering by null percentage: {str(e)}"
            self.logger.error(error_msg)
            return ProcessingResult(
                success=False,
                processed_records=0,
                quality_score=0.0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                errors=[error_msg],
                metadata={}
            )
    
    def filter_by_row_completeness(self, acceptable_max_null: int = None) -> ProcessingResult:
        """
        กรองแถวที่มีข้อมูลครบถ้วนตามเกณฑ์
        (จากโค้ดเดิม ETL-dev (1).py)
        """
        if self.processed_df is None:
            raise ValueError("No processed data found. Please run filter_by_null_percentage() first.")
        
        if acceptable_max_null is None:
            acceptable_max_null = self.acceptable_max_null
        
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Filtering rows with null count <= {acceptable_max_null}")
            
            # สร้างรายการของคอลัมน์ที่มี null values <= threshold
            selected_columns = [
                col for col in self.processed_df.columns 
                if self.processed_df[col].isnull().sum() <= acceptable_max_null
            ]
            
            # สร้าง DataFrame ใหม่จากคอลัมน์ที่เลือก
            df_selected = self.processed_df[selected_columns]
            
            # ลบแถวที่มีค่า null ในคอลัมน์เหล่านั้น
            no_null_df = df_selected.dropna()
            
            self.processed_df = no_null_df
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"Row filtering completed. Final shape: {no_null_df.shape}")
            
            return ProcessingResult(
                success=True,
                processed_records=len(no_null_df),
                quality_score=0.0,
                processing_time=processing_time,
                errors=[],
                metadata={
                    'selected_columns': len(selected_columns),
                    'final_shape': no_null_df.shape,
                    'selected_column_names': selected_columns
                }
            )
            
        except Exception as e:
            error_msg = f"Error in row completeness filtering: {str(e)}"
            self.logger.error(error_msg)
            return ProcessingResult(
                success=False,
                processed_records=0,
                quality_score=0.0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                errors=[error_msg],
                metadata={}
            )
    
    def apply_data_transformations(self) -> ProcessingResult:
        """
        ใช้การแปลงข้อมูลพิเศษ 
        (จากโค้ดเดิม ETL-dev (1).py)
        """
        if self.processed_df is None:
            raise ValueError("No processed data found.")
        
        start_time = datetime.now()
        
        try:
            self.logger.info("Applying data transformations")
            
            # ทำสำเนาตัวแปร
            df_prepared = self.processed_df.copy()
            
            # เปลี่ยน data type เป็น datetime สำหรับ col: issue_d
            if 'issue_d' in df_prepared.columns:
                df_prepared['issue_d'] = pd.to_datetime(df_prepared['issue_d'], format='%b-%Y')
                self.logger.info("Converted issue_d to datetime")
            
            # นำเครื่องหมาย % ออกจากค่าใน col: int_rate แล้วเปลี่ยน data type เป็น float
            if 'int_rate' in df_prepared.columns:
                if df_prepared['int_rate'].dtype == 'object':
                    df_prepared['int_rate'] = (
                        df_prepared['int_rate'].str.rstrip('%').astype('float') / 100.0
                    )
                    self.logger.info("Converted int_rate from percentage string to float")
            
            self.processed_df = df_prepared
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                success=True,
                processed_records=len(df_prepared),
                quality_score=0.0,
                processing_time=processing_time,
                errors=[],
                metadata={
                    'transformations_applied': ['issue_d_datetime', 'int_rate_percentage']
                }
            )
            
        except Exception as e:
            error_msg = f"Error in data transformations: {str(e)}"
            self.logger.error(error_msg)
            return ProcessingResult(
                success=False,
                processed_records=0,
                quality_score=0.0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                errors=[error_msg],
                metadata={}
            )
    
    def create_dimensional_model(self) -> ProcessingResult:
        """
        สร้าง dimensional model (Star Schema) จากข้อมูล
        (จากโค้ดเดิม ETL-dev (1).py)
        """
        if self.processed_df is None:
            raise ValueError("No processed data found.")
        
        start_time = datetime.now()
        
        try:
            self.logger.info("Creating dimensional model")
            
            dimension_tables = {}
            
            # ทำข้อ (1) สำหรับ home_ownership
            if 'home_ownership' in self.processed_df.columns:
                home_ownership_dim = (
                    self.processed_df[['home_ownership']]
                    .drop_duplicates()
                    .reset_index(drop=True)
                )
                # ทำข้อ (2) สำหรับ home_ownership
                home_ownership_dim['home_ownership_id'] = home_ownership_dim.index
                dimension_tables['home_ownership'] = home_ownership_dim
                self.logger.info(f"Created home_ownership dimension: {len(home_ownership_dim)} records")
            
            # ทำข้อ (1) สำหรับ loan_status
            if 'loan_status' in self.processed_df.columns:
                loan_status_dim = (
                    self.processed_df[['loan_status']]
                    .drop_duplicates()
                    .reset_index(drop=True)
                )
                # ทำข้อ (2) สำหรับ loan_status
                loan_status_dim['loan_status_id'] = loan_status_dim.index
                dimension_tables['loan_status'] = loan_status_dim
                self.logger.info(f"Created loan_status dimension: {len(loan_status_dim)} records")
            
            # ทำข้อ (1) สำหรับ issue_d
            if 'issue_d' in self.processed_df.columns:
                issue_d_dim = (
                    self.processed_df[['issue_d']]
                    .drop_duplicates()
                    .reset_index(drop=True)
                )
                issue_d_dim['month'] = issue_d_dim['issue_d'].dt.month
                issue_d_dim['year'] = issue_d_dim['issue_d'].dt.year
                # ทำข้อ (2) สำหรับ issue_d
                issue_d_dim['issue_d_id'] = issue_d_dim.index
                dimension_tables['issue_d'] = issue_d_dim
                self.logger.info(f"Created issue_d dimension: {len(issue_d_dim)} records")
            
            self.dimension_tables = dimension_tables
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                success=True,
                processed_records=sum(len(dim) for dim in dimension_tables.values()),
                quality_score=0.0,
                processing_time=processing_time,
                errors=[],
                metadata={
                    'dimensions_created': list(dimension_tables.keys()),
                    'dimension_sizes': {k: len(v) for k, v in dimension_tables.items()}
                }
            )
            
        except Exception as e:
            error_msg = f"Error creating dimensional model: {str(e)}"
            self.logger.error(error_msg)
            return ProcessingResult(
                success=False,
                processed_records=0,
                quality_score=0.0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                errors=[error_msg],
                metadata={}
            )
    
    def create_fact_table(self) -> ProcessingResult:
        """
        สร้าง fact table พร้อม foreign keys
        (จากโค้ดเดิม ETL-dev (1).py)
        """
        if self.processed_df is None or not self.dimension_tables:
            raise ValueError("Missing processed data or dimension tables.")
        
        start_time = datetime.now()
        
        try:
            self.logger.info("Creating fact table")
            
            # ทำข้อ (1) - สร้าง python's dict. ขึ้นมาใช้ key mapping
            mappings = {}
            
            if 'home_ownership' in self.dimension_tables:
                home_ownership_map = (
                    self.dimension_tables['home_ownership']
                    .set_index('home_ownership')['home_ownership_id']
                    .to_dict()
                )
                mappings['home_ownership'] = home_ownership_map
            
            if 'loan_status' in self.dimension_tables:
                loan_status_map = (
                    self.dimension_tables['loan_status']
                    .set_index('loan_status')['loan_status_id']
                    .to_dict()
                )
                mappings['loan_status'] = loan_status_map
            
            if 'issue_d' in self.dimension_tables:
                issue_d_map = (
                    self.dimension_tables['issue_d']
                    .set_index('issue_d')['issue_d_id']
                    .to_dict()
                )
                mappings['issue_d'] = issue_d_map
            
            # ทำข้อ (2) - สร้าง fact table
            loans_fact = self.processed_df.copy()
            
            # Map foreign keys
            if 'home_ownership' in mappings:
                loans_fact['home_ownership_id'] = loans_fact['home_ownership'].map(mappings['home_ownership'])
            
            if 'loan_status' in mappings:
                loans_fact['loan_status_id'] = loans_fact['loan_status'].map(mappings['loan_status'])
            
            if 'issue_d' in mappings:
                loans_fact['issue_d_id'] = loans_fact['issue_d'].map(mappings['issue_d'])
            
            # เลือกคอลัมน์ที่จำเป็นสำหรับ Fact Table
            fact_columns = ['application_type', 'loan_amnt', 'funded_amnt', 'term', 
                          'int_rate', 'installment']
            
            # เพิ่ม foreign key columns
            if 'home_ownership_id' in loans_fact.columns:
                fact_columns.append('home_ownership_id')
            if 'loan_status_id' in loans_fact.columns:
                fact_columns.append('loan_status_id')
            if 'issue_d_id' in loans_fact.columns:
                fact_columns.append('issue_d_id')
            
            # กรองเฉพาะคอลัมน์ที่มีจริง
            available_columns = [col for col in fact_columns if col in loans_fact.columns]
            loans_fact = loans_fact[available_columns]
            
            self.fact_table = loans_fact
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"Fact table created with {len(loans_fact)} records and {len(available_columns)} columns")
            
            return ProcessingResult(
                success=True,
                processed_records=len(loans_fact),
                quality_score=0.0,
                processing_time=processing_time,
                errors=[],
                metadata={
                    'fact_table_columns': available_columns,
                    'fact_table_shape': loans_fact.shape,
                    'foreign_keys_mapped': list(mappings.keys())
                }
            )
            
        except Exception as e:
            error_msg = f"Error creating fact table: {str(e)}"
            self.logger.error(error_msg)
            return ProcessingResult(
                success=False,
                processed_records=0,
                quality_score=0.0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                errors=[error_msg],
                metadata={}
            )
    
    def save_to_database(self, server: str = None, database: str = None, 
                        username: str = None, password: str = None) -> ProcessingResult:
        """
        บันทึกข้อมูลลงฐานข้อมูล MSSQL
        (จากโค้ดเดิม ETL-dev (1).py)
        """
        if not self.dimension_tables or self.fact_table is None:
            raise ValueError("Missing dimension tables or fact table.")
        
        start_time = datetime.now()
        
        # ใช้ค่าจาก config หรือ parameter
        server = server or self.config.get('database', {}).get('primary', {}).get('host', '35.185.131.47')
        database = database or self.config.get('database', {}).get('primary', {}).get('database', 'TestDB')
        username = username or self.config.get('database', {}).get('primary', {}).get('username', 'SA')
        password = password or self.config.get('database', {}).get('primary', {}).get('password', 'Passw0rd123456')
        
        try:
            self.logger.info(f"Connecting to database: {server}/{database}")
            
            # Using pymssql (จากโค้ดเดิม)
            engine = create_engine(f'mssql+pymssql://{username}:{password}@{server}/{database}')
            
            # นำเข้าข้อมูล Dimension Tables ไปยัง MSSQL
            for dim_name, dim_df in self.dimension_tables.items():
                table_name = f'{dim_name}_dim'
                dim_df.to_sql(table_name, con=engine, if_exists='replace', index=False)
                self.logger.info(f"Saved {dim_name} dimension table: {len(dim_df)} records")
            
            # นำเข้าข้อมูล Fact Table ไปยัง MSSQL
            self.fact_table.to_sql('loans_fact', con=engine, if_exists='replace', index=False)
            self.logger.info(f"Saved fact table: {len(self.fact_table)} records")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                success=True,
                processed_records=len(self.fact_table) + sum(len(dim) for dim in self.dimension_tables.values()),
                quality_score=0.0,
                processing_time=processing_time,
                errors=[],
                metadata={
                    'database_server': server,
                    'database_name': database,
                    'tables_created': ['loans_fact'] + [f'{name}_dim' for name in self.dimension_tables.keys()]
                }
            )
            
        except Exception as e:
            error_msg = f"Error saving to database: {str(e)}"
            self.logger.error(error_msg)
            return ProcessingResult(
                success=False,
                processed_records=0,
                quality_score=0.0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                errors=[error_msg],
                metadata={}
            )
    
    def run_full_pipeline(self, file_path: str, **kwargs) -> ProcessingResult:
        """รันขั้นตอนการประมวลผล ETL ทั้งหมด"""
        self.logger.info("Starting full ETL pipeline")
        overall_start_time = datetime.now()
        
        try:
            # 1. Load data
            result = self.load_data(file_path, **kwargs)
            if not result.success:
                return result
            
            # 2. Infer column types
            success, column_types = self.guess_column_types(file_path)
            if not success:
                return ProcessingResult(
                    success=False,
                    processed_records=0,
                    quality_score=0.0,
                    processing_time=0.0,
                    errors=[column_types],
                    metadata={}
                )
            
            # 3. Filter by null percentage
            result = self.filter_by_null_percentage()
            if not result.success:
                return result
            
            # 4. Filter by row completeness
            result = self.filter_by_row_completeness()
            if not result.success:
                return result
            
            # 5. Apply transformations
            result = self.apply_data_transformations()
            if not result.success:
                return result
            
            # 6. Create dimensional model
            result = self.create_dimensional_model()
            if not result.success:
                return result
            
            # 7. Create fact table
            result = self.create_fact_table()
            if not result.success:
                return result
            
            # 8. Save to database
            result = self.save_to_database()
            if not result.success:
                return result
            
            total_time = (datetime.now() - overall_start_time).total_seconds()
            
            self.logger.info(f"Full ETL pipeline completed successfully in {total_time:.2f} seconds")
            
            return ProcessingResult(
                success=True,
                processed_records=len(self.fact_table) if self.fact_table is not None else 0,
                quality_score=100.0,  # Assume success = 100% quality
                processing_time=total_time,
                errors=[],
                metadata={
                    'pipeline_completed': True,
                    'final_fact_table_shape': self.fact_table.shape if self.fact_table is not None else (0, 0),
                    'dimensions_created': list(self.dimension_tables.keys())
                }
            )
            
        except Exception as e:
            error_msg = f"Error in full pipeline: {str(e)}"
            self.logger.error(error_msg)
            return ProcessingResult(
                success=False,
                processed_records=0,
                quality_score=0.0,
                processing_time=(datetime.now() - overall_start_time).total_seconds(),
                errors=[error_msg],
                metadata={}
            )


def main():
    """ตัวอย่างการใช้งาน ETL Processor"""
    print("=== DataOps Foundation ETL Processor ===")
    print("Enhanced version of ETL-dev (1).py")
    
    processor = ETLProcessor()
    
    # ตัวอย่างการใช้งาน
    file_path = 'examples/sample_data/LoanStats_web_14422.csv'
    
    if os.path.exists(file_path):
        result = processor.run_full_pipeline(file_path)
        
        if result.success:
            print(f"✅ ETL Pipeline completed successfully!")
            print(f"📊 Processed {result.processed_records} records")
            print(f"⏱️  Processing time: {result.processing_time:.2f} seconds")
            print(f"🎯 Quality score: {result.quality_score}%")
        else:
            print(f"❌ ETL Pipeline failed!")
            for error in result.errors:
                print(f"   Error: {error}")
    else:
        print(f"⚠️  Sample data file not found: {file_path}")
        print("   Please add sample data to test the processor.")


if __name__ == "__main__":
    main()
