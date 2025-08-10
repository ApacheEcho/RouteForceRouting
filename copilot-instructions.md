# RouteForce MCP Server Instructions

## Overview
This project includes a Model Context Protocol (MCP) server that provides route optimization capabilities through a standardized interface.

## MCP Server Features
- Route optimization using multiple algorithms (genetic, simulated annealing, multi-objective)
- Real-time analytics and performance metrics
- Demand prediction using machine learning
- Comprehensive delivery reporting
- Direct API integration with RouteForce platform

## Development Setup
The MCP server is located in the `mcp-server/` directory and provides:

### Tools Available:
- `optimize_route` - Route optimization with algorithm selection
- `get_route_analytics` - Route performance analysis  
- `predict_demand` - ML-powered demand forecasting
- `generate_delivery_report` - Comprehensive reporting

### Resources Available:
- `routeforce://routes/active` - Active route data
- `routeforce://analytics/performance` - Performance metrics
- `routeforce://config/algorithms` - Algorithm configurations

## SDK Reference
For more information about MCP server development, see: https://github.com/modelcontextprotocol/create-python-server

## Integration
The server integrates directly with RouteForce API endpoints and can be used with any MCP-compatible client for advanced route optimization workflows.
