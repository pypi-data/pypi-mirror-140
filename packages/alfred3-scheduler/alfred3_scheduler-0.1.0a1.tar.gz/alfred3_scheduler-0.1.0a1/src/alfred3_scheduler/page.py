"""Pages for the scheduler."""

from datetime import datetime
from email.message import EmailMessage
from string import Template

from alfred3.page import Page
from alfred3.admin import OperatorPage
from alfred3.element.display import Text
from alfred3.element.display import VerticalSpace
from alfred3.element.core import Row
from alfred3.element.misc import WebExitEnabler
from alfred3.element.misc import Style
from alfred3.element.misc import JavaScript
from alfred3.element.misc import HideNavigation
from alfred3.element.misc import Callback
from alfred3.util import icon

from .scheduler import DateSlot
from .element import DateSlotRegistration
from .element import DateSlotTable
from .element import AddDateSlot


class RegistrationPage(Page):
    """Displays date slots and allows participants to register."""

    def __init__(self, scheduler=None, **kwargs):
        if scheduler is not None:
            self.scheduler = scheduler
        if self.scheduler is None:
            raise ValueError("Must supply scheduler.")

        name = self.scheduler.registration
        super().__init__(name=name, **kwargs)

        if not self.title:
            self.title = self.scheduler.txt.get("registration_page_title")

    def on_exp_access(self):
        slots = self.exp.db_misc.find(
            {"type": "scheduler_slot", "scheduler_name": self.scheduler.name}
        )
        slotlist = []
        for data in slots:
            slot = DateSlot(data["dateslot_id"], self.exp)

            if slot.over(data):
                self.log.info(f"Skipping slot {data['dateslot_id']}, because it lies in the past.")
                continue

            street = data['street']
            city = data['city']
            if street and city:
                address = f"{street}, {city}"
            else:
                address = ""

            slot = DateSlotRegistration(
                date=datetime.fromtimestamp(data["start"]),
                duration=data["duration"],
                msg=data["msg"],
                address=address,
                name=data["dateslot_id"],
            )
            slotlist.append(slot)

        self += Row(*slotlist)
        self.vargs.slots = slotlist

    def on_each_hide(self):
        if "page" in self.exp.urlargs:
            return

        slotlist = self.vargs.slots
        selected = [slot for slot in slotlist if slot.input == "1"]
        if len(selected) > 1:
            msg = (
                "Sorry! There was an error. Multiple slots seem to "
                "have been selected, but only one is allowed. Please try again."
            )
            self.exp.abort(
                reason="More than one slot selected",
                title="Error in slot selection",
                msg=msg,
            )
        self.vargs.selected_dateslot_id = selected[0].name


class RegistrationInitiatedPage(Page):
    """
    Displayed to participants after they clicked to initiate their
    registration.
    """

    def __init__(self, scheduler=None, **kwargs):
        if scheduler is not None:
            self.scheduler = scheduler
        if self.scheduler is None:
            raise ValueError("Must supply scheduler.")

        name = self.scheduler.registration_initiated
        super().__init__(name=name, **kwargs)

    def send_message(self):
        url_handler = self.scheduler.url_handler(self.exp)
        email = self.section.email

        selection_page = self.section[self.scheduler.registration]
        selected_dateslot_id = selection_page.vargs.selected_dateslot_id
        slot = DateSlot(selected_dateslot_id, self.exp)
        data = slot.data_handler.load()
        registration_time = data["reservation_time"]

        last_time_to_cancel = data["start"] - self.scheduler.cancellation_time
        now = datetime.now().timestamp()
        cancel_link_validity = last_time_to_cancel - now

        data = self.scheduler.mail_data(data)
        data["confirm"] = url_handler.confirm_url(
            email, selected_dateslot_id, valid_for=registration_time
        )
        data["cancel"] = url_handler.cancel_url(
            email, selected_dateslot_id, valid_for=cancel_link_validity
        )

        msg = EmailMessage()
        msg["Subject"] = self.scheduler.txt.get("registration_mail_subject")
        msg["To"] = email

        content = self.scheduler.txt.get("registration_mail")

        msg.set_content(content.render(data))

        self.exp.send_mail(msg)

    def on_first_show(self):
        self += WebExitEnabler()
        self += Callback(func=self.send_message, followup="none", submit_first=False)

        selection_page = self.exp[self.scheduler.name + "_registration__"]
        selected_dateslot_id = selection_page.vargs.selected_dateslot_id
        slot = DateSlot(selected_dateslot_id, self.exp)
        email = self.section.email

        success = slot.register_participant(email)

        if success:
            self.successful_registration()
        else:
            self.registration_failed()

    def registration_failed(self):
        self += Style(code="#forward_button {display: none;}")
        self.title = self.scheduler.txt.get("registration_failed_title")

        self += VerticalSpace("20px")
        self += Text(icon("times-circle", size="70pt"), align="center")
        self += VerticalSpace("20px")

        msg = self.scheduler.txt.get("registration_failed_msg")
        self += Text(msg, align="center")

    def successful_registration(self):
        self += HideNavigation()
        self.title = self.scheduler.txt.get("registration_success_title")

        self += Text(f"{icon('envelope', size='70pt')}", align="center")
        self += VerticalSpace("20px")

        msg = Template(self.scheduler.txt.get("registration_success_msg"))
        mins = self.scheduler.txt.get("minutes")
        reservation_time = str(round(self.scheduler.reservation_time / 60)) + " " + mins
        msg = msg.substitute(reservation_time=reservation_time)

        self += Text(msg, align="center")


