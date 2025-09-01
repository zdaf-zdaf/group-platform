class ExternalServiceException(Exception):
    """外部服务异常基类"""
    def __init__(self, message, service_name=None):
        super().__init__(message)
        self.service_name = service_name
        self.message = message
        self.details = {}
        
    def __str__(self):
        return f"[{self.service_name}] {self.message}"

class ExternalServiceTimeout(ExternalServiceException):
    """外部服务超时异常"""
    def __init__(self, message, service_name="ExternalService"):
        super().__init__(f"Timeout: {message}", service_name)

class ExternalServiceError(ExternalServiceException):
    """外部服务错误异常"""
    def __init__(self, message, service_name="ExternalService", status_code=None):
        super().__init__(f"Error: {message}", service_name)
        self.status_code = status_code