"""Elements for the scheduler"""
# pylint: disable=invalid-name
import io
import csv
import typing as t
from email.message import EmailMessage
from datetime import datetime
from dataclasses import asdict

from jinja2 import PackageLoader
from jinja2 import Environment
from alfred3.element.core import InputElement, Element
from alfred3.element.input import TextArea

from .scheduler import DateSlot
from .scheduler import DateSlotData
from .text import TEXTS

env = Environment(loader=PackageLoader("alfred3_scheduler", "templates"))


class AddDateSlot(TextArea):
    """
    Displays all necessary elements to create a new date slot,
    including a button for submitting.
    """

    element_template = env.get_template("html/AddDateSlot.html.j2")
    js_template = env.get_template("js/add_date_slot.js.j2")

    def __init__(
        self, name: str, scheduler: str, reservation_time: int = 60 * 60, delimiter: str = ","
    ):
        default = [
            "start date",
            "start time",
            "duration",
            "n_participants",
            "n_overbook",
            "street",
            "city",
            "place_hint",
            "msg",
        ]
        default = delimiter.join(default)
        super().__init__(default=default, nrows=10, name=name)
        self.delimiter = delimiter
        self.scheduler = scheduler
        self.reservation_time = reservation_time
        self.url = None

    def added_to_experiment(self, experiment):
        super().added_to_experiment(experiment)
        self.url = self.exp.ui.add_callable(self.write_slots)

    def prepare_web_widget(self):
        self._js_code = []
        d = {}
        d["url"] = self.url
        d["name"] = self.name
        d["set_data_url"] = self.exp.ui.set_page_data_url
        js = self.js_template.render(d)
        self.add_js(js)

    def write_slots(self):

        try:
            slots = self.prepare_slots()
        except Exception:  # pylint: disable=broad-except
            msg = (
                "There was an exception during date slot preparation. "
                "No data was written to the database."
            )
            self.exp.log.exception(msg)
            self.input = self.default
            return msg

        slots = [asdict(slot) for slot in slots]
        if slots:
            try:
                result = self.exp.db_misc.insert_many(slots)
                msg = (
                    f"<i class='fas fa-check-circle mr-1'></i> "
                    f"Inserted {len(result.inserted_ids)} date slots."
                )
            except Exception:  # pylint: disable=broad-except
                msg = "There was an exception while writing date slots to the database."
                self.exp.log.exception(msg)
        else:
            msg = "<i class='fas fa-check-circle mr-1'></i> Inserted 0 date slots."

        self.input = self.default
        return msg

    def prepare_slots(self) -> t.List[DateSlotData]:
        f = io.StringIO(self.input)
        reader = csv.DictReader(f, delimiter=self.delimiter)
        if reader.fieldnames != self.default.split(self.delimiter):
            raise ValueError("Wrong column names.")

        slots = []
        for row in reader:
            row.update(
                {
                    "scheduler_name": self.scheduler,
                    "reservation_time": self.reservation_time,
                    "exp_id": self.exp.exp_id,
                }
            )
            slot = DateSlotData.from_dict(row)
            slots.append(slot)
        return slots


class DateSlotRegistration(InputElement):
    """
    Participant-facing view of a date slot.
    Displays useful information and allows participants to register at
    the click of a button.
    """

    element_template = env.get_template("html/DateSlotRegistration.html.j2")
    js_template = env.get_template("js/dateslot_registration.js.j2")

    def __init__(
        self,
        date: t.Union[float, datetime],
        duration: str,
        msg: str,
        address: str,
        name: str,
        lang: str = "de",
        **kwargs,
    ):
        super().__init__(name=name, **kwargs)
        try:
            self.date = date.timestamp()
        except AttributeError:
            self.date = date
        self.texts = TEXTS[lang]
        self.duration = str(round(duration / 60)) + " " + self.texts.get("minutes")
        self.msg = msg
        self.address = address

    def added_to_experiment(self, experiment):
        super().added_to_experiment(experiment)
        js = self.js_template.render(name=self.name)
        self.add_js(js)

    @property
    def template_data(self) -> dict:
        d = super().template_data
        d.update(self.texts)

        date = datetime.fromtimestamp(self.date)
        d["date"] = date.strftime(self.texts.get("date_format", "%Y-%m-%d"))
        d["day"] = date.strftime("%A")
        d["start_time"] = date.strftime("%H:%M")
        d["duration"] = self.duration
        d["nopen"] = DateSlot(self.name, self.exp).nopen()
        d["msg"] = self.msg
        d["address"] = self.address
        return d


