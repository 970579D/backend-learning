class Response_Model:
    def __init__(self, status: str, message: str, data: any = None):
        self.status = status
        self.message = message
        self.data = data if data is not None else None