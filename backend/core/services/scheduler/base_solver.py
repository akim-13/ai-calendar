from core.entities.scheduler import UserPrompt, Ump, EventList
from ortools.sat.python import cp_model
from pathlib import Path
import json

# TODO: Move out of core.
BASE_DIR = Path(__file__).resolve().parents[3]  
TEST_DATA = BASE_DIR / "infra/test_data"
with open(TEST_DATA / "user_prompt.json", encoding="utf-8") as f:
    raw_user_prompt = json.load(f)
with open(TEST_DATA / "ump.json", encoding="utf-8") as f:
    raw_ump = json.load(f)
with open(TEST_DATA / "database.json", encoding="utf-8") as f:
    database_raw = json.load(f)

ump = Ump.model_validate(raw_ump)
user_prompt = UserPrompt.model_validate(raw_user_prompt)
events = EventList(events=database_raw)


model = cp_model.CpModel()

scope = user_prompt.scope
scope_length = scope.end - scope.start
