from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import google.generativeai as genai
import os
import json
import subprocess
from datetime import datetime
import requests
from dotenv import load_dotenv
from jmeter_runner import JMeterRunner
from load_runner import HTTPLoadRunner
import threading
import time

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# CORS Configuration - Flexible through environment variables
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
CORS_METHODS = os.getenv('CORS_METHODS', 'GET,POST,PUT,DELETE,OPTIONS').split(',')
CORS_HEADERS = os.getenv('CORS_HEADERS', 'Content-Type,Authorization').split(',')

# Apply CORS with flexible configuration
CORS(app, 
     origins=CORS_ORIGINS,
     methods=CORS_METHODS,
     allow_headers=CORS_HEADERS)

# Socket.IO with flexible CORS
socketio = SocketIO(app, 
                   cors_allowed_origins=CORS_ORIGINS,
                   async_mode='threading')

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-gemini-api-key-here')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Environment configuration
IS_PRODUCTION = os.getenv('FLASK_ENV') == 'production'
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
PORT = int(os.getenv('PORT', 5000))

# Initialize JMeter Runner
jmeter_runner = JMeterRunner()

# Global variables for real-time monitoring
active_tests = {}
test_monitors = {}

class PerformanceAnalyzer:
    def __init__(self):
        self.test_history = []
        self.agent_memory = []
        self.ai_provider = self._determine_ai_provider()

    def _determine_ai_provider(self):
        """Determine which AI provider to use based on available API keys"""
        if GEMINI_API_KEY != 'your-gemini-api-key-here':
            return 'gemini'
        else:
            return 'fallback'

    def agent_brain(self, jmeter_output, image_url=None):
        """
        AI Agent Brain - Analyzes JMeter output and makes intelligent decisions
        Supports both text and image analysis
        """
        try:
            if self.ai_provider == 'gemini':
                return self._gemini_analysis(jmeter_output, image_url)
            else:
                return self._generate_fallback_analysis(jmeter_output)

        except Exception as e:
            print(f"AI analysis failed: {e}")
            return self._generate_fallback_analysis(jmeter_output)

    def _gemini_analysis(self, jmeter_output, image_url=None):
        """Use Google Gemini Pro for analysis"""
        try:
            prompt = f"""
            You are an intelligent Performance Testing AI Agent. Analyze the following JMeter test results and act as a performance engineer would.
            
            JMETER TEST RESULTS:
            {json.dumps(jmeter_output, indent=2)}
            
            As an AI Agent, you need to:
            1. Identify the MAIN PROBLEM (if any)
            2. Determine the ROOT CAUSE
            3. Provide SPECIFIC RECOMMENDATIONS
            4. Decide if a RETRY TEST is needed
            
            Consider these factors:
            - Response times and their distribution
            - Success/failure rates
            - Throughput and RPS patterns
            - Error patterns and types
            - Resource utilization indicators
            - Performance degradation patterns
            
            Respond ONLY with valid JSON in this exact format:
            {{
                "problem": "Clear description of the main issue or 'No significant problems detected'",
                "root_cause": "Technical root cause analysis",
                "recommendations": ["Specific recommendation 1", "Specific recommendation 2"],
                "retry_test": true/false,
                "confidence": 0.85,
                "severity": "high/medium/low"
            }}
            """
            
            response = model.generate_content(prompt)
            response_text = response.text
            
            # Parse JSON response
            try:
                agent_result = json.loads(response_text)
                return {
                    "success": True,
                    "agent_response": agent_result,
                    "raw_response": response_text,
                    "ai_provider": "gemini",
                    "model": "gemini-pro",
                    "timestamp": datetime.now().isoformat()
                }
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "success": True,
                    "agent_response": {
                        "problem": "AI analysis completed but response format was unexpected",
                        "root_cause": "Response parsing issue",
                        "recommendations": ["Review AI response format", "Check API configuration"],
                        "retry_test": False,
                        "confidence": 0.5,
                        "severity": "medium"
                    },
                    "raw_response": response_text,
                    "ai_provider": "gemini",
                    "model": "gemini-pro",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"Gemini analysis failed: {e}")
            return {
                "success": False,
                "error": f"Gemini analysis failed: {str(e)}",
                "ai_provider": "gemini",
                "timestamp": datetime.now().isoformat()
            }

    def analyze_performance_data(self, test_results, image_url=None):
        """Analyze performance test results with AI agent"""
        try:
            # Perform AI analysis
            ai_result = self.agent_brain(test_results, image_url)
            
            if ai_result.get("success"):
                # Store in agent memory
                memory_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "test_results": test_results,
                    "ai_analysis": ai_result,
                    "image_url": image_url
                }
                self.agent_memory.append(memory_entry)
                
                # Keep only last 50 entries
                if len(self.agent_memory) > 50:
                    self.agent_memory = self.agent_memory[-50:]
                
                # Determine overall assessment
                assessment = self._determine_assessment(ai_result)
                
                return {
                    "success": True,
                    "assessment": assessment,
                    "ai_analysis": ai_result,
                    "memory_count": len(self.agent_memory),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return ai_result
                
        except Exception as e:
            print(f"Performance analysis failed: {e}")
            return {
                "success": False,
                "error": f"Performance analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def _determine_assessment(self, agent_result):
        """Determine overall performance assessment based on AI analysis"""
        try:
            agent_response = agent_result.get("agent_response", {})
            confidence = agent_response.get("confidence", 0.5)
            severity = agent_response.get("severity", "medium")
            
            if confidence > 0.8:
                if severity == "high":
                    return "Poor Performance - Critical Issues Detected"
                elif severity == "medium":
                    return "Moderate Performance - Issues Found"
                else:
                    return "Good Performance - Minor Issues"
            elif confidence > 0.6:
                return "Moderate Performance - Further Analysis Recommended"
            else:
                return "Unknown Performance - Insufficient Data"
                
        except Exception as e:
            return "Assessment Error - Unable to Determine"

    def _generate_fallback_analysis(self, test_results):
        """Generate basic analysis when AI services are unavailable"""
        try:
            # Basic rule-based analysis
            total_requests = test_results.get('totalRequests', 0)
            successful_requests = test_results.get('successfulRequests', 0)
            avg_response_time = test_results.get('avgResponseTime', 0)
            
            success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
            
            # Determine performance level
            if success_rate >= 95 and avg_response_time <= 500:
                assessment = "Good Performance"
                problem = "No significant problems detected"
                recommendations = ["Continue monitoring", "Consider load testing at higher scale"]
                retry_test = False
                severity = "low"
            elif success_rate >= 80 and avg_response_time <= 1000:
                assessment = "Moderate Performance"
                problem = "Some performance degradation detected"
                recommendations = ["Optimize database queries", "Consider caching", "Monitor resource usage"]
                retry_test = True
                severity = "medium"
            else:
                assessment = "Poor Performance"
                problem = "Significant performance issues detected"
                recommendations = ["Investigate server resources", "Check database performance", "Review application code"]
                retry_test = True
                severity = "high"
            
            return {
                "success": True,
                "agent_response": {
                    "problem": problem,
                    "root_cause": "Basic analysis - AI services unavailable",
                    "recommendations": recommendations,
                    "retry_test": retry_test,
                    "confidence": 0.6,
                    "severity": severity
                },
                "assessment": assessment,
                "ai_provider": "fallback",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Fallback analysis failed: {str(e)}",
                "ai_provider": "fallback",
                "timestamp": datetime.now().isoformat()
            }

# Initialize analyzer
analyzer = PerformanceAnalyzer()

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to Ludo Performance Suite'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    if request.sid in test_monitors:
        del test_monitors[request.sid]

@socketio.on('join_test_monitor')
def handle_join_test_monitor(data):
    test_id = data.get('test_id')
    if test_id:
        test_monitors[request.sid] = test_id
        print(f"Client {request.sid} monitoring test {test_id}")

def monitor_test_real_time(test_id, test_config):
    """Monitor JMeter test in real-time and emit updates"""
    try:
        start_time = time.time()
        duration = test_config.get('duration', 60)
        
        while time.time() - start_time < duration:
            try:
                # Get current test status
                status = jmeter_runner.get_test_status(test_id)
                
                if status.get('status') == 'running':
                    # Calculate progress
                    elapsed = time.time() - start_time
                    progress = min((elapsed / duration) * 100, 100)
                    
                    # Generate real-time metrics
                    real_time_data = {
                        'test_id': test_id,
                        'progress': progress,
                        'elapsed_time': elapsed,
                        'active_users': test_config.get('userCount', 0),
                        'avg_response_time': status.get('results', {}).get('avgResponseTime', 0),
                        'success_rate': status.get('results', {}).get('successRate', 0),
                        'requests_per_second': status.get('results', {}).get('requestsPerSecond', 0),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Emit to all clients monitoring this test
                    socketio.emit('test_update', real_time_data)
                    
                    # Also emit to specific test room
                    socketio.emit(f'test_{test_id}_update', real_time_data)
                    
                elif status.get('status') == 'completed':
                    # Test completed, emit final results
                    final_results = {
                        'test_id': test_id,
                        'status': 'completed',
                        'results': status.get('results', {}),
                        'ai_analysis': None,  # Will be generated separately
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    socketio.emit('test_completed', final_results)
                    socketio.emit(f'test_{test_id}_completed', final_results)
                    
                    # Generate AI analysis
                    if status.get('results'):
                        ai_analysis = analyzer.analyze_performance_data(status['results'])
                        final_results['ai_analysis'] = ai_analysis
                        
                        socketio.emit('ai_analysis_ready', {
                            'test_id': test_id,
                            'analysis': ai_analysis
                        })
                    
                    break
                    
                elif status.get('status') == 'failed':
                    # Test failed
                    error_data = {
                        'test_id': test_id,
                        'status': 'failed',
                        'error': status.get('error', 'Unknown error'),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    socketio.emit('test_failed', error_data)
                    socketio.emit(f'test_{test_id}_failed', error_data)
                    break
                
                time.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                print(f"Error monitoring test {test_id}: {e}")
                time.sleep(5)
                
    except Exception as e:
        print(f"Test monitoring failed for {test_id}: {e}")
        socketio.emit('test_error', {
            'test_id': test_id,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/')
def home():
    return jsonify({
        "message": "Loadosaurus AI Backend",
        "version": "1.0.0",
        "gemini_connected": GEMINI_API_KEY != 'your-gemini-api-key-here',
        "openrouter_connected": False, # Removed OpenRouter connection status
        "ai_provider": analyzer.ai_provider,
        "jmeter_available": True,
        "environment": "production" if IS_PRODUCTION else "development",
        "backend_url": BACKEND_URL,
        "frontend_url": FRONTEND_URL,
        "endpoints": {
            "POST /analyze": "Analyze performance test results with AI",
            "POST /analyze/image": "Analyze performance test results with image",
            "GET /health": "Health check",
            "POST /test/start": "Start a new JMeter test",
            "GET /test/:id/status": "Get test status",
            "GET /tests": "List all tests",
            "POST /test/:id/stop": "Stop a running test",
            "GET /test-api": "Test all HTTP methods",
            "GET /test-api/delay/:seconds": "Test with configurable delay",
            "GET /store/inventory": "Get pet inventory status",
            "POST /store/order": "Place new pet order",
            "GET /store/order/:orderId": "Get order by ID",
            "DELETE /store/order/:orderId": "Delete order by ID",
            "POST /user": "Create new user",
            "GET /user/:username": "Get user by username",
            "PUT /user/:username": "Update user",
            "DELETE /user/:username": "Delete user",
            "POST /pet": "Add new pet",
            "GET /pet/:petId": "Get pet by ID",
            "PUT /pet/:petId": "Update pet",
            "DELETE /pet/:petId": "Delete pet"
        }
    })

@app.route('/health')
def health():
    # Check JMeter availability
    jmeter_available = False
    jmeter_path = os.getenv('JMETER_HOME', 'C:\\Users\\Sneha\\Downloads\\apache-jmeter-5.6.3')
    jmeter_bin = os.path.join(jmeter_path, 'bin', 'jmeter.bat' if os.name == 'nt' else 'jmeter')
    
    if os.path.exists(jmeter_bin):
        try:
            result = subprocess.run([jmeter_bin, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            jmeter_available = result.returncode == 0
        except:
            jmeter_available = False
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "gemini_available": GEMINI_API_KEY != 'your-gemini-api-key-here',
        "openrouter_available": False, # Removed OpenRouter connection status
        "ai_provider": analyzer.ai_provider,
        "jmeter_available": jmeter_available,
        "jmeter_path": jmeter_path,
        "environment": "production" if IS_PRODUCTION else "development",
        "endpoints": {
            "POST /analyze": "Analyze performance test results with AI",
            "POST /analyze/image": "Analyze performance test results with image",
            "GET /health": "Health check",
            "POST /test/start": "Start a new JMeter test",
            "GET /test/:id/status": "Get test status",
            "GET /tests": "List all tests",
            "POST /test/:id/stop": "Stop a running test",
            "GET /test-api": "Test all HTTP methods",
            "GET /test-api/delay/:seconds": "Test with configurable delay",
            "GET /store/inventory": "Get pet inventory status",
            "POST /store/order": "Place new pet order",
            "GET /store/order/:orderId": "Get order by ID",
            "DELETE /store/order/:orderId": "Delete order by ID",
            "POST /user": "Create new user",
            "GET /user/:username": "Get user by username",
            "PUT /user/:username": "Update user",
            "DELETE /user/:username": "Delete user",
            "POST /pet": "Add new pet",
            "GET /pet/:petId": "Get pet by ID",
            "PUT /pet/:petId": "Update pet",
            "DELETE /pet/:petId": "Delete pet"
        }
    })

@app.route('/analyze', methods=['POST'])
def analyze_performance():
    """Enhanced AI Agent Analysis with auto-retry capability"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No test data provided"
            }), 400
        
        # Perform AI agent analysis
        analysis_result = analyzer.analyze_performance_data(data)
        
        # Check if agent recommends retry test
        if analysis_result.get("success") and analysis_result.get("agent_response", {}).get("retry_test", False):
            # Auto-trigger new test if recommended
            try:
                retry_response = requests.post(f'{BACKEND_URL}/test/start', 
                                             json=data,  # Use same test parameters
                                             headers={'Content-Type': 'application/json'})
                
                if retry_response.status_code == 200:
                    retry_data = retry_response.json()
                    analysis_result["auto_retry"] = {
                        "triggered": True,
                        "new_test_id": retry_data.get("testId"),
                        "message": "Auto-retry test initiated based on AI agent recommendation"
                    }
                else:
                    analysis_result["auto_retry"] = {
                        "triggered": False,
                        "error": "Failed to start retry test"
                    }
            except Exception as retry_error:
                analysis_result["auto_retry"] = {
                    "triggered": False,
                    "error": f"Retry test failed: {str(retry_error)}"
                }
        else:
            analysis_result["auto_retry"] = {
                "triggered": False,
                "reason": "No retry recommended by AI agent"
            }
        
        return jsonify(analysis_result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"AI agent analysis failed: {str(e)}"
        }), 500

@app.route('/analyze/image', methods=['POST'])
def analyze_performance_with_image():
    """AI Agent Analysis with image support"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No test data provided"
            }), 400
        
        test_data = data.get('test_data', {})
        image_url = data.get('image_url')
        
        # Perform AI agent analysis with image
        analysis_result = analyzer.analyze_performance_data(test_data, image_url)
        
        return jsonify(analysis_result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"AI agent analysis with image failed: {str(e)}"
        }), 500

@app.route('/test/start', methods=['POST'])
def start_test():
    """Start a new JMeter performance test"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No test configuration provided"
            }), 400
        
        # If type is 'HTTP Test' use async HTTP runner; else keep JMeter flow
        test_type = data.get('type', 'Load Test')

        # Validate required fields (keep legacy names as-is for UI compatibility) for JMeter modes
        required_fields = ['type', 'url', 'users', 'duration']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Create test configuration
        test_id = f"test_{int(datetime.now().timestamp())}"
        test_config = {
            "id": test_id,
            "type": data.get("type", "Load Test"),
            "url": data.get("url", "http://localhost:3000"),
            "users": data.get("users", 100),
            "duration": data.get("duration", 600),  # Convert to seconds
            "ramp_up": data.get("rampUp", 10),
            "think_time": data.get("thinkTime", 1000)
        }

        # Advanced optional fields (no UI/layout change required)
        # HTTP sampler(s)
        if 'httpSampler' in data:
            test_config['httpSampler'] = data['httpSampler']
        if 'httpSamplers' in data:
            test_config['httpSamplers'] = data['httpSamplers']
        # Auth
        if 'auth' in data:
            test_config['auth'] = data['auth']
        # Assertions
        if 'assertions' in data:
            test_config['assertions'] = data['assertions']
        # TPS control
        if 'tps' in data:
            test_config['tps'] = data['tps']
        # Scheduling
        if 'schedule' in data:
            test_config['schedule'] = data['schedule']
        
        # HTTP precise TPS runner
        if test_type == 'HTTP Test':
            http_cfg = {
                'url': data.get('url'),
                'method': data.get('method', 'GET'),
                'headers': data.get('headers'),
                'params': data.get('params'),
                'body': data.get('body'),
                'bodyType': data.get('bodyType'),
                'auth': data.get('auth'),
                'users': data.get('users', 50),
                'target_tps': data.get('target_tps') or data.get('tps'),
                'duration_seconds': data.get('duration'),
                'ramp_up_seconds': data.get('rampUp'),
                'loop_count': data.get('loopCount')
            }

            def _emit_tick(tick):
                socketio.emit('test_update', {
                    'test_id': test_id,
                    'progress': min((tick.get('elapsed', 0) / max(1, test_config['duration'])) * 100, 100),
                    'avg_response_time': tick.get('avgResponseTime', 0),
                    'requests_per_second': tick.get('rps', 0),
                    'timestamp': datetime.now().isoformat()
                })

            runner = HTTPLoadRunner(http_cfg, on_tick=_emit_tick)

            def _run_http():
                results = runner.run()
                jmeter_runner.active_tests[test_id] = {
                    'config': test_config,
                    'start_time': datetime.now(),
                    'status': 'completed',
                    'results': results
                }
                socketio.emit('test_completed', {
                    'test_id': test_id,
                    'status': 'completed',
                    'results': results,
                    'timestamp': datetime.now().isoformat()
                })

            threading.Thread(target=_run_http, daemon=True).start()
            return jsonify({
                'success': True,
                'testId': test_id,
                'message': 'HTTP Test started successfully',
                'config': test_config
            })

        # Start JMeter test for existing types
        result = jmeter_runner.run_jmeter_test(test_config)
        
        if result['success']:
            # Start real-time monitoring in a separate thread
            threading.Thread(target=monitor_test_real_time, args=(test_id, test_config)).start()

            return jsonify({
                "success": True,
                "testId": test_id,
                "message": f"JMeter {test_config['type']} started successfully",
                "config": test_config
            })
        else:
            return jsonify({
                "success": False,
                "error": result['error']
            }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to start test: {str(e)}"
        }), 500

@app.route('/test/plan/save', methods=['POST'])
def save_test_plan():
    try:
        payload = request.get_json() or {}
        name = payload.get('name') or f"plan_{int(datetime.now().timestamp())}"
        plan = payload.get('plan') or {}
        result = jmeter_runner.save_test_plan(name, plan)
        return jsonify(result), (200 if result.get('success') else 400)
    except Exception as e:
        return jsonify({ 'success': False, 'error': str(e) }), 500

@app.route('/test/plan/load', methods=['GET'])
def load_test_plan():
    try:
        name = request.args.get('name')
        if not name:
            return jsonify({ 'success': False, 'error': 'name is required' }), 400
        result = jmeter_runner.load_test_plan(name)
        return jsonify(result), (200 if result.get('success') else 404)
    except Exception as e:
        return jsonify({ 'success': False, 'error': str(e) }), 500

@app.route('/test/plan/export-http', methods=['POST'])
def export_http_config():
    try:
        payload = request.get_json() or {}
        result = jmeter_runner.export_http_config(payload)
        return jsonify(result), (200 if result.get('success') else 400)
    except Exception as e:
        return jsonify({ 'success': False, 'error': str(e) }), 500

@app.route('/test/plan/import-http', methods=['POST'])
def import_http_config():
    try:
        payload = request.get_json() or {}
        plan = payload.get('plan') or {}
        http_cfg = payload.get('http') or payload
        result = jmeter_runner.import_http_config(plan, http_cfg)
        return jsonify(result), (200 if result.get('success') else 400)
    except Exception as e:
        return jsonify({ 'success': False, 'error': str(e) }), 500

@app.route('/test/<test_id>/status', methods=['GET'])
def get_test_status(test_id):
    """Get JMeter test status"""
    try:
        status = jmeter_runner.get_test_status(test_id)
        return jsonify({
            "success": True,
            "status": status
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get test status: {str(e)}"
        }), 500

@app.route('/test/<test_id>/stop', methods=['POST'])
def stop_test(test_id):
    """Stop a running JMeter test"""
    try:
        result = jmeter_runner.stop_test(test_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to stop test: {str(e)}"
        }), 500

@app.route('/tests', methods=['GET'])
def list_tests():
    """List all JMeter tests"""
    try:
        tests = jmeter_runner.list_tests()
        test_statuses = []
        for test_id in tests:
            status = jmeter_runner.get_test_status(test_id)
            test_statuses.append(status)
        
        return jsonify({
            "success": True,
            "tests": test_statuses
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to list tests: {str(e)}"
        }), 500

@app.route('/tests/history', methods=['GET'])
def get_test_history():
    """Get test history from JMeter results"""
    try:
        # Get completed tests from JMeter runner
        tests = jmeter_runner.list_tests()
        history = []
        
        for test_id in tests:
            status = jmeter_runner.get_test_status(test_id)
            if status.get('status') == 'completed' and 'results' in status:
                results = status['results']
                history.append({
                    "id": test_id,
                    "type": status.get('config', {}).get('type', 'Unknown'),
                    "url": status.get('config', {}).get('url', 'Unknown'),
                    "users": status.get('config', {}).get('users', 0),
                    "duration": status.get('config', {}).get('duration', 0),
                    "status": status.get('status', 'unknown'),
                    "success_rate": results.get('successRate', 0),
                    "avg_response_time": results.get('avgResponseTime', 0),
                    "peak_rps": results.get('peakRPS', 0),
                    "timestamp": status.get('startTime', datetime.now().isoformat())
                })
        
        return jsonify({
            "success": True,
            "history": history
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get test history: {str(e)}"
        }), 500

@app.route('/agent/memory', methods=['GET'])
def get_agent_memory():
    """Get AI agent's analysis memory"""
    return jsonify({
        "success": True,
        "agent_memory": analyzer.agent_memory,
        "memory_count": len(analyzer.agent_memory),
        "ai_provider": analyzer.ai_provider,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/agent/status', methods=['GET'])
def get_agent_status():
    """Get AI agent status and capabilities"""
    return jsonify({
        "success": True,
        "agent_status": "active",
        "capabilities": [
            "Performance analysis",
            "Problem identification",
            "Root cause analysis",
            "Recommendation generation",
            "Auto-retry decision making",
            "Memory retention",
            "Image analysis (OpenRouter)",
            "JMeter integration"
        ],
        "gemini_connected": GEMINI_API_KEY != 'your-gemini-api-key-here',
        "openrouter_connected": False, # Removed OpenRouter connection status
        "ai_provider": analyzer.ai_provider,
        "memory_entries": len(analyzer.agent_memory),
        "jmeter_available": True,
        "environment": "production" if IS_PRODUCTION else "development",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/test-api', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
def test_api():
    """Test endpoint for HTTP method testing"""
    method = request.method
    headers = dict(request.headers)
    body = request.get_data(as_text=True) if request.data else None
    
    # Parse JSON body if present
    json_body = None
    if body and request.content_type == 'application/json':
        try:
            json_body = request.get_json()
        except:
            json_body = None
    
    response_data = {
        "method": method,
        "url": request.url,
        "headers": headers,
        "query_params": dict(request.args),
        "body": body,
        "json_body": json_body,
        "timestamp": datetime.now().isoformat(),
        "message": f"Successfully received {method} request"
    }
    
    # Return different status codes for testing
    if method == 'POST':
        return jsonify(response_data), 201
    elif method == 'DELETE':
        return jsonify(response_data), 204
    else:
        return jsonify(response_data), 200

@app.route('/test-api/delay/<int:seconds>', methods=['GET'])
def test_api_delay(seconds):
    """Test endpoint with configurable delay for response time testing"""
    import time
    time.sleep(seconds)
    
    response_data = {
        "method": "GET",
        "url": request.url,
        "delay_seconds": seconds,
        "timestamp": datetime.now().isoformat(),
        "message": f"Response delayed by {seconds} {'second' if seconds == 1 else 'seconds'}"
    }
    
    return jsonify(response_data), 200

# Petstore-style API endpoints for comprehensive testing
@app.route('/store/inventory', methods=['GET'])
def get_store_inventory():
    """Returns test inventories by status"""
    inventory = {
        "available": 150,
        "pending": 25,
        "sold": 75,
        "total": 250,
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    }
    return jsonify(inventory), 200

@app.route('/store/order', methods=['POST'])
def place_store_order():
    """Place a test order"""
    try:
        order_data = request.get_json()
        if not order_data:
            return jsonify({"error": "Order data required"}), 400
        
        # Generate a mock order ID
        order_id = f"ORDER_{int(time.time())}"
        
        order_response = {
            "id": order_id,
            "petId": order_data.get("petId", 1),
            "quantity": order_data.get("quantity", 1),
            "shipDate": datetime.now().isoformat(),
            "status": "placed",
            "complete": False,
            "message": "Order placed successfully"
        }
        
        return jsonify(order_response), 201
        
    except Exception as e:
        return jsonify({"error": f"Failed to place order: {str(e)}"}), 400

@app.route('/store/order/<order_id>', methods=['GET'])
def get_store_order(order_id):
    """Find test order by ID"""
    # Mock order data
    order = {
        "id": order_id,
        "petId": 1,
        "quantity": 1,
        "shipDate": datetime.now().isoformat(),
        "status": "placed",
        "complete": False,
        "message": f"Order {order_id} found"
    }
    
    if not order_id.startswith("ORDER_"):
        return jsonify({"error": "Order not found"}), 404
    
    return jsonify(order), 200

@app.route('/store/order/<order_id>', methods=['DELETE'])
def delete_store_order(order_id):
    """Delete test order by ID"""
    if not order_id.startswith("ORDER_"):
        return jsonify({"error": "Order not found"}), 404
    
    return jsonify({"message": f"Order {order_id} deleted successfully"}), 200

# User management endpoints
@app.route('/user', methods=['POST'])
def create_user():
    """Create a test user"""
    try:
        user_data = request.get_json()
        if not user_data:
            return jsonify({"error": "User data required"}), 400
        
        user_id = f"USER_{int(time.time())}"
        user_response = {
            "id": user_id,
            "username": user_data.get("username", "testuser"),
            "email": user_data.get("email", "test@example.com"),
            "firstName": user_data.get("firstName", "Test"),
            "lastName": user_data.get("lastName", "User"),
            "status": "active",
            "message": "User created successfully"
        }
        
        return jsonify(user_response), 201
        
    except Exception as e:
        return jsonify({"error": f"Failed to create user: {str(e)}"}), 400

@app.route('/user/<username>', methods=['GET'])
def get_user(username):
    """Get test user by username"""
    user = {
        "id": f"USER_{hash(username) % 10000}",
        "username": username,
        "email": f"{username}@example.com",
        "firstName": "Test",
        "lastName": "User",
        "status": "active",
        "message": f"User {username} found"
    }
    
    return jsonify(user), 200

@app.route('/user/<username>', methods=['PUT'])
def update_user(username):
    """Update test user"""
    try:
        user_data = request.get_json()
        if not user_data:
            return jsonify({"error": "User data required"}), 400
        
        user_response = {
            "id": f"USER_{hash(username) % 10000}",
            "username": username,
            "email": user_data.get("email", f"{username}@example.com"),
            "firstName": user_data.get("firstName", "Updated"),
            "lastName": user_data.get("lastName", "User"),
            "status": "active",
            "message": f"User {username} updated successfully"
        }
        
        return jsonify(user_response), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to update user: {str(e)}"}), 400

@app.route('/user/<username>', methods=['DELETE'])
def delete_user(username):
    """Delete test user"""
    return jsonify({"message": f"User {username} deleted successfully"}), 200

# Pet management endpoints
@app.route('/pet', methods=['POST'])
def add_pet():
    """Add a test pet"""
    try:
        pet_data = request.get_json()
        if not pet_data:
            return jsonify({"error": "Pet data required"}), 400
        
        pet_id = f"PET_{int(time.time())}"
        pet_response = {
            "id": pet_id,
            "name": pet_data.get("name", "Fluffy"),
            "category": pet_data.get("category", {"id": 1, "name": "Dogs"}),
            "tags": pet_data.get("tags", [{"id": 1, "name": "friendly"}]),
            "status": "available",
            "message": "Pet added successfully"
        }
        
        return jsonify(pet_response), 201
        
    except Exception as e:
        return jsonify({"error": f"Failed to add pet: {str(e)}"}), 400

@app.route('/pet/<pet_id>', methods=['GET'])
def get_pet(pet_id):
    """Find pet by ID"""
    if not pet_id.startswith("PET_"):
        return jsonify({"error": "Pet not found"}), 404
    
    pet = {
        "id": pet_id,
        "name": "Fluffy",
        "category": {"id": 1, "name": "Dogs"},
        "tags": [{"id": 1, "name": "friendly"}],
        "status": "available",
        "message": f"Pet {pet_id} found"
    }
    
    return jsonify(pet), 200

@app.route('/pet/<pet_id>', methods=['PUT'])
def update_pet(pet_id):
    """Update pet"""
    try:
        pet_data = request.get_json()
        if not pet_data:
            return jsonify({"error": "Pet data required"}), 400
        
        if not pet_id.startswith("PET_"):
            return jsonify({"error": "Pet not found"}), 404
        
        pet_response = {
            "id": pet_id,
            "name": pet_data.get("name", "Updated Fluffy"),
            "category": pet_data.get("category", {"id": 1, "name": "Dogs"}),
            "tags": pet_data.get("tags", [{"id": 1, "name": "updated"}]),
            "status": pet_data.get("status", "available"),
            "message": f"Pet {pet_id} updated successfully"
        }
        
        return jsonify(pet_response), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to update pet: {str(e)}"}), 400

@app.route('/pet/<pet_id>', methods=['DELETE'])
def delete_pet(pet_id):
    """Delete pet"""
    if not pet_id.startswith("PET_"):
        return jsonify({"error": "Pet not found"}), 404
    
    return jsonify({"message": f"Pet {pet_id} deleted successfully"}), 200

@app.route('/docs')
def api_docs():
    """API Documentation with Swagger UI"""
    swagger_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="description" content="Loadosaurus Performance Testing Suite API Documentation" />
        <title>Loadosaurus API Docs</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
        <style>
            html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
            *, *:before, *:after { box-sizing: inherit; }
            body { margin:0; background: #fafafa; }
            .swagger-ui .topbar { display: none; }
            .swagger-ui .info { margin: 20px 0; }
            .swagger-ui .info .title { color: #3b4151; font-size: 36px; font-weight: 600; }
            .swagger-ui .info .description { color: #3b4151; font-size: 14px; }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
        <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"></script>
        <script>
            window.onload = function() {
                const ui = SwaggerUIBundle({
                    url: '/swagger.json',
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                    ],
                    plugins: [
                        SwaggerUIBundle.plugins.DownloadUrl
                    ],
                    layout: "StandaloneLayout"
                });
            };
        </script>
    </body>
    </html>
    """
    return swagger_html

@app.route('/swagger.json')
def swagger_json():
    """Swagger JSON specification"""
    swagger_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Loadosaurus Performance Testing Suite API",
            "description": "Advanced performance testing tool with JMeter integration and AI analysis",
            "version": "1.0.0",
            "contact": {
                "name": "LUDO Team",
                "url": "https://github.com/your-repo"
            }
        },
        "servers": [
            {
                "url": "http://127.0.0.1:5000",
                "description": "Development server"
            }
        ],
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health check",
                    "description": "Get backend health status and available endpoints",
                    "responses": {
                        "200": {
                            "description": "Backend is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "endpoints": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/store/inventory": {
                "get": {
                    "tags": ["store"],
                    "summary": "Returns pet inventories by status",
                    "description": "Get current pet inventory status",
                    "responses": {
                        "200": {
                            "description": "Successful operation",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "available": {"type": "integer"},
                                            "pending": {"type": "integer"},
                                            "sold": {"type": "integer"},
                                            "total": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/store/order": {
                "post": {
                    "tags": ["store"],
                    "summary": "Place an order for a pet",
                    "description": "Create a new pet order",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "petId": {"type": "integer"},
                                        "quantity": {"type": "integer"},
                                        "status": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Order created successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string"},
                                            "petId": {"type": "integer"},
                                            "quantity": {"type": "integer"},
                                            "status": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/store/order/{orderId}": {
                "get": {
                    "tags": ["store"],
                    "summary": "Find purchase order by ID",
                    "description": "Retrieve order details by order ID",
                    "parameters": [
                        {
                            "name": "orderId",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Order found",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string"},
                                            "petId": {"type": "integer"},
                                            "status": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "delete": {
                    "tags": ["store"],
                    "summary": "Delete purchase order by ID",
                    "description": "Remove order by order ID",
                    "parameters": [
                        {
                            "name": "orderId",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Order deleted successfully"
                        }
                    }
                }
            },
            "/user": {
                "post": {
                    "tags": ["user"],
                    "summary": "Create new user",
                    "description": "Create a new user account",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "username": {"type": "string"},
                                        "email": {"type": "string"},
                                        "firstName": {"type": "string"},
                                        "lastName": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "User created successfully"
                        }
                    }
                }
            },
            "/user/{username}": {
                "get": {
                    "tags": ["user"],
                    "summary": "Get user by username",
                    "description": "Retrieve user information",
                    "parameters": [
                        {
                            "name": "username",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "User found"
                        }
                    }
                },
                "put": {
                    "tags": ["user"],
                    "summary": "Update user",
                    "description": "Update user information",
                    "parameters": [
                        {
                            "name": "username",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "User updated successfully"
                        }
                    }
                },
                "delete": {
                    "tags": ["user"],
                    "summary": "Delete user",
                    "description": "Remove user account",
                    "parameters": [
                        {
                            "name": "username",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "User deleted successfully"
                        }
                    }
                }
            },
            "/pet": {
                "post": {
                    "tags": ["pet"],
                    "summary": "Add a new pet",
                    "description": "Create a new pet record",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "category": {"type": "object"},
                                            "tags": {"type": "array"}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Pet created successfully"
                        }
                    }
                }
            },
            "/pet/{petId}": {
                "get": {
                    "tags": ["pet"],
                    "summary": "Find pet by ID",
                    "description": "Retrieve pet information",
                    "parameters": [
                        {
                            "name": "petId",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Pet found"
                        }
                    }
                },
                "put": {
                    "tags": ["pet"],
                    "summary": "Update pet",
                    "description": "Update pet information",
                    "parameters": [
                        {
                            "name": "petId",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Pet updated successfully"
                        }
                    }
                },
                "delete": {
                    "tags": ["pet"],
                    "summary": "Delete pet",
                    "description": "Remove pet record",
                    "parameters": [
                        {
                            "name": "petId",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Pet deleted successfully"
                        }
                    }
                }
            },
            "/test-api": {
                "get": {
                    "tags": ["testing"],
                    "summary": "Test all HTTP methods",
                    "description": "General endpoint for testing various HTTP verbs",
                    "responses": {
                        "200": {
                            "description": "Request processed successfully"
                        }
                    }
                },
                "post": {
                    "tags": ["testing"],
                    "summary": "Test POST method",
                    "description": "Test POST request handling",
                    "responses": {
                        "200": {
                            "description": "POST request processed"
                        }
                    }
                }
            },
            "/test-api/delay/{seconds}": {
                "get": {
                    "tags": ["testing"],
                    "summary": "Test with configurable delay",
                    "description": "Test response time with specified delay",
                    "parameters": [
                        {
                            "name": "seconds",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Response with delay"
                        }
                    }
                }
            }
        },
        "tags": [
            {
                "name": "store",
                "description": "Access to Petstore orders"
            },
            {
                "name": "user",
                "description": "Operations about user"
            },
            {
                "name": "pet",
                "description": "Everything about your pets"
            },
            {
                "name": "testing",
                "description": "Testing and performance endpoints"
            }
        ]
    }
    return jsonify(swagger_spec)

if __name__ == '__main__':
    print("🚀 Starting Loadosaurus AI Performance Testing Suite...")
    print(f"📍 Backend URL: {BACKEND_URL}")
    print(f"📍 Frontend URL: {FRONTEND_URL}")
    print(f"🤖 AI Provider: {analyzer.ai_provider}")
    print(f"🔧 Environment: {'Production' if IS_PRODUCTION else 'Development'}")
    print("=" * 60)
    
    # Start Flask server (HTTP endpoints will work, Socket.IO will also work)
    app.run(host='0.0.0.0', port=PORT, debug=not IS_PRODUCTION) 