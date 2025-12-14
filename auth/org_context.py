class OrgContext:
    def __init__(self, org):
        self.org = org

    def assert_active(self):
        if not self.org.active:
            raise PermissionError("Organization suspended")
