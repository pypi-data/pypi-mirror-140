from respec import Specification

from devdiary.specification.registration.dsl import RegistrationDsl


class RegistrationSpecification(Specification):
    dsl: RegistrationDsl

    # User Story: #1
    def should_be_able_to_register_to_the_system(self):
        self.dsl.register("MyUsername", "MyPassword", "MyDisplayName", "myemail@devdiary.link")
        self.dsl.confirm_registration('myemail@devdiary.link')
        self.dsl.login("MyUsername", "MyPassword")
        self.dsl.verify_current_user("MyUsername")
