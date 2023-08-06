class SuccessionDoesNotMatch(Exception):
    def __init__(self, value):
        self.message = "The value '{}' does not correspond to the pattern of the succession".format(
            value
        )
        super().__init__(self.message)
