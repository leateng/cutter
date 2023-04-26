class User:
    def __init__(
        self,
        id=None,
        name=None,
        password=None,
        role_id=None,
        department=None,
        created_at=None,
    ) -> None:
        self._id = id
        self._name = name
        self._password = password
        self._role_id = role_id
        self._department = department
        self._created_at = created_at

    # def get_id(self):
    #     return self._id
    #
    # def set_id(self, id):
    #     self._id = id
    #
    # def get_name(self):
    #     return self._name
    #
    # def set_name(self, name):
    #     self._name = name
    #
    # def get_password(self):
    #     return self._password
    #
    # def set_password(self, password):
    #     self._password = password
    #
    # def get_role_id(self):
    #     return self._role_id
    #
    # def set_role_id(self, role_id):
    #     self._role_id = role_id
    #
    # def get_department(self):
    #     return self._department
    #
    # def set_department(self, department):
    #     self._department = department
    #
    # def get_created_at(self):
    #     return self._created_at
    #
    # def set_created_at(self, created_at):
    #     self._created_at = created_at
