#!/usr/bin/env python3
"""Unit tests for the AIP SDK Exceptions.

Tests the custom exception hierarchy without external dependencies.
"""

import pytest

from glaip_sdk.exceptions import (
    AIPError,
    AmbiguousResourceError,
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ServerError,
    ValidationError,
)


@pytest.mark.unit
class TestExceptionHierarchy:
    """Test the exception class hierarchy."""

    def test_exception_inheritance(self):
        """Test that all exceptions inherit from AIPError."""
        assert issubclass(AuthenticationError, AIPError)
        assert issubclass(ValidationError, AIPError)
        assert issubclass(NotFoundError, AIPError)
        assert issubclass(ServerError, AIPError)
        assert issubclass(ConflictError, AIPError)
        assert issubclass(ForbiddenError, AIPError)
        assert issubclass(AmbiguousResourceError, AIPError)

    def test_exception_instances(self):
        """Test that exceptions can be instantiated."""
        # Test base exception
        base_error = AIPError("Base error message")
        assert str(base_error) == "Base error message"
        assert isinstance(base_error, AIPError)

        # Test specific exceptions
        auth_error = AuthenticationError("Authentication failed")
        assert str(auth_error) == "Authentication failed"
        assert isinstance(auth_error, AuthenticationError)
        assert isinstance(auth_error, AIPError)

        validation_error = ValidationError("Validation failed")
        assert str(validation_error) == "Validation failed"
        assert isinstance(validation_error, ValidationError)
        assert isinstance(validation_error, AIPError)

        not_found_error = NotFoundError("Resource not found")
        assert str(not_found_error) == "Resource not found"
        assert isinstance(not_found_error, NotFoundError)
        assert isinstance(not_found_error, AIPError)

        server_error = ServerError("Server error occurred")
        assert str(server_error) == "Server error occurred"
        assert isinstance(server_error, ServerError)
        assert isinstance(server_error, AIPError)

        conflict_error = ConflictError("Resource conflict")
        assert str(conflict_error) == "Resource conflict"
        assert isinstance(conflict_error, ConflictError)
        assert isinstance(conflict_error, AIPError)

        forbidden_error = ForbiddenError("Access forbidden")
        assert str(forbidden_error) == "Access forbidden"
        assert isinstance(forbidden_error, ForbiddenError)
        assert isinstance(forbidden_error, AIPError)

        ambiguous_error = AmbiguousResourceError("Multiple resources found")
        assert str(ambiguous_error) == "Multiple resources found"
        assert isinstance(ambiguous_error, AmbiguousResourceError)
        assert isinstance(ambiguous_error, AIPError)


@pytest.mark.unit
class TestExceptionMessages:
    """Test exception message handling."""

    def test_exception_with_simple_message(self):
        """Test exceptions with simple string messages."""
        message = "Simple error message"

        error = AIPError(message)
        assert str(error) == message
        assert error.args == (message,)

    def test_exception_with_formatted_message(self):
        """Test exceptions with formatted messages."""
        resource_type = "agent"
        resource_id = "123"
        message = f"{resource_type} with ID {resource_id} not found"

        error = NotFoundError(message)
        assert str(error) == message
        assert "agent" in str(error)
        assert "123" in str(error)

    def test_exception_with_complex_message(self):
        """Test exceptions with complex error messages."""
        error_details = {"field": "name", "value": "", "constraint": "required"}
        message = f"Validation failed: {error_details}"

        error = ValidationError(message)
        assert str(error) == message
        assert "Validation failed" in str(error)
        assert "name" in str(error)

    def test_exception_message_encoding(self):
        """Test exception message encoding handling."""
        # Test with unicode characters
        unicode_message = "Error with unicode: 🚀✨"
        error = AIPError(unicode_message)
        assert str(error) == unicode_message

        # Test with special characters
        special_chars = "Error with special chars: !@#$%^&*()"
        error = AIPError(special_chars)
        assert str(error) == special_chars


