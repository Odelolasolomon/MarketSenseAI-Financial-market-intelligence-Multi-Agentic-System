"""
Custom Exception Classes
"""
from typing import Optional, Dict, Any


class MultiAssetAIException(Exception):
    """Base exception for Multi-Asset AI application"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class DataCollectionError(MultiAssetAIException):
    """Exception raised when data collection fails"""
    pass


class AnalysisError(MultiAssetAIException):
    """Exception raised when analysis process fails"""
    pass


class ConfigurationError(MultiAssetAIException):
    """Exception raised when configuration is invalid"""
    pass


class ExternalAPIError(MultiAssetAIException):
    """Exception raised when external API call fails"""
    
    def __init__(
        self,
        message: str,
        api_name: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict] = None
    ):
        super().__init__(
            message=message,
            error_code=f"{api_name.upper()}_API_ERROR",
            details={
                "api_name": api_name,
                "status_code": status_code,
                "response": response_data
            }
        )


class ValidationError(MultiAssetAIException):
    """Exception raised when data validation fails"""
    pass


class CacheError(MultiAssetAIException):
    """Exception raised when cache operation fails"""
    pass


class DatabaseError(MultiAssetAIException):
    """Exception raised when database operation fails"""
    pass


class AgentExecutionError(MultiAssetAIException):
    """Exception raised when agent execution fails"""
    pass