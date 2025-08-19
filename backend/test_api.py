#!/usr/bin/env python3
"""
Simple API Testing Script for LUDO Performance Testing Suite
Tests all the new Petstore-style endpoints
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(method, url, data=None, headers=None):
    """Test a single endpoint"""
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        print(f"✅ {method} {url}")
        print(f"   Status: {response.status_code}")
        if response.content:
            try:
                content = response.json()
                print(f"   Response: {json.dumps(content, indent=2)}")
            except:
                print(f"   Response: {response.text}")
        print()
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {url} - Connection failed (Is backend running?)")
        return False
    except Exception as e:
        print(f"❌ {method} {url} - Error: {e}")
        return False

def main():
    """Test all endpoints"""
    print("🧪 Testing Loadosaurus Performance Testing Suite API Endpoints")
    print("=" * 60)
    
    # Test basic endpoints
    print("🔍 Testing Basic Endpoints:")
    test_endpoint("GET", f"{BASE_URL}/health")
    test_endpoint("GET", f"{BASE_URL}/test-api")
    
    # Test Store API
    print("🏪 Testing Store API:")
    test_endpoint("GET", f"{BASE_URL}/store/inventory")
    
    order_data = {"petId": 1, "quantity": 2}
    test_endpoint("POST", f"{BASE_URL}/store/order", order_data)
    
    test_endpoint("GET", f"{BASE_URL}/store/order/ORDER_12345")
    test_endpoint("DELETE", f"{BASE_URL}/store/order/ORDER_12345")
    
    # Test User API
    print("👤 Testing User API:")
    user_data = {"username": "testuser", "email": "test@example.com", "firstName": "Test", "lastName": "User"}
    test_endpoint("POST", f"{BASE_URL}/user", user_data)
    
    test_endpoint("GET", f"{BASE_URL}/user/testuser")
    
    update_data = {"firstName": "Updated", "lastName": "User", "email": "updated@example.com"}
    test_endpoint("PUT", f"{BASE_URL}/user/testuser", update_data)
    
    test_endpoint("DELETE", f"{BASE_URL}/user/testuser")
    
    # Test Pet API
    print("🐕 Testing Pet API:")
    pet_data = {"name": "Fluffy", "category": {"id": 1, "name": "Dogs"}, "tags": [{"id": 1, "name": "friendly"}]}
    test_endpoint("POST", f"{BASE_URL}/pet", pet_data)
    
    test_endpoint("GET", f"{BASE_URL}/pet/PET_12345")
    
    update_pet = {"name": "Updated Fluffy", "status": "sold"}
    test_endpoint("PUT", f"{BASE_URL}/pet/PET_12345", update_pet)
    
    test_endpoint("DELETE", f"{BASE_URL}/pet/PET_12345")
    
    # Test delay endpoint
    print("⏱️ Testing Delay Endpoint:")
    test_endpoint("GET", f"{BASE_URL}/test-api/delay/1")
    
    print("🎉 API Testing Complete!")

if __name__ == "__main__":
    main()