@pytest.mark.unit
class TestExceptionContext:
    """Test exception context and attributes."""

    def test_exception_with_context(self):
        """Test exceptions with additional context."""
        message = "API request failed"
        status_code = 500
        error_type = "InternalServerError"

        # Create exception with context
        error = ServerError(
            f"{message} (status={status_code}, error_type={error_type})"
        )

        assert (
            str(error) == f"{message} (status={status_code}, error_type={error_type})"
        )
        assert "500" in str(error)
        assert "InternalServerError" in str(error)

    def test_exception_with_details(self):
        """Test exceptions with detailed information."""
        base_message = "Validation failed"
        details = {
            "validation_errors": ["Field 'name' is required"],
            "raw_errors": [{"type": "missing", "loc": ["body", "name"]}],
        }

        message = f"{base_message} details={details}"
        error = ValidationError(message)

        assert str(error) == message
        assert "Validation failed" in str(error)
        assert "Field 'name' is required" in str(error)

    def test_exception_with_suggestions(self):
        """Test exceptions with helpful suggestions."""
        message = "Resource not found. Available resources: agent1, agent2"
        error = NotFoundError(message)

        assert str(error) == message
        assert "Resource not found" in str(error)
        assert "agent1" in str(error)
        assert "agent2" in str(error)


@pytest.mark.unit
class TestExceptionUsage:
    """Test how exceptions are used in practice."""

    def test_raise_and_catch_exception(self):
        """Test raising and catching exceptions."""
        try:
            raise ValidationError("Invalid input data")
        except ValidationError as e:
            assert str(e) == "Invalid input data"
            assert isinstance(e, AIPError)
        except Exception:
            pytest.fail("Should have caught ValidationError")

    def test_exception_chaining(self):
        """Test exception chaining."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise ValidationError(f"Validation failed: {e}") from e
        except ValidationError as e:
            assert "Validation failed" in str(e)
            assert "Original error" in str(e)
            assert e.__cause__ is not None

    def test_exception_in_conditional_logic(self):
        """Test exceptions in conditional logic."""

        def process_resource(resource_id):
            if not resource_id:
                raise ValidationError("Resource ID is required")
            if resource_id == "deleted":
                raise NotFoundError("Resource has been deleted")
            if resource_id == "locked":
                raise ForbiddenError("Resource is locked")
            return f"Processing resource {resource_id}"

        # Test valid case
        result = process_resource("123")
        assert result == "Processing resource 123"

        # Test validation error
        with pytest.raises(ValidationError):
            process_resource("")

        # Test not found error
        with pytest.raises(NotFoundError):
            process_resource("deleted")

        # Test forbidden error
        with pytest.raises(ForbiddenError):
            process_resource("locked")


@pytest.mark.unit
class TestExceptionComparison:
    """Test exception comparison and equality."""

    def test_exception_equality(self):
        """Test exception equality."""
        error1 = ValidationError("Same message")
        error2 = ValidationError("Same message")
        error3 = ValidationError("Different message")

        # Same class and message should be equal
        # Note: Exception equality is based on identity, not content
        assert error1 is not error2  # Different instances
        assert str(error1) == str(error2)  # Same string representation
        assert error1 != error3

        # Different exception types should not be equal
        auth_error = AuthenticationError("Same message")
        assert error1 != auth_error

    def test_exception_hashability(self):
        """Test that exceptions are hashable."""
        error = ValidationError("Test error")

        # Should be able to create a set of exceptions
        error_set = {error}
        assert len(error_set) == 1
        assert error in error_set

        # Should be able to use as dictionary key
        error_dict = {error: "error_info"}
        assert error_dict[error] == "error_info"


@pytest.mark.unit
class TestExceptionDocumentation:
    """Test exception documentation and help."""

    def test_exception_docstrings(self):
        """Test that exceptions have proper docstrings."""
        assert AIPError.__doc__ is not None
        # Check actual docstring content
        assert "Base exception for AIP SDK" in AIPError.__doc__

        assert AuthenticationError.__doc__ is not None
        assert "authentication" in AuthenticationError.__doc__.lower()

        assert ValidationError.__doc__ is not None
        assert "validation" in ValidationError.__doc__.lower()

        assert NotFoundError.__doc__ is not None
        assert "not found" in NotFoundError.__doc__.lower()

        assert ServerError.__doc__ is not None
        assert "server" in ServerError.__doc__.lower()

        assert ConflictError.__doc__ is not None
        assert "conflict" in ConflictError.__doc__.lower()

        assert ForbiddenError.__doc__ is not None
        assert "forbidden" in ForbiddenError.__doc__.lower()

        assert AmbiguousResourceError.__doc__ is not None
        assert "multiple resources" in AmbiguousResourceError.__doc__.lower()

    def test_exception_help(self):
        """Test exception help information."""
        error = ValidationError("Test error")

        # Should have help method or similar
        assert hasattr(error, "__class__")
        assert hasattr(error.__class__, "__doc__")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "unit"])
