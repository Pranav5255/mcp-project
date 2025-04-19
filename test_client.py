import requests
import json

def test_outfit_evaluation_bee():
    """Test the Bee Framework tool integration"""
    bee_url = "http://localhost:8001/tools/evaluateOutfit"
    
    test_cases = [
        {
            "top_type": "t-shirt",
            "top_color": "white",
            "bottom_type": "jeans",
            "bottom_color": "blue"
        },
        {
            "top_type": "shirt",
            "top_color": "purple",
            "bottom_type": "pants",
            "bottom_color": "green"
        }
    ]
    
    print("\n=== TESTING BEE FRAMEWORK INTEGRATION ===")
    for idx, test_case in enumerate(test_cases, 1):
        payload = {
            "type": "action_input",
            "content": test_case
        }
        
        print(f"\nTest case {idx}: {test_case['top_color']} {test_case['top_type']} with {test_case['bottom_color']} {test_case['bottom_type']}")
        
        response = requests.post(bee_url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("Result:")
            print(result["action_input"]["answer"])
        else:
            print(f"Error: {response.status_code} - {response.text}")
        
        print("-" * 50)

def test_mcp_inspector_endpoints():
    """Test the MCP Inspector compatible endpoints"""
    base_url = "http://localhost:8000"
    
    print("\n=== TESTING MCP INSPECTOR COMPATIBILITY ===")
    
    # Test health endpoint
    print("\nTesting health endpoint...")
    health_response = requests.get(f"{base_url}/health")
    if health_response.status_code == 200:
        print(f"Status: {health_response.status_code}")
        print(f"Response: {json.dumps(health_response.json(), indent=2)}")
    else:
        print(f"Error: {health_response.status_code} - {health_response.text}")
    
    # Test metadata endpoint
    print("\nTesting metadata endpoint...")
    metadata_response = requests.get(f"{base_url}/metadata")
    if metadata_response.status_code == 200:
        print(f"Status: {metadata_response.status_code}")
        print(f"Response: {json.dumps(metadata_response.json(), indent=2)}")
    else:
        print(f"Error: {metadata_response.status_code} - {metadata_response.text}")
    
    # Test MCP-compatible prediction endpoint
    print("\nTesting prediction endpoint...")
    test_case = {
        "inputs": {
            "top_type": "sweater",
            "top_color": "navy",
            "bottom_type": "chinos",
            "bottom_color": "khaki"
        }
    }
    
    predict_response = requests.post(
        f"{base_url}/v1/models/clothing-advisor:predict",
        json=test_case
    )
    
    if predict_response.status_code == 200:
        print(f"Status: {predict_response.status_code}")
        print(f"Response: {json.dumps(predict_response.json(), indent=2)}")
    else:
        print(f"Error: {predict_response.status_code} - {predict_response.text}")
    
    print("-" * 50)

def test_original_mcp_endpoint():
    """Test the original MCP endpoint"""
    mcp_url = "http://localhost:8000/mcp"
    
    print("\n=== TESTING ORIGINAL MCP ENDPOINT ===")
    
    payload = {
        "action": "evaluate_outfit",
        "action_input": {
            "top_type": "hoodie",
            "top_color": "black",
            "bottom_type": "jeans",
            "bottom_color": "blue"
        }
    }
    
    response = requests.post(mcp_url, json=payload)
    
    if response.status_code == 200:
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
    print("-" * 50)

if __name__ == "__main__":
    # Test all endpoints
    try:
        test_outfit_evaluation_bee()
    except Exception as e:
        print(f"Bee Framework test failed: {str(e)}")
    
    try:
        test_mcp_inspector_endpoints()
    except Exception as e:
        print(f"MCP Inspector test failed: {str(e)}")
    
    try:
        test_original_mcp_endpoint()
    except Exception as e:
        print(f"Original MCP endpoint test failed: {str(e)}")
    
    print("\nAll tests completed!")