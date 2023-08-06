from alfred3.section import Section
from alfred3.admin import AdminAccess

from .page import ManageDateSlotsPage
from .page import AddDateSlotsPage
from .page import RegistrationPage
from .page import RegistrationInitiatedPage
from .page import ConfirmationPage
from .page import CancelPage


class SchedulerAdmin(Section):
    scheduler = None
    access_level = AdminAccess.LEVEL2

    def __init__(self, scheduler=None, **kwargs):
        if scheduler is not None:
            self.scheduler = scheduler
        if self.scheduler is None:
            raise ValueError("Must supply scheduler.")

        name = self.scheduler.admin
        super().__init__(name=name, **kwargs)

    def on_exp_access(self):
        self += ManageDateSlotsPage(self.scheduler)
        self += AddDateSlotsPage(self.scheduler)


class SchedulerInterface(Section):
    scheduler = None
    email: str = None

    def __init__(self, scheduler=None, email: str = None, **kwargs):
        if scheduler is not None:
            self.scheduler = scheduler
        if self.scheduler is None:
            raise ValueError("Must supply scheduler.")

        if email is not None:
            self.email = email

        name = self.scheduler.interface
        super().__init__(name=name, **kwargs)

    def showif(self) -> bool:
        return self.exp.urlargs.get("scheduler") == self.scheduler.name

    def on_exp_access(self):
        if self.should_be_shown:
            if self.email is None:
                raise ValueError("Must supply email.")
            self += RegistrationPage(self.scheduler)
            self += RegistrationInitiatedPage(self.scheduler)
            self += ConfirmationPage(self.scheduler)
            self += CancelPage(self.scheduler)
