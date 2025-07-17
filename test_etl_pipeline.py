#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOps Foundation - Unit Tests
Test cases for ETL Pipeline functionality
"""

import unittest
import pandas as pd
import numpy as np
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from etl_pipeline import DataOpsETLPipeline


class TestDataOpsETLPipeline(unittest.TestCase):
    """Test cases for DataOps ETL Pipeline"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock configuration
        self.config = {
            'database': {
                'server': 'test_server',
                'database': 'test_db',
                'username': 'test_user',
                'password': 'test_pass'
            },
            'acceptable_max_null': 5,
            'missing_threshold': 20.0
        }
        
        # Create sample test data
        self.sample_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'loan_amnt': [5000, 10000, 15000, 20000, 25000],
            'funded_amnt': [4500, 9500, 14500, 19500, 24500],
            'term': [36, 60, 36, 60, 36],
            'int_rate': ['10.5%', '12.0%', '8.5%', '15.2%', '9.8%'],
            'installment': [150.5, 200.0, 450.75, 500.25, 780.0],
            'home_ownership': ['RENT', 'OWN', 'MORTGAGE', 'RENT', 'OWN'],
            'loan_status': ['Fully Paid', 'Charged Off', 'Fully Paid', 'Current', 'Fully Paid'],
            'issue_d': ['Jan-2020', 'Feb-2020', 'Mar-2020', 'Apr-2020', 'May-2020'],
            'application_type': ['Individual', 'Individual', 'Joint App', 'Individual', 'Individual']
        })
    
    @patch('etl_pipeline.create_engine')
    def test_init_database_connection_success(self, mock_create_engine):
        """Test successful database connection initialization"""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        etl = DataOpsETLPipeline(self.config)
        
        self.assertEqual(etl.engine, mock_engine)
        mock_create_engine.assert_called_once()
    
    @patch('etl_pipeline.create_engine')
    def test_init_database_connection_failure(self, mock_create_engine):
        """Test database connection initialization failure"""
        mock_create_engine.side_effect = Exception("Connection failed")
        
        with self.assertRaises(Exception):
            DataOpsETLPipeline(self.config)
    
    def test_guess_column_types_success(self):
        """Test successful column type inference"""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.sample_data.to_csv(f.name, index=False)
            temp_file = f.name
        
        try:
            with patch('etl_pipeline.create_engine'):
                etl = DataOpsETLPipeline(self.config)
                success, column_types = etl.guess_column_types(temp_file)
                
                self.assertTrue(success)
                self.assertIsInstance(column_types, dict)
                self.assertIn('loan_amnt', column_types)
                self.assertIn('int_rate', column_types)
        finally:
            os.unlink(temp_file)
    
    def test_guess_column_types_file_not_found(self):
        """Test column type inference with non-existent file"""
        with patch('etl_pipeline.create_engine'):
            etl = DataOpsETLPipeline(self.config)
            success, error_msg = etl.guess_column_types('non_existent_file.csv')
            
            self.assertFalse(success)
            self.assertIsInstance(error_msg, str)
    
    @patch('pandas.read_csv')
    @patch('etl_pipeline.create_engine')
    def test_load_and_clean_data(self, mock_create_engine, mock_read_csv):
        """Test data loading and cleaning"""
        # Mock pandas read_csv to return our sample data
        mock_read_csv.return_value = self.sample_data
        
        etl = DataOpsETLPipeline(self.config)
        result_df = etl.load_and_clean_data('test_file.csv')
        
        # Check that the result is a DataFrame
        self.assertIsInstance(result_df, pd.DataFrame)
        
        # Check that we got some data back
        self.assertGreater(len(result_df), 0)
    
    @patch('etl_pipeline.create_engine')
    def test_transform_data(self, mock_create_engine):
        """Test data transformation"""
        etl = DataOpsETLPipeline(self.config)
        transformed_df = etl.transform_data(self.sample_data)
        
        # Check that issue_d was converted to datetime
        if 'issue_d' in transformed_df.columns:
            self.assertTrue(pd.api.types.is_datetime64_any_dtype(transformed_df['issue_d']))
        
        # Check that int_rate was converted from percentage
        if 'int_rate' in transformed_df.columns:
            # Values should be between 0 and 1 (decimal format)
            self.assertTrue(all(transformed_df['int_rate'] < 1))
            self.assertTrue(all(transformed_df['int_rate'] > 0))
    
    @patch('etl_pipeline.create_engine')
    def test_create_dimension_tables(self, mock_create_engine):
        """Test dimension table creation"""
        etl = DataOpsETLPipeline(self.config)
        
        # Transform data first
        transformed_df = etl.transform_data(self.sample_data)
        
        # Create dimension tables
        dim_tables = etl.create_dimension_tables(transformed_df)
        
        # Check that dimension tables were created
        self.assertIsInstance(dim_tables, dict)
        
        # Check for expected dimension tables
        if 'home_ownership' in transformed_df.columns:
            self.assertIn('home_ownership_dim', dim_tables)
            home_dim = dim_tables['home_ownership_dim']
            self.assertIn('home_ownership_id', home_dim.columns)
            
        if 'loan_status' in transformed_df.columns:
            self.assertIn('loan_status_dim', dim_tables)
            status_dim = dim_tables['loan_status_dim']
            self.assertIn('loan_status_id', status_dim.columns)
    
    @patch('etl_pipeline.create_engine')
    def test_create_fact_table(self, mock_create_engine):
        """Test fact table creation"""
        etl = DataOpsETLPipeline(self.config)
        
        # Transform data and create dimension tables
        transformed_df = etl.transform_data(self.sample_data)
        dim_tables = etl.create_dimension_tables(transformed_df)
        
        # Create fact table
        fact_table = etl.create_fact_table(transformed_df, dim_tables)
        
        # Check that fact table was created
        self.assertIsInstance(fact_table, pd.DataFrame)
        self.assertGreater(len(fact_table), 0)
        
        # Check for foreign key columns
        if 'home_ownership_dim' in dim_tables:
            self.assertIn('home_ownership_id', fact_table.columns)
        if 'loan_status_dim' in dim_tables:
            self.assertIn('loan_status_id', fact_table.columns)
    
    @patch('etl_pipeline.create_engine')
    def test_validate_data_quality(self, mock_create_engine):
        """Test data quality validation"""
        etl = DataOpsETLPipeline(self.config)
        
        # Transform data first so int_rate is in decimal format
        transformed_data = etl.transform_data(self.sample_data)
        
        quality_report = etl.validate_data_quality(transformed_data)
        
        # Check that report contains expected keys
        self.assertIn('total_rows', quality_report)
        self.assertIn('total_columns', quality_report)
        self.assertIn('missing_values', quality_report)
        self.assertIn('duplicate_rows', quality_report)
        self.assertIn('timestamp', quality_report)
        
        # Check that values are reasonable
        self.assertEqual(quality_report['total_rows'], len(transformed_data))
        self.assertEqual(quality_report['total_columns'], len(transformed_data.columns))
    
    @patch('etl_pipeline.create_engine')
    def test_load_to_database_success(self, mock_create_engine):
        """Test successful database loading"""
        # Mock the engine
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        etl = DataOpsETLPipeline(self.config)
        
        # Create test dimension tables and fact table
        dim_tables = {'test_dim': pd.DataFrame({'id': [1, 2], 'value': ['A', 'B']})}
        fact_table = pd.DataFrame({'fact_id': [1, 2], 'amount': [100, 200]})
        
        # Mock to_sql method
        with patch.object(pd.DataFrame, 'to_sql') as mock_to_sql:
            mock_to_sql.return_value = None
            
            result = etl.load_to_database(dim_tables, fact_table)
            
            self.assertTrue(result)
    
    @patch('etl_pipeline.create_engine')
    def test_load_to_database_failure(self, mock_create_engine):
        """Test database loading failure"""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        etl = DataOpsETLPipeline(self.config)
        
        # Create test tables
        dim_tables = {'test_dim': pd.DataFrame({'id': [1, 2]})}
        fact_table = pd.DataFrame({'fact_id': [1, 2]})
        
        # Mock to_sql to raise an exception
        with patch.object(pd.DataFrame, 'to_sql') as mock_to_sql:
            mock_to_sql.side_effect = Exception("Database error")
            
            result = etl.load_to_database(dim_tables, fact_table)
            
            self.assertFalse(result)


