SEARCH_FIELDS = [
    "birth_name",
    "id_ca",
    "birth_year",
    "current_residence",
    "salary_decision_year",
    "work_unit",
    "specialized_work",
    "other_work",
    "most_work",
    "phone_number",
    "bank_account_BIDV",
    "id_citizen",
    "year_join_party",
    "year_join_party_official",
    "year_join_CA",
]

FILTER_FIELDS = [
    "military_type",
    "military_rank",
    "blood_type",
    "size_of_hat",
    "political_theory",
    "position",
    "birth_place",
    "gender",
    "party_position",
    "salary_coefficient",
    "equipment_type",
    "size_of_shoes",
    "size_of_hat",
    "size_of_clothes",
    "certi_of_IT",
    "certi_of_foreign_language",
    "blood_type",
    "profile_address",
]

REQUIRED_FIELDS = [
    "birth_name",
    "id_ca",
]

# Thông tin chung
GENERAL_INFO_FIELDS = {
    "id_ca": "Số hiệu - Số hồ sơ",
    "birth_name": "Họ và tên khai sinh",
    "current_name": "Tên đang dùng",
    "gender": "Giới tính",
    "birth_place": "Nơi sinh",
    "current_residence": "Chỗ ở hiện nay",
    "folk": "Dân tộc",
    "religion": "Tôn giáo",
    "date_of_birth": "Ngày sinh",
    "month_join_group": "Tháng năm vào Đoàn",
    "group": "Đoàn thể",
    "month_join_party": "Tháng năm vào Đảng",
    "month_join_party_official": "Tháng năm chính thức",
    "party_card_number": "Số thẻ Đảng",
    "party_position": "Chức vụ Đảng",
    "month_recruit": "Tháng năm tuyển dụng",
    "month_join_CA": "Tháng năm vào CA",
    "recruit_unit": "Đơn vị tuyển",
    "recruit_source": "Nguồn tuyển",
    "unit_notation": "Ký hiệu đơn vị",
    "position": "Chức vụ",
    "military_rank": "Cấp bậc hàm",
    "salary_coefficient": "Hệ số lương",
    "salary_decision": "Quyết định lương",
    "salary_decision_year": "Năm quyết định lương",
    "work_unit": "Đơn vị công tác",
    "military_type": "Lực lượng",
    "rank_type": "Loại hàm",
    "equipment_type": "Quân trang",
    "size_of_shoes": "Giày",
    "size_of_hat": "Mũ",
    "size_of_clothes": "Quần áo",
    "specialized_work": "Công tác chuyên trách",
    "maneuver_decision": "Quyết định điều động",
    "other_work": "Công tác khác",
    "most_work": "Công tác làm nhiều nhất",
    "education": "Trình độ học vấn",
    "certi_of_IT": "Tin học",
    "certi_of_foreign_language": "Ngoại ngữ",
    "political_theory": "Trình độ chính trị",
    "strength": "Năng lực sở trường",
    "blood_type": "Nhóm máu",
    "compete_title": "Danh hiệu",
    "policy_family": "Gia đình chính sách",
    "profile_address": "Địa chỉ hồ sơ",
    "phone_number": "Số điện thoại",
    "bank_account_BIDV": "Số TK BIDV",
    "insurance_number": "Số sổ bảo hiểm",
    "id_citizen": "Số CCCD",
    "date_update": "Ngày cập nhật",
}

GENERAL_INFO_ADDED_FIELDS = {
    "next_salary_coefficient": "Hệ số lương tiếp theo",
    "next_salary_decision_year": "Năm quyết định lương tiếp theo",
    "birth_year": "Năm sinh",
    "year_join_party": "Năm vào Đảng",
    "year_join_party_official": "Năm chính thức",
    "year_join_CA": "Năm vào CA",
}

GENERAL_INFO_MONTH_FIELDS = [
    "month_join_group",
    "month_join_party",
    "month_join_party_official",
    "month_recruit",
    "month_join_CA",
]


# Chức danh
TITLE_FIELDS = {
    "appointed_date": "Ngày bổ nhiệm",  # change to date_appointed
    "title": "Chức danh",
}

