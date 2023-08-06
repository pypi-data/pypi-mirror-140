import importlib.resources
import json

from jinja2 import PackageLoader
from jinja2 import Environment

from . import static

env = Environment(loader=PackageLoader("alfred3_scheduler", "templates"))

TEXTS = dict()

with importlib.resources.path(static, "de.json") as fp:
    with open(fp, "r", encoding="utf-8") as f:
        TEXTS["de"] = json.load(f)
        TEXTS["de"]["registration_mail"] = env.get_template("html/confirm_registration_de.html.j2")
        TEXTS["de"]["reminder_mail"] = env.get_template("html/remind_participants.html.j2")
        TEXTS["de"]["cancel_mail"] = env.get_template("html/cancel_slot.html.j2")

with importlib.resources.path(static, "en.json") as fp:
    with open(fp, "r", encoding="utf-8") as f:
        TEXTS["en"] = json.load(f)
