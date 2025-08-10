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
import { promises as fs } from 'fs';
import * as path from 'path';

/**
 * RouteForce Filesystem MCP Server
 * Provides file system access and management capabilities for RouteForce project
 */

interface FileSystemConfig {
  allowedPaths: string[];
  maxFileSize: number;
  allowedExtensions: string[];
}

class RouteForceFilesystemServer {
  private server: Server;
  private config: FileSystemConfig;

  constructor() {
    this.server = new Server(
      {
        name: "routeforce-filesystem-server",
        version: "1.0.0",
      },
      {
        capabilities: {
          resources: {},
          tools: {},
        },
      }
    );

    // Default configuration - can be overridden by environment variables
    this.config = {
      allowedPaths: [
        process.cwd(), // Current directory
        path.join(process.cwd(), '..'), // Parent RouteForce directory
        ...process.argv.slice(2), // Additional paths from command line
      ],
      maxFileSize: 10 * 1024 * 1024, // 10MB
      allowedExtensions: [
        '.py', '.js', '.ts', '.tsx', '.jsx', '.json', '.yaml', '.yml',
        '.md', '.txt', '.csv', '.sql', '.html', '.css', '.scss',
        '.env', '.gitignore', '.dockerignore', '.toml', '.ini'
      ],
    };

    this.setupToolHandlers();
    this.setupResourceHandlers();
  }

  private isPathAllowed(targetPath: string): boolean {
    const resolvedPath = path.resolve(targetPath);
    return this.config.allowedPaths.some(allowedPath => {
      const resolvedAllowed = path.resolve(allowedPath);
      return resolvedPath.startsWith(resolvedAllowed);
    });
  }

  private isFileAllowed(filePath: string): boolean {
    const ext = path.extname(filePath).toLowerCase();
    return this.config.allowedExtensions.includes(ext) || ext === '';
  }