class ConfirmationPage(Page):
    """
    Displayed to participants after they clicked to confirm their
    registration.
    """

    def __init__(self, scheduler=None, **kwargs):
        if scheduler is not None:
            self.scheduler = scheduler
        if self.scheduler is None:
            raise ValueError("Must supply scheduler.")

        name = self.scheduler.registration_confirmed
        if "title" not in kwargs:
            kwargs["title"] = self.scheduler.txt.get("registration_initiated_title")

        super().__init__(name=name, **kwargs)

    def on_first_show(self):
        self += HideNavigation()
        self += WebExitEnabler()

        url_handler = self.scheduler.url_handler(self.exp)
        data = url_handler.extract_url_data()
        valid = url_handler.validate(data)

        if not valid:
            self.confirmation_failed()
            return

        dateslot_id = data["dateslot_id"]
        email = data["email"]
        slot = DateSlot(dateslot_id, self.exp)
        success = slot.confirm_participant(email)

        if success:
            self.successful_confirmation()
        else:
            self.confirmation_failed()

    def confirmation_failed(self):
        self += HideNavigation()
        self.title = self.scheduler.txt.get("confirmation_failed_title")

        self += VerticalSpace("20px")
        self += Text(icon("times-circle", size="70pt"), align="center")
        self += VerticalSpace("20px")

        msg = self.scheduler.txt.get("confirmation_failed_msg")
        self += Text(msg, align="center")

    def successful_confirmation(self):
        self += HideNavigation()
        self.title = self.scheduler.txt.get("confirmation_success_title")

        self += Text(f"{icon('check-circle', size='70pt')}", align="center")
        self += VerticalSpace("20px")

        msg = self.scheduler.txt.get("confirmation_success_msg")
        self += Text(msg, align="center")


class CancelPage(Page):
    """
    Displayed to participants if they choose to cancel their
    registration.
    """

    def __init__(self, scheduler=None, **kwargs):
        if scheduler is not None:
            self.scheduler = scheduler
        if self.scheduler is None:
            raise ValueError("Must supply scheduler.")

        name = self.scheduler.registration_cancelled
        super().__init__(name=name, **kwargs)

    def on_first_show(self):
        self += HideNavigation()
        self += WebExitEnabler()

        url_handler = self.scheduler.url_handler(self.exp)
        data = url_handler.extract_url_data()
        valid = url_handler.validate(data)

        if not valid:
            self.cancellation_late()
            return

        dateslot_id = data["dateslot_id"]
        email = data["email"]
        slot = DateSlot(dateslot_id, self.exp)
        success = slot.cancel_participant(email)

        if success:
            self.successful_cancellation()
        else:
            self.cancellation_failed()

    def cancellation_late(self):
        self += HideNavigation()
        self.title = self.scheduler.txt.get("cancellation_late_title")

        self += VerticalSpace("20px")
        self += Text(icon("times-circle", size="70pt"), align="center")
        self += VerticalSpace("20px")

        msg = self.scheduler.txt.get("cancellation_late_msg")
        self += Text(msg, align="center")

    def cancellation_failed(self):
        self += HideNavigation()
        self.title = self.scheduler.txt.get("cancellation_failed_title")

        self += VerticalSpace("20px")
        self += Text(icon("times-circle", size="70pt"), align="center")
        self += VerticalSpace("20px")

        msg = self.scheduler.txt.get("cancellation_failed_msg")
        self += Text(msg, align="center")

    def successful_cancellation(self):
        self += HideNavigation()
        self.title = self.scheduler.txt.get("cancellation_success_title")

        self += Text(f"{icon('check-circle', size='70pt')}", align="center")
        self += VerticalSpace("20px")

        msg = self.scheduler.txt.get("cancellation_success_msg")
        self += Text(msg, align="center")


class ManageDateSlotsPage(OperatorPage):
    title = "Manage Timeslots"
    responsive_width = "85%, 75%, 75%, 70%"

    def __init__(self, scheduler=None, **kwargs):
        if scheduler is not None:
            self.scheduler = scheduler
        if self.scheduler is None:
            raise ValueError("Must supply scheduler.")

        name = self.scheduler.manage_slots
        super().__init__(name=name, **kwargs)

    def on_each_show(self):
        self += DateSlotTable(scheduler_name=self.scheduler.name)
        self += WebExitEnabler()

        self += Style(url="https://cdn.datatables.net/1.10.24/css/dataTables.bootstrap4.min.css")
        self += JavaScript(url="//cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js")
        self += JavaScript(
            url="https://cdn.datatables.net/1.10.24/js/dataTables.bootstrap4.min.js"
        )

    def on_each_hide(self):
        self.elements = {}
        self._set_width()
        self._set_color()


class AddDateSlotsPage(OperatorPage):
    title = "Add Timeslots"

    def __init__(self, scheduler=None, **kwargs):
        if scheduler is not None:
            self.scheduler = scheduler
        if self.scheduler is None:
            raise ValueError("Must supply scheduler.")

        name = self.scheduler.add_slots
        super().__init__(name=name, **kwargs)

    def on_exp_access(self):
        self += AddDateSlot(
            scheduler=self.scheduler.name,
            name="add_dateslot",
            reservation_time=self.scheduler.reservation_time,
            delimiter=self.scheduler.delimiter,
        )
