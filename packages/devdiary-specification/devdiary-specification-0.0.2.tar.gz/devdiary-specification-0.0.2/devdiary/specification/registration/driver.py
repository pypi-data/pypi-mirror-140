from abc import ABC, abstractmethod
from respec import Driver


class RegistrationDriver(Driver, ABC):
    @abstractmethod
    def submit_registration(self, username: str, password: str, display_name: str, email: str):
        pass

    @abstractmethod
    def confirm_registration_by_email(self, email: str):
        pass

    @abstractmethod
    def login_with_username_and_password(self, username: str, password: str):
        pass

    @abstractmethod
    def get_current_username(self) -> str:
        pass
