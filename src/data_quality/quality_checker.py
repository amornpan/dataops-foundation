#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOps Foundation - Data Quality Checker
เครื่องมือตรวจสอบคุณภาพข้อมูลขั้นสูง

Features:
- Data profiling และ statistics
- Business rules validation
- Anomaly detection
- Quality scoring
- Automated reporting
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')


@dataclass
class QualityResult:
    """ผลลัพธ์การตรวจสอบคุณภาพข้อมูล"""
    overall_score: float
    passed_checks: int
    failed_checks: int
    total_checks: int
    check_results: Dict[str, Any]
    recommendations: List[str]
    execution_time: float


class DataQualityChecker:
    """
    Data Quality Checker ขั้นสูงสำหรับ DataOps Foundation
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """เริ่มต้น Data Quality Checker"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Quality thresholds
        self.thresholds = {
            'completeness': 0.95,  # 95% completeness
            'uniqueness': 0.98,    # 98% uniqueness for keys
            'validity': 0.90,      # 90% valid values
            'consistency': 0.95,   # 95% consistency
            'accuracy': 0.90       # 90% accuracy
        }
        
        # Update thresholds from config
        if 'data_quality' in self.config:
            self.thresholds.update(self.config['data_quality'].get('thresholds', {}))
    
    def run_checks(self, dataframe: pd.DataFrame) -> QualityResult:
        """รันการตรวจสอบคุณภาพข้อมูลครบถ้วน"""
        start_time = datetime.now()
        
        check_results = {}
        passed_checks = 0
        failed_checks = 0
        recommendations = []
        
        # 1. Completeness Check
        completeness_result = self._check_completeness(dataframe)
        check_results['completeness'] = completeness_result
        if completeness_result['passed']:
            passed_checks += 1
        else:
            failed_checks += 1
            recommendations.append("Consider handling missing values in columns with low completeness")
        
        # 2. Uniqueness Check
        uniqueness_result = self._check_uniqueness(dataframe)
        check_results['uniqueness'] = uniqueness_result
        if uniqueness_result['passed']:
            passed_checks += 1
        else:
            failed_checks += 1
            recommendations.append("Check for duplicate records in key columns")
        
        # 3. Data Type Validity
        validity_result = self._check_validity(dataframe)
        check_results['validity'] = validity_result
        if validity_result['passed']:
            passed_checks += 1
        else:
            failed_checks += 1
            recommendations.append("Review data types and format consistency")
        
        # 4. Business Rules
        business_rules_result = self._check_business_rules(dataframe)
        check_results['business_rules'] = business_rules_result
        if business_rules_result['passed']:
            passed_checks += 1
        else:
            failed_checks += 1
            recommendations.append("Validate business logic and constraints")
        
        # 5. Statistical Anomalies
        anomaly_result = self._check_anomalies(dataframe)
        check_results['anomalies'] = anomaly_result
        if anomaly_result['passed']:
            passed_checks += 1
        else:
            failed_checks += 1
            recommendations.append("Investigate statistical anomalies in the data")
        
        # Calculate overall score
        total_checks = passed_checks + failed_checks
        overall_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return QualityResult(
            overall_score=overall_score,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            total_checks=total_checks,
            check_results=check_results,
            recommendations=recommendations,
            execution_time=execution_time
        )
    
    def _check_completeness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """ตรวจสอบความครบถ้วนของข้อมูล"""
        try:
            null_percentages = df.isnull().mean()
            completeness_scores = 1 - null_percentages
            
            # Overall completeness score
            overall_completeness = completeness_scores.mean()
            
            # Check if meets threshold
            passed = overall_completeness >= self.thresholds['completeness']
            
            # Identify problematic columns
            problematic_columns = null_percentages[null_percentages > (1 - self.thresholds['completeness'])].to_dict()
            
            return {
                'passed': passed,
                'score': overall_completeness,
                'threshold': self.thresholds['completeness'],
                'column_scores': completeness_scores.to_dict(),
                'problematic_columns': problematic_columns,
                'details': f"Overall completeness: {overall_completeness:.2%}"
            }
        except Exception as e:
            self.logger.error(f"Error in completeness check: {e}")
            return {
                'passed': False,
                'score': 0.0,
                'error': str(e)
            }
    
    def _check_uniqueness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """ตรวจสอบความไม่ซ้ำของข้อมูล"""
        try:
            # Check for duplicate rows
            total_rows = len(df)
            duplicate_rows = df.duplicated().sum()
            uniqueness_score = 1 - (duplicate_rows / total_rows) if total_rows > 0 else 1
            
            passed = uniqueness_score >= self.thresholds['uniqueness']
            
            # Check individual columns for uniqueness
            column_uniqueness = {}
            for col in df.columns:
                if df[col].dtype in ['object', 'string']:
                    unique_ratio = df[col].nunique() / len(df.dropna(subset=[col]))
                    column_uniqueness[col] = unique_ratio
            
            return {
                'passed': passed,
                'score': uniqueness_score,
                'threshold': self.thresholds['uniqueness'],
                'duplicate_rows': duplicate_rows,
                'total_rows': total_rows,
                'column_uniqueness': column_uniqueness,
                'details': f"Uniqueness score: {uniqueness_score:.2%}, Duplicates: {duplicate_rows}"
            }
        except Exception as e:
            self.logger.error(f"Error in uniqueness check: {e}")
            return {
                'passed': False,
                'score': 0.0,
                'error': str(e)
            }
    
    def _check_validity(self, df: pd.DataFrame) -> Dict[str, Any]:
        """ตรวจสอบความถูกต้องของประเภทข้อมูล"""
        try:
            validity_issues = []
            column_validity = {}
            
            for col in df.columns:
                # Check for mixed types
                if df[col].dtype == 'object':
                    # Check if numeric column stored as string
                    try:
                        pd.to_numeric(df[col], errors='raise')
                        validity_issues.append(f"Column '{col}' appears to be numeric but stored as text")
                        column_validity[col] = 0.5
                    except:
                        column_validity[col] = 1.0
                else:
                    column_validity[col] = 1.0
            
            # Overall validity score
            overall_validity = np.mean(list(column_validity.values()))
            passed = overall_validity >= self.thresholds['validity'] and len(validity_issues) == 0
            
            return {
                'passed': passed,
                'score': overall_validity,
                'threshold': self.thresholds['validity'],
                'column_validity': column_validity,
                'issues': validity_issues,
                'details': f"Validity score: {overall_validity:.2%}, Issues: {len(validity_issues)}"
            }
        except Exception as e:
            self.logger.error(f"Error in validity check: {e}")
            return {
                'passed': False,
                'score': 0.0,
                'error': str(e)
            }
    
    def _check_business_rules(self, df: pd.DataFrame) -> Dict[str, Any]:
        """ตรวจสอบกฎทางธุรกิจ"""
        try:
            business_rule_results = []
            passed_rules = 0
            total_rules = 0
            
            # Rule 1: Loan amounts should be positive
            if 'loan_amnt' in df.columns:
                total_rules += 1
                positive_loans = (df['loan_amnt'] > 0).sum()
                total_loans = len(df)
                rule_score = positive_loans / total_loans if total_loans > 0 else 0
                
                rule_result = {
                    'rule_name': 'positive_loan_amount',
                    'description': 'Loan amounts must be positive',
                    'score': rule_score,
                    'passed': rule_score >= 0.99,
                    'violations': total_loans - positive_loans
                }
                business_rule_results.append(rule_result)
                if rule_result['passed']:
                    passed_rules += 1
            
            # Rule 2: Funded amount <= Loan amount
            if 'loan_amnt' in df.columns and 'funded_amnt' in df.columns:
                total_rules += 1
                valid_funding = (df['funded_amnt'] <= df['loan_amnt']).sum()
                total_records = len(df)
                rule_score = valid_funding / total_records if total_records > 0 else 0
                
                rule_result = {
                    'rule_name': 'funded_not_exceed_loan',
                    'description': 'Funded amount should not exceed loan amount',
                    'score': rule_score,
                    'passed': rule_score >= 0.95,
                    'violations': total_records - valid_funding
                }
                business_rule_results.append(rule_result)
                if rule_result['passed']:
                    passed_rules += 1
            
            # Rule 3: Interest rate in reasonable range
            if 'int_rate' in df.columns:
                total_rules += 1
                valid_rates = ((df['int_rate'] >= 0) & (df['int_rate'] <= 1)).sum()
                total_records = len(df)
                rule_score = valid_rates / total_records if total_records > 0 else 0
                
                rule_result = {
                    'rule_name': 'interest_rate_range',
                    'description': 'Interest rate should be between 0 and 1',
                    'score': rule_score,
                    'passed': rule_score >= 0.99,
                    'violations': total_records - valid_rates
                }
                business_rule_results.append(rule_result)
                if rule_result['passed']:
                    passed_rules += 1
            
            # Overall business rules score
            overall_score = passed_rules / total_rules if total_rules > 0 else 1.0
            passed = overall_score >= 0.8  # 80% of business rules should pass
            
            return {
                'passed': passed,
                'score': overall_score,
                'passed_rules': passed_rules,
                'total_rules': total_rules,
                'rule_results': business_rule_results,
                'details': f"Business rules: {passed_rules}/{total_rules} passed"
            }
        except Exception as e:
            self.logger.error(f"Error in business rules check: {e}")
            return {
                'passed': False,
                'score': 0.0,
                'error': str(e)
            }
    
    def _check_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """ตรวจสอบความผิดปกติทางสถิติ"""
        try:
            anomaly_results = []
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            for col in numeric_columns:
                if col in df.columns:
                    # Calculate Z-scores
                    mean_val = df[col].mean()
                    std_val = df[col].std()
                    
                    if std_val > 0:
                        z_scores = np.abs((df[col] - mean_val) / std_val)
                        anomalies = (z_scores > 3).sum()  # Values more than 3 standard deviations
                        anomaly_rate = anomalies / len(df)
                        
                        anomaly_results.append({
                            'column': col,
                            'anomalies': anomalies,
                            'anomaly_rate': anomaly_rate,
                            'mean': mean_val,
                            'std': std_val
                        })
            
            # Overall anomaly score (lower anomaly rate is better)
            if anomaly_results:
                avg_anomaly_rate = np.mean([r['anomaly_rate'] for r in anomaly_results])
                anomaly_score = 1 - avg_anomaly_rate  # Convert to quality score
            else:
                anomaly_score = 1.0
            
            passed = anomaly_score >= 0.95  # Less than 5% anomalies
            
            return {
                'passed': passed,
                'score': anomaly_score,
                'anomaly_results': anomaly_results,
                'details': f"Anomaly score: {anomaly_score:.2%}"
            }
        except Exception as e:
            self.logger.error(f"Error in anomaly check: {e}")
            return {
                'passed': False,
                'score': 0.0,
                'error': str(e)
            }
    
    def generate_report(self, quality_result: QualityResult) -> str:
        """สร้างรายงานคุณภาพข้อมูล"""
        report = []
        report.append("=" * 80)
        report.append("📊 DATA QUALITY REPORT")
        report.append("=" * 80)
        report.append(f"🎯 Overall Score: {quality_result.overall_score:.1f}%")
        report.append(f"✅ Passed Checks: {quality_result.passed_checks}")
        report.append(f"❌ Failed Checks: {quality_result.failed_checks}")
        report.append(f"⏱️  Execution Time: {quality_result.execution_time:.2f} seconds")
        report.append("")
        
        # Detailed results
        report.append("📋 DETAILED RESULTS:")
        report.append("-" * 40)
        
        for check_name, result in quality_result.check_results.items():
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            score = result.get('score', 0) * 100
            report.append(f"{status} {check_name.upper()}: {score:.1f}%")
            if 'details' in result:
                report.append(f"    {result['details']}")
        
        # Recommendations
        if quality_result.recommendations:
            report.append("")
            report.append("💡 RECOMMENDATIONS:")
            report.append("-" * 40)
            for i, rec in enumerate(quality_result.recommendations, 1):
                report.append(f"{i}. {rec}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """ตัวอย่างการใช้งาน Data Quality Checker"""
    print("=== DataOps Foundation Data Quality Checker ===")
    
    # สร้างข้อมูลตัวอย่าง
    np.random.seed(42)
    sample_data = pd.DataFrame({
        'loan_amnt': np.random.uniform(1000, 50000, 1000),
        'funded_amnt': np.random.uniform(800, 45000, 1000),
        'int_rate': np.random.uniform(0.05, 0.25, 1000),
        'home_ownership': np.random.choice(['RENT', 'OWN', 'MORTGAGE'], 1000),
        'loan_status': np.random.choice(['Fully Paid', 'Current', 'Charged Off'], 1000)
    })
    
    # เพิ่มค่า null บางตัว
    sample_data.loc[np.random.choice(1000, 50, replace=False), 'home_ownership'] = None
    
    # รัน quality checks
    checker = DataQualityChecker()
    result = checker.run_checks(sample_data)
    
    # แสดงรายงาน
    report = checker.generate_report(result)
    print(report)


if __name__ == "__main__":
    main()
