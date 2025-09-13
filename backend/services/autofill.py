# !!!
# DEPRECATED: To be replaced with autofilling a config.
# !!!

import datetime
from typing import Literal, Optional

from dotenv import load_dotenv
from joblib import Memory
from openai import OpenAI
from pydantic import BaseModel

from backend.misc.logger import get_logger

log = get_logger(__name__)

load_dotenv()

client = OpenAI()


system_prompt = (
    "You are part of a time management application, responsible for translating the user's task description into a structured object."
    "The first message will include some context. Use reasonable guesses for fields if unsure, but always use user input whrere possible."
    "Use the string None if completely not applicable."
    "Do not do anything which could mislead users into thinking properties have been set for the event that have not,"
    "for example don't say 'recurring task' in the description or imply that the task repeats if you cannot actually set the task as recurring, as you cannot.\n\n"
    "There are two types that can be returned: Task and Event. Task is a to-do item with an associated deadline, whereas Event is a calendar item with a time slot.\n"
    "Make sure to pick the appropriate type. Tasks don't happen at a specific time, but must be completed at some point before the given time; they will be split into events by the system.\n"
    'Events are calendar items with a specific time slot. For example, "prepare for exam" is a task, but "go to exam" is an event.\n\n'
    "For tasks, the fields are:\n"
    "Title should be a short description, ideally no more than 40 characters, that should be recognisable to remind the user which task is being shown on the calendar.\n"
    "Description is longer and should include the details the user gave that are not stored in other fields.\n"
    "Deadline is the date and time the task is due, in the format YYYY-MM-DDTHH:MM:SS. If it's due by a certain day but without a known time, use 23:59 on the previous day. Of course, if the time is known (e.g. 3pm), use that, on the same day given.\n"
    "e.g. a deadline of 3rd Jan 2024 would ourput 2024-01-03T00:00:00, 8PM on the 5th Jan 2024 would output 2024-01-05T20:00:00.\n"
    "DurationMinutes is the estimated time to complete the task in minutes. This is the time taken to actually do the thing specified in the task, for example a submission may take only 5-10 minutes, but revision may take a few hours.\n"
    "For a submission task (submit homework by tomorrow) we assume this refers to the actual act of submitting so go for the lower end of the range.\n\n"
    "For events, the fields are:\n"
    "Title (as above)\n"
    "Description (as above)\n"
    "Start is the date and time the event starts, in the format YYYY-MM-DDTHH:MM:SS.\n"
    "End is the date and time the event ends, in the format YYYY-MM-DDTHH:MM:SS.\n"
    "Usually, start and end will be close together.\n\n"
    "All fields can take the value None if needed. This includes numeric ones (duration). Only do this if any other output is very unlikely to be useful to the user even as a rough guess. If the input is too malformed/vague to pick Task or Event, default to Task, with fields as None if appropriate. Prefer None to something completely generic or empty.\n\n"
    "Reason about the duration and deadline (including the reason for the specific date of the month) in the provided field before outputting it; think about how long it may take and when it is due. Keep this to a few sentences max.\n\n"
)


class TaskModelOutput(BaseModel):
    type: Literal["Task"]
    title: str
    description: str
    deadline: str
    durationMinutes: str


class EventModelOutput(BaseModel):
    type: Literal["Event"]
    title: str
    description: str
    start: str
    end: str


class ModelOutput(BaseModel):
    reasoning: str
    taskOrEvent: TaskModelOutput | EventModelOutput


class Task(BaseModel):
    type: Literal["Task"]
    title: Optional[str]
    description: Optional[str]
    deadline: Optional[datetime.datetime]
    durationMinutes: Optional[int]


class Event(BaseModel):
    type: Literal["Event"]
    title: Optional[str]
    description: Optional[str]
    start: Optional[datetime.datetime]
    end: Optional[datetime.datetime]


def validateString(string: str) -> Optional[str]:
    if string == "None":
        return None
    if len(string) == 0:
        return None
    return string


