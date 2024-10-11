import boto3, json, os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

def invoke_model(client, model_id, prompt: str) -> str:
    formatted_prompt = f"""
    <|begin_of_text|>
    <|start_header_id|>user<|end_header_id|>
    {prompt}
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """
    request = json.dumps({"prompt": formatted_prompt, "max_gen_len": 2048, "temperature": 0.2,})
    try:
        response = client.invoke_model(modelId=model_id, body=request)
        model_response = json.loads(response["body"].read())
        return model_response.get("generation", "")
    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)

def wipe(file_path):
    with open(file_path, 'w') as _:
        pass

def write(file_path, output, ifwipe=True):
    if (ifwipe): 
        wipe(file_path)
    with open(file_path, 'a') as file:
        file.write(output)
