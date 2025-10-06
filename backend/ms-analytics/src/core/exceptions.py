from fastapi import HTTPException, status

class AthenaQueryException(HTTPException):
    """Excepción cuando falla una query de Athena"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Athena Query Error: {detail}"
        )

class AthenaTimeoutException(HTTPException):
    """Excepción cuando timeout en Athena"""
    def __init__(self, detail: str = "Query timeout"):
        super().__init__(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Athena Timeout: {detail}"
        )

class DataNotFoundException(HTTPException):
    """Excepción cuando no se encuentran datos"""
    def __init__(self, detail: str = "No data found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )
