import calendar
import datetime as dt

from flask import render_template

from mealswap.controller.controls import get_diets_in_current_month

month_dict = {1: "January",
              2: "February",
              3: "March",
              4: "April",
              5: "May",
              6: "June",
              7: "July",
              8: "August",
              9: "September",
              10: "October",
              11: "November",
              12: "December"}


def get_calendar():
    """Creates a calendar widget for diet homepage."""
    diets = get_diets_in_current_month()
    days = [diet.date.day for diet in diets]

    today = dt.date.today()
    year = today.year
    month = today.month
    first_day = dt.date(year, month, 1)
    last_day = dt.date(year, month, calendar.monthrange(year, month)[1])
    first_day_weekday = first_day.weekday()

    table_rows = "<tr>\n"
    for _ in range(first_day_weekday):
        table_rows += "\t<td></td>\n"
    day_count = 1
    for day in range(first_day_weekday, 7):
        date = f'{year}-{month}-{day_count:02d}'
        if day_count in days:
            table_rows += f'\t<td class="filled">' \
                          f'<a href="/day/{date}">{day_count}</a>' \
                          f'</td>\n'
        else:
            table_rows += f'\t<td class="open">' \
                          f'<a href="/day/{date}">{day_count}</a>' \
                          f'</td>\n'
        day_count += 1
    table_rows += "</tr>\n<tr>\n"

    weekday_count = 1
    while True:
        date = f'{year}-{month}-{day_count:02d}'
        if day_count in days:
            table_rows += f'\t<td class="filled">' \
                          f'<a href="/day/{date}">{day_count}</a>' \
                          f'</td>\n'
        else:
            table_rows += f'\t<td class="open">' \
                          f'<a href="/day/{date}">{day_count}</a>' \
                          f'</td>\n'
        day_count += 1
        weekday_count += 1
        if day_count == last_day.day + 1:
            break
        if weekday_count == 8:
            weekday_count = 1
            table_rows += "</tr>\n<tr>\n"

    while weekday_count < 8:
        table_rows += "\t<td></td>\n"
        weekday_count += 1
    table_rows += "</tr>\n"

    table_title = f"{month_dict[today.month]} {today.year}"

    return table_title, table_rows


