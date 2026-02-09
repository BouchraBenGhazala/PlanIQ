import requests
from opik import Opik
from opik.evaluation import evaluate

# --- CONFIGURATION ---
API_URL = "http://localhost:8080/chat"  # port 8080
PROJECT_NAME = "PlanIQ"
DATASET_NAME = "PlanIQ_dataset"       # dataset UI

client = Opik(project_name=PROJECT_NAME)

def query_planiq_api(dataset_item):
    """
    This function plays the user's role.
    Takes the question from the dataset and send it to the API.
    """

    raw_input = dataset_item.get("input")
    
    user_question = ""
    
    if isinstance(raw_input, dict):
        user_question = raw_input.get("input") or raw_input.get("user_message") or raw_input.get("question")
    elif isinstance(raw_input, str):
        user_question = raw_input
    else:
        user_question = dataset_item.get("user_message") or dataset_item.get("question")

    if not user_question:
        print(f"DEBUG: received item not recognized: {dataset_item}")
        return {"output": "Error: Question not found in dataset item"}
    
    # --- FIX DONE ---

    payload = {
        "messages": [
            {"role": "user", "content": user_question}
        ]
    }
    
    try:
        # backend 
        response = requests.post(API_URL, json=payload)
        
        # Errors HTTP (404, 500...)
        if response.status_code != 200:
            return {"output": f"Error {response.status_code}: {response.text}"}

        data = response.json()
        
        # response Opik AI
        return {
            "output": data.get("response", "No response received")
        }
    except Exception as e:
        return {"output": f"Connection Error: {str(e)}"}

# --- 2. Validation ---
class KeywordCheck:
    name = "Non-empty response check" 
    
    def score(self, input, output, expected_output=None, **kwargs):
        ai_response = output.get("output", "")
        
        # Technical error
        if "Error" in ai_response:
            return 0.0
            
        # Empty response
        if not ai_response or len(ai_response.strip()) < 2:
            return 0.0
            
        return 1.0


if __name__ == "__main__":
    print(f"Apploading the dataset '{DATASET_NAME}' in the project '{PROJECT_NAME}'...")
    
    try:
        dataset = client.get_dataset(name=DATASET_NAME)
        print(f"Dataset found with success.")
    except Exception as e:
        print(f"CRITICAL Error: Impossible to find the dataset '{DATASET_NAME}'.")
        print(f"Details: {e}")
        exit()

    print("Experience starts...")
    
    try:
        evaluate(
            experiment_name="PlanIQ_Final_Validation",
            dataset=dataset,
            task=query_planiq_api,
            scoring_metrics=[KeywordCheck()],
            project_name=PROJECT_NAME
        )
        print("\nExperience done ! Return to Opik UI > Experiments.")
        
    except Exception as e:
        print(f"\nError during evaluation : {e}")