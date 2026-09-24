class User:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def is_admin(self):
        return getattr(self, 'role', '') == 'admin'

    @classmethod
    def from_row(cls, row):
        return cls(**row) if row else None