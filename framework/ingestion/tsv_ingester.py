from .base_ingester import BaseIngester

class TsvIngester(BaseIngester):
    def read_data(self, file_path: str):
        self.logger.info(f"Reading TSV data from {file_path}")
        return (
            self.spark.read
            .option("header", "true")  # First line as header
            .option("inferSchema", "true")  # Infer data types
            .option("delimiter", "\t")  # Set delimiter to tab
            .option("mode", "PERMISSIVE")  # Handle malformed TSV gracefully
            .csv(file_path)
        )