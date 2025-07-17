#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOps Foundation - Data Quality Checker
ตัวตรวจสอบคุณภาพข้อมูลขั้นสูง

Features:
- Comprehensive data quality assessments
- Multiple quality metrics (completeness, uniqueness, consistency)
- Configurable quality thresholds
- Detailed quality reports
- Integration with ETL pipeline
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re
import os


@dataclass
class QualityMetric:
    """เก็บข้อมูล quality metric แต่ละตัว"""
    name: str
    value: float
    threshold: float
    passed: bool
    description: str
    details: Dict[str, Any] = None


@dataclass
class QualityResult:
    """ผลลัพธ์การตรวจสอบคุณภาพข้อมูล"""
    overall_score: float
    grade: str
    passed: bool
    metrics: List[QualityMetric]
    metadata: Dict[str, Any]
    recommendations: List[str]


class DataQualityChecker:
    """
    ตัวตรวจสอบคุณภาพข้อมูลที่ครอบคลุม
    รองรับหลากหลายมาตรการวัดคุณภาพข้อมูล
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """เริ่มต้น Quality Checker"""
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Default thresholds
        self.default_thresholds = {
            'completeness': 0.85,      # 85% complete
            'uniqueness': 0.90,        # 90% unique
            'consistency': 0.90,       # 90% consistent
            'validity': 0.85,          # 85% valid
            'accuracy': 0.80,          # 80% accurate
            'timeliness': 0.85         # 85% timely
        }
        
        # Override with config values
        self.thresholds = self.config.get('quality_thresholds', {})
        for key, value in self.default_thresholds.items():
            if key not in self.thresholds:
                self.thresholds[key] = value
        
        self.logger.info("Data Quality Checker initialized")
    
    def calculate_completeness(self, df: pd.DataFrame) -> QualityMetric:
        """
        คำนวณความสมบูรณ์ของข้อมูล (Completeness)
        ตรวจสอบว่ามีข้อมูลครบถ้วนเพียงใด
        """
        try:
            total_values = df.size
            non_null_values = df.count().sum()
            completeness_score = non_null_values / total_values if total_values > 0 else 0
            
            # รายละเอียดเพิ่มเติม
            column_completeness = {}
            for col in df.columns:
                col_completeness = df[col].count() / len(df) if len(df) > 0 else 0
                column_completeness[col] = {
                    'completeness': col_completeness,
                    'null_count': df[col].isnull().sum(),
                    'total_count': len(df)
                }
            
            return QualityMetric(
                name='completeness',
                value=completeness_score,
                threshold=self.thresholds['completeness'],
                passed=completeness_score >= self.thresholds['completeness'],
                description=f'Data completeness: {completeness_score:.2%}',
                details={
                    'total_values': total_values,
                    'non_null_values': non_null_values,
                    'column_completeness': column_completeness
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating completeness: {e}")
            return QualityMetric(
                name='completeness',
                value=0.0,
                threshold=self.thresholds['completeness'],
                passed=False,
                description='Error calculating completeness',
                details={'error': str(e)}
            )
    
    def calculate_uniqueness(self, df: pd.DataFrame) -> QualityMetric:
        """
        คำนวณความเป็นเอกลักษณ์ของข้อมูล (Uniqueness)
        ตรวจสอบว่ามีข้อมูลที่ซ้ำกันเพียงใด
        """
        try:
            total_rows = len(df)
            if total_rows == 0:
                return QualityMetric(
                    name='uniqueness',
                    value=0.0,
                    threshold=self.thresholds['uniqueness'],
                    passed=False,
                    description='No data to assess uniqueness',
                    details={}
                )
            
            unique_rows = len(df.drop_duplicates())
            uniqueness_score = unique_rows / total_rows
            
            # รายละเอียดเพิ่มเติม
            column_uniqueness = {}
            for col in df.columns:
                if df[col].dtype in ['object', 'string']:
                    unique_values = df[col].nunique()
                    total_values = df[col].count()
                    col_uniqueness = unique_values / total_values if total_values > 0 else 0
                    column_uniqueness[col] = {
                        'uniqueness': col_uniqueness,
                        'unique_values': unique_values,
                        'total_values': total_values
                    }
            
            return QualityMetric(
                name='uniqueness',
                value=uniqueness_score,
                threshold=self.thresholds['uniqueness'],
                passed=uniqueness_score >= self.thresholds['uniqueness'],
                description=f'Data uniqueness: {uniqueness_score:.2%}',
                details={
                    'total_rows': total_rows,
                    'unique_rows': unique_rows,
                    'duplicate_rows': total_rows - unique_rows,
                    'column_uniqueness': column_uniqueness
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating uniqueness: {e}")
            return QualityMetric(
                name='uniqueness',
                value=0.0,
                threshold=self.thresholds['uniqueness'],
                passed=False,
                description='Error calculating uniqueness',
                details={'error': str(e)}
            )
    
    def calculate_consistency(self, df: pd.DataFrame) -> QualityMetric:
        """
        คำนวณความสม่ำเสมอของข้อมูล (Consistency)
        ตรวจสอบรูปแบบข้อมูลและความสม่ำเสมอ
        """
        try:
            consistency_checks = []
            
            for col in df.columns:
                if df[col].dtype == 'object':
                    # ตรวจสอบรูปแบบข้อมูล
                    non_null_values = df[col].dropna()
                    if len(non_null_values) > 0:
                        # ตรวจสอบว่าเป็นอีเมลหรือไม่
                        if 'email' in col.lower():
                            valid_emails = non_null_values.str.match(r'^[^@]+@[^@]+\.[^@]+$')
                            consistency_checks.append({
                                'column': col,
                                'check': 'email_format',
                                'valid_count': valid_emails.sum(),
                                'total_count': len(non_null_values),
                                'consistency': valid_emails.sum() / len(non_null_values)
                            })
                        
                        # ตรวจสอบว่าเป็นเบอร์โทรหรือไม่
                        elif 'phone' in col.lower():
                            valid_phones = non_null_values.str.match(r'^[\d\-\+\(\)\s]{10,}$')
                            consistency_checks.append({
                                'column': col,
                                'check': 'phone_format',
                                'valid_count': valid_phones.sum(),
                                'total_count': len(non_null_values),
                                'consistency': valid_phones.sum() / len(non_null_values)
                            })
                        
                        # ตรวจสอบความสม่ำเสมอของตัวอักษร
                        else:
                            # ตรวจสอบความสม่ำเสมอของ case
                            lower_count = non_null_values.str.islower().sum()
                            upper_count = non_null_values.str.isupper().sum()
                            title_count = non_null_values.str.istitle().sum()
                            
                            max_case_count = max(lower_count, upper_count, title_count)
                            case_consistency = max_case_count / len(non_null_values)
                            
                            consistency_checks.append({
                                'column': col,
                                'check': 'case_consistency',
                                'valid_count': max_case_count,
                                'total_count': len(non_null_values),
                                'consistency': case_consistency
                            })
                
                elif df[col].dtype in ['int64', 'float64']:
                    # ตรวจสอบค่าที่เป็นไปได้
                    non_null_values = df[col].dropna()
                    if len(non_null_values) > 0:
                        # ตรวจสอบค่าลบที่ไม่เหมาะสม
                        if any(word in col.lower() for word in ['amount', 'price', 'salary', 'income']):
                            positive_count = (non_null_values >= 0).sum()
                            consistency_checks.append({
                                'column': col,
                                'check': 'positive_values',
                                'valid_count': positive_count,
                                'total_count': len(non_null_values),
                                'consistency': positive_count / len(non_null_values)
                            })
            
            # คำนวณ consistency score โดยรวม
            if consistency_checks:
                avg_consistency = sum(check['consistency'] for check in consistency_checks) / len(consistency_checks)
            else:
                avg_consistency = 1.0  # ถ้าไม่มีการตรวจสอบ ถือว่าผ่าน
            
            return QualityMetric(
                name='consistency',
                value=avg_consistency,
                threshold=self.thresholds['consistency'],
                passed=avg_consistency >= self.thresholds['consistency'],
                description=f'Data consistency: {avg_consistency:.2%}',
                details={
                    'consistency_checks': consistency_checks,
                    'checks_performed': len(consistency_checks)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating consistency: {e}")
            return QualityMetric(
                name='consistency',
                value=0.0,
                threshold=self.thresholds['consistency'],
                passed=False,
                description='Error calculating consistency',
                details={'error': str(e)}
            )
    
    def calculate_validity(self, df: pd.DataFrame) -> QualityMetric:
        """
        คำนวณความถูกต้องของข้อมูล (Validity)
        ตรวจสอบว่าข้อมูลอยู่ในรูปแบบที่ถูกต้อง
        """
        try:
            validity_checks = []
            
            for col in df.columns:
                non_null_values = df[col].dropna()
                if len(non_null_values) == 0:
                    continue
                
                # ตรวจสอบตามประเภทข้อมูล
                if df[col].dtype == 'object':
                    # ตรวจสอบว่าข้อมูลไม่ว่างเปล่า
                    non_empty_count = (non_null_values.str.strip() != '').sum()
                    validity_checks.append({
                        'column': col,
                        'check': 'non_empty_strings',
                        'valid_count': non_empty_count,
                        'total_count': len(non_null_values),
                        'validity': non_empty_count / len(non_null_values)
                    })
                
                elif df[col].dtype in ['int64', 'float64']:
                    # ตรวจสอบค่าที่เป็น infinite หรือ NaN
                    finite_count = np.isfinite(non_null_values).sum()
                    validity_checks.append({
                        'column': col,
                        'check': 'finite_numbers',
                        'valid_count': finite_count,
                        'total_count': len(non_null_values),
                        'validity': finite_count / len(non_null_values)
                    })
                
                elif df[col].dtype == 'datetime64[ns]':
                    # ตรวจสอบว่าวันที่อยู่ในช่วงที่เหมาะสม
                    current_year = datetime.now().year
                    valid_dates = ((non_null_values.dt.year >= 1900) & 
                                  (non_null_values.dt.year <= current_year + 10)).sum()
                    validity_checks.append({
                        'column': col,
                        'check': 'valid_dates',
                        'valid_count': valid_dates,
                        'total_count': len(non_null_values),
                        'validity': valid_dates / len(non_null_values)
                    })
            
            # คำนวณ validity score โดยรวม
            if validity_checks:
                avg_validity = sum(check['validity'] for check in validity_checks) / len(validity_checks)
            else:
                avg_validity = 1.0
            
            return QualityMetric(
                name='validity',
                value=avg_validity,
                threshold=self.thresholds['validity'],
                passed=avg_validity >= self.thresholds['validity'],
                description=f'Data validity: {avg_validity:.2%}',
                details={
                    'validity_checks': validity_checks,
                    'checks_performed': len(validity_checks)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating validity: {e}")
            return QualityMetric(
                name='validity',
                value=0.0,
                threshold=self.thresholds['validity'],
                passed=False,
                description='Error calculating validity',
                details={'error': str(e)}
            )
    
    def run_checks(self, df: pd.DataFrame) -> QualityResult:
        """
        รันการตรวจสอบคุณภาพข้อมูลทั้งหมด
        """
        self.logger.info("Starting data quality checks")
        
        try:
            # รันการตรวจสอบแต่ละประเภท
            metrics = [
                self.calculate_completeness(df),
                self.calculate_uniqueness(df),
                self.calculate_consistency(df),
                self.calculate_validity(df)
            ]
            
            # คำนวณ overall score
            weights = {
                'completeness': 0.30,
                'uniqueness': 0.25,
                'consistency': 0.25,
                'validity': 0.20
            }
            
            overall_score = sum(
                metric.value * weights.get(metric.name, 0.25) 
                for metric in metrics
            )
            
            # กำหนดเกรด
            if overall_score >= 0.90:
                grade = 'A'
            elif overall_score >= 0.80:
                grade = 'B'
            elif overall_score >= 0.70:
                grade = 'C'
            elif overall_score >= 0.60:
                grade = 'D'
            else:
                grade = 'F'
            
            # ตรวจสอบว่าผ่านทุกเกณฑ์หรือไม่
            passed = all(metric.passed for metric in metrics)
            
            # สร้างข้อเสนอแนะ
            recommendations = self._generate_recommendations(metrics, df)
            
            result = QualityResult(
                overall_score=overall_score * 100,  # แปลงเป็นเปอร์เซ็นต์
                grade=grade,
                passed=passed,
                metrics=metrics,
                metadata={
                    'dataset_shape': df.shape,
                    'column_count': len(df.columns),
                    'row_count': len(df),
                    'data_types': df.dtypes.to_dict(),
                    'check_timestamp': datetime.now().isoformat()
                },
                recommendations=recommendations
            )
            
            self.logger.info(f"Quality checks completed. Overall score: {overall_score:.1%}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in quality checks: {e}")
            return QualityResult(
                overall_score=0.0,
                grade='F',
                passed=False,
                metrics=[],
                metadata={'error': str(e)},
                recommendations=['Fix errors in quality checking process']
            )
    
    def _generate_recommendations(self, metrics: List[QualityMetric], df: pd.DataFrame) -> List[str]:
        """สร้างข้อเสนอแนะสำหรับปรับปรุงคุณภาพข้อมูล"""
        recommendations = []
        
        for metric in metrics:
            if not metric.passed:
                if metric.name == 'completeness':
                    recommendations.append(
                        f"❌ Completeness below threshold ({metric.value:.1%} < {metric.threshold:.1%}): "
                        f"Consider data imputation or removing incomplete records"
                    )
                    
                elif metric.name == 'uniqueness':
                    recommendations.append(
                        f"❌ Uniqueness below threshold ({metric.value:.1%} < {metric.threshold:.1%}): "
                        f"Remove duplicate records or investigate data collection process"
                    )
                    
                elif metric.name == 'consistency':
                    recommendations.append(
                        f"❌ Consistency below threshold ({metric.value:.1%} < {metric.threshold:.1%}): "
                        f"Standardize data formats and validate input rules"
                    )
                    
                elif metric.name == 'validity':
                    recommendations.append(
                        f"❌ Validity below threshold ({metric.value:.1%} < {metric.threshold:.1%}): "
                        f"Validate data formats and remove invalid entries"
                    )
        
        # เพิ่มข้อเสนอแนะทั่วไป
        if len(df) < 100:
            recommendations.append("⚠️ Small dataset detected. Consider collecting more data for reliable analysis")
        
        if df.isnull().sum().sum() / df.size > 0.20:
            recommendations.append("⚠️ High percentage of missing values. Consider data collection improvements")
        
        return recommendations if recommendations else ["✅ Data quality is acceptable"]
    
    def generate_report(self, result: QualityResult) -> str:
        """สร้างรายงานคุณภาพข้อมูลแบบละเอียด"""
        report = []
        
        # Header
        report.append("=" * 70)
        report.append("📊 DATA QUALITY ASSESSMENT REPORT")
        report.append("=" * 70)
        report.append(f"⏰ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"📋 Dataset: {result.metadata.get('row_count', 0):,} rows × {result.metadata.get('column_count', 0)} columns")
        report.append("")
        
        # Overall score
        report.append("🎯 OVERALL QUALITY SCORE")
        report.append("-" * 30)
        report.append(f"Score: {result.overall_score:.1f}%")
        report.append(f"Grade: {result.grade}")
        report.append(f"Status: {'✅ PASSED' if result.passed else '❌ FAILED'}")
        report.append("")
        
        # Detailed metrics
        report.append("📈 DETAILED METRICS")
        report.append("-" * 30)
        
        for metric in result.metrics:
            status = "✅ PASSED" if metric.passed else "❌ FAILED"
            report.append(f"{metric.name.upper()}: {metric.value:.1%} (threshold: {metric.threshold:.1%}) {status}")
            
            if metric.details:
                # แสดงรายละเอียดสำคัญ
                if metric.name == 'completeness' and 'column_completeness' in metric.details:
                    worst_columns = sorted(
                        metric.details['column_completeness'].items(),
                        key=lambda x: x[1]['completeness']
                    )[:3]
                    
                    if worst_columns:
                        report.append(f"   📉 Columns with most missing data:")
                        for col, data in worst_columns:
                            report.append(f"      - {col}: {data['completeness']:.1%} complete")
                
                elif metric.name == 'uniqueness' and 'duplicate_rows' in metric.details:
                    if metric.details['duplicate_rows'] > 0:
                        report.append(f"   📉 Duplicate rows: {metric.details['duplicate_rows']:,}")
        
        report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS")
        report.append("-" * 30)
        for i, rec in enumerate(result.recommendations, 1):
            report.append(f"{i}. {rec}")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


def main():
    """ตัวอย่างการใช้งาน Quality Checker"""
    print("=== DataOps Foundation Quality Checker ===")
    
    # สร้างข้อมูลตัวอย่าง
    sample_data = pd.DataFrame({
        'id': [1, 2, 3, 4, 5, 5],  # มีข้อมูลซ้ำ
        'name': ['John', 'Jane', '', 'Bob', 'Alice', 'Alice'],  # มีข้อมูลว่าง
        'email': ['john@test.com', 'jane@test.com', 'invalid-email', 'bob@test.com', None, 'alice@test.com'],
        'age': [25, 30, -5, 35, 28, 28],  # มีอายุติดลบ
        'salary': [50000, 60000, 70000, None, 55000, 55000]  # มีค่าว่าง
    })
    
    print(f"Sample data shape: {sample_data.shape}")
    print(f"Sample data:\n{sample_data}")
    print()
    
    # สร้าง quality checker
    checker = DataQualityChecker()
    
    # รันการตรวจสอบ
    result = checker.run_checks(sample_data)
    
    # แสดงรายงาน
    report = checker.generate_report(result)
    print(report)


if __name__ == "__main__":
    main()
