import logging

log = logging.getLogger('etl_logger') # logger name : etl_logger

log.setLevel(logging.INFO) # it ensures that error and other infos are shown

# Create console handler
console = logging.StreamHandler()
console.setLevel(logging.INFO)

# Create log format
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    "%Y-%m-%d %H-%M-%S"
)
# 2025-01-01 12:25:01 - INFO - Loading 5000 rows into warehouse.dim_customers

console.setFormatter(formatter) # console format set

# Attach handler to logger 
log.addHandler(console)