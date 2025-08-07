from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import google.generativeai as genai
import openai
import os
import json
import subprocess
from datetime import datetime
import requests
from dotenv import load_dotenv
from jmeter_runner import JMeterRunner
import threading
import time

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-gemini-api-key-here')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Configure OpenRouter API
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', 'your-openrouter-api-key-here')
OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
OPENROUTER_SITE_URL = os.getenv('OPENROUTER_SITE_URL', 'https://your-site-url.com')
OPENROUTER_SITE_NAME = os.getenv('OPENROUTER_SITE_NAME', 'Ludo Performance Suite')

# Initialize OpenRouter client
openai.api_key = OPENROUTER_API_KEY
openai.api_base = OPENROUTER_BASE_URL

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
        if OPENROUTER_API_KEY != 'your-openrouter-api-key-here':
            return 'openrouter'
        elif GEMINI_API_KEY != 'your-gemini-api-key-here':
            return 'gemini'
        else:
            return 'fallback'

    def agent_brain(self, jmeter_output, image_url=None):
        """
        AI Agent Brain - Analyzes JMeter output and makes intelligent decisions
        Supports both text and image analysis
        """
        try:
            if self.ai_provider == 'openrouter':
                return self._openrouter_analysis(jmeter_output, image_url)
            elif self.ai_provider == 'gemini':
                return self._gemini_analysis(jmeter_output, image_url)
            else:
                return self._generate_fallback_analysis(jmeter_output)

        except Exception as e:
            print(f"AI analysis failed: {e}")
            return self._generate_fallback_analysis(jmeter_output)

    def _openrouter_analysis(self, jmeter_output, image_url=None):
        """Use OpenRouter API with Gemini 2.0 Flash for analysis"""
        try:
            # Enhanced prompt for AI agent behavior
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
            
            # Add image analysis if provided
            if image_url:
                # Multi-modal analysis with image
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ]
            else:
                # Text-only analysis
                messages = [
                    {"role": "user", "content": prompt}
                ]
            
            completion = openai.ChatCompletion.create(
                model="google/gemini-2.0-flash-exp",
                messages=messages,
                max_tokens=1000,
                temperature=0.3
            )
            
            response_text = completion.choices[0].message.content
            
            # Parse JSON response
            try:
                agent_result = json.loads(response_text)
                return {
                    "success": True,
                    "agent_response": agent_result,
                    "raw_response": response_text,
                    "ai_provider": "openrouter",
                    "model": "gemini-2.0-flash-exp",
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
                    "ai_provider": "openrouter",
                    "model": "gemini-2.0-flash-exp",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"OpenRouter analysis failed: {e}")
            return {
                "success": False,
                "error": f"OpenRouter analysis failed: {str(e)}",
                "ai_provider": "openrouter",
                "timestamp": datetime.now().isoformat()
            }

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
        "message": "Ludeosaurous AI Backend",
        "version": "1.0.0",
        "gemini_connected": GEMINI_API_KEY != 'your-gemini-api-key-here',
        "openrouter_connected": OPENROUTER_API_KEY != 'your-openrouter-api-key-here',
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
            "POST /test/:id/stop": "Stop a running test"
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
        "openrouter_available": OPENROUTER_API_KEY != 'your-openrouter-api-key-here',
        "ai_provider": analyzer.ai_provider,
        "jmeter_available": jmeter_available,
        "jmeter_path": jmeter_path,
        "environment": "production" if IS_PRODUCTION else "development"
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
        
        # Validate required fields
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
        
        # Start JMeter test
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
        "openrouter_connected": OPENROUTER_API_KEY != 'your-openrouter-api-key-here',
        "ai_provider": analyzer.ai_provider,
        "memory_entries": len(analyzer.agent_memory),
        "jmeter_available": True,
        "environment": "production" if IS_PRODUCTION else "development",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting Ludeosaurous AI Performance Testing Suite...")
    print(f"📍 Backend URL: {BACKEND_URL}")
    print(f"📍 Frontend URL: {FRONTEND_URL}")
    print(f"🤖 AI Provider: {analyzer.ai_provider}")
    print(f"🔧 Environment: {'Production' if IS_PRODUCTION else 'Development'}")
    print("=" * 60)
    
    # Start Flask server (HTTP endpoints will work, Socket.IO will also work)
    app.run(host='0.0.0.0', port=PORT, debug=not IS_PRODUCTION) 