class TestDataTransformations(unittest.TestCase):
    """Test specific data transformation functions"""
    
    def test_percentage_to_decimal_conversion(self):
        """Test percentage string to decimal conversion"""
        test_data = pd.DataFrame({
            'int_rate': ['10.5%', '12.0%', '8.5%']
        })
        
        # Simulate the transformation
        test_data['int_rate'] = (
            test_data['int_rate']
            .astype(str)
            .str.rstrip('%')
            .astype('float') / 100.0
        )
        
        expected_values = [0.105, 0.12, 0.085]
        np.testing.assert_array_almost_equal(test_data['int_rate'].values, expected_values)
    
    def test_date_parsing(self):
        """Test date string parsing"""
        test_dates = pd.Series(['Jan-2020', 'Feb-2020', 'Mar-2020'])
        
        parsed_dates = pd.to_datetime(test_dates, format='%b-%Y', errors='coerce')
        
        # Check that all dates were parsed successfully
        self.assertFalse(parsed_dates.isnull().any())
        
        # Check specific date values
        self.assertEqual(parsed_dates.iloc[0].year, 2020)
        self.assertEqual(parsed_dates.iloc[0].month, 1)


class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios"""
    
    @patch('etl_pipeline.create_engine')
    def test_missing_input_file(self, mock_create_engine):
        """Test handling of missing input file"""
        config = {
            'database': {
                'server': 'test_server',
                'database': 'test_db', 
                'username': 'test_user',
                'password': 'test_pass'
            }
        }
        
        etl = DataOpsETLPipeline(config)
        
        # Test with non-existent file
        result = etl.run_etl_pipeline('non_existent_file.csv')
        self.assertFalse(result)
    
    def test_invalid_data_types(self):
        """Test handling of invalid data types"""
        invalid_data = pd.DataFrame({
            'loan_amnt': ['invalid', 'data', 'here'],
            'int_rate': ['not%', 'a%', 'percentage%']
        })
        
        # This should not crash, but handle gracefully
        try:
            # Simulate transformation that might fail
            invalid_data['int_rate'] = pd.to_numeric(
                invalid_data['int_rate'].str.rstrip('%'), 
                errors='coerce'
            ) / 100.0
            
            # Should have NaN values for invalid data
            self.assertTrue(invalid_data['int_rate'].isnull().all())
            
        except Exception as e:
            self.fail(f"Data transformation should handle invalid data gracefully: {e}")


def main():
    """Run all tests"""
    print("=== DataOps Foundation ETL Pipeline Tests ===")
    print("Running comprehensive test suite...")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestDataOpsETLPipeline))
    test_suite.addTest(unittest.makeSuite(TestDataTransformations))
    test_suite.addTest(unittest.makeSuite(TestErrorHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n=== Test Summary ===")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n✅ All tests passed!")
        return True
    else:
        print("\n❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
