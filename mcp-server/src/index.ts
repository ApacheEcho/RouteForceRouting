import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ErrorCode,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  McpError,
  ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";

/**
 * RouteForce MCP Server
 * Provides route optimization and management capabilities through MCP protocol
 */

interface RouteOptimizationRequest {
  locations: Array<{
    id: string;
    name: string;
    address: string;
    lat: number;
    lng: number;
    priority?: number;
  }>;
  algorithm?: 'genetic' | 'simulated_annealing' | 'multi_objective';
  constraints?: {
    maxDistance?: number;
    maxTime?: number;
    vehicleCapacity?: number;
  };
}

interface RouteResult {
  routeId: string;
  totalDistance: number;
  totalTime: number;
  optimizedOrder: string[];
  algorithm: string;
  performance: {
    executionTime: number;
    iterations?: number;
  };
}

class RouteForceServer {
  private server: Server;
  private apiBaseUrl: string;

  constructor() {
    this.server = new Server(
      {
        name: "routeforce-mcp-server",
        version: "1.0.0",
      },
      {
        capabilities: {
          resources: {},
          tools: {},
        },
      }
    );

    this.apiBaseUrl = process.env.ROUTEFORCE_API_URL || "http://localhost:5000";
    this.setupToolHandlers();
    this.setupResourceHandlers();
  }

