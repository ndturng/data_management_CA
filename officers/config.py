from . import constants as c
from . import models as m
from .classes import SheetConfig

SHEET_TO_MODEL_FIELDS = {
    "Chức danh": SheetConfig(m.Title, c.TITLE_FIELDS, "titles"),
    "Quy hoạch": SheetConfig(m.PositionPlan, c.POSITION_PLAN_FIELDS, "position_plans"),
    "Đào tạo": SheetConfig(m.LearningPath, c.LEARNING_PATH_FIELDS, "learning_paths"),
    "Quá trình công tác": SheetConfig(m.WorkProcess, c.WORK_PROCESS_FIELDS, "work_processes"),
    "Quá trình lương": SheetConfig(m.SalaryProcess, c.SALARY_PROCESS_FIELDS, "salary_processes"),
    "Khen thưởng": SheetConfig(m.Laudatory, c.LAUDATORY_FIELDS, "laudatories"),
    "Kỷ luật": SheetConfig(m.Discipline, c.DISCIPLINE_FIELDS, "disciplines"),
    "Thân nhân": SheetConfig(m.Relative, c.RELATIVE_FIELDS, "relatives"),
    "Ra nước ngoài": SheetConfig(m.Abroad, c.ABROAD_FIELDS, "abroads"),
    "Tham gia quân đội": SheetConfig(
        m.ArmyJoinHistory, c.ARMY_JOIN_HISTORY_FIELDS, "army_join_histories"
    ),
    "Sức khoẻ": SheetConfig(m.Health, c.HEALTH_FIELDS, "healths"),
}
