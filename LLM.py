import boto3, json, os
from dotenv import load_dotenv
from util import invoke_model
from botocore.exceptions import ClientError

# load env vars
load_dotenv()
# keyId = os.getenv('AWS_ACCESS_KEY_ID')
# secretKey = os.getenv('AWS_SECRET_ACCESS_KEY')
# region = os.getenv('AWS_REGION')
path = os.getenv('FILE_PATH')

# init boto3 client, model config
client = boto3.client('bedrock-runtime')
model_id = "meta.llama3-70b-instruct-v1:0"


# Read activity data
def load_activities(path: str) -> list:
    return [
        open(os.path.join(path, f), 'r').read().split('\n') 
        for f in os.listdir(path)[::-1]
    ]

# Calculate RMSE
def calculate_rmse(activities: list) -> float:
    prompt_template = "How long is this activity going to take in terms of hours? Just answer the total time in hours without additional explanation or extra words.\n\nActivity description:\n"
    rmse_data = []
    for activity, actual_time in activities:
        prompt = prompt_template + activity
        predicted_time = invoke_model(client, model_id, prompt)
        if "-" in predicted_time:
            f, s = predicted_time.split("-")
            predicted_time = (float(f)+float(s)) / 2
        else:
            predicted_time = eval(predicted_time)
        rmse_data.append((predicted_time, float(actual_time)))
        print((predicted_time, float(actual_time)))
    N = len(rmse_data)
    rmse = sum(((x1-x2)**2) for x1, x2 in rmse_data)/N
    return rmse**0.5

def main():
    activities = load_activities(path)
    rmse = calculate_rmse(activities)
    print(f"RMSE: {rmse}")

if __name__ == "__main__":
    main()

