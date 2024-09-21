from .constants import POSITION_PLAN_FIELDS, TITLE_FIELDS
from .classes import SheetConfig
from .models import PositionPlan, Title

SHEET_TO_MODEL_FIELDS = {
    "Chức danh": SheetConfig(Title, TITLE_FIELDS),
    "Quy hoạch": SheetConfig(PositionPlan, POSITION_PLAN_FIELDS),
}
