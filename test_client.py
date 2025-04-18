import requests
import json

def test_outfit_evaluation():
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

if __name__ == "__main__":
    test_outfit_evaluation()