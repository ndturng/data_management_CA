from . import constants as c
from . import models as m
from .classes import SheetConfig

SHEET_TO_MODEL_FIELDS = {
    "Chức danh": SheetConfig(m.Title, c.TITLE_FIELDS),
    "Quy hoạch": SheetConfig(m.PositionPlan, c.POSITION_PLAN_FIELDS),
    "Đào tạo": SheetConfig(m.LearningPath, c.LEARNING_PATH_FIELDS),
    "Quá trình công tác": SheetConfig(m.WorkProcess, c.WORK_PROCESS_FIELDS),
    "Quá trình lương": SheetConfig(m.SalaryProcess, c.SALARY_PROCESS_FIELDS),
    "Khen thưởng": SheetConfig(m.Laudatory, c.LAUDATORY_FIELDS),
    "Kỷ luật": SheetConfig(m.Discipline, c.DISCIPLINE_FIELDS),
    "Thân nhân": SheetConfig(m.Relative, c.RELATIVE_FIELDS),
    "Ra nước ngoài": SheetConfig(m.Abroad, c.ABROAD_FIELDS),
    "Tham gia quân đội": SheetConfig(
        m.ArmyJoinHistory, c.ARMY_JOIN_HISTORY_FIELDS
    ),
    "Sức khoẻ": SheetConfig(m.Health, c.HEALTH_FIELDS),
}
