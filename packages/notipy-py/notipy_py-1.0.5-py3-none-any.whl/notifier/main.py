from datetime import datetime
import time
from plyer import notification
import pkgutil


def check_day_status():
    return 1 <= datetime.today().isoweekday() <= 5


def notifier_weekday(weekend_mess):
    notification.notify(
        title=weekend_mess,
        message="Have a good day",
        app_icon=pkgutil.get_data('notifier', 'sea_fishes.ico'),
        timeout=60
    )


def notifier_break():
    notification.notify(
        title="Break",
        message="Rest for 10 minutes before continue working",
        app_icon=r"break.ico",
        timeout=60*10
    )
    time.sleep(60*10)


def notifier_lunch():
    notification.notify(
        title="Lunch Time",
        message="Go and eat something delicious",
        app_icon=r"food.ico",
        timeout=60*60
    )
    time.sleep(60*60)


def notifier_end_workday():
    notification.notify(
        title="The end!",
        message="See you tomorrow",
        app_icon=r"end.ico",
        timeout=60
    )
    time.sleep(10)


def notifier_workday(workday_mess, num):
    notification.notify(
        title=workday_mess + f"Session {num}/8",
        message="Work is in progress...",
        app_icon=r"sea_fishes.ico",
        timeout=60 * 50
    )
    time.sleep(60 * 50)


def notifier(workday_mess):
    for num in range(1, 9):
        notifier_workday(workday_mess, num)
        if num == 4:
            notifier_lunch()
        elif num == 8:
            notifier_end_workday()
        else:
            notifier_break()