def validateInt(string: str) -> Optional[int]:
    if string == "None":
        return None

    try:
        return int(string)
    except ValueError:
        return None


def validateDatetime(string: str) -> Optional[datetime.datetime]:
    if string == "None":
        return None

    try:
        return datetime.datetime.fromisoformat(string)
    except ValueError:
        return None


# Usually won't do anything because the dates change
# However it can be useful when running tests
# If this code is changed then this will automatically invalidate the cache
memory = Memory("cache")


@memory.cache
def runModel(
    system_prompt: str,
    user_prompt: str,
    iso: Optional[str] = None,
    local: Optional[str] = None,
    weekdayHelper: Optional[str] = None,
) -> ModelOutput:  # pragma: no cover
    if not (None in (iso, local, weekdayHelper)):
        system_prompt = (
            system_prompt + f"\nLocal time: {local}\n"
            f"ISO time: {iso}\n"
            f"Weekday helper: {weekdayHelper}\n"
        )

    completion = client.beta.chat.completions.parse(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "User input:" + user_prompt},
        ],
        response_format=ModelOutput,
    )

    return completion.choices[0].message.parsed


def gen(description: str, currentDate: datetime.datetime) -> Task | Event:
    iso = currentDate.isoformat().split(".")[0]
    local = currentDate.strftime("%Y-%m-%d at %H:%M:%S on %A")

    # Help the AI get the weekdays right
    weekdayHelper = ""
    fmtOrdinal = lambda x: str(x) + (  # noqa: E731
        "th" if 11 <= x <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(x % 10, "th")
    )
    for i in range(1, 8):
        newDate = currentDate + datetime.timedelta(days=i)
        weekdayHelper += f"{fmtOrdinal(newDate.day)} is {newDate.strftime('%A')}, "
    weekdayHelper = weekdayHelper[:-2]

    out = runModel(description, iso, local, weekdayHelper)

    return parseOutput(out.taskOrEvent, currentDate)


def parseOutput(
    taskOrEvent: TaskModelOutput | EventModelOutput, currentDate: datetime.datetime
) -> Task | Event:
    if taskOrEvent.type == "Event":
        event_out = taskOrEvent
        result = Event(
            type="Event",
            title=validateString(event_out.title),
            description=validateString(event_out.description),
            start=validateDatetime(event_out.start),
            end=validateDatetime(event_out.end),
        )

        # If the end is before the start, set both to None
        if result.start is not None and result.end is not None and result.end < result.start:
            result.start = None
            result.end = None

        # If the start is in the past, set both to None
        if result.start is not None and result.start < currentDate:
            result.start = None
            result.end = None

    else:
        task_out = taskOrEvent
        result = Task(
            type="Task",
            title=validateString(task_out.title),
            description=validateString(task_out.description),
            deadline=validateDatetime(task_out.deadline),
            durationMinutes=validateInt(task_out.durationMinutes),
        )

        # If the date is in the past, set it to None
        if result.deadline is not None and result.deadline < currentDate:
            result.deadline = None

        # If the duration is negative or more than 1000000 minutes, set it to None
        if result.durationMinutes is not None and (
            result.durationMinutes < 0 or result.durationMinutes > 1000000
        ):
            result.durationMinutes = None

    return result


if __name__ == "__main__":  # pragma: no cover
    description = input("Enter task: ")
    currentDate = datetime.datetime.now()
    task = gen(description, currentDate)
    if isinstance(task, Event):
        log.info("TYPE: Event")
        log.info("TITLE: %s", task.title)
        log.info("DESCRIPTION: %s", task.description)
        log.info("START: %s", task.start)
        log.info("END: %s", task.end)
    else:
        log.info("TYPE: Task")
        log.info("TITLE: %s", task.title)
        log.info("DESCRIPTION: %s", task.description)
        log.info("DEADLINE: %s", task.deadline)
        log.info("DURATION: %s", task.durationMinutes)
