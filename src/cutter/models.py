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

    def get_name(self):
        return self._name