  private setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: "read_file",
            description: "Read contents of a file within allowed directories",
            inputSchema: {
              type: "object",
              properties: {
                path: {
                  type: "string",
                  description: "Path to the file to read",
                },
                encoding: {
                  type: "string",
                  description: "File encoding (default: utf8)",
                  default: "utf8",
                },
              },
              required: ["path"],
            },
          },
          {
            name: "write_file",
            description: "Write content to a file within allowed directories",
            inputSchema: {
              type: "object",
              properties: {
                path: {
                  type: "string",
                  description: "Path to the file to write",
                },
                content: {
                  type: "string",
                  description: "Content to write to the file",
                },
                encoding: {
                  type: "string",
                  description: "File encoding (default: utf8)",
                  default: "utf8",
                },
              },
              required: ["path", "content"],
            },
          },
          {
            name: "list_directory",
            description: "List contents of a directory within allowed paths",
            inputSchema: {
              type: "object",
              properties: {
                path: {
                  type: "string",
                  description: "Path to the directory to list",
                },
                recursive: {
                  type: "boolean",
                  description: "List recursively (default: false)",
                  default: false,
                },
                includeHidden: {
                  type: "boolean",
                  description: "Include hidden files (default: false)",
                  default: false,
                },
              },
              required: ["path"],
            },
          },
          {
            name: "create_directory",
            description: "Create a directory within allowed paths",
            inputSchema: {
              type: "object",
              properties: {
                path: {
                  type: "string",
                  description: "Path to the directory to create",
                },
                recursive: {
                  type: "boolean",
                  description: "Create parent directories if needed (default: true)",
                  default: true,
                },
              },
              required: ["path"],
            },
          },
          {
            name: "delete_file",
            description: "Delete a file within allowed directories",
            inputSchema: {
              type: "object",
              properties: {
                path: {
                  type: "string",
                  description: "Path to the file to delete",
                },
              },
              required: ["path"],
            },
          },
          {
            name: "file_stats",
            description: "Get file or directory statistics",
            inputSchema: {
              type: "object",
              properties: {
                path: {
                  type: "string",
                  description: "Path to the file or directory",
                },
              },
              required: ["path"],
            },
          },
          {
            name: "search_files",
            description: "Search for files by name pattern within allowed directories",
            inputSchema: {
              type: "object",
              properties: {
                pattern: {
                  type: "string",
                  description: "Search pattern (supports glob patterns)",
                },
                directory: {
                  type: "string",
                  description: "Directory to search in (default: current)",
                  default: ".",
                },
                recursive: {
                  type: "boolean",
                  description: "Search recursively (default: true)",
                  default: true,
                },
              },
              required: ["pattern"],
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
          case "read_file":
            return await this.handleReadFile(args as any);
          case "write_file":
            return await this.handleWriteFile(args as any);
          case "list_directory":
            return await this.handleListDirectory(args as any);
          case "create_directory":
            return await this.handleCreateDirectory(args as any);
          case "delete_file":
            return await this.handleDeleteFile(args as any);
          case "file_stats":
            return await this.handleFileStats(args as any);
          case "search_files":
            return await this.handleSearchFiles(args as any);
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
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => {
      const resources = [];
      
      for (const allowedPath of this.config.allowedPaths) {
        try {
          const resolvedPath = path.resolve(allowedPath);
          const stats = await fs.stat(resolvedPath);
          if (stats.isDirectory()) {
            resources.push({
              uri: `file://${resolvedPath}`,
              name: `Directory: ${path.basename(resolvedPath)}`,
              description: `File system access to ${resolvedPath}`,
              mimeType: "inode/directory",
            });
          }
        } catch (error) {
          // Skip paths that don't exist
        }
      }

      return { resources };
    });

    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const { uri } = request.params;
      
      if (!uri.startsWith("file://")) {
        throw new McpError(ErrorCode.InvalidRequest, "Only file:// URIs are supported");
      }

      const filePath = uri.substring(7); // Remove "file://" prefix
      
      if (!this.isPathAllowed(filePath)) {
        throw new McpError(ErrorCode.InvalidRequest, "Path not allowed");
      }

      try {
        const stats = await fs.stat(filePath);
        if (stats.isDirectory()) {
          const files = await fs.readdir(filePath);
          return {
            contents: [
              {
                uri,
                mimeType: "application/json",
                text: JSON.stringify(files, null, 2),
              },
            ],
          };
        } else {
          const content = await fs.readFile(filePath, 'utf8');
          return {
            contents: [
              {
                uri,
                mimeType: "text/plain",
                text: content,
              },
            ],
          };
        }
      } catch (error) {
        throw new McpError(ErrorCode.InternalError, `Failed to read resource: ${error}`);
      }
    });
  }

  // Tool implementation methods
  private async handleReadFile(args: { path: string; encoding?: string }) {
    if (!this.isPathAllowed(args.path)) {
      throw new Error(`Path not allowed: ${args.path}`);
    }

    if (!this.isFileAllowed(args.path)) {
      throw new Error(`File type not allowed: ${path.extname(args.path)}`);
    }

    try {
      const stats = await fs.stat(args.path);
      if (stats.size > this.config.maxFileSize) {
        throw new Error(`File too large: ${stats.size} bytes (max: ${this.config.maxFileSize})`);
      }

      const content = await fs.readFile(args.path, (args.encoding as BufferEncoding) || 'utf8');
      
      return {
        content: [
          {
            type: "text",
            text: `File: ${args.path}\nSize: ${stats.size} bytes\n\n${content}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to read file: ${error}`);
    }
  }

  private async handleWriteFile(args: { path: string; content: string; encoding?: string }) {
    if (!this.isPathAllowed(args.path)) {
      throw new Error(`Path not allowed: ${args.path}`);
    }

    if (!this.isFileAllowed(args.path)) {
      throw new Error(`File type not allowed: ${path.extname(args.path)}`);
    }

    try {
      // Ensure directory exists
      const dir = path.dirname(args.path);
      await fs.mkdir(dir, { recursive: true });
      
      await fs.writeFile(args.path, args.content, (args.encoding as BufferEncoding) || 'utf8');
      
      return {
        content: [
          {
            type: "text",
            text: `Successfully wrote ${args.content.length} characters to ${args.path}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to write file: ${error}`);
    }
  }

  private async handleListDirectory(args: { path: string; recursive?: boolean; includeHidden?: boolean }) {
    if (!this.isPathAllowed(args.path)) {
      throw new Error(`Path not allowed: ${args.path}`);
    }

    try {
      const listDir = async (dirPath: string, currentDepth = 0): Promise<string[]> => {
        const entries = await fs.readdir(dirPath, { withFileTypes: true });
        const results: string[] = [];

        for (const entry of entries) {
          if (!args.includeHidden && entry.name.startsWith('.')) {
            continue;
          }

          const fullPath = path.join(dirPath, entry.name);
          const relativePath = path.relative(args.path, fullPath);
          
          if (entry.isDirectory()) {
            results.push(`📁 ${relativePath}/`);
            if (args.recursive) {
              const subFiles = await listDir(fullPath, currentDepth + 1);
              results.push(...subFiles);
            }
          } else {
            const stats = await fs.stat(fullPath);
            results.push(`📄 ${relativePath} (${stats.size} bytes)`);
          }
        }

        return results;
      };

      const files = await listDir(args.path);
      
      return {
        content: [
          {
            type: "text",
            text: `Directory listing for: ${args.path}\n\n${files.join('\n')}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to list directory: ${error}`);
    }
  }

  private async handleCreateDirectory(args: { path: string; recursive?: boolean }) {
    if (!this.isPathAllowed(args.path)) {
      throw new Error(`Path not allowed: ${args.path}`);
    }

    try {
      await fs.mkdir(args.path, { recursive: args.recursive !== false });
      
      return {
        content: [
          {
            type: "text",
            text: `Successfully created directory: ${args.path}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to create directory: ${error}`);
    }
  }

  private async handleDeleteFile(args: { path: string }) {
    if (!this.isPathAllowed(args.path)) {
      throw new Error(`Path not allowed: ${args.path}`);
    }

    try {
      const stats = await fs.stat(args.path);
      
      if (stats.isDirectory()) {
        await fs.rmdir(args.path);
      } else {
        await fs.unlink(args.path);
      }
      
      return {
        content: [
          {
            type: "text",
            text: `Successfully deleted: ${args.path}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to delete: ${error}`);
    }
  }

  private async handleFileStats(args: { path: string }) {
    if (!this.isPathAllowed(args.path)) {
      throw new Error(`Path not allowed: ${args.path}`);
    }

    try {
      const stats = await fs.stat(args.path);
      
      const statsInfo = {
        path: args.path,
        size: stats.size,
        type: stats.isDirectory() ? 'directory' : 'file',
        created: stats.birthtime.toISOString(),
        modified: stats.mtime.toISOString(),
        accessed: stats.atime.toISOString(),
        permissions: `0${(stats.mode & parseInt('777', 8)).toString(8)}`,
        isReadable: (stats.mode & parseInt('444', 8)) !== 0,
        isWritable: (stats.mode & parseInt('222', 8)) !== 0,
        isExecutable: (stats.mode & parseInt('111', 8)) !== 0,
      };
      
      return {
        content: [
          {
            type: "text",
            text: `File Statistics for: ${args.path}\n\n${JSON.stringify(statsInfo, null, 2)}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to get file stats: ${error}`);
    }
  }

  private async handleSearchFiles(args: { pattern: string; directory?: string; recursive?: boolean }) {
    const searchDir = args.directory || '.';
    
    if (!this.isPathAllowed(searchDir)) {
      throw new Error(`Path not allowed: ${searchDir}`);
    }

    try {
      const searchInDir = async (dirPath: string): Promise<string[]> => {
        const entries = await fs.readdir(dirPath, { withFileTypes: true });
        const results: string[] = [];

        for (const entry of entries) {
          const fullPath = path.join(dirPath, entry.name);
          
          // Simple pattern matching (could be enhanced with proper glob support)
          const matches = entry.name.toLowerCase().includes(args.pattern.toLowerCase()) ||
                         (args.pattern.includes('*') && 
                          new RegExp(args.pattern.replace(/\*/g, '.*')).test(entry.name));

          if (matches) {
            const relativePath = path.relative(searchDir, fullPath);
            if (entry.isDirectory()) {
              results.push(`📁 ${relativePath}/`);
            } else {
              results.push(`📄 ${relativePath}`);
            }
          }

          if (entry.isDirectory() && args.recursive !== false) {
            const subResults = await searchInDir(fullPath);
            results.push(...subResults);
          }
        }

        return results;
      };

      const results = await searchInDir(searchDir);
      
      return {
        content: [
          {
            type: "text",
            text: `Search results for "${args.pattern}" in ${searchDir}:\n\n${results.length > 0 ? results.join('\n') : 'No matches found'}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Search failed: ${error}`);
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    
    console.error("RouteForce Filesystem MCP server running on stdio");
    console.error(`Allowed paths: ${this.config.allowedPaths.join(', ')}`);
    console.error(`Max file size: ${this.config.maxFileSize} bytes`);
    console.error(`Allowed extensions: ${this.config.allowedExtensions.join(', ')}`);
  }
}

const server = new RouteForceFilesystemServer();
server.run().catch(console.error);
