from .base_ingester import BaseIngester

class CsvIngester(BaseIngester):
    def read_data(self, file_path: str):
        self.logger.info(f"Reading CSV data from {file_path}")
        return (
            self.spark.read
            .option("header", "true")  # First line as header
            .option("inferSchema", "true")  # Infer data types
            .option("mode", "PERMISSIVE")  # Handle malformed CSV gracefully
            .csv(file_path)
        )