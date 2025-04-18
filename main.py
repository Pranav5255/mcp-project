from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import pandas as pd
from typing import Dict, Any, List, Optional
import uvicorn
import os

app = FastAPI()

# Load model and encoders
with open('clothing_combo_model.pkl', 'rb') as file:
    model = pickle.load(file)

with open('encoders.pkl', 'rb') as file:
    encoders = pickle.load(file)

class ClothingInput(BaseModel):
    top_type: str
    top_color: str
    bottom_type: str
    bottom_color: str

class MCPRequest(BaseModel):
    action: str
    action_input: Dict[str, Any]

class MCPResponse(BaseModel):
    response: Dict[str, Any]

def get_color_compatibility_rules(top_color: str, bottom_color: str) -> List[str]:
    """Generate style rules based on color combinations"""
    neutral_colors = ['black', 'white', 'gray', 'beige', 'khaki', 'navy', 'brown']
    
    suggestions = []
    
    # Basic rules
    if top_color == bottom_color:
        suggestions.append("Wearing the same color for top and bottom can look monochromatic. Consider adding a contrasting accessory.")
    
    # Color wheel opposites generally work well
    good_pairs = [
        {'blue', 'orange'}, {'red', 'green'}, {'yellow', 'purple'},
        {'black', 'white'}, {'navy', 'khaki'}, {'burgundy', 'blue'}
    ]
    
    # Some challenging combinations
    difficult_pairs = [
        {'red', 'pink'}, {'orange', 'red'}, {'brown', 'black'},
        {'neon_green', 'neon_pink'}, {'purple', 'green'}, {'yellow', 'red'}
    ]
    
    current_pair = {top_color, bottom_color}
    
    for pair in good_pairs:
        if current_pair == pair:
            suggestions.append(f"The {top_color} and {bottom_color} combination is complementary and works well.")
    
    for pair in difficult_pairs:
        if current_pair == pair:
            suggestions.append(f"The {top_color} and {bottom_color} combination can be challenging. Consider replacing one with a neutral.")
    
    if top_color in neutral_colors and bottom_color in neutral_colors:
        suggestions.append("Your outfit is neutral and versatile but might benefit from a pop of color with accessories.")
    
    if not suggestions:  # If no specific rules matched
        suggestions.append(f"Consider whether {top_color} and {bottom_color} complement each other based on the color wheel.")
    
    return suggestions

@app.post("/mcp", response_model=MCPResponse)
async def mcp_endpoint(request: MCPRequest):
    if request.action == "evaluate_outfit":
        return evaluate_outfit(request.action_input)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported action: {request.action}")

def evaluate_outfit(input_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Extract clothing details
        top_type = input_data.get('top_type', '')
        top_color = input_data.get('top_color', '')
        bottom_type = input_data.get('bottom_type', '')
        bottom_color = input_data.get('bottom_color', '')
        
        # Encode inputs
        encoded_top_type = encoders['top_type'].transform([top_type])[0] if top_type in encoders['top_type'].classes_ else -1
        encoded_top_color = encoders['top_color'].transform([top_color])[0] if top_color in encoders['top_color'].classes_ else -1
        encoded_bottom_type = encoders['bottom_type'].transform([bottom_type])[0] if bottom_type in encoders['bottom_type'].classes_ else -1
        encoded_bottom_color = encoders['bottom_color'].transform([bottom_color])[0] if bottom_color in encoders['bottom_color'].classes_ else -1
        
        # Check if any encoding failed
        if -1 in [encoded_top_type, encoded_top_color, encoded_bottom_type, encoded_bottom_color]:
            return {
                "response": {
                    "is_good_combination": False,
                    "confidence": 0.0,
                    "suggestions": ["One or more of your clothing items or colors are not in my database. Please check your spelling or try different options."],
                    "message": "Unknown clothing item or color"
                }
            }
        
        # Predict with model
        X = [[encoded_top_type, encoded_top_color, encoded_bottom_type, encoded_bottom_color]]
        prediction = model.predict(X)[0]
        confidence = model.predict_proba(X)[0][1]  # Probability of good combination
        
        # Generate suggestions based on prediction
        suggestions = []
        
        if prediction == 1:
            message = "This is a good outfit combination!"
            suggestions.append("Your combination looks great!")
            
            # Add style tips even for good combinations
            color_rules = get_color_compatibility_rules(top_color, bottom_color)
            suggestions.extend(color_rules)
            
        else:
            message = "This combination could be improved."
            
            # Suggest alternatives based on what works well with the top
            similar_tops_df = pd.read_csv('clothing_combinations.csv')
            similar_tops = similar_tops_df[(similar_tops_df['top_type'] == top_type) & 
                                          (similar_tops_df['good_combination'] == 1)]
            
            if not similar_tops.empty:
                alternative = similar_tops.iloc[0]
                suggestions.append(f"Consider pairing your {top_color} {top_type} with {alternative['bottom_color']} {alternative['bottom_type']} instead.")
            
            # Add general rules for the combination
            color_rules = get_color_compatibility_rules(top_color, bottom_color)
            suggestions.extend(color_rules)
            
            # Add general advice
            if bottom_type == "jeans":
                suggestions.append("Jeans are versatile - try a different colored top to create a better match.")
            
        return {
            "response": {
                "is_good_combination": bool(prediction),
                "confidence": float(confidence),
                "suggestions": suggestions,
                "message": message
            }
        }
        
    except Exception as e:
        return {
            "response": {
                "is_good_combination": False,
                "confidence": 0.0,
                "suggestions": ["An error occurred while processing your request."],
                "message": f"Error: {str(e)}"
            }
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)