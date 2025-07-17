#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOps Foundation - Sample Data Generator
สร้างข้อมูลตัวอย่างสำหรับทดสอบระบบ ETL
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_loan_data(n_records=1000, output_file=None):
    """สร้างข้อมูล loan ตัวอย่างที่คล้ายกับ LoanStats_web_14422.csv"""
    
    print(f"🏭 กำลังสร้างข้อมูลตัวอย่าง {n_records:,} รายการ...")
    
    # Set random seed สำหรับความสม่ำเสมอ
    np.random.seed(42)
    
    # สร้างข้อมูลหลัก
    data = {
        # Basic loan information
        'application_type': np.random.choice(['Individual', 'Joint App'], n_records, p=[0.85, 0.15]),
        'loan_amnt': np.random.uniform(1000, 40000, n_records).round(2),
        'funded_amnt': None,  # จะคำนวณหลังจากสร้าง loan_amnt
        'term': np.random.choice([' 36 months', ' 60 months'], n_records, p=[0.7, 0.3]),
        'int_rate': [f"{rate:.2f}%" for rate in np.random.uniform(5.0, 25.0, n_records)],
        'installment': np.random.uniform(50, 1500, n_records).round(2),
        
        # Borrower information
        'home_ownership': np.random.choice(['RENT', 'OWN', 'MORTGAGE', 'OTHER'], n_records, p=[0.4, 0.3, 0.25, 0.05]),
        'annual_inc': np.random.lognormal(10.5, 0.5, n_records).round(2),
        'verification_status': np.random.choice(['Verified', 'Source Verified', 'Not Verified'], n_records, p=[0.3, 0.4, 0.3]),
        
        # Loan status
        'loan_status': np.random.choice([
            'Fully Paid', 'Current', 'Charged Off', 'Late (31-120 days)', 
            'In Grace Period', 'Late (16-30 days)', 'Default'
        ], n_records, p=[0.6, 0.2, 0.1, 0.03, 0.03, 0.02, 0.02]),
        
        # Date information
        'issue_d': None,  # จะสร้างหลังจากนี้
        
        # Employment information
        'emp_length': np.random.choice([
            '< 1 year', '1 year', '2 years', '3 years', '4 years', '5 years',
            '6 years', '7 years', '8 years', '9 years', '10+ years', 'n/a'
        ], n_records, p=[0.1, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.15, 0.03]),
        
        # Purpose
        'purpose': np.random.choice([
            'debt_consolidation', 'credit_card', 'home_improvement', 'major_purchase',
            'medical', 'car', 'vacation', 'moving', 'house', 'other'
        ], n_records, p=[0.6, 0.15, 0.08, 0.05, 0.03, 0.03, 0.02, 0.02, 0.01, 0.01]),
        
        # Geographic
        'addr_state': np.random.choice([
            'CA', 'NY', 'FL', 'TX', 'NJ', 'IL', 'PA', 'VA', 'GA', 'OH',
            'NC', 'MI', 'MD', 'AZ', 'WA', 'CO', 'MA', 'TN', 'MO', 'WI'
        ], n_records),
        
        # Credit information
        'dti': np.random.uniform(0, 40, n_records).round(2),
        'delinq_2yrs': np.random.poisson(0.5, n_records),
        'earliest_cr_line': None,  # จะสร้างหลังจากนี้
        'inq_last_6mths': np.random.poisson(1, n_records),
        'open_acc': np.random.poisson(10, n_records),
        'pub_rec': np.random.poisson(0.1, n_records),
        'revol_bal': np.random.lognormal(8, 1, n_records).round(2),
        'revol_util': np.random.uniform(0, 100, n_records).round(1),
        'total_acc': np.random.poisson(20, n_records),
    }
    
    # สร้าง DataFrame
    df = pd.DataFrame(data)
    
    # คำนวณ funded_amnt (โดยปกติจะเท่ากับ loan_amnt หรือน้อยกว่าเล็กน้อย)
    df['funded_amnt'] = df['loan_amnt'] * np.random.uniform(0.95, 1.0, n_records)
    df['funded_amnt'] = df['funded_amnt'].round(2)
    
    # สร้าง issue_d (วันที่ออก loan) ตั้งแต่ 2015 ถึงปัจจุบัน
    start_date = datetime(2015, 1, 1)
    end_date = datetime(2023, 12, 31)
    date_range = pd.date_range(start_date, end_date, freq='M')
    
    # สุ่มเลือกเดือนสำหรับแต่ละ loan
    issue_dates = np.random.choice(date_range, n_records)
    df['issue_d'] = pd.to_datetime(issue_dates).strftime('%b-%Y')
    
    # สร้าง earliest_cr_line (วันที่เปิด credit line แรก)
    # โดยปกติจะเป็นก่อน issue_d หลายปี
    earliest_years = np.random.randint(1990, 2015, n_records)
    earliest_months = np.random.randint(1, 13, n_records)
    df['earliest_cr_line'] = [f"{month:02d}-{year}" for month, year in zip(earliest_months, earliest_years)]
    
    # เพิ่มคอลัมน์ที่มี null values บางตัว (เหมือนข้อมูลจริง)
    null_columns = {
        'desc': 0.8,  # 80% null
        'mths_since_last_delinq': 0.7,
        'mths_since_last_record': 0.9,
        'mths_since_last_major_derog': 0.85,
        'annual_inc_joint': 0.9,  # เฉพาะ joint applications
        'dti_joint': 0.9,
        'verification_status_joint': 0.9,
    }
    
    for col, null_rate in null_columns.items():
        if col in ['annual_inc_joint', 'dti_joint', 'verification_status_joint']:
            # เฉพาะ joint applications
            joint_mask = df['application_type'] == 'Joint App'
            df[col] = None
            df.loc[joint_mask, col] = np.random.choice(
                ['Value', None], 
                joint_mask.sum(), 
                p=[1-null_rate, null_rate]
            )
        else:
            df[col] = np.random.choice(
                ['Value', None], 
                n_records, 
                p=[1-null_rate, null_rate]
            )
    
    # เพิ่ม grade และ sub_grade
    grades = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    df['grade'] = np.random.choice(grades, n_records, p=[0.2, 0.25, 0.25, 0.15, 0.08, 0.05, 0.02])
    df['sub_grade'] = df['grade'] + np.random.choice(['1', '2', '3', '4', '5'], n_records)
    
    print(f"✅ สร้างข้อมูลเสร็จสิ้น: {df.shape[0]:,} รายการ, {df.shape[1]} คอลัมน์")
    
    # แสดงสถิติพื้นฐาน
    print(f"\n📊 สถิติข้อมูล:")
    print(f"   💰 จำนวนเงินกู้เฉลี่ย: ${df['loan_amnt'].mean():,.2f}")
    print(f"   📈 อัตราดอกเบี้ยเฉลี่ย: {df['int_rate'].str.rstrip('%').astype(float).mean():.2f}%")
    print(f"   🏠 การเป็นเจ้าของบ้าน: {df['home_ownership'].value_counts().to_dict()}")
    print(f"   📅 ช่วงเวลา: {df['issue_d'].min()} ถึง {df['issue_d'].max()}")
    
    # บันทึกไฟล์หากระบุ
    if output_file:
        # สร้างไดเรกทอรีหากไม่มี
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
        
        df.to_csv(output_file, index=False)
        print(f"\n💾 บันทึกไฟล์: {output_file}")
        print(f"   📏 ขนาดไฟล์: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")
    
    return df

