# !!!
# DEPRECATED: To be replaced with autofilling a config.
# !!!

import json

from config import DATETIME_FORMAT, API_KEY
from openai import OpenAI
from datetime import datetime
from database import Task, Event
from sqlalchemy.orm import Session
from tools import convertToJson
from backend.services.events import get_standalone_events, get_events, delete_events_from_task
from services.autofill import client
from dotenv import load_dotenv
load_dotenv()
print(f"API_KEY:{API_KEY}")


client = OpenAI()

system_prompt = \
    """You are a calendar and task manager. Your job: break down tasks into events to be placed in a calendar. 
The number of events is determined by the the complexity and length of the task. 
Your response should be in JSON only, no markdown, explanation or any other text. store it like this: {"events": [list of events here]}

An event has 3 keys: ['taskID', 'start', 'end']. Here are their descriptions:
'taskID': task id of this event (integer),
'start': start datetime (string),
'end': end datetime (string).

The user will also provide a calendar, as a list of events, so you can avoid conflicts and space out events effectively.

IMPORTANT: the length of each of these events (end-start) should be appropriately chosen to prevent overloading students with work, about 30 to 120 minutes long. You receive the duration of the
task in minutes, so you can use this to help determine the length of each event. Sum of events length should be equal to the duration of the task.

Schedule events as if you are a real human, i.e. a real human would not schedule
all events at 3 AM even though technically this time is available on the
calendar. Be more sensible, and think about how a real human would spread their
workload throughout the day. Think about how the events would be spread out
throughout multiple days as well, don't just clump everything in one day.

Do NOT schedule any events between 11 PM and 6 AM !! This period is reserved
only for sleep. IT IS STRICTLY FORBIDDEN TO SCHEDLUE ANYTHING BETWEEN THE TIMES
23:00-6:00
"""


def get_user_prompt(task: Task, calendar: dict):
    return \
    f"""This is my task:
{convertToJson(task)}
A priority of 2 is most important.

This is my calendar (events only have start and end times to save space):
{calendar}"""

def breakdown_task_LLM(user_prompt):
    try:
        completion = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
        )
        
        if (not completion) or (not completion.choices):
                print("Error: API response is empty.")
                return {}  
        
        print(completion)
        response = completion.choices[0].message.content

        if response is None:
                print("Error: API response message content is None.")
                return {}  
            
        print(response)
        response = json.loads(response)
        
        return response

    except Exception as e:
        print("API Error:", str(e))
        return {}  
    

def break_down_add_events(username: str, taskID: int, db: Session) -> dict:
    task = db.query(Task).filter(Task.taskID == taskID).first()
    events = get_events(username, (datetime.now(), task.deadline), db)["events"]
    
    if task.events != []:
        delete_events_from_task(taskID, db)  # Delete all the events that are prexisting
        
    print("Doing some shit")
    
    standalone_events = get_standalone_events(username, (datetime.now(), task.deadline), db)["standalone_events"]
    
    calendar = [{"start": event["start"], "end": event["end"]} for event in events]
    calendar.extend([{"start": s_event["start"], "end": s_event["end"]} for s_event in standalone_events])
    out = breakdown_task_LLM(get_user_prompt(task, calendar))
    new_events_json = out['events']
    
    print("EVENTS: ", new_events_json, type(new_events_json))
    
    new_events = [Event(taskID=v["taskID"], 
                        start=datetime.strptime(v["start"], DATETIME_FORMAT), 
                        end=datetime.strptime(v["end"], DATETIME_FORMAT)) for v in new_events_json]
    
    db.bulk_save_objects(new_events)    
    db.commit()
    
    return {"events_added": new_events_json}