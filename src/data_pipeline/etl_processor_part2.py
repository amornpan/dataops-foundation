        if columns_removed:
            self.logger.warning(f"Removed {len(columns_removed)} columns with high null percentage: {columns_removed}")
        
        # Apply filter
        self.processed_data = self.raw_data[columns_to_keep].copy()
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Log results
        self.logger.info(f"Filtered data: {len(columns_to_keep)} columns kept, {len(columns_removed)} removed")
        
        result = ProcessingResult(
            success=True,
            message=f"Filtered columns by null percentage (threshold: {max_null_pct}%)",
            data=self.processed_data.copy(),
            metadata={
                'columns_kept': columns_to_keep,
                'columns_removed': columns_removed,
                'threshold': max_null_pct,
                'original_columns': self.raw_data.shape[1],
                'filtered_columns': len(columns_to_keep)
            },
            processing_time=processing_time,
            warnings=[f"Removed {len(columns_removed)} columns"] if columns_removed else []
        )
        
        return result
    
    def filter_by_row_completeness(self, min_acceptable_nulls: Optional[int] = None) -> ProcessingResult:
        """
        Filter rows based on acceptable null count per row
        
        Args:
            min_acceptable_nulls: Maximum acceptable null values per row
            
        Returns:
            ProcessingResult with filtered data
        """
        if self.processed_data is None:
            raise ValueError("No processed data available. Run filter_by_null_percentage() first.")
        
        start_time = datetime.now()
        max_nulls = min_acceptable_nulls or self.acceptable_max_null
        
        self.logger.info(f"Filtering rows with null count <= {max_nulls}")
        
        # Calculate null count per row
        null_count_per_row = self.processed_data.isnull().sum(axis=1)
        
        # Filter rows
        rows_to_keep = null_count_per_row <= max_nulls
        rows_removed = (~rows_to_keep).sum()
        
        self.processed_data = self.processed_data[rows_to_keep].copy()
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Log results
        self.logger.info(f"Filtered rows: {len(self.processed_data)} rows kept, {rows_removed} removed")
        
        result = ProcessingResult(
            success=True,
            message=f"Filtered rows by null count (max nulls: {max_nulls})",
            data=self.processed_data.copy(),
            metadata={
                'rows_kept': len(self.processed_data),
                'rows_removed': rows_removed,
                'max_nulls_threshold': max_nulls,
                'null_count_stats': null_count_per_row.describe().to_dict()
            },
            processing_time=processing_time,
            warnings=[f"Removed {rows_removed} rows"] if rows_removed > 0 else []
        )
        
        return result
    
    def apply_data_transformations(self) -> ProcessingResult:
        """
        Apply data transformations based on inferred types
        
        Returns:
            ProcessingResult with transformed data
        """
        if self.processed_data is None:
            raise ValueError("No processed data available.")
        
        start_time = datetime.now()
        
        self.logger.info("Applying data transformations...")
        
        transformation_log = []
        
        for column, type_info in self.column_types.items():
            if column not in self.processed_data.columns:
                continue
            
            try:
                if type_info.inferred_type == DataTypeEnum.DATETIME.value:
                    # Convert to datetime
                    if column == 'issue_d':  # Special handling for issue_d format
                        self.processed_data[column] = pd.to_datetime(
                            self.processed_data[column], 
                            format='%b-%Y'
                        )
                    else:
                        self.processed_data[column] = pd.to_datetime(
                            self.processed_data[column]
                        )
                    transformation_log.append(f"{column}: converted to datetime")
                    
                elif type_info.inferred_type == DataTypeEnum.DATE.value:
                    # Convert to date
                    self.processed_data[column] = pd.to_datetime(
                        self.processed_data[column]
                    ).dt.date
                    transformation_log.append(f"{column}: converted to date")
                    
                elif type_info.inferred_type == DataTypeEnum.FLOAT.value:
                    # Handle special cases like percentage strings
                    if column == 'int_rate' and self.processed_data[column].dtype == 'object':
                        # Remove % sign and convert to float
                        self.processed_data[column] = (
                            self.processed_data[column]
                            .str.rstrip('%')
                            .astype('float') / 100.0
                        )
                        transformation_log.append(f"{column}: converted percentage to float")
                    else:
                        self.processed_data[column] = pd.to_numeric(
                            self.processed_data[column], 
                            errors='coerce'
                        )
                        transformation_log.append(f"{column}: converted to float")
                        
                elif type_info.inferred_type == DataTypeEnum.INTEGER.value:
                    self.processed_data[column] = pd.to_numeric(
                        self.processed_data[column], 
                        errors='coerce'
                    ).astype('Int64')  # Nullable integer
                    transformation_log.append(f"{column}: converted to integer")
                    
                elif type_info.inferred_type == DataTypeEnum.CATEGORICAL.value:
                    self.processed_data[column] = self.processed_data[column].astype('category')
                    transformation_log.append(f"{column}: converted to category")
                    
            except Exception as e:
                warning_msg = f"Failed to transform column {column}: {str(e)}"
                self.logger.warning(warning_msg)
                transformation_log.append(warning_msg)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        self.logger.info(f"Data transformations completed: {len(transformation_log)} transformations applied")
        
        result = ProcessingResult(
            success=True,
            message="Data transformations applied successfully",
            data=self.processed_data.copy(),
            metadata={
                'transformations_applied': transformation_log,
                'final_dtypes': self.processed_data.dtypes.to_dict()
            },
            processing_time=processing_time
        )
        
        return result
    
    def run_quality_checks(self) -> ProcessingResult:
        """
        Run comprehensive data quality checks
        
        Returns:
            ProcessingResult with quality check results
        """
        if self.processed_data is None:
            raise ValueError("No processed data available.")
        
        start_time = datetime.now()
        
        self.logger.info("Running data quality checks...")
        
        # Run quality checks
        quality_result = self.quality_checker.run_checks(self.processed_data)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        self.logger.info(f"Quality checks completed: {quality_result.overall_score:.2f}% passed")
        
        result = ProcessingResult(
            success=quality_result.overall_score >= 80,  # 80% threshold
            message=f"Data quality check completed (score: {quality_result.overall_score:.2f}%)",
            data=self.processed_data.copy(),
            metadata={
                'quality_score': quality_result.overall_score,
                'checks_passed': quality_result.checks_passed,
                'checks_failed': quality_result.checks_failed,
                'detailed_results': quality_result.detailed_results
            },
            processing_time=processing_time,
            warnings=quality_result.warnings
        )
        
        return result
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """
        Get summary of processing operations
        
        Returns:
            Dictionary with processing summary
        """
        if self.raw_data is None:
            return {'status': 'No data loaded'}
        
        summary = {
            'data_loaded': True,
            'original_shape': self.raw_data.shape,
            'processed_shape': self.processed_data.shape if self.processed_data is not None else None,
            'column_types': {
                col: {
                    'type': info.inferred_type,
                    'confidence': info.confidence,
                    'null_percentage': info.null_percentage
                }
                for col, info in self.column_types.items()
            },
            'processing_history': self.processing_history,
            'memory_usage': {
                'raw_data': self.raw_data.memory_usage(deep=True).sum(),
                'processed_data': self.processed_data.memory_usage(deep=True).sum() if self.processed_data is not None else 0
            }
        }
        
        return summary
    
    def export_processed_data(self, output_path: Union[str, Path], 
                            format: str = 'csv', 
                            **kwargs) -> ProcessingResult:
        """
        Export processed data to file
        
        Args:
            output_path: Output file path
            format: Export format ('csv', 'parquet', 'json', 'excel')
            **kwargs: Additional export parameters
            
        Returns:
            ProcessingResult with export status
        """
        if self.processed_data is None:
            raise ValueError("No processed data available for export.")
        
        start_time = datetime.now()
        output_path = Path(output_path)
        
        try:
            if format.lower() == 'csv':
                self.processed_data.to_csv(output_path, index=False, **kwargs)
            elif format.lower() == 'parquet':
                self.processed_data.to_parquet(output_path, **kwargs)
            elif format.lower() == 'json':
                self.processed_data.to_json(output_path, **kwargs)
            elif format.lower() == 'excel':
                self.processed_data.to_excel(output_path, index=False, **kwargs)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"Data exported successfully to {output_path}")
            
            result = ProcessingResult(
                success=True,
                message=f"Data exported to {output_path} ({format} format)",
                metadata={
                    'output_path': str(output_path),
                    'format': format,
                    'file_size': output_path.stat().st_size,
                    'rows_exported': len(self.processed_data)
                },
                processing_time=processing_time
            )
            
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Export failed: {str(e)}"
            self.logger.error(error_msg)
            
            return ProcessingResult(
                success=False,
                message=error_msg,
                errors=[error_msg],
                processing_time=processing_time
            )


def main():
    """
    Example usage of ETL Processor
    """
    # Initialize processor
    processor = ETLProcessor()
    
    # Example workflow
    try:
        # Load data
        result = processor.load_data('examples/sample_data/sample_loans.csv')
        if not result.success:
            print(f"Failed to load data: {result.message}")
            return
        
        # Infer column types
        processor.infer_column_types()
        
        # Filter by null percentage
        result = processor.filter_by_null_percentage()
        if not result.success:
            print(f"Failed to filter columns: {result.message}")
            return
        
        # Filter by row completeness
        result = processor.filter_by_row_completeness()
        if not result.success:
            print(f"Failed to filter rows: {result.message}")
            return
        
        # Apply transformations
        result = processor.apply_data_transformations()
        if not result.success:
            print(f"Failed to transform data: {result.message}")
            return
        
        # Run quality checks
        result = processor.run_quality_checks()
        print(f"Quality check result: {result.message}")
        
        # Get processing summary
        summary = processor.get_processing_summary()
        print(f"Processing completed. Final shape: {summary['processed_shape']}")
        
    except Exception as e:
        print(f"Error in processing: {str(e)}")


if __name__ == "__main__":
    main()
