"""
Claude Opus 4.1 Integration for RouteForce
Provides AI-powered route optimization, analysis, and intelligent assistance
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import httpx
from flask import current_app


logger = logging.getLogger(__name__)


@dataclass
class ClaudeConfig:
    """Configuration for Claude Opus 4.1 API"""
    api_key: str
    model: str = "claude-opus-4-1-20250805"
    max_tokens: int = 4096
    temperature: float = 0.1
    timeout: int = 120
    base_url: str = "https://api.anthropic.com"


class ClaudeOpus4Service:
    """
    Service class for interacting with Claude Opus 4.1 API
    Provides route optimization, analysis, and intelligent assistance
    """

    def __init__(self, config: Optional[ClaudeConfig] = None):
        """Initialize Claude service with configuration"""
        if config is None:
            config = self._load_config_from_env()
        
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": self.config.api_key,
                "anthropic-version": "2023-06-01"
            }
        )

    def _load_config_from_env(self) -> ClaudeConfig:
        """Load configuration from environment variables"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key or api_key == "your-anthropic-api-key-here":
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is required. "
                "Get your API key from https://console.anthropic.com/"
            )

        return ClaudeConfig(
            api_key=api_key,
            model=os.getenv("CLAUDE_MODEL", "claude-opus-4-1-20250805"),
            max_tokens=int(os.getenv("CLAUDE_MAX_TOKENS", "4096")),
            temperature=float(os.getenv("CLAUDE_TEMPERATURE", "0.1")),
            timeout=int(os.getenv("CLAUDE_TIMEOUT", "120"))
        )

    async def _make_request(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make a request to Claude API"""
        try:
            payload = {
                "model": self.config.model,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "messages": messages
            }

            if system_prompt:
                payload["system"] = system_prompt

            response = await self.client.post("/v1/messages", json=payload)
            response.raise_for_status()
            
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"Claude API HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Claude API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Claude API request failed: {str(e)}")
            raise

    async def optimize_route_with_ai(
        self,
        route_data: Dict[str, Any],
        optimization_goals: List[str] = None
    ) -> Dict[str, Any]:
        """
        Use Claude Opus 4.1 to analyze and optimize routes
        
        Args:
            route_data: Route information including stops, constraints, etc.
            optimization_goals: List of optimization objectives (e.g., 'distance', 'time', 'fuel')
        
        Returns:
            AI-generated route optimization recommendations
        """
        if optimization_goals is None:
            optimization_goals = ["distance", "time", "fuel_efficiency"]

        system_prompt = """You are an expert route optimization AI with deep knowledge of logistics, 
        traffic patterns, and efficient delivery strategies. Analyze the provided route data and 
        provide intelligent optimization recommendations. Focus on practical, actionable insights."""

        user_message = f"""
        Please analyze this route data and provide optimization recommendations:

        Route Data:
        {json.dumps(route_data, indent=2)}

        Optimization Goals: {', '.join(optimization_goals)}

        Provide your analysis in the following JSON format:
        {{
            "analysis_summary": "Brief overview of the route analysis",
            "optimization_recommendations": [
                {{
                    "type": "recommendation_type",
                    "description": "detailed_description",
                    "impact": "estimated_impact",
                    "priority": "high|medium|low"
                }}
            ],
            "efficiency_score": "score_out_of_100",
            "potential_savings": {{
                "distance": "percentage_or_absolute",
                "time": "percentage_or_absolute",
                "fuel": "percentage_or_absolute"
            }},
            "risk_factors": ["list", "of", "identified", "risks"],
            "alternative_routes": [
                {{
                    "description": "alternative_description",
                    "advantages": ["list", "of", "advantages"],
                    "trade_offs": ["list", "of", "trade_offs"]
                }}
            ]
        }}
        """

        messages = [{"role": "user", "content": user_message}]
        
        try:
            response = await self._make_request(messages, system_prompt)
            
            # Extract the content from Claude's response
            content = response.get("content", [])
            if content and len(content) > 0:
                text_content = content[0].get("text", "")
                
                # Try to parse JSON from the response
                try:
                    # Look for JSON in the response
                    json_start = text_content.find('{')
                    json_end = text_content.rfind('}') + 1
                    if json_start != -1 and json_end > json_start:
                        json_content = text_content[json_start:json_end]
                        analysis = json.loads(json_content)
                        return {
                            "success": True,
                            "analysis": analysis,
                            "raw_response": text_content,
                            "model_used": self.config.model,
                            "timestamp": datetime.now().isoformat()
                        }
                except json.JSONDecodeError:
                    pass
                
                # If JSON parsing fails, return the raw response
                return {
                    "success": True,
                    "analysis": {"raw_analysis": text_content},
                    "raw_response": text_content,
                    "model_used": self.config.model,
                    "timestamp": datetime.now().isoformat()
                }
            
            return {
                "success": False,
                "error": "No content in Claude response",
                "response": response
            }

        except Exception as e:
            logger.error(f"Route optimization failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def analyze_route_performance(
        self,
        route_history: List[Dict[str, Any]],
        metrics: List[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze historical route performance using Claude Opus 4.1
        
        Args:
            route_history: Historical route data and performance metrics
            metrics: Specific metrics to analyze
        
        Returns:
            AI-generated performance analysis and insights
        """
        if metrics is None:
            metrics = ["efficiency", "punctuality", "fuel_consumption", "customer_satisfaction"]

        system_prompt = """You are an expert data analyst specializing in route performance 
        and logistics optimization. Analyze the provided historical route data to identify 
        patterns, trends, and actionable insights for improvement."""

        user_message = f"""
        Analyze this historical route performance data:

        Route History:
        {json.dumps(route_history, indent=2)}

        Focus on these metrics: {', '.join(metrics)}

        Provide analysis in JSON format:
        {{
            "performance_summary": "overall_performance_assessment",
            "key_insights": [
                {{
                    "insight": "description",
                    "evidence": "supporting_data",
                    "impact": "high|medium|low"
                }}
            ],
            "trends_identified": [
                {{
                    "trend": "trend_description",
                    "direction": "improving|declining|stable",
                    "timeframe": "time_period"
                }}
            ],
            "improvement_opportunities": [
                {{
                    "opportunity": "description",
                    "potential_impact": "estimated_improvement",
                    "implementation_effort": "low|medium|high"
                }}
            ],
            "performance_scores": {{
                "overall": "score_out_of_100",
                "efficiency": "score_out_of_100",
                "punctuality": "score_out_of_100",
                "cost_effectiveness": "score_out_of_100"
            }}
        }}
        """

        messages = [{"role": "user", "content": user_message}]
        
        try:
            response = await self._make_request(messages, system_prompt)
            content = response.get("content", [])
            
            if content and len(content) > 0:
                text_content = content[0].get("text", "")
                
                try:
                    json_start = text_content.find('{')
                    json_end = text_content.rfind('}') + 1
                    if json_start != -1 and json_end > json_start:
                        json_content = text_content[json_start:json_end]
                        analysis = json.loads(json_content)
                        return {
                            "success": True,
                            "analysis": analysis,
                            "raw_response": text_content,
                            "model_used": self.config.model,
                            "timestamp": datetime.now().isoformat()
                        }
                except json.JSONDecodeError:
                    pass
                
                return {
                    "success": True,
                    "analysis": {"raw_analysis": text_content},
                    "raw_response": text_content,
                    "model_used": self.config.model,
                    "timestamp": datetime.now().isoformat()
                }
            
            return {
                "success": False,
                "error": "No content in Claude response",
                "response": response
            }

        except Exception as e:
            logger.error(f"Performance analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def generate_route_insights(
        self,
        query: str,
        context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate intelligent insights based on a natural language query
        
        Args:
            query: Natural language question or request
            context_data: Optional context data to inform the response
        
        Returns:
            AI-generated insights and recommendations
        """
        system_prompt = """You are an intelligent routing and logistics assistant powered by 
        Claude Opus 4.1. You help users understand their routing data, optimize operations, 
        and make data-driven decisions. Provide clear, actionable insights."""

        context_text = ""
        if context_data:
            context_text = f"\nContext Data:\n{json.dumps(context_data, indent=2)}\n"

        user_message = f"""
        User Query: {query}
        {context_text}
        
        Please provide a helpful, detailed response that addresses the user's question. 
        If relevant, include specific recommendations, data insights, or actionable steps.
        """

        messages = [{"role": "user", "content": user_message}]
        
        try:
            response = await self._make_request(messages, system_prompt)
            content = response.get("content", [])
            
            if content and len(content) > 0:
                text_content = content[0].get("text", "")
                return {
                    "success": True,
                    "insights": text_content,
                    "query": query,
                    "model_used": self.config.model,
                    "timestamp": datetime.now().isoformat()
                }
            
            return {
                "success": False,
                "error": "No content in Claude response",
                "response": response
            }

        except Exception as e:
            logger.error(f"Insight generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def close(self):
        """Close the HTTP client"""
        if hasattr(self, 'client'):
            await self.client.aclose()

    def __del__(self):
        """Cleanup when service is destroyed"""
        try:
            # Try to close the client if it exists
            if hasattr(self, 'client') and self.client:
                asyncio.create_task(self.client.aclose())
        except:
            pass


# Convenience functions for easy integration
def create_claude_service() -> ClaudeOpus4Service:
    """Create a new Claude Opus 4.1 service instance"""
    return ClaudeOpus4Service()


async def quick_route_optimization(route_data: Dict[str, Any]) -> Dict[str, Any]:
    """Quick route optimization using Claude Opus 4.1"""
    service = create_claude_service()
    try:
        result = await service.optimize_route_with_ai(route_data)
        return result
    finally:
        await service.close()


async def quick_route_analysis(route_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Quick route performance analysis using Claude Opus 4.1"""
    service = create_claude_service()
    try:
        result = await service.analyze_route_performance(route_history)
        return result
    finally:
        await service.close()


async def quick_route_insights(query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Quick insights generation using Claude Opus 4.1"""
    service = create_claude_service()
    try:
        result = await service.generate_route_insights(query, context)
        return result
    finally:
        await service.close()


# Flask integration helper
def init_claude_service(app):
    """Initialize Claude service with Flask app"""
    if not hasattr(app, 'claude_service'):
        app.claude_service = create_claude_service()
    return app.claude_service
