class NoRecordFoundError(Exception):
    def __init__(self, name: str):
        super().__init__(f'No record found with name: {name}')