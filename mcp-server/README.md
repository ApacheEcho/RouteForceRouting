# RouteForce MCP Server

A Model Context Protocol (MCP) server that provides route optimization and file system management capabilities for the RouteForce platform.

## Servers

### 1. Route Optimization Server
Provides route optimization and logistics management capabilities.

### 2. Filesystem Server  
Provides secure file system access within allowed directories.

## Features

### Route Optimization Server:
- **Route Optimization**: Access to genetic algorithms, simulated annealing, and multi-objective optimization
- **Analytics Integration**: Real-time performance metrics and route analytics
- **Demand Prediction**: ML-powered demand forecasting for delivery planning  
- **Delivery Reports**: Comprehensive reporting and data export capabilities
- **Resource Access**: Direct access to active routes, performance data, and algorithm configurations

### Filesystem Server:
- **Secure File Access**: Read/write files within allowed directories only
- **Directory Operations**: List, create, and manage directories
- **File Search**: Search for files by name pattern with glob support
- **File Statistics**: Get detailed file and directory information
- **Safety Features**: Path validation, file type restrictions, size limits

## Installation

1. Install dependencies:
```bash
npm install
```

2. Build the servers:
```bash
npm run build
```

3. Start the optimization server:
```bash
npm start
```

4. Start the filesystem server:
```bash
npm run start:filesystem
```

Or use the convenient launcher script:
```bash
# Default paths (RouteForce project directories)
./start-filesystem-server.sh

# Custom paths
./start-filesystem-server.sh /path/to/dir1 /path/to/dir2
```

## VS Code Integration

Both servers are configured for VS Code debugging via `.vscode/mcp.json`. Use VS Code's MCP debugging features to test and interact with the servers.

## Tools Available

### Route Optimization Server:
- `optimize_route` - Find optimal routes using various algorithms
- `get_route_analytics` - Get performance metrics and analytics
- `predict_demand` - ML-powered demand forecasting
- `generate_delivery_report` - Generate comprehensive delivery reports

### Filesystem Server:
- `read_file` - Read file contents with encoding support
- `write_file` - Write content to files
- `list_directory` - List directory contents with details
- `create_directory` - Create new directories
- `delete_file` - Delete files or directories
- `file_stats` - Get file/directory statistics
- `search_files` - Search files by glob patterns

## Security

The filesystem server implements several security measures:
- **Path Validation**: Only allows access to specified directories
- **File Type Restrictions**: Blocks dangerous file types (.exe, .bat, etc.)
- **Size Limits**: Maximum 10MB file read/write operations
- **Path Traversal Protection**: Prevents access outside allowed directories

## API Integration

The optimization server integrates with RouteForce API endpoints:
- `/api/v1/routes/optimize` - Route optimization
- `/api/v1/ml/predict` - ML predictions
- `/api/v1/analytics/routes` - Route analytics

## Development

For development with automatic rebuilding:
```bash
npm run dev
```

To watch for changes:
```bash
npm run watch
```

## Available Tools

### `optimize_route`
Optimize delivery routes using various algorithms (genetic, simulated_annealing, multi_objective).

### `get_route_analytics`  
Get comprehensive analytics for existing routes including distance, time, and efficiency metrics.

### `predict_demand`
Predict delivery demand for specific locations and time periods using ML models.

### `generate_delivery_report`
Generate detailed performance reports with customizable metrics and formats.

## Available Resources

### `routeforce://routes/active`
Access current active delivery routes and their status.

### `routeforce://analytics/performance` 
Real-time performance analytics and optimization metrics.

### `routeforce://config/algorithms`
Available optimization algorithms and their configuration parameters.

## Configuration

Set the RouteForce API URL via environment variable:
```bash
export ROUTEFORCE_API_URL=http://localhost:5000
```

## Integration with VS Code

This MCP server can be debugged and tested directly in VS Code using the MCP configuration.

## API Integration

The server integrates with the RouteForce API endpoints:
- `/api/v1/routes/optimize/*` - Route optimization
- `/api/v1/routes/*` - Route management  
- `/api/v1/ml/*` - Machine learning predictions
- `/api/v1/analytics` - Performance analytics
- `/api/v1/metrics` - System metrics

## License

MIT
