import uuid

from nandboxbots.data.Button import Button
from nandboxbots.outmessages.SetNavigationButtonOutMessage import SetNavigationButtonOutMessage


def get_unique_id():
    return int(uuid.uuid4().hex[:14], base=16)


def format_date(now):
    dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
    return dt_string


def set_navigation_button(chat_id, next_menu, api):
    btn = Button({})

    btn.next_menu = next_menu

    nav_msg = SetNavigationButtonOutMessage()
    nav_msg.chat_id = chat_id
    nav_msg.navigation_buttons = []
    _, btn_dict = btn.to_json_obj()
    nav_msg.navigation_buttons.append(btn_dict)
    msg, _ = nav_msg.to_json_obj()

    api.send(msg)


def format_duration(duration):
    if duration is not None:
        millis = int(duration)
        seconds = (millis / 1000) % 60
        seconds = int(seconds)
        minutes = (millis / (1000 * 60)) % 60
        minutes = int(minutes)
        hours = (millis / (1000 * 60 * 60)) % 24
        return "%d:%d:%d" % (hours, minutes, seconds)
    return None


