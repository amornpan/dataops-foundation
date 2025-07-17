#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOps Foundation - Sample Data Generator
สร้างข้อมูลตัวอย่างสำหรับการทดสอบ ETL pipeline

Features:
- Generate realistic loan data similar to ETL-dev (1).py
- Configurable data size and quality
- Various data types and formats
- Intentional data quality issues for testing
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
import logging
from faker import Faker


def generate_loan_data(num_records: int = 1000, output_file: str = None) -> pd.DataFrame:
    """
    สร้างข้อมูลเงินกู้ตัวอย่าง (คล้ายกับ LoanStats_web_14422.csv)
    จาก ETL-dev (1).py
    """
    
    # Initialize Faker
    fake = Faker()
    
    # Set random seed for reproducibility
    np.random.seed(42)
    random.seed(42)
    
    print(f"🏭 Generating {num_records:,} loan records...")
    
    # Define data generation parameters
    loan_purposes = [
        'debt_consolidation', 'credit_card', 'home_improvement', 'other',
        'major_purchase', 'medical', 'small_business', 'car', 'vacation',
        'moving', 'wedding', 'renewable_energy', 'educational'
    ]
    
    home_ownership_types = ['RENT', 'OWN', 'MORTGAGE', 'OTHER']
    
    loan_statuses = [
        'Fully Paid', 'Current', 'Charged Off', 'Late (31-120 days)',
        'In Grace Period', 'Late (16-30 days)', 'Default'
    ]
    
    application_types = ['Individual', 'Joint App']
    
    employment_lengths = [
        '< 1 year', '1 year', '2 years', '3 years', '4 years', '5 years',
        '6 years', '7 years', '8 years', '9 years', '10+ years'
    ]
    
    verification_statuses = ['Verified', 'Source Verified', 'Not Verified']
    
    # Generate data
    data = []
    
    for i in range(num_records):
        # Basic loan information
        loan_amnt = np.random.normal(15000, 8000)
        loan_amnt = max(1000, min(40000, loan_amnt))  # Limit range
        
        funded_amnt = loan_amnt * np.random.uniform(0.95, 1.0)
        
        # Interest rate (with some percentage format)
        int_rate = np.random.normal(12.5, 4.0)
        int_rate = max(5.0, min(30.0, int_rate))
        
        # Term (36 or 60 months)
        term = np.random.choice([36, 60], p=[0.7, 0.3])
        
        # Calculate installment
        monthly_rate = int_rate / 100 / 12
        installment = (loan_amnt * monthly_rate * (1 + monthly_rate)**term) / ((1 + monthly_rate)**term - 1)
        
        # Issue date (random date in last 2 years)
        issue_date = fake.date_between(start_date='-2y', end_date='today')
        
        # Personal information
        annual_inc = np.random.lognormal(10.5, 0.8)
        annual_inc = max(20000, min(300000, annual_inc))
        
        # Introduce some data quality issues
        home_ownership = np.random.choice(home_ownership_types)
        if np.random.random() < 0.05:  # 5% chance of null
            home_ownership = None
        
        # Employment length
        emp_length = np.random.choice(employment_lengths)
        if np.random.random() < 0.08:  # 8% chance of null
            emp_length = None
        
        # Verification status
        verification_status = np.random.choice(verification_statuses)
        
        # Loan status
        loan_status = np.random.choice(loan_statuses, p=[0.6, 0.15, 0.15, 0.05, 0.02, 0.02, 0.01])
        
        # Application type
        application_type = np.random.choice(application_types, p=[0.85, 0.15])
        
        # Credit information
        dti = np.random.normal(15, 8)
        dti = max(0, min(40, dti))
        
        # Address information
        addr_state = fake.state_abbr()
        zip_code = fake.postcode()
        
        # Some additional fields that might have missing values
        desc = fake.text(max_nb_chars=200) if np.random.random() < 0.3 else None
        title = fake.job() if np.random.random() < 0.7 else None
        
        # Create record
        record = {
            'loan_amnt': round(loan_amnt, 2),
            'funded_amnt': round(funded_amnt, 2),
            'funded_amnt_inv': round(funded_amnt * np.random.uniform(0.9, 1.0), 2),
            'term': f" {term} months",
            'int_rate': f"{int_rate:.2f}%",
            'installment': round(installment, 2),
            'grade': np.random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G'], p=[0.1, 0.2, 0.3, 0.2, 0.1, 0.05, 0.05]),
            'sub_grade': np.random.choice(['A1', 'A2', 'A3', 'A4', 'A5', 'B1', 'B2', 'B3', 'B4', 'B5']),
            'emp_title': fake.job() if np.random.random() < 0.8 else None,
            'emp_length': emp_length,
            'home_ownership': home_ownership,
            'annual_inc': round(annual_inc, 2),
            'verification_status': verification_status,
            'issue_d': issue_date.strftime('%b-%Y'),
            'loan_status': loan_status,
            'purpose': np.random.choice(loan_purposes),
            'title': title,
            'zip_code': zip_code,
            'addr_state': addr_state,
            'dti': round(dti, 2),
            'earliest_cr_line': fake.date_between(start_date='-20y', end_date='-5y').strftime('%b-%Y'),
            'open_acc': np.random.randint(3, 25),
            'pub_rec': np.random.randint(0, 3),
            'revol_bal': np.random.randint(0, 50000),
            'revol_util': round(np.random.uniform(0, 100), 1) if np.random.random() < 0.9 else None,
            'total_acc': np.random.randint(5, 50),
            'application_type': application_type,
            'mort_acc': np.random.randint(0, 10) if np.random.random() < 0.6 else None,
            'pub_rec_bankruptcies': np.random.randint(0, 2) if np.random.random() < 0.1 else None,
            'desc': desc,
            'url': f"https://www.lendingclub.com/browse/loanDetail.action?loan_id={fake.uuid4()}",
            'member_id': fake.uuid4(),
            'policy_code': 1,
            'initial_list_status': np.random.choice(['w', 'f']),
            'out_prncp': round(np.random.uniform(0, loan_amnt * 0.5), 2),
            'out_prncp_inv': round(np.random.uniform(0, loan_amnt * 0.5), 2),
            'total_pymnt': round(np.random.uniform(0, loan_amnt * 1.2), 2),
            'total_pymnt_inv': round(np.random.uniform(0, loan_amnt * 1.2), 2),
            'total_rec_prncp': round(np.random.uniform(0, loan_amnt), 2),
            'total_rec_int': round(np.random.uniform(0, loan_amnt * 0.3), 2),
            'total_rec_late_fee': round(np.random.uniform(0, 100), 2),
            'recoveries': round(np.random.uniform(0, 1000), 2),
            'collection_recovery_fee': round(np.random.uniform(0, 100), 2),
            'last_pymnt_d': fake.date_between(start_date='-1y', end_date='today').strftime('%b-%Y') if np.random.random() < 0.8 else None,
            'last_pymnt_amnt': round(np.random.uniform(0, installment * 2), 2),
            'next_pymnt_d': fake.date_between(start_date='today', end_date='+1y').strftime('%b-%Y') if np.random.random() < 0.7 else None,
            'last_credit_pull_d': fake.date_between(start_date='-1y', end_date='today').strftime('%b-%Y') if np.random.random() < 0.8 else None,
            'collections_12_mths_ex_med': np.random.randint(0, 3) if np.random.random() < 0.1 else None,
            'mths_since_last_major_derog': np.random.randint(1, 120) if np.random.random() < 0.2 else None,
            'acc_now_delinq': np.random.randint(0, 3),
            'tot_coll_amt': np.random.randint(0, 10000) if np.random.random() < 0.3 else None,
            'tot_cur_bal': np.random.randint(0, 100000) if np.random.random() < 0.8 else None,
            'open_acc_6m': np.random.randint(0, 5) if np.random.random() < 0.7 else None,
            'open_il_6m': np.random.randint(0, 5) if np.random.random() < 0.7 else None,
            'open_il_12m': np.random.randint(0, 10) if np.random.random() < 0.7 else None,
            'open_il_24m': np.random.randint(0, 15) if np.random.random() < 0.7 else None,
            'mths_since_rcnt_il': np.random.randint(1, 60) if np.random.random() < 0.8 else None,
            'total_bal_il': np.random.randint(0, 50000) if np.random.random() < 0.8 else None,
            'il_util': round(np.random.uniform(0, 100), 1) if np.random.random() < 0.6 else None,
            'open_rv_12m': np.random.randint(0, 10) if np.random.random() < 0.7 else None,
            'open_rv_24m': np.random.randint(0, 15) if np.random.random() < 0.7 else None,
            'max_bal_bc': np.random.randint(0, 20000) if np.random.random() < 0.8 else None,
            'all_util': round(np.random.uniform(0, 100), 1) if np.random.random() < 0.8 else None,
            'total_rev_hi_lim': np.random.randint(0, 100000) if np.random.random() < 0.8 else None,
            'inq_fi': np.random.randint(0, 10) if np.random.random() < 0.7 else None,
            'total_cu_tl': np.random.randint(0, 20) if np.random.random() < 0.7 else None,
            'inq_last_12m': np.random.randint(0, 20) if np.random.random() < 0.8 else None,
            'acc_open_past_24mths': np.random.randint(0, 20) if np.random.random() < 0.8 else None,
            'avg_cur_bal': np.random.randint(0, 50000) if np.random.random() < 0.8 else None,
            'bc_open_to_buy': np.random.randint(0, 50000) if np.random.random() < 0.8 else None,
            'bc_util': round(np.random.uniform(0, 100), 1) if np.random.random() < 0.8 else None,
            'chargeoff_within_12_mths': np.random.randint(0, 2) if np.random.random() < 0.1 else None,
            'delinq_amnt': np.random.randint(0, 10000) if np.random.random() < 0.1 else None,
            'mo_sin_old_il_acct': np.random.randint(1, 300) if np.random.random() < 0.8 else None,
            'mo_sin_old_rev_tl_op': np.random.randint(1, 300) if np.random.random() < 0.8 else None,
            'mo_sin_rcnt_rev_tl_op': np.random.randint(1, 60) if np.random.random() < 0.8 else None,
            'mo_sin_rcnt_tl': np.random.randint(1, 60) if np.random.random() < 0.8 else None,
            'mort_acc': np.random.randint(0, 10) if np.random.random() < 0.6 else None,
            'mths_since_recent_bc': np.random.randint(1, 120) if np.random.random() < 0.8 else None,
            'mths_since_recent_bc_dlq': np.random.randint(1, 120) if np.random.random() < 0.3 else None,
            'mths_since_recent_inq': np.random.randint(1, 24) if np.random.random() < 0.8 else None,
            'mths_since_recent_revol_delinq': np.random.randint(1, 120) if np.random.random() < 0.3 else None,
            'num_accts_ever_120_pd': np.random.randint(0, 5) if np.random.random() < 0.2 else None,
            'num_actv_bc_tl': np.random.randint(0, 20) if np.random.random() < 0.8 else None,
            'num_actv_rev_tl': np.random.randint(0, 30) if np.random.random() < 0.8 else None,
            'num_bc_sats': np.random.randint(0, 30) if np.random.random() < 0.8 else None,
            'num_bc_tl': np.random.randint(0, 40) if np.random.random() < 0.8 else None,
            'num_il_tl': np.random.randint(0, 30) if np.random.random() < 0.8 else None,
            'num_op_rev_tl': np.random.randint(0, 40) if np.random.random() < 0.8 else None,
            'num_rev_accts': np.random.randint(0, 50) if np.random.random() < 0.8 else None,
            'num_rev_tl_bal_gt_0': np.random.randint(0, 30) if np.random.random() < 0.8 else None,
            'num_sats': np.random.randint(0, 50) if np.random.random() < 0.8 else None,
            'num_tl_120dpd_2m': np.random.randint(0, 5) if np.random.random() < 0.1 else None,
            'num_tl_30dpd': np.random.randint(0, 10) if np.random.random() < 0.2 else None,
            'num_tl_90g_dpd_24m': np.random.randint(0, 5) if np.random.random() < 0.1 else None,
            'num_tl_op_past_12m': np.random.randint(0, 20) if np.random.random() < 0.8 else None,
            'pct_tl_nvr_dlq': round(np.random.uniform(50, 100), 1) if np.random.random() < 0.8 else None,
            'percent_bc_gt_75': round(np.random.uniform(0, 100), 1) if np.random.random() < 0.8 else None,
            'pub_rec_bankruptcies': np.random.randint(0, 2) if np.random.random() < 0.1 else None,
            'tax_liens': np.random.randint(0, 3) if np.random.random() < 0.05 else None,
            'tot_hi_cred_lim': np.random.randint(0, 200000) if np.random.random() < 0.8 else None,
            'total_bal_ex_mort': np.random.randint(0, 100000) if np.random.random() < 0.8 else None,
            'total_bc_limit': np.random.randint(0, 100000) if np.random.random() < 0.8 else None,
            'total_il_high_credit_limit': np.random.randint(0, 100000) if np.random.random() < 0.8 else None,
            'hardship_flag': np.random.choice(['Y', 'N'], p=[0.1, 0.9]),
            'debt_settlement_flag': np.random.choice(['Y', 'N'], p=[0.05, 0.95]),
        }
        
        # Add some completely random columns with high null rates (to test filtering)
        if np.random.random() < 0.05:  # 5% chance of having data
            record['random_field_1'] = fake.text(max_nb_chars=50)
        else:
            record['random_field_1'] = None
            
        if np.random.random() < 0.02:  # 2% chance of having data
            record['random_field_2'] = np.random.randint(1, 100)
        else:
            record['random_field_2'] = None
            
        if np.random.random() < 0.08:  # 8% chance of having data
            record['random_field_3'] = fake.date_between(start_date='-5y', end_date='today').strftime('%Y-%m-%d')
        else:
            record['random_field_3'] = None
        
        data.append(record)
        
        # Progress indicator
        if (i + 1) % 1000 == 0:
            print(f"   Generated {i + 1:,} records...")
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add some duplicate records (for testing duplicate removal)
    if num_records > 100:
        duplicate_count = int(num_records * 0.02)  # 2% duplicates
        duplicate_indices = np.random.choice(df.index, duplicate_count, replace=False)
        duplicate_rows = df.iloc[duplicate_indices].copy()
        df = pd.concat([df, duplicate_rows], ignore_index=True)
        print(f"   Added {duplicate_count:,} duplicate records for testing")
    
    # Shuffle the data
    df = df.sample(frac=1).reset_index(drop=True)
    
    # Save to file if specified
    if output_file:
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        df.to_csv(output_file, index=False)
        print(f"   Saved to: {output_file}")
    
    print(f"✅ Generated dataset with {len(df):,} records and {len(df.columns)} columns")
    
    # Print data quality summary
    print(f"\n📊 Data Quality Summary:")
    print(f"   Total records: {len(df):,}")
    print(f"   Total columns: {len(df.columns)}")
    print(f"   Missing values: {df.isnull().sum().sum():,}")
    print(f"   Duplicate records: {df.duplicated().sum():,}")
    
    # Show columns with high null rates
    null_percentages = (df.isnull().sum() / len(df)) * 100
    high_null_columns = null_percentages[null_percentages > 50].sort_values(ascending=False)
    
    if not high_null_columns.empty:
        print(f"\n📉 Columns with >50% null values:")
        for col, pct in high_null_columns.items():
            print(f"   {col}: {pct:.1f}% null")
    
    return df