# Quy hoạch
POSITION_PLAN_FIELDS = {
    "period": "Giai đoạn",
    "position": "Quy hoạch",
}

# Đào tạo
LEARNING_PATH_FIELDS = {
    "period": "Giai đoạn",
    "learning_content": "Đào tạo",
}

# Quá trình công tác
WORK_PROCESS_FIELDS = {
    "period": "Giai đoạn",
    "work_content": "Công tác",
}

# Quá trình lương
SALARY_PROCESS_FIELDS = {
    "time": "Thời gian",
    "mil_rank": "Cấp bậc hàm",
    "salary_coefficient": "Hệ số lương",
}

# Khen thưởng
LAUDATORY_FIELDS = {
    "time": "Thời gian",
    "form": "Hình thức",
    "content": "Nội dung",
}

# Kỷ luật
DISCIPLINE_FIELDS = {
    "time": "Thời gian",
    "form": "Hình thức",
    "content": "Nội dung",
}

# Thân nhân
RELATIVE_FIELDS = {
    "relationship": "Quan hệ",
    "name": "Họ và tên",
    "birth_year": "Năm sinh",
    "job": "Nghề nghiệp",
    "current_residence": "Chỗ ở hiện nay",
}

# Ra nước ngoài
ABROAD_FIELDS = {
    "time": "Thời gian",
    "country": "Địa điểm",
    "purpose": "Mục đích",
}

# Tham gia quân đội
ARMY_JOIN_HISTORY_FIELDS = {
    "period": "Giai đoạn",
    "unit": "Đơn vị",
    "form": "Hình thức",
}

# Sức khoẻ
HEALTH_FIELDS = {
    "weight": "Cân nặng (kg)",
    "height": "Chiều cao (cm)",
    "medical_history": "Lịch sử bệnh",
    "other": "Khác",
}

RANK_SCALE = {
    "Hạ sĩ": 3.2,
    "Trung sĩ": 3.5,
    "Thượng sĩ": 3.8,
    "Thiếu úy": 4.2,
    "Trung úy": 4.6,
    "Thượng úy": 5.0,
    "Đại úy": 5.4,
    "Thiếu tá": 6.0,
    "Trung tá": 6.6,
    "Thượng tá": 7.3,
    "Đại tá": 8.0,
    "Thiếu tướng": 8.6,
    "Trung tướng": 9.2,
    "Thượng tướng": 9.8,
    "Đại tướng": 10.4,
}

SALARY_SCALE = {
    # salary_coefficient: (military_rank, next_salary_coefficient, promotion_year)
    3.2: ("Hạ sĩ", 3.5, 1),
    3.5: ("Trung sĩ", 3.8, 1),
    3.8: ("Thượng sĩ", 4.2, 2),
    4.2: ("Thiếu úy", 4.6, 2),
    4.6: ("Trung úy", 5.0, 3),
    5.0: ("Thượng úy", 5.4, 3),
    5.4: ("Đại úy", 6.0, 4),
    6.0: ("Thiếu tá", 6.6, 4),
    6.6: ("Trung tá", 7.3, 4),
    7.3: ("Thượng tá", 8.0, 4),
    8.0: ("Đại tá", 8.6, 4),
    8.6: ("Thiếu tướng", 9.2, 4),
    9.2: ("Trung tướng", 9.8, 4),
    9.8: ("Thượng tướng", 10.4, 4),
    10.4: ("Đại tướng", 11.0, 4),
}

# Chu kỳ tăng lương sau khi đạt mức lương tối đa
PERIOD_INCREASE_CEILING_SALARY = 4
SALARY_AFTER_CEILING = {
    5.0: (5.35, 5.7),
    5.4: (5.8, 6.2),
    6.0: (6.4, 6.8),
    6.6: (7.0, 7.4),
    7.3: (7.7, 8.1),
    8.0: (8.4, 8.6),
    8.6: (9.2, 9.2),
    9.2: (9.8, 9.8),
    9.8: (10.4, 10.4),
    10.4: (11.0, 11.0),
}
