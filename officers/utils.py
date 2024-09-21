from datetime import datetime

import pandas as pd
from django.contrib import messages
from django.db import IntegrityError

from officers.constants import SALARY_SCALE


def extract_officer_data(index, row, fields_dict, required_fields):  # noqa
    officer_data = {}
    row_missing_fields = {"row": index + 1, "missing_fields": []}
    skip_row = False

    for field, column in fields_dict.items():
        if "date" in field:
            officer_data[field] = get_day(row, column)
        else:
            officer_data[field] = row.get(column, "")

        # Add the empty fields to the missing_fields list
        if (
            not officer_data[field]
            or officer_data[field] == "nan"
            or pd.isna(officer_data[field])
        ):
            row_missing_fields["missing_fields"].append(field)

            # If the field is required and empty, skip this row
            if field in required_fields:
                skip_row = True

    return officer_data, row_missing_fields, skip_row


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


def create_officer_related_objects(
    request,
    officer,
    file,
    sheet_name,
    model_class,
    fields,
    error_message_prefix,
):
    """
    Reusable function to create related objects (Title, PositionPlan, etc.) for an officer.

    :param request: The current request object.
    :param officer: The officer instance to associate with the related objects.
    :param file: The Excel file being processed.
    :param sheet_name: The name of the sheet in the Excel file.
    :param model_class: The model class (e.g., Title, PositionPlan) to create objects for.
    :param fields: A dictionary of fields to extract from the Excel sheet.
    :param error_message_prefix: A prefix for the error message in case of IntegrityError.
    """
    try:
        df = pd.read_excel(file, sheet_name)
        for index, row in df.iterrows():
            officer_related_data, _, _ = extract_officer_data(
                index, row, fields, []
            )

            try:
                # Create the related object using the model class and officer instance
                model_class.objects.create(
                    officer=officer, **officer_related_data
                )
            except IntegrityError as e:
                messages.error(
                    request,
                    f"{error_message_prefix} for officer {officer.birth_name}: {e}",
                )
    except Exception as e:
        messages.error(request, f"Error processing {sheet_name} sheet: {e}")


def get_day(row, column):
    default_date = datetime(1800, 1, 1)
    try:
        day = row.get(column, None)
        # print(f"Raw value for day: {day}, Type: {type(day)}")

        if pd.isna(day):  # Check for NaT or NaN values
            return default_date

        if isinstance(day, str):
            # Handle string dates
            date_time = datetime.strptime(day, "%d/%m/%Y")
        elif isinstance(day, pd.Timestamp):
            # If it's a pandas Timestamp, we can convert it directly
            date_time = day.to_pydatetime()
        elif isinstance(day, datetime):
            # If it's already a datetime object, just return it
            date_time = day
        else:
            return default_date

        return date_time
    except ValueError:
        print(f"Failed to parse date for {row['birth_name']} with value: {day}")
        return default_date
