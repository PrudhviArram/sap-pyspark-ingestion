#This is the reusable engine. A 'base class' holds all the common logic. 
#Each file type (JSON/CSV/TSV) has a small class that extends it — like filling in a form template.

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
import logging

class BaseIngester:
    def __init__(self, spark: SparkSession, logger: logging.Logger, config: dict):
        self.spark = spark
        self.logger = logger.getLogger(self.__class__.__name__)
        self.config = config
    
    def read_data(self, file_path: str) -> DataFrame:
        raise NotImplementedError("Subclasses must implement read_data method")

    def add_metadata(self, df: DataFrame, source_path: str) -> DataFrame:
        return ( df.withColumn("ingestion_timestamp", F.current_timestamp()) 
                   .withColumn("source_file", F.lit(source_path)) 
                   .withColumn("ingestion_date", F.current_date())
                )
    
    def validate_data(self, df: DataFrame) -> bool:
        # Basic validation: check if DataFrame is not empty
        if df.rdd.isEmpty():
            self.logger.warning("DataFrame is empty after reading data.")
            return False
        return True

    def write_data(self, df: DataFrame, output_path: str, fmt: str = "parquet", mode: str = "overwrite"):
        (
            df.write.format(fmt)
              .mode(mode)
              .options('mergeSchema', 'true')
              .save(output_path)
        )
        self.logger.info(f"Data written to {output_path} in {fmt} format.")
    
    def ingest(self, source_path: str, output_path: str, fmt: str = "parquet"):
        self.logger.info(f"Starting ingestion for {source_path}")
        df = self.read_data(source_path)
        
        if not self.validate_data(df):
            self.logger.error("Data validation failed. Ingestion aborted.")
            return
        
        df_with_metadata = self.add_metadata(df, source_path)
        self.write_data(df_with_metadata, output_path, fmt)
        self.logger.info(f"Ingestion completed for {source_path}")
        return df_with_metadata

