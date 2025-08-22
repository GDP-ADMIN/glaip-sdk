"""Calculator tool plugin for testing CLI tool creation."""

from typing import Any

from gllm_plugin.tools import tool_plugin
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class CalculatorInput(BaseModel):
    """Input for calculator operations."""

    operation: str = Field(description="Mathematical operation to perform")
    precision: int = Field(default=2, description="Number of decimal places for result")


@tool_plugin(version="1.0.0")
class CalculatorTool(BaseTool):
    """A mathematical calculator tool."""

    name: str = "calculator-tool"
    description: str = (
        "A mathematical calculator that can perform basic arithmetic operations"
    )
    args_schema: type[BaseModel] = CalculatorInput

    def _run(self, operation: str, precision: int = 2, **kwargs: Any) -> str:
        """Run the calculator tool."""
        try:
            operation = operation.strip()
            allowed_chars = set("0123456789+-*/.()** ")
            if not all(c in allowed_chars for c in operation):
                raise ValueError("Invalid characters in operation")

            result = eval(operation)
            rounded_result = round(float(result), precision)
            return f"{operation} = {rounded_result}"
        except Exception as e:
            raise ValueError(f"Calculation failed: {str(e)}")
