# Use the Converse API to send a text message to Llama 2 Chat 70B.
import boto3, util, sys
from botocore.exceptions import ClientError
input = sys.stdin.readline

client = boto3.client('bedrock-runtime')
model_id = "meta.llama3-70b-instruct-v1:0"
output_path = "/Users/ssnipro/kitchen/a/output.txt"

conversation = []
util.wipe(output_path)
for _ in range(3):
    user_msg = input().strip()
    conversation.append({
        "role": "user",
        "content": [{"text": user_msg}]
    })
    try:
        response = client.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={"maxTokens":512,"temperature":0.5,"topP":0.9},
            additionalModelRequestFields={}
        )
        response_text = response["output"]["message"]["content"][0]["text"]
        conversation.append({
            "role": "assistant",
            "content": [{"text": response_text}]
        })
        util.write(output_path, response_text, False)
    except (ClientError, Exception) as e:
        util.write(output_path, f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)