class Model():
    def __init__(self, title : str, link = None):
        self.title = title
        self.link = link
        self.properties = {}

    """
    fields : list[dict]
    """
    def add(self, fields : list):
        for field in fields:
            name = next(iter(field))
            type_ = field[name]

            self.properties[name] = {
                type_: {}
            }