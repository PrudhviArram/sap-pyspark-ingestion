from .base_ingester import BaseIngester

class JsonIngester(BaseIngester):
    def read_data(self, file_path: str):
        self.logger.info(f"Reading JSON data from {file_path}")
        return (
            self.spark.read
            .option("multiline", "true")  # Handle multi-line JSON files
            .option("mode", "PERMISSIVE")  # Handle malformed JSON gracefully
            .json(file_path)
        )
        