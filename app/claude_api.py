"""
Claude Opus 4.1 API Endpoints for RouteForce
Provides REST API endpoints for AI-powered route analysis and optimization
"""

from flask import Blueprint, request, jsonify, current_app
import asyncio
import functools
import logging
from typing import Dict, Any

from app.claude_integration import ClaudeOpus4Service, create_claude_service
from app.security import require_api_key


logger = logging.getLogger(__name__)

# Create Blueprint for Claude API endpoints
claude_bp = Blueprint('claude', __name__, url_prefix='/api/claude')


def async_route(f):
    """Decorator to handle async functions in Flask routes"""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(f(*args, **kwargs))
    return wrapper


@claude_bp.route('/health', methods=['GET'])
def claude_health():
    """Health check for Claude integration"""
    try:
        # Check if API key is configured
        service = create_claude_service()
        return jsonify({
            "status": "healthy",
            "service": "Claude Opus 4.1",
            "model": service.config.model,
            "configured": True
        })
    except ValueError as e:
        return jsonify({
            "status": "unhealthy",
            "service": "Claude Opus 4.1",
            "error": str(e),
            "configured": False
        }), 500
    except Exception as e:
        logger.error(f"Claude health check failed: {str(e)}")
        return jsonify({
            "status": "error",
            "service": "Claude Opus 4.1",
            "error": "Health check failed",
            "configured": False
        }), 500


@claude_bp.route('/optimize-route', methods=['POST'])
@require_api_key
@async_route
async def optimize_route():
    """
    Optimize a route using Claude Opus 4.1 AI analysis
    
    Expects JSON payload:
    {
        "route_data": {
            "stops": [...],
            "constraints": {...},
            "current_route": [...],
            "objectives": ["distance", "time", "fuel"]
        },
        "optimization_goals": ["distance", "time", "fuel_efficiency"]
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        route_data = data.get('route_data')
        if not route_data:
            return jsonify({"error": "route_data is required"}), 400

        optimization_goals = data.get('optimization_goals', ["distance", "time", "fuel_efficiency"])

        service = create_claude_service()
        try:
            result = await service.optimize_route_with_ai(route_data, optimization_goals)
            
            if result.get('success'):
                return jsonify({
                    "status": "success",
                    "optimization_result": result['analysis'],
                    "model_used": result['model_used'],
                    "timestamp": result['timestamp']
                })
            else:
                return jsonify({
                    "status": "error",
                    "error": result.get('error', 'Unknown error'),
                    "timestamp": result.get('timestamp')
                }), 500

        finally:
            await service.close()

    except Exception as e:
        logger.error(f"Route optimization failed: {str(e)}")
        return jsonify({
            "status": "error",
            "error": "Route optimization failed",
            "details": str(e)
        }), 500


@claude_bp.route('/analyze-performance', methods=['POST'])
@require_api_key
@async_route
async def analyze_performance():
    """
    Analyze route performance using Claude Opus 4.1
    
    Expects JSON payload:
    {
        "route_history": [
            {
                "route_id": "...",
                "date": "...",
                "metrics": {...},
                "performance_data": {...}
            }
        ],
        "metrics": ["efficiency", "punctuality", "fuel_consumption"]
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        route_history = data.get('route_history')
        if not route_history:
            return jsonify({"error": "route_history is required"}), 400

        metrics = data.get('metrics', ["efficiency", "punctuality", "fuel_consumption", "customer_satisfaction"])

        service = create_claude_service()
        try:
            result = await service.analyze_route_performance(route_history, metrics)
            
            if result.get('success'):
                return jsonify({
                    "status": "success",
                    "performance_analysis": result['analysis'],
                    "model_used": result['model_used'],
                    "timestamp": result['timestamp']
                })
            else:
                return jsonify({
                    "status": "error",
                    "error": result.get('error', 'Unknown error'),
                    "timestamp": result.get('timestamp')
                }), 500

        finally:
            await service.close()

    except Exception as e:
        logger.error(f"Performance analysis failed: {str(e)}")
        return jsonify({
            "status": "error",
            "error": "Performance analysis failed",
            "details": str(e)
        }), 500


@claude_bp.route('/insights', methods=['POST'])
@require_api_key
@async_route
async def generate_insights():
    """
    Generate intelligent insights using Claude Opus 4.1
    
    Expects JSON payload:
    {
        "query": "What can you tell me about route efficiency patterns?",
        "context_data": {
            "optional": "context data to inform the response"
        }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        query = data.get('query')
        if not query:
            return jsonify({"error": "query is required"}), 400

        context_data = data.get('context_data')

        service = create_claude_service()
        try:
            result = await service.generate_route_insights(query, context_data)
            
            if result.get('success'):
                return jsonify({
                    "status": "success",
                    "insights": result['insights'],
                    "query": result['query'],
                    "model_used": result['model_used'],
                    "timestamp": result['timestamp']
                })
            else:
                return jsonify({
                    "status": "error",
                    "error": result.get('error', 'Unknown error'),
                    "timestamp": result.get('timestamp')
                }), 500

        finally:
            await service.close()

    except Exception as e:
        logger.error(f"Insight generation failed: {str(e)}")
        return jsonify({
            "status": "error",
            "error": "Insight generation failed",
            "details": str(e)
        }), 500


@claude_bp.route('/chat', methods=['POST'])
@require_api_key
@async_route
async def chat_with_claude():
    """
    Chat interface for Claude Opus 4.1
    
    Expects JSON payload:
    {
        "message": "User message to Claude",
        "context": "Optional context about routing/logistics",
        "conversation_history": [
            {"role": "user", "content": "previous message"},
            {"role": "assistant", "content": "previous response"}
        ]
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        message = data.get('message')
        if not message:
            return jsonify({"error": "message is required"}), 400

        context = data.get('context', '')
        conversation_history = data.get('conversation_history', [])

        # Build the conversation
        messages = []
        
        # Add conversation history
        for msg in conversation_history[-10:]:  # Limit to last 10 messages
            if msg.get('role') in ['user', 'assistant']:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })

        # Add current message with context
        if context:
            user_content = f"Context: {context}\n\nUser: {message}"
        else:
            user_content = message

        messages.append({
            "role": "user", 
            "content": user_content
        })

        service = create_claude_service()
        try:
            system_prompt = """You are Claude Opus 4.1, an intelligent assistant specialized in 
            routing, logistics, and transportation optimization. You help users with route planning, 
            performance analysis, cost optimization, and strategic logistics decisions. Provide 
            helpful, accurate, and actionable responses."""

            response = await service._make_request(messages, system_prompt)
            content = response.get("content", [])
            
            if content and len(content) > 0:
                assistant_message = content[0].get("text", "")
                return jsonify({
                    "status": "success",
                    "response": assistant_message,
                    "model_used": service.config.model,
                    "timestamp": result.get('timestamp', ''),
                    "conversation_id": data.get('conversation_id', '')
                })
            else:
                return jsonify({
                    "status": "error",
                    "error": "No response from Claude",
                    "response": response
                }), 500

        finally:
            await service.close()

    except Exception as e:
        logger.error(f"Chat failed: {str(e)}")
        return jsonify({
            "status": "error",
            "error": "Chat failed",
            "details": str(e)
        }), 500


