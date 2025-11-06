"""
Custom exception classes for the application
"""


class TrafficSystemException(Exception):
    """Base exception for traffic system"""
    pass


class DatabaseException(TrafficSystemException):
    """Database related exceptions"""
    pass


class AuthenticationException(TrafficSystemException):
    """Authentication related exceptions"""
    pass


class AuthorizationException(TrafficSystemException):
    """Authorization related exceptions"""
    pass


class ValidationException(TrafficSystemException):
    """Validation related exceptions"""
    pass


class NotFoundException(TrafficSystemException):
    """Resource not found exceptions"""
    pass

