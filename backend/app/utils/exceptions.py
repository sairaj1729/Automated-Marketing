class AppException(Exception):
    """Base application exception"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class UserNotFoundError(AppException):
    """Raised when a user is not found"""
    pass

class InvalidCredentialsError(AppException):
    """Raised when user credentials are invalid"""
    pass

class LinkedInAuthError(AppException):
    """Raised when LinkedIn authentication fails"""
    pass

class AIServiceError(AppException):
    """Raised when AI service encounters an error"""
    pass

class DatabaseError(AppException):
    """Raised when database operations fail"""
    pass

class ValidationError(AppException):
    """Raised when data validation fails"""
    pass