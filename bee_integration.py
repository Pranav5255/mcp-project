from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import httpx
import json
from typing import Dict, Any, List, Optional

app = FastAPI()

# Configuration
MCP_SERVER_URL = "http://localhost:8000/mcp"

class BeeRequest(BaseModel):
    type: str
    content: Dict[str, Any]

class BeeResponse(BaseModel):
    action: str
    action_input: Dict[str, Any]

class MCPRequest(BaseModel):
    action: str
    action_input: Dict[str, Any]

@app.post("/tools/evaluateOutfit")
async def evaluate_outfit(request: BeeRequest):
    """Tool to evaluate clothing combinations"""
    try:
        if request.type != "action_input":
            raise HTTPException(status_code=400, detail="Invalid request type")
        
        content = request.content
        
        # Validate required fields
        required_fields = ["top_type", "top_color", "bottom_type", "bottom_color"]
        for field in required_fields:
            if field not in content:
                return {
                    "action": "final_answer",
                    "action_input": {
                        "answer": f"I need to know the {field} to evaluate the outfit. Please provide this information."
                    }
                }
        
        # Forward request to MCP server
        mcp_request = MCPRequest(
            action="evaluate_outfit",
            action_input={
                "top_type": content["top_type"],
                "top_color": content["top_color"],
                "bottom_type": content["bottom_type"],
                "bottom_color": content["bottom_color"]
            }
        )
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                MCP_SERVER_URL,
                json=mcp_request.dict()
            )
            
            if response.status_code != 200:
                return {
                    "action": "final_answer",
                    "action_input": {
                        "answer": "I encountered an error while evaluating your outfit combination. Please try again later."
                    }
                }
            
            mcp_response = response.json()
            outfit_eval = mcp_response["response"]
            
            # Craft a response for the user
            if outfit_eval["is_good_combination"]:
                result = f"👍 Great choice! Your {content['top_color']} {content['top_type']} and {content['bottom_color']} {content['bottom_type']} make a good combination."
            else:
                result = f"🤔 The combination of {content['top_color']} {content['top_type']} with {content['bottom_color']} {content['bottom_type']} could be improved."
                
            # Add suggestions
            suggestions = "\n\nSuggestions:\n"
            for i, suggestion in enumerate(outfit_eval["suggestions"], 1):
                suggestions += f"{i}. {suggestion}\n"
                
            final_answer = result + suggestions
            
            return {
                "action": "final_answer",
                "action_input": {
                    "answer": final_answer
                }
            }
            
    except Exception as e:
        return {
            "action": "final_answer",
            "action_input": {
                "answer": f"I encountered an error: {str(e)}. Please try again."
            }
        }

# Define the tool specifications for the Bee Framework
@app.get("/tools")
async def get_tools():
    return [
        {
            "name": "evaluateOutfit",
            "description": "Evaluates if a clothing combination looks good together and provides suggestions for improvement",
            "parameters": {
                "type": "object",
                "properties": {
                    "top_type": {
                        "type": "string",
                        "description": "Type of top wear (e.g., t-shirt, shirt, blouse, sweater, hoodie)"
                    },
                    "top_color": {
                        "type": "string",
                        "description": "Color of the top wear"
                    },
                    "bottom_type": {
                        "type": "string",
                        "description": "Type of bottom wear (e.g., jeans, chinos, skirt, shorts, trousers)"
                    },
                    "bottom_color": {
                        "type": "string",
                        "description": "Color of the bottom wear"
                    }
                },
                "required": ["top_type", "top_color", "bottom_type", "bottom_color"]
            }
        }
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bee_integration:app", host="0.0.0.0", port=8001, reload=True)