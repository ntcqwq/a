from botocore.exceptions import ClientError
from dotenv import load_dotenv
import boto3, json, os

load_dotenv()
keyId = os.getenv('AWS_ACCESS_KEY_ID')
secretKey = os.getenv('AWS_SECRET_ACCESS_KEY')
region = os.getenv('AWS_REGION')

client = boto3.client('bedrock-runtime', region_name=region, aws_access_key_id=keyId, aws_secret_access_key=secretKey)
model_id = "meta.llama3-70b-instruct-v1:0"
prompt = "what is the 5th fibonacci number"

def invoke(prompt) -> str:
    formatted_prompt = f"""
    <|begin_of_text|>
    <|start_header_id|>user<|end_header_id|>
    {prompt}
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """
    native_request = {
        "prompt": formatted_prompt,
        "max_gen_len": 512,
        "temperature": 0.2,
    }
    request = json.dumps(native_request)
    try:
        response = client.invoke_model(modelId=model_id, body=request)
    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)
    model_response = json.loads(response["body"].read())
    response_text = model_response["generation"]
    return response_text

# glob
path = "/Users/ssnipro/kitchen/a/activityData"
afiles = os.listdir(path)

def activity():
    activities = []
    for f in afiles[::-1]:
        f_path = os.path.join(path, f)
        with open(f_path, 'r') as file:
            content = file.read()
            activities.append(content.split('\n'))
    return activities

def main():
    rmse = []
    prefix = "How long is this activity going to take in term of hours? Just answer the total time in hours without additional explanation or extra words. \n\nActivity description:\n"
    a = activity()
    for content, ans in a:
        rmse.append([])
        prompt = prefix+content
        print("Llama")
        output = invoke(prompt)
        print(output)
        if "-" in output:
            f, s = output.split("-")
            rmse[-1].append((float(f)+float(s))/2)
        else:
            rmse[-1].append(eval(output))
        print("Actual")
        print(ans)
        rmse[-1].append(float(ans))
        print('=============')
    N = len(rmse)
    ans = 0
    for x1, x2 in rmse:
        ans += ((x1-x2)**2)/N
    ans**=0.5
    print("RSME:",ans)
main()