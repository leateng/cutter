class User:
    def __init__(self, id, name, password, role_id, department, created_at) -> None:
        self._id = id
        self._name = name
        self._password = password
        self._role_id = role_id
        self._department = department
        self._created_at = created_at
