# Routing configuration constants

# Distance and optimization settings
MAX_DISTANCE_KM = 50  # Maximum distance between consecutive stops
KEY_ACCOUNT_WEIGHT = 1.5  # Weight multiplier for key accounts
ROUTING_ENGINE_VERSION = "v1.0"

# Geocoding settings
GEOCODING_TIMEOUT = 10  # Timeout for geocoding requests in seconds
GEOCODING_RETRY_ATTEMPTS = 3  # Number of retry attempts for failed geocoding

# Route optimization settings
MAX_STORES_PER_ROUTE = 100  # Maximum number of stores in a single route
ROUTE_OPTIMIZATION_TIMEOUT = 300  # Timeout for route optimization in seconds

# File processing settings
MAX_FILE_SIZE_MB = 100  # Maximum file size for processing
SUPPORTED_FILE_EXTENSIONS = ('.csv', '.xlsx', '.xls')

# Map settings
DEFAULT_MAP_ZOOM_LEVEL = 12  # Default zoom level for map links