@claude_bp.route('/models', methods=['GET'])
def list_models():
    """List available Claude models and current configuration"""
    try:
        service = create_claude_service()
        return jsonify({
            "current_model": service.config.model,
            "available_models": [
                {
                    "name": "claude-opus-4-1-20250805",
                    "description": "Claude Opus 4.1 - Most intelligent model with hybrid reasoning",
                    "use_cases": ["complex coding", "agentic tasks", "deep analysis"],
                    "current": service.config.model == "claude-opus-4-1-20250805"
                },
                {
                    "name": "claude-opus-4-20250514",
                    "description": "Claude Opus 4 - Previous version",
                    "use_cases": ["coding", "analysis", "creative writing"],
                    "current": service.config.model == "claude-opus-4-20250514"
                },
                {
                    "name": "claude-sonnet-4-20250514",
                    "description": "Claude Sonnet 4 - Balanced performance and speed",
                    "use_cases": ["everyday tasks", "rapid processing"],
                    "current": service.config.model == "claude-sonnet-4-20250514"
                }
            ],
            "configuration": {
                "max_tokens": service.config.max_tokens,
                "temperature": service.config.temperature,
                "timeout": service.config.timeout
            }
        })
    except Exception as e:
        logger.error(f"Model listing failed: {str(e)}")
        return jsonify({
            "error": "Failed to list models",
            "details": str(e)
        }), 500


def register_claude_endpoints(app):
    """Register Claude endpoints with the Flask app"""
    app.register_blueprint(claude_bp)
    logger.info("Claude Opus 4.1 API endpoints registered")
