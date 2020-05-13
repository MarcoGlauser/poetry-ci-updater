class Provider:
    def __init__(self, branch_name:str, updates:[str]):
        self.branch_name = branch_name
        self.updates = updates

    def updates_string(self):
        return '\n\n'.join(self.updates)

    def run(self):
        raise NotImplemented