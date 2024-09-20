from officers.constants import SALARY_SCALE


def cal_next_rank(salary_coefficient, salary_decision_year):

    if salary_coefficient in SALARY_SCALE:
        next_salary_coefficient, promotion_year = SALARY_SCALE[
            salary_coefficient
        ][1:]
        next_salary_decision_year = salary_decision_year + promotion_year
    else:
        next_salary_coefficient, next_salary_decision_year = 0, 0

    return next_salary_coefficient, next_salary_decision_year


next_coefficient, next_promotion_year = cal_next_rank(5.0, 2020)
print(next_coefficient, next_promotion_year)
# Run by command: python3 -m officers.utils
