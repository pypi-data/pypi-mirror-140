"""Functionality for coordinating session slots."""

import base64
from email.message import EmailMessage
import json
import time
import typing as t
from dataclasses import asdict, dataclass, field
from datetime import datetime
from logging import Logger
from traceback import format_exception
from uuid import uuid4

from flask import url_for
from pymongo import ReturnDocument
from pymongo.collection import Collection
from alfred3.experiment import ExperimentSession

from .text import TEXTS


class SchedulerException(Exception):
    """Base class for scheduler exceptions."""


class Busy(SchedulerException):
    """
    Raised if access to a database object fails because it is busy
    (i.e., locked).
    """


class DataTypes:
    """Data types for identifying database objects."""

    SLOT = "scheduler_slot"
    SCHEDULER = "scheduler"


class DataHandler:
    """
    Handles atomic interactions with MongoDB objects.

    Args:
        col (Collection): MongoDB collection to use.
        identifier (dict): Dictionary to use as identifier for the
            database object to operate on.
        log (Logger): Logger to use for logging exceptions if something
            goes wrong.
    """

    def __init__(self, col: Collection, identifier: dict, log: Logger):
        self.col = col
        self.identifier = identifier
        self.log = log
        self.data_save = None

    def save(self, data: dict) -> dict:
        """
        Saves *data* to the database. Returns the document.
        """
        document = self.col.find_one_and_update(
            filter=self.identifier,
            update={"$set": data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
            projection={"_id": False},
        )
        return document

    def delete(self):
        """Deletes the associated document from the database."""
        return self.col.delete_one(self.identifier)

    def load(self) -> dict:
        """Returns data dictionary without locking."""
        return self.col.find_one(self.identifier)

    def lock(self) -> t.Union[dict, None]:
        """
        Locks data set and returns data dictionary.
        Returns *None*, if data set was already locked.
        """
        query = self.identifier.copy()
        query["busy"] = False
        document = self.col.find_one_and_update(
            query,
            {"$set": {"busy": True}},
            return_document=ReturnDocument.AFTER,
            projection={"_id": False},
        )
        return document

    def release(self) -> None:
        """Changes the status of the database object from any state to *busy=False*."""
        self.col.find_one_and_update(self.identifier, {"$set": {"busy": False}})

    def __enter__(self):
        data = self.lock()
        i = 0

        while not data:
            i += 1
            if i > 5:
                break
            time.sleep(1)
            data = self.lock()

        if not data:
            raise Busy

        self.data_save = data
        return data

    def __exit__(self, exc_type, exc_value, traceback):
        # log exception
        if exc_type:
            traceback = "".join(format_exception(exc_type, exc_value, traceback))
            self.log.error(
                (
                    "There was an error in a database operation. "
                    f"Identifier: {self.identifier}.\n{traceback}"
                )
            )

            # restore previous data
            self.save(self.data_save)

        self.release()


@dataclass
class DateSlotData:
    """Date slot class."""

    start: t.Union[float, datetime]
    duration: int
    n_participants: int
    n_overbook: int
    reservation_time: int
    msg: str

    street: str
    city: str
    place_hint: str

    scheduler_name: str
    exp_id: str

    participants_registered: dict = field(default_factory=dict)
    participants_confirmed: dict = field(default_factory=dict)
    participants_cancelled: dict = field(default_factory=dict)

    active: bool = True
    busy: bool = False
    dateslot_id: str = field(default_factory=lambda: "slotid_" + uuid4().hex)
    type: str = DataTypes.SLOT

    @classmethod
    def from_dict(cls, data: dict):
        """Alternative constructor from dictionary."""
        start_date = data.pop("start date").strip()
        start_time = data.pop("start time").strip()
        try:
            date_format = "%Y-%m-%d %H:%M"
            start = datetime.strptime(f"{start_date} {start_time}", date_format)
        except ValueError:
            date_format = "%d.%m.%Y %H:%M"
            start = datetime.strptime(f"{start_date} {start_time}", date_format)

        data["start"] = start.timestamp()
        data["duration"] = int(data["duration"].strip()) * 60
        data["n_participants"] = int(data["n_participants"].strip())
        data["n_overbook"] = int(data["n_overbook"].strip())

        return cls(**data)

    def __post_init__(self):
        try:
            self.start = self.start.timestamp()
        except AttributeError:
            pass


class DateSlot:
    """Date slot class."""

    def __init__(self, dateslot_id: str, exp: ExperimentSession):
        self.exp = exp
        self.dateslot_id = dateslot_id
        identifier = {"dateslot_id": dateslot_id, "type": DataTypes.SLOT}
        self.data_handler = DataHandler(exp.db_misc, identifier, exp.log)

        # data = self.data_handler.load()
        # self.time = Time(data["start"], data["duration"])

    @classmethod
    def new(cls, dateslot_data: DateSlotData, exp: ExperimentSession):
        """Creates a new date slot and inserts it into the database."""
        data_handler = DataHandler(col=exp.db_misc, identifier=asdict(dateslot_data), log=exp.log)
        data_handler.save(asdict(dateslot_data))
        return cls(dateslot_id=dateslot_data.dateslot_id, exp=exp)

    def cancel_slot(self):
        """Called when a date slot is cancelled."""
        with self.data_handler as data:
            data["active"] = False
            self.data_handler.save(data)
            self.exp.log.info(f"Scheduler: Cancelled slot {self.dateslot_id}")

    def send_mail(self, msg: EmailMessage) -> int:
        """
        Sends the *msg* to all confirmed participants.

        Returns:
            int: The number of recipients.
        """
        data = self.data_handler.load()
        emails = list(data["participants_confirmed"])
        msg["Bcc"] = ", ".join(emails)
        self.exp.send_mail(msg)
        return len(emails)

    def npending(self, data: dict = None) -> int:
        """
        Returns number of participants registered for this slot who have
        *not* yet confirmed their email adresses.

        Pending participants have a reserved place in a date slot for
        30 minutes.
        """
        if data is None:
            data = self.data_handler.load()

        pending = []
        for email in data["participants_registered"]:  # pylint: disable=redefined-outer-name
            reservation_expired = self.registration_expired(email, data)

            if reservation_expired:
                continue

            if email in data["participants_cancelled"]:
                continue

            if not email in data["participants_confirmed"]:
                pending.append(email)

        return len(pending)

    def nconfirmed(self, data: dict = None) -> int:
        """
        Returns number of confirmed participants in this date slot.
        """
        if data is None:
            data = self.data_handler.load()
        participants = data["participants_confirmed"]
        return len(participants)

    def nopen(self, data: dict = None) -> int:
        """
        Returns number of open spaces in this date slot, i.e., the number
        of total spaces (including overbooking) minus the number of confirmed
        participants.
        """
        if data is None:
            data = self.data_handler.load()
        nconfirmed = self.nconfirmed(data)
        npending = self.npending(data)
        nreserved = nconfirmed + npending
        ntotal = data["n_participants"] + data["n_overbook"]
        return ntotal - nreserved

    def over(self, data: dict = None) -> bool:
        """
        bool: Indicates whether the slot's start time lies in the past
            (*True*) or future (*False*).
        """
        if data is None:
            data = self.data_handler.load()

        now = datetime.now().timestamp()
        start = data["start"]
        return start < now

    def register_participant(self, email: str) -> bool:
        """
        Registers a participant email for this slot.

        Returns:
            bool: True, if registration was completed. False, if
                registration was not completed.
        """
        with self.data_handler as data:

            if self.nopen(data) == 0:
                return False

            new = self.participant_new(email, data)
            expired = self.registration_expired(email, data)

            if new or expired:
                data["participants_registered"][email] = datetime.now().timestamp()
                self.data_handler.save(data)
                return True

            return False

    def confirm_participant(self, email: str) -> bool:
        """
        Confirms a participant email for this slot.

        Returns:
            bool: True, if confirmation was completed. False, if
                confirmation was not completed.
        """
        with self.data_handler as data:
            if not email in data["participants_confirmed"]:
                now = datetime.now().timestamp()
                data["participants_confirmed"][email] = now
                self.data_handler.save(data)
                return True

            return False

    def cancel_participant(self, email: str) -> bool:
        """
        Cancels a participant email for this slot.

        Returns:
            bool: *True*, if a confirmed or registered participation was
                cancelled. *False*, if no registration or confirmed
                participation was found.
        """
        with self.data_handler as data:
            confirmation_cancelled = False
            registration_cancelled = False
            if email in data["participants_confirmed"]:
                del data["participants_confirmed"][email]
                confirmation_cancelled = True
            if email in data["participants_registered"]:
                del data["participants_registered"][email]
                registration_cancelled = True

            return confirmation_cancelled or registration_cancelled

    @staticmethod
    def participant_new(email: str, data: dict) -> bool:
        """
        bool: True, if the email address has not been registered.
        """
        return not email in data["participants_registered"]

    @staticmethod
    def registration_expired(email: str, data: dict) -> t.Union[bool, None]:
        """
        Returns:
            bool: If the registration is registered. A value of *True*
                indicates that the registration has expired, a value of
                *False* indicates that it has not.
            NoneType: If the participant is not registered.

        """
        if not email in data["participants_registered"]:
            return None
        now = datetime.now().timestamp()
        reserved_for = data["reservation_time"]
        registration_time = data["participants_registered"].get(email, now)
        return (now - registration_time) > reserved_for

    @staticmethod
    def participant_confirmed(email: str, data: dict) -> bool:
        """
        bool: *True*, if the participant has confirmed their email address.
        """
        return email in data["participants_confirmed"]


class SchedulerURLHandler:
    """Handles URLs for the Scheduler."""

    def __init__(self, scheduler, exp: ExperimentSession):
        self.exp = exp
        self.scheduler = scheduler
        self.name = self.scheduler.name
        self.encoded_name = base64.b64encode(self.name.encode()).decode()
        self.cancel_page = self.scheduler.registration_cancelled
        self.confirm_page = self.scheduler.registration_confirmed

    def create_url(self, data: dict, to_page: str, valid_for: int) -> str:
        """Creates a URL to include in emails."""
        data.update({"valid_for": valid_for, "created": datetime.now().timestamp()})
        kwargs = {self.encoded_name: base64.b64encode(json.dumps(data).encode())}
        expurl = url_for(
            "alfredo.start",
            expid=self.exp.exp_id,
            _external=True,
            page=to_page,
            scheduler=self.name,
            **kwargs,
        )
        return expurl

    def cancel_url(self, email: str, dateslot_id: str, valid_for: int) -> str:
        """Creates a CANCEL url."""
        data = {"email": email, "dateslot_id": dateslot_id}
        return self.create_url(data=data, to_page=self.cancel_page, valid_for=valid_for)

    def confirm_url(self, email: str, dateslot_id: str, valid_for: int) -> str:
        """Creates a CONFIRM url. Validity default is 24h."""
        data = {"email": email, "dateslot_id": dateslot_id}
        return self.create_url(data=data, to_page=self.confirm_page, valid_for=valid_for)

    def extract_url_data(self) -> dict:
        """Returns JSON data passed in a start link for this scheduler."""
        data = self.exp.urlargs.get(self.encoded_name)
        decoded_data = base64.b64decode(data).decode(encoding="utf-8")
        return json.loads(decoded_data)

    @staticmethod
    def validate(data: dict) -> bool:
        """
        Checks whether data submitted via URL are expired.

        Returns:
            bool: *True*, if the data are valid, *False* otherwise.
        """
        valid_for = data.get("valid_for", 0)
        if valid_for == -1:
            return True

        created = data.get("created", 0)
        now = datetime.now().timestamp()
        passed_time = now - created

        return passed_time <= valid_for


class Scheduler:
    """Scheduler class."""

    def __init__(
        self,
        name: str,
        lang: str,
        reservation_time: int = 60 * 60,
        cancellation_time: int = 60 * 60 * 3,
        csv_delimiter: str = ",",
    ):
        self.name = name
        self.txt = TEXTS[lang]
        self.reservation_time = reservation_time
        self.cancellation_time = cancellation_time
        self.delimiter = csv_delimiter

    def url_handler(self, exp) -> SchedulerURLHandler:
        return SchedulerURLHandler(self, exp=exp)

    @property
    def registration(self) -> str:
        return self.name + "_registration__"

    @property
    def registration_initiated(self) -> str:
        return self.name + "_registration_initiated__"

    @property
    def registration_confirmed(self) -> str:
        return self.name + "_registration_confirmed__"

    @property
    def registration_cancelled(self) -> str:
        return self.name + "_registration_cancelled__"

    @property
    def add_slots(self) -> str:
        return self.name + "_add_slots__"

    @property
    def manage_slots(self) -> str:
        return self.name + "_manage_slots__"

    @property
    def interface(self) -> str:
        return self.name + "_interface__"

    @property
    def admin(self) -> str:
        return self.name + "_admin__"

    def mail_data(self, data: dict) -> dict:
        start = datetime.fromtimestamp(data["start"])
        data["date"] = start.strftime(self.txt.get("date_format"))
        data["time"] = start.strftime(self.txt.get("time_format"))
        data["duration"] = str(round(data["duration"] / 60)) + " m"
        data["cancellation_time"] = str(round(self.cancellation_time / 60)) + " m"
        data["reservation_time"] = str(round(self.reservation_time / 60)) + " m"

        return data

    def render_mail(self, data: dict, template: str) -> str:
        data = self.mail_data(data)
        template = self.txt.get(template)
        return template.render(data)
