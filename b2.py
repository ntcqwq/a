from botocore.exceptions import ClientError
import os, sys, glob, boto3, json, pandas as pd, datetime
import util

def load_activities(file_paths: list) -> list:
    result = []
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            result.append(file.read().split('\n'))
    return result

def split_into_chunks(tasks: list, chunk_size: int) -> list:
    """Divides the tasks list into smaller chunks of a specified size."""
    for i in range(0, len(tasks), chunk_size):
        yield tasks[i:i + chunk_size]

def invoke_model_in_chunks(client, model_id, prompt_template, tasks, chunk_size):
    all_scheduled_tasks = []
    
    # Break down tasks into smaller chunks
    for chunk in split_into_chunks(tasks, chunk_size):
        # Prepare chunk prompt
        chunk_prompt = prompt_template + str(chunk)
        
        # Invoke the model for each chunk
        ret = util.invoke_model(client, model_id, chunk_prompt)
        
        # Evaluate and collect the response
        chunk_tasks = eval(ret)
        all_scheduled_tasks.extend(chunk_tasks)

    return all_scheduled_tasks

client = boto3.client('bedrock-runtime')
model_id = "meta.llama3-70b-instruct-v1:0"
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

"""

if __name__ == "__main__":
    file_paths = sorted(glob.glob("/Users/ssnipro/kitchen/a/activityData/*.txt"))
    
    # Load activities from files
    tasks = load_activities(file_paths)

    # Define the chunk size based on how many tasks you estimate would fit under the token limit
    chunk_size = 10  # Adjust this based on the size of tasks and token limits

    # Invoke model with chunked tasks
    all_scheduled_tasks = invoke_model_in_chunks(client, model_id, prompt_template, tasks, chunk_size)

    # Process the result into a pandas DataFrame
    df = pd.DataFrame(all_scheduled_tasks)
    df['start'] = pd.to_datetime(df['start'])
    df['end'] = pd.to_datetime(df['end'])
    df = df.sort_values(by='start')

    # Write the output to a file
    util.wipe("/Users/ssnipro/kitchen/a/output.txt")
    for i, r in df.iterrows():
        util.write("/Users/ssnipro/kitchen/a/output.txt", f"{r['start']} - {r['end']}: {r['description']}\n", False)