def generate_multiple_datasets(datasets_config: Dict[str, Any], output_dir: str = "examples/sample_data"):
    """สร้างหลายชุดข้อมูลตัวอย่าง"""
    
    print("🏭 Generating multiple datasets...")
    
    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for dataset_name, config in datasets_config.items():
        print(f"\n🔄 Generating {dataset_name}...")
        
        num_records = config.get('records', 1000)
        output_file = os.path.join(output_dir, f"{dataset_name}.csv")
        
        df = generate_loan_data(num_records, output_file)
        
        # Additional processing based on config
        if config.get('add_quality_issues', False):
            df = add_data_quality_issues(df)
            df.to_csv(output_file, index=False)
            print(f"   Added additional quality issues to {dataset_name}")
    
    print(f"\n✅ All datasets generated in: {output_dir}")


def add_data_quality_issues(df: pd.DataFrame) -> pd.DataFrame:
    """เพิ่มปัญหาคุณภาพข้อมูลเพื่อการทดสอบ"""
    
    df_modified = df.copy()
    
    # 1. Add more missing values randomly
    for col in df_modified.columns:
        if df_modified[col].dtype == 'object':
            # 10% chance to add more nulls in text columns
            mask = np.random.random(len(df_modified)) < 0.1
            df_modified.loc[mask, col] = None
    
    # 2. Add invalid email formats
    if 'email' in df_modified.columns:
        mask = np.random.random(len(df_modified)) < 0.05
        df_modified.loc[mask, 'email'] = 'invalid-email-format'
    
    # 3. Add negative values in amount columns
    amount_columns = [col for col in df_modified.columns if 'amnt' in col.lower()]
    for col in amount_columns:
        if df_modified[col].dtype in ['int64', 'float64']:
            mask = np.random.random(len(df_modified)) < 0.02
            df_modified.loc[mask, col] = -abs(df_modified.loc[mask, col])
    
    # 4. Add inconsistent date formats
    date_columns = [col for col in df_modified.columns if 'd' in col.lower() and df_modified[col].dtype == 'object']
    for col in date_columns:
        if col in df_modified.columns:
            mask = np.random.random(len(df_modified)) < 0.03
            df_modified.loc[mask, col] = '2023-13-45'  # Invalid date
    
    # 5. Add inconsistent text casing
    text_columns = ['emp_title', 'purpose', 'title']
    for col in text_columns:
        if col in df_modified.columns:
            mask = np.random.random(len(df_modified)) < 0.1
            df_modified.loc[mask, col] = df_modified.loc[mask, col].str.upper()
    
    return df_modified


def main():
    """ตัวอย่างการใช้งาน Sample Data Generator"""
    print("=== DataOps Foundation Sample Data Generator ===")
    
    # Generate single dataset
    print("\n1. Generating single dataset...")
    df = generate_loan_data(1000, "examples/sample_data/test_data.csv")
    
    # Generate multiple datasets
    print("\n2. Generating multiple datasets...")
    datasets_config = {
        'small_dataset': {
            'records': 500,
            'add_quality_issues': False
        },
        'medium_dataset': {
            'records': 2000,
            'add_quality_issues': True
        },
        'large_dataset': {
            'records': 5000,
            'add_quality_issues': False
        },
        'quality_test_dataset': {
            'records': 1000,
            'add_quality_issues': True
        }
    }
    
    generate_multiple_datasets(datasets_config)
    
    print("\n✅ Sample data generation completed!")
    print("📁 Check examples/sample_data/ directory for generated files")


if __name__ == "__main__":
    main()
