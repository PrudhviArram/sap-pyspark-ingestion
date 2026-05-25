from .json_ingester import JsonIngester
from .csv_ingester import CsvIngester
from .tsv_ingester import TsvIngester

def get_ingester(file_type: str, spark, config: dict):
    ingester_classes = {
        "json": JsonIngester,
        "csv": CsvIngester,
        "tsv": TsvIngester
    }
    
    ingester_class = ingester_classes.get(file_type.lower())
    if not ingester_class:
        raise ValueError(f"Unsupported file type: {file_type}. Supported types are: {list(ingester_classes.keys())}")
    
    return ingester_class(spark, config)