class InvalidViewBoxError(Exception):
    ERROR_MESSAGE = "Invalid view box specified. Please make sure that the view box only contains numerical values."

    def __init__(self):
        self.message = self.ERROR_MESSAGE
        super().__init__(self.message)

    def __str__(self):
        return self.message


class SvgToPngImageError(Exception):
    ERROR_MESSAGE = "Cannot convert SVG to PNG. Reason: {message}."

    def __init__(self, message):
        self.message = self.ERROR_MESSAGE.format(message=message)
        super().__init__(self.message)

    def __str__(self):
        return self.message