class DateSlotTable(Element):
    """
    Displays a table of date slots for the admin view.
    """

    element_template = env.get_template("html/ViewDateSlots.html.j2")
    js_template = env.get_template("js/view_date_slots.js.j2")

    def __init__(self, scheduler_name: str, **kwargs):
        super().__init__(**kwargs)
        self.scheduler_name = scheduler_name
        self.render_url = None
        self.mail_buttons = None
        self.reminder_buttons = None
        self.cancel_buttons = None
        self.delete_buttons = None

    def added_to_experiment(self, experiment):
        super().added_to_experiment(experiment)

        self.render_url = self.exp.ui.add_callable(self.render_table_body)
        cols = [
            "ID",
            "Date",
            "Start",
            "Duration",
            "Active",
            "N",
            "Confirmed",
            "Participants",
            "Send Email",
            "Send Reminder",
            "Cancel",
            "Delete",
        ]

        js = self.js_template.render(
            name=self.name,
            render_url=self.render_url,
            cols=cols,
        )

        self.add_js(js)

        self.participant_buttons = self.prepare_buttons(ShowParticipantsButton)
        self.mail_buttons = self.prepare_buttons(SendMailButton)
        self.reminder_buttons = self.prepare_buttons(SendReminderButton)
        self.cancel_buttons = self.prepare_buttons(CancelSlotButton)
        self.delete_buttons = self.prepare_buttons(DeleteSlotButton)

    def render_table_body(self) -> dict:

        slots = self.exp.db_misc.find(
            {"type": "scheduler_slot", "scheduler_name": self.scheduler_name}
        )
        tbody = []
        for slot in slots:
            del slot["_id"]
            slot.pop("cancelled", None)
            if not "exp_id" in slot:
                slot["exp_id"] = self.exp.exp_id
            slot = DateSlotData(**slot)
            d = {}
            d["ID"] = ".." + slot.dateslot_id[-4:]

            start = datetime.fromtimestamp(slot.start)
            d["Date"] = start.strftime("%Y-%m-%d")
            d["Start"] = start.strftime("%H:%M")
            d["Duration"] = f"{round(slot.duration / 60)} m"
            d["Active"] = slot.active
            d["N"] = (
                f"<b>{slot.n_participants}</b> "
                f"<span class='text-muted'>(+{slot.n_overbook})</span>"
            )
            d["Confirmed"] = (
                f"<b>{len(slot.participants_confirmed)}</b> / "
                f"<span class='text-muted'>{len(slot.participants_registered)}</span>"
            )
            d["Participants"] = self.participant_buttons.get(slot.dateslot_id, "n/a")
            d["Send Email"] = self.mail_buttons.get(slot.dateslot_id, "n/a")
            d["Send Reminder"] = self.reminder_buttons.get(slot.dateslot_id, "n/a")
            d["Cancel"] = self.cancel_buttons.get(slot.dateslot_id, "n/a")
            d["Delete"] = self.delete_buttons.get(slot.dateslot_id, "n/a")
            tbody.append(d)

        return {"data": tbody}

    def prepare_buttons(self, btn_cls) -> dict:
        btns = dict()
        slots = self.exp.db_misc.find(
            {"type": "scheduler_slot", "scheduler_name": self.scheduler_name}
        )
        for slot in slots:
            dateslot_id = slot["dateslot_id"]

            btn = btn_cls(dateslot_id)
            self.page += btn
            btns[dateslot_id] = btn.web_widget

        return btns


class SendMailButton(Element):

    element_template = env.get_template("html/SendMailButton.html.j2")
    js_template = env.get_template("js/send_mail_button.js.j2")

    def __init__(self, dateslot_id: str):
        super().__init__()
        self.url = None
        self.textarea = None
        self.dateslot_id = dateslot_id
        self.display_standalone = False

    @property
    def button_style(self) -> str:
        return "primary"

    @property
    def default(self) -> str:
        return "Example subject\n\nHello,\nthis is an example message.\n\nBest regards\nExample"

    @property
    def text(self) -> str:
        return "<i class='fas fa-envelope mr-2'></i>Send Mail"

    @property
    def modal_title(self) -> str:
        return "Send email to confirmed participants"

    def added_to_page(self, page):
        super().added_to_page(page)
        self.textarea = TextArea(
            toplab="Enter your message here. The first line is used as subject.",
            bottomlab="The message will be sent to all confirmed participants of this slot.",
            default=self.default,
            name=self.name + "_textarea",
            nrows=15,
        )
        self.page += self.textarea
        self.textarea.display_standalone = False

    def added_to_experiment(self, experiment):
        super().added_to_experiment(experiment)
        self.url = self.exp.ui.add_callable(self.send_mail)

    def prepare_web_widget(self):
        self._js_code = []
        d = {}
        d["url"] = self.url
        d["name"] = self.name
        d["set_data_url"] = self.exp.ui.set_page_data_url
        js = self.js_template.render(d)
        self.add_js(js)

    def prepare_message(self) -> EmailMessage:
        msg = EmailMessage()
        content = self.textarea.input if self.textarea.input is not None else ""
        content = content.split("\n")
        subject = content[0]
        body = content[1:]

        n_newlines = 0
        while True:
            line = body[0]
            if not line and len(body) > 2:
                body = body[1:]
                n_newlines += 1
            else:
                break

        body = "\n".join(body)

        msg["Subject"] = subject
        msg.set_content(body)
        return msg

    def send_mail(self) -> str:
        msg = self.prepare_message()

        slot = DateSlot(self.dateslot_id, self.exp)
        nrecipients = slot.send_mail(msg)
        icon = "<i class='fas fa-check-circle mr-1'></i>"
        return icon + f"Email sent to {nrecipients} confirmed participant(s)."

    @property
    def template_data(self) -> dict:
        d = super().template_data
        d["mail_textarea"] = self.textarea
        d["button_style"] = self.button_style
        d["text"] = self.text
        d["modal_title"] = self.modal_title
        return d


