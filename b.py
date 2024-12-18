from botocore.exceptions import ClientError
import os, sys, glob, boto3, json, util, pandas as pd

def load_activities(file_paths: list) -> list:
    result = []
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            result.append(file.read().split('\n'))
    return result

# add existing commitments to prompt?
# Existing commitments:
# [[existing_task1, existing_start1, existing_end1], [existing_task2, existing_start2, existing_end2] ... and so on]

client = boto3.client('bedrock-runtime')
model_id = "meta.llama3-70b-instruct-v1:0"
op = "/Users/ssnipro/kitchen/a/output.txt"

prompt_template = """You are an AI assistant helping me manage my time by scheduling tasks into my calendar. I will provide you with a list of tasks along with their predicted durations. Your job is to assign viable timeframes for each task based on the following guidelines:

Output Format: For each task, provide:

Output an array of dictionaries in this format:
[
    {"description": string (the task description), "start": datetime (when the task should begin), "end": datetime (when the task should end)},
    {"description": string (the task description), "start": datetime (when the task should begin), "end": datetime (when the task should end)},
    ... (for each task)
]

Just output the python list of dictionaries without additional explanation or extra words.

Scheduling Constraints:

- Assume that I wake up at 8 AM and sleep at 12 AM, and that I have no unavailable times other than that constraint or prior commitments. The tasks can only be scheduled within these hours.
- Ensure there are reasonable breaks between tasks if necessary.
- If tasks have dependencies or need to be in a specific order, schedule them accordingly.
- The tasks do not have to neccesarily be in order, and make sure that it is realistic to transition from one task to another task. 
- For example, if one of my tasks is to "drive from Toronto to Montreal", and another one of my tasks is "drive from Toronto to New York", please consider addictional factors that might impact my schedule (in this case, time driving from Monteral to New York)
- Events could be planned throughout several days.
- Please ensure the start time and end time of a task is valid (e.g. 2:87 PM cannot exist)

Here is the list of tasks with their predicted durations:

[[prompt1, duration1 (in hours)], [prompt2, duration2 (in hours)]...and so on]

Please provide the schedule in a clear and organized manner.

Example Input:

[["Write project report", "2"], ["Team meeting", "1"], ["Code review", "1.5"]]

Example Output:

[
    {"description": "Team meeting", "start": "2023-10-05 09:00 AM", "end": "2023-10-05 11:00 AM",
    {"description": "Write project report", "start": "2023-10-05 10:15 AM", "end": "2023-10-05 11:15 PM"},
    ... (for each task)
]

Attached below are my actual tasks.

"""

if __name__ == "__main__":
    conversation = []
    file_paths = sorted(glob.glob("/Users/ssnipro/kitchen/a/activityData/*.txt"))
    chunked_paths = [file_paths[i:i+10] for i in range(0, len(file_paths), 10)]
    tasks = []
    for i, chunk in enumerate(chunked_paths):
        result = load_activities(chunk)
        conversation.append({
            "role": "user",
            "content": [{"text": (prompt_template if i == 0 else "")+str(result)}]
        }) 
        try:
            response = client.converse(
                modelId=model_id,
                messages=conversation,
                inferenceConfig={"maxTokens":2048,"temperature":0.5,"topP":0.9},
                additionalModelRequestFields={}
            )
            response_text = response["output"]["message"]["content"][0]["text"]
            conversation.append({
                "role": "assistant",
                "content": [{"text": response_text}]
            })
            tasks = tasks+eval(response_text)
        except (ClientError, Exception) as e:
            util.write(op, f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
            exit(1)
    df = pd.DataFrame(tasks)
    df['start'] = pd.to_datetime(df['start'])
    df['end'] = pd.to_datetime(df['end'])
    df = df.sort_values(by='start')
    util.wipe(op)
    for i, r in df.iterrows():
        util.write(op, f"{r['start']} - {r['end']}: {r['description']}\n", False)

# ERROR: Can't invoke 'meta.llama3-70b-instruct-v1:0'. Reason: An error occurred (ValidationException) when calling the InvokeModel operation: Malformed input request: #/max_gen_len: 16384 is not less or equal to 2048, please reformat your input and try again.