def generate_multiple_datasets():
    """สร้างข้อมูลตัวอย่างหลายชุด"""
    
    datasets = [
        {'name': 'small_sample', 'records': 100, 'description': 'ข้อมูลขนาดเล็กสำหรับทดสอบเร็ว'},
        {'name': 'medium_sample', 'records': 1000, 'description': 'ข้อมูลขนาดกลางสำหรับ development'},
        {'name': 'large_sample', 'records': 10000, 'description': 'ข้อมูลขนาดใหญ่สำหรับ performance testing'},
    ]
    
    print("🏭 สร้างข้อมูลตัวอย่างหลายชุด")
    print("=" * 60)
    
    for dataset in datasets:
        print(f"\n📊 {dataset['description']}")
        output_file = f"examples/sample_data/{dataset['name']}.csv"
        
        df = generate_loan_data(
            n_records=dataset['records'],
            output_file=output_file
        )
        
        print(f"   ✅ สร้างเสร็จ: {dataset['name']}.csv")

def main():
    """Main function"""
    print("🚀 DataOps Foundation - Sample Data Generator")
    print("=" * 60)
    
    # สร้างข้อมูลตัวอย่างหลายชุด
    generate_multiple_datasets()
    
    print(f"\n🎉 การสร้างข้อมูลตัวอย่างเสร็จสิ้น!")
    print(f"📁 ไฟล์ถูกบันทึกในโฟลเดอร์ examples/sample_data/")
    print(f"\n💡 การใช้งาน:")
    print(f"   python src/data_pipeline/etl_processor.py")
    print(f"   python tests/test_enhanced_etl.py")

if __name__ == "__main__":
    main()