class SendReminderButton(SendMailButton):
    @property
    def button_style(self) -> str:
        return "info"

    @property
    def default(self):
        slot = DateSlot(self.dateslot_id, self.exp)
        data = slot.data_handler.load()
        return self.page.scheduler.render_mail(data, "reminder_mail")

    @property
    def text(self) -> str:
        return "<i class='fas fa-bell mr-2'></i> Send Reminder"

    @property
    def modal_title(self) -> str:
        return "Send reminder to confirmed participants"


class CancelSlotButton(SendMailButton):
    @property
    def default(self):
        slot = DateSlot(self.dateslot_id, self.exp)
        data = slot.data_handler.load()
        return self.page.scheduler.render_mail(data, "cancel_mail")

    @property
    def button_style(self) -> str:
        return "warning"

    @property
    def text(self) -> str:
        return "<i class='fas fa-stop-circle mr-2'></i> Cancel"

    @property
    def modal_title(self) -> str:
        return "Cancel slot and notify confirmed participants"

    def added_to_experiment(self, experiment):
        super().added_to_experiment(experiment)
        self.url = self.exp.ui.add_callable(self.cancel_slot)

    def cancel_slot(self) -> str:
        msg = self.prepare_message()
        slot = DateSlot(self.dateslot_id, self.exp)
        slot.cancel_slot()

        slot = DateSlot(self.dateslot_id, self.exp)
        nrecipients = slot.send_mail(msg)

        icon = "<i class='fas fa-check-circle mr-1'></i>"
        return icon + f"Cancelled slot and notified {nrecipients} confirmed participant(s)."


class DeleteSlotButton(Element):

    element_template = env.get_template("html/DeleteSlotButton.html.j2")
    js_template = env.get_template("js/send_mail_button.js.j2")

    def __init__(self, dateslot_id: str):
        super().__init__()
        self.url = None
        self.dateslot_id = dateslot_id
        self.display_standalone = False

    @property
    def button_style(self) -> str:
        return "danger"

    @property
    def text(self) -> str:
        return "<i class='fas fa-trash-alt mr-2'></i>Delete"

    def added_to_experiment(self, experiment):
        super().added_to_experiment(experiment)
        self.url = self.exp.ui.add_callable(self.delete_slot)

    def prepare_web_widget(self):
        self._js_code = []
        d = {}
        d["url"] = self.url
        d["name"] = self.name
        d["set_data_url"] = self.exp.ui.set_page_data_url
        js = self.js_template.render(d)
        self.add_js(js)

    def delete_slot(self) -> str:
        slot = DateSlot(self.dateslot_id, self.exp)
        data = slot.data_handler.load()

        if data["active"]:
            icon = "<i class='fas fa-times-circle mr-1'></i>"
            return icon + "Slot must be cancelled before it can be deleted."

        result = slot.data_handler.delete()
        icon = "<i class='fas fa-check-circle mr-1'></i>"
        return icon + f"Deleted {result.deleted_count} slot."

    @property
    def template_data(self) -> dict:
        d = super().template_data
        d["button_style"] = self.button_style
        d["text"] = self.text
        return d


class ShowParticipantsButton(Element):

    element_template = env.get_template("html/ShowParticipantsButton.html.j2")

    def __init__(self, dateslot_id: str):
        super().__init__()
        self.textarea = None
        self.dateslot_id = dateslot_id
        self.display_standalone = False

    @property
    def button_style(self) -> str:
        return "primary"

    @property
    def default(self) -> str:
        slot = DateSlot(self.dateslot_id, self.exp)
        data = slot.data_handler.load()
        registered = "\n".join(list(data["participants_registered"]))
        confirmed = "\n".join(list(data["participants_confirmed"]))
        cancelled = "\n".join(list(data["participants_cancelled"]))

        registered = f"Registered\n--------\n{registered}"
        confirmed = f"Confirmed\n--------\n{confirmed}"
        cancelled = f"Cancelled\n--------\n{cancelled}"

        text = registered + "\n\n" + confirmed + "\n\n" + cancelled

        return text

    @property
    def text(self) -> str:
        return "<i class='fas fa-users mr-2'></i>Show Participants"

    @property
    def modal_title(self) -> str:
        return "Participant list"

    def added_to_page(self, page):
        super().added_to_page(page)
        self.textarea = TextArea(
            toplab="This is a list of all participants for this slot.",
            default=self.default,
            name=self.name + "_textarea",
            nrows=15,
        )
        self.page += self.textarea
        self.textarea.display_standalone = False

    @property
    def template_data(self) -> dict:
        d = super().template_data
        d["textarea"] = self.textarea
        d["button_style"] = self.button_style
        d["text"] = self.text
        d["modal_title"] = self.modal_title
        return d