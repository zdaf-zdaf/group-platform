class ExternalServiceError(Exception):
    """外部服务异常基类"""
    pass

class ExternalServiceTimeout(ExternalServiceError):
    """外部服务超时异常"""
    pass

class ExperimentServiceError(Exception):
    """实验服务业务异常"""
    pass