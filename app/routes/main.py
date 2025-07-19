"""
Main routes blueprint for RouteForce Routing
"""
from flask import Blueprint, render_template, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
import os
import logging
from typing import Dict, Any, List, Optional

from app.services.routing_service import RoutingService
from app.services.file_service import FileService
from app.models.route_request import RouteRequest
from app import cache, limiter

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main index page"""
    return render_template('main.html')

@main_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'RouteForce Routing',
        'version': '1.0.0'
    })

@main_bp.route('/generate', methods=['POST'])
@limiter.limit("10 per minute")
def generate_route():
    """
    Generate optimized route with comprehensive validation and caching
    """
    try:
        # Initialize services
        routing_service = RoutingService()
        file_service = FileService()
        
        # Parse and validate request
        try:
            route_request = RouteRequest.from_request(request)
        except Exception as e:
            # Handle request parsing errors (like file size limits)
            if "413" in str(e) or "Request Entity Too Large" in str(e):
                return jsonify({
                    'error': 'File too large',
                    'details': ['The uploaded file exceeds the maximum size limit of 16MB.']
                }), 413
            else:
                return jsonify({
                    'error': 'Invalid request',
                    'details': [str(e)]
                }), 400
        
        if not route_request.is_valid():
            return jsonify({
                'error': 'Invalid request',
                'details': route_request.get_validation_errors()
            }), 400
        
        # Check cache first
        cache_key = route_request.get_cache_key()
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached route for key: {cache_key}")
            return jsonify(cached_result), 200
        
        # Save and process uploaded file
        file_path = file_service.save_uploaded_file(route_request.file)
        
        try:
            # Validate file content
            if not file_service.validate_file_content(file_path):
                return jsonify({
                    'error': 'Invalid file format or missing required columns'
                }), 400
            
            # Generate route
            route_result = routing_service.generate_route_with_filters(
                file_path=file_path,
                filters=route_request.get_filters()
            )
            
            # Load stores for response
            stores = file_service.load_stores_from_file(file_path)
            
            # Apply optimization if requested
            if route_request.proximity:
                final_route = routing_service.generate_route_with_filters(
                    file_path, {
                        'proximity': route_request.proximity,
                        'time_start': route_request.time_start,
                        'time_end': route_request.time_end,
                        'exclude_days': route_request.exclude_days,
                        'max_stores_per_chain': route_request.max_stores_per_chain,
                        'min_sales_threshold': route_request.min_sales_threshold
                    }
                )
            else:
                final_route = route_result
            
            # Prepare response for dashboard
            response_data = {
                'success': True,
                'stores': stores,
                'route': final_route,
                'metrics': {
                    'total_stores': len(stores),
                    'route_stores': len(final_route) if final_route else 0,
                    'optimization_score': routing_service.metrics.optimization_score if routing_service.metrics else 0,
                    'processing_time': routing_service.metrics.processing_time if routing_service.metrics else 0
                }
            }
            
            # Cache the result
            cache.set(cache_key, response_data, timeout=1800)
            
            # Return JSON for dashboard or HTML for regular form
            if request.headers.get('Accept') == 'application/json':
                return jsonify(response_data), 200
            else:
                # Return HTML response as before
                return render_template('main.html', 
                                       route_generated=True,
                                       route=final_route,
                                       store_count=len(stores))

        finally:
            # Clean up uploaded file
            file_service.cleanup_file(file_path)
            
    except Exception as e:
        logger.error(f"Error generating route: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to generate route'
        }), 500

@main_bp.route('/export', methods=['POST'])
@limiter.limit("5 per minute")
def export_route():
    """
    Export route to CSV format with enhanced error handling
    """
    try:
        file_service = FileService()
        routing_service = RoutingService()
        
        # Validate and process files
        stores_file = request.files.get('file')
        playbook_file = request.files.get('playbook')
        
        if not stores_file:
            return jsonify({'error': 'No stores file provided'}), 400
        
        # Process stores file
        stores_path = file_service.save_uploaded_file(stores_file)
        
        try:
            stores = file_service.load_stores_from_file(stores_path)
            
            # Process optional playbook
            playbook = {}
            if playbook_file and playbook_file.filename:
                playbook_path = file_service.save_uploaded_file(playbook_file)
                try:
                    playbook = file_service.load_playbook_from_file(playbook_path)
                finally:
                    file_service.cleanup_file(playbook_path)
            
            # Generate and export route
            route = routing_service.generate_route(stores, playbook)
            csv_response = file_service.export_route_to_csv(route)
            
            logger.info(f"Exported route with {len(route) if route else 0} stops")
            return csv_response
            
        finally:
            file_service.cleanup_file(stores_path)
            
    except Exception as e:
        logger.error(f"Error exporting route: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to export route',
            'details': str(e)
        }), 500

@main_bp.route('/dashboard')
def dashboard():
    """
    Real-time route optimization dashboard
    """
    return render_template('dashboard.html')

@main_bp.route('/generate_route', methods=['POST'])
@limiter.limit("10 per minute")
def generate_route_api():
    """
    Generate optimized route for dashboard API integration
    """
    try:
        # Initialize services
        routing_service = RoutingService()
        file_service = FileService()
        
        # Check if file is uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get form parameters
        use_proximity = request.form.get('use_proximity') == 'true'
        radius_km = float(request.form.get('radius_km', '2.0'))
        start_time = request.form.get('start_time', '09:00')
        end_time = request.form.get('end_time', '17:00')
        max_stores = int(request.form.get('max_stores', '50'))
        
        # Save uploaded file
        file_path = file_service.save_uploaded_file(file)
        
        try:
            # Validate file content
            if not file_service.validate_file_content(file_path):
                return jsonify({
                    'error': 'Invalid file format or missing required columns'
                }), 400
            
            # Load stores
            stores = file_service.load_stores_from_file(file_path)
            
            # Apply proximity clustering if requested
            clusters = []
            if use_proximity:
                clusters = routing_service.cluster_stores_by_proximity(stores, radius_km)
                logger.info(f"Created {len(clusters)} clusters with radius {radius_km}km")
            
            # Apply filters
            filters = {
                'time_start': start_time,
                'time_end': end_time,
                'max_stores': max_stores
            }
            
            # Generate optimized route
            route_result = routing_service.generate_route_with_filters(
                file_path=file_path,
                filters=filters
            )
            
            # Calculate metrics
            optimization_score = routing_service.calculate_optimization_score(route_result)
            processing_time = routing_service.get_last_processing_time()
            
            # Prepare response
            response_data = {
                'status': 'success',
                'stores': stores[:max_stores],  # Return processed stores
                'route': route_result,
                'clusters': clusters,
                'metrics': {
                    'total_stores': len(stores),
                    'route_stores': len(route_result) if route_result else 0,
                    'cluster_count': len(clusters) if clusters else 0,
                    'optimization_score': optimization_score,
                    'processing_time': processing_time,
                    'radius_km': radius_km
                }
            }
            
            return jsonify(response_data), 200
            
        finally:
            # Clean up uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)
        
    except Exception as e:
        logger.error(f"Error generating route: {str(e)}")
        return jsonify({
            'error': 'Route generation failed',
            'details': str(e)
        }), 500