  private setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: "optimize_route",
            description: "Optimize delivery routes using various algorithms",
            inputSchema: {
              type: "object",
              properties: {
                locations: {
                  type: "array",
                  description: "Array of locations to visit",
                  items: {
                    type: "object",
                    properties: {
                      id: { type: "string" },
                      name: { type: "string" },
                      address: { type: "string" },
                      lat: { type: "number" },
                      lng: { type: "number" },
                      priority: { type: "number", optional: true },
                    },
                    required: ["id", "name", "address", "lat", "lng"],
                  },
                },
                algorithm: {
                  type: "string",
                  enum: ["genetic", "simulated_annealing", "multi_objective"],
                  description: "Optimization algorithm to use",
                  default: "genetic",
                },
                constraints: {
                  type: "object",
                  description: "Route constraints",
                  properties: {
                    maxDistance: { type: "number" },
                    maxTime: { type: "number" },
                    vehicleCapacity: { type: "number" },
                  },
                  optional: true,
                },
              },
              required: ["locations"],
            },
          },
          {
            name: "get_route_analytics",
            description: "Get analytics for existing routes",
            inputSchema: {
              type: "object",
              properties: {
                routeId: {
                  type: "string",
                  description: "ID of the route to analyze",
                },
                metrics: {
                  type: "array",
                  items: { type: "string" },
                  description: "Specific metrics to retrieve",
                  default: ["distance", "time", "efficiency"],
                },
              },
              required: ["routeId"],
            },
          },
          {
            name: "predict_demand",
            description: "Predict delivery demand for locations and time periods",
            inputSchema: {
              type: "object",
              properties: {
                locations: {
                  type: "array",
                  items: { type: "string" },
                  description: "Location IDs to predict demand for",
                },
                timeHorizon: {
                  type: "number",
                  description: "Prediction horizon in hours",
                  default: 24,
                },
                includeWeather: {
                  type: "boolean",
                  description: "Include weather factors in prediction",
                  default: false,
                },
              },
              required: ["locations"],
            },
          },
          {
            name: "generate_delivery_report",
            description: "Generate comprehensive delivery performance reports",
            inputSchema: {
              type: "object",
              properties: {
                dateRange: {
                  type: "object",
                  properties: {
                    start: { type: "string", format: "date" },
                    end: { type: "string", format: "date" },
                  },
                  required: ["start", "end"],
                },
                includeMetrics: {
                  type: "array",
                  items: { type: "string" },
                  default: ["efficiency", "cost", "time", "distance"],
                },
                format: {
                  type: "string",
                  enum: ["json", "csv", "pdf"],
                  default: "json",
                },
              },
              required: ["dateRange"],
            },
          },
        ],
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case "optimize_route":
            return await this.handleRouteOptimization(args as any);

          case "get_route_analytics":
            return await this.handleRouteAnalytics(args as any);

          case "predict_demand":
            return await this.handleDemandPrediction(args as any);

          case "generate_delivery_report":
            return await this.handleDeliveryReport(args as any);

          default:
            throw new McpError(ErrorCode.MethodNotFound, `Tool ${name} not found`);
        }
      } catch (error) {
        if (error instanceof McpError) {
          throw error;
        }
        throw new McpError(ErrorCode.InternalError, `Tool execution failed: ${error}`);
      }
    });
  }

  private setupResourceHandlers() {
    // List available resources
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => {
      return {
        resources: [
          {
            uri: "routeforce://routes/active",
            name: "Active Routes",
            description: "Current active delivery routes",
            mimeType: "application/json",
          },
          {
            uri: "routeforce://analytics/performance",
            name: "Performance Analytics",
            description: "Route optimization performance metrics",
            mimeType: "application/json",
          },
          {
            uri: "routeforce://config/algorithms",
            name: "Algorithm Configuration",
            description: "Available optimization algorithms and their parameters",
            mimeType: "application/json",
          },
        ],
      };
    });

    // Handle resource reads
    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const { uri } = request.params;

      try {
        switch (uri) {
          case "routeforce://routes/active":
            return await this.getActiveRoutes();

          case "routeforce://analytics/performance":
            return await this.getPerformanceAnalytics();

          case "routeforce://config/algorithms":
            return await this.getAlgorithmConfig();

          default:
            throw new McpError(ErrorCode.InvalidRequest, `Resource ${uri} not found`);
        }
      } catch (error) {
        if (error instanceof McpError) {
          throw error;
        }
        throw new McpError(ErrorCode.InternalError, `Resource read failed: ${error}`);
      }
    });
  }

  // Tool implementation methods
  private async handleRouteOptimization(request: RouteOptimizationRequest) {
    const algorithm = request.algorithm || 'genetic';
    const endpoint = `${this.apiBaseUrl}/api/v1/routes/optimize/${algorithm}`;

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        locations: request.locations,
        constraints: request.constraints,
      }),
    });

    if (!response.ok) {
      throw new Error(`Route optimization failed: ${response.statusText}`);
    }

    const result = await response.json() as any;

    return {
      content: [
        {
          type: "text",
          text: `Route optimization completed successfully!\n\n` +
                `Algorithm: ${algorithm}\n` +
                `Total Distance: ${result.total_distance || 'N/A'} km\n` +
                `Total Time: ${result.total_time || 'N/A'} minutes\n` +
                `Locations Optimized: ${request.locations.length}\n` +
                `Execution Time: ${result.execution_time || 'N/A'}ms\n\n` +
                `Optimized Route Order:\n${result.route_order ? result.route_order.map((id: string, index: number) => 
                  `${index + 1}. ${request.locations.find(loc => loc.id === id)?.name || id}`
                ).join('\n') : 'N/A'}`,
        },
      ],
    };
  }

  private async handleRouteAnalytics(args: { routeId: string; metrics?: string[] }) {
    const endpoint = `${this.apiBaseUrl}/api/v1/routes/${args.routeId}`;
    
    const response = await fetch(endpoint);
    if (!response.ok) {
      throw new Error(`Failed to fetch route analytics: ${response.statusText}`);
    }

    const route = await response.json() as any;
    const metrics = args.metrics || ['distance', 'time', 'efficiency'];

    let analyticsText = `Route Analytics for ${args.routeId}:\n\n`;
    
    if (metrics.includes('distance')) {
      analyticsText += `Distance: ${route.total_distance || 'N/A'} km\n`;
    }
    if (metrics.includes('time')) {
      analyticsText += `Time: ${route.total_time || 'N/A'} minutes\n`;
    }
    if (metrics.includes('efficiency')) {
      analyticsText += `Efficiency Score: ${route.efficiency_score || 'N/A'}/100\n`;
    }

    return {
      content: [
        {
          type: "text",
          text: analyticsText,
        },
      ],
    };
  }

  private async handleDemandPrediction(args: {
    locations: string[];
    timeHorizon?: number;
    includeWeather?: boolean;
  }) {
    const endpoint = `${this.apiBaseUrl}/api/v1/ml/predict`;
    
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        locations: args.locations,
        time_horizon: args.timeHorizon || 24,
        include_weather: args.includeWeather || false,
      }),
    });

    if (!response.ok) {
      throw new Error(`Demand prediction failed: ${response.statusText}`);
    }

    const prediction = await response.json() as any;

    return {
      content: [
        {
          type: "text",
          text: `Demand Prediction Results:\n\n` +
                `Locations: ${args.locations.join(', ')}\n` +
                `Time Horizon: ${args.timeHorizon || 24} hours\n` +
                `Weather Included: ${args.includeWeather ? 'Yes' : 'No'}\n\n` +
                `Predicted Demand: ${JSON.stringify(prediction.predictions || {}, null, 2)}`,
        },
      ],
    };
  }

  private async handleDeliveryReport(args: {
    dateRange: { start: string; end: string };
    includeMetrics?: string[];
    format?: string;
  }) {
    const endpoint = `${this.apiBaseUrl}/api/v1/analytics`;
    
    const response = await fetch(endpoint + 
      `?start_date=${args.dateRange.start}&end_date=${args.dateRange.end}`);
    
    if (!response.ok) {
      throw new Error(`Report generation failed: ${response.statusText}`);
    }

    const analytics = await response.json();
    const format = args.format || 'json';

    let reportText = `Delivery Report (${args.dateRange.start} to ${args.dateRange.end}):\n\n`;
    
    if (format === 'json') {
      reportText += JSON.stringify(analytics, null, 2);
    } else {
      reportText += `Format: ${format}\n`;
      reportText += `Metrics: ${(args.includeMetrics || []).join(', ')}\n`;
      reportText += `Data: ${JSON.stringify(analytics, null, 2)}`;
    }

    return {
      content: [
        {
          type: "text",
          text: reportText,
        },
      ],
    };
  }

  // Resource implementation methods
  private async getActiveRoutes() {
    const endpoint = `${this.apiBaseUrl}/api/v1/routes`;
    const response = await fetch(endpoint);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch active routes: ${response.statusText}`);
    }

    const routes = await response.json();

    return {
      contents: [
        {
          uri: "routeforce://routes/active",
          mimeType: "application/json",
          text: JSON.stringify(routes, null, 2),
        },
      ],
    };
  }

  private async getPerformanceAnalytics() {
    const endpoint = `${this.apiBaseUrl}/api/v1/metrics`;
    const response = await fetch(endpoint);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch performance analytics: ${response.statusText}`);
    }

    const metrics = await response.json();

    return {
      contents: [
        {
          uri: "routeforce://analytics/performance",
          mimeType: "application/json",
          text: JSON.stringify(metrics, null, 2),
        },
      ],
    };
  }

  private async getAlgorithmConfig() {
    const endpoint = `${this.apiBaseUrl}/api/v1/routes/algorithms`;
    const response = await fetch(endpoint);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch algorithm config: ${response.statusText}`);
    }

    const algorithms = await response.json();

    return {
      contents: [
        {
          uri: "routeforce://config/algorithms",
          mimeType: "application/json",
          text: JSON.stringify(algorithms, null, 2),
        },
      ],
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("RouteForce MCP server running on stdio");
  }
}

const server = new RouteForceServer();
server.run().catch(console.error);
