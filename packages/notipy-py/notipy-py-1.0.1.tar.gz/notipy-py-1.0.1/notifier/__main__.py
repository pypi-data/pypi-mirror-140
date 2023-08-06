import calendar
from datetime import datetime

from notifier.main import check_day_status, notifier, notifier_weekday


def start_notifier():
    if check_day_status():
        input_message = f"Working hours for {calendar.day_name[datetime.today().weekday()]}\n"
        notifier(input_message)
    else:
        input_message = f"Today is {calendar.day_name[datetime.today().weekday()]}! Take a break!"
        notifier_weekday(input_message)

if __name__ == "__main__":
    start_notifier()
