from typing import List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

"""
Test Example Python File for AST Extraction
Reference: embedding_service.py
"""




@dataclass
class DataClassExample:
    """
    Example dataclass for AST extraction.
    """
    id: int
    name: str
    created: datetime = datetime.now()

    def get_id(self) -> int:
        """Return the id."""
        return self.id

    def get_name(self) -> str:
        """Return the name."""
        return self.name


class ExampleClass(BaseClass):
    """
    Example class for AST extraction testing.
    """
    def __init__(self, value: int, name: str = "default") -> None:
        """
        Initialize ExampleClass.
        Args:
            value (int): The value to store.
            name (str): Optional name.
        """
        self.value = value
        self.name = name

    @staticmethod
    def static_method(x: int) -> int:
        """Static method example."""
        return x * 2

    @classmethod
    def class_method(cls, items: List[int]) -> int:
        """Class method example."""
        return sum(items)


    def instance_method(self, flag: bool = True) -> str:
        """Instance method example."""
        if flag:
            return self.name
        return str(self.value)

    def validate(self, text: str, max_length: int = 2000) -> Tuple[bool, str]:
        """
        Validate text input for testing.
        Args:
            text (str): Text to validate.
            max_length (int): Maximum allowed length.
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not text:
            return False, "Text cannot be empty"
        if len(text) > max_length:
            return False, f"Text too long: {len(text)} chars (max: {max_length})"
        return True, ""


async def example_function(vallll,  a: int, c:bool, items: List[int], b: str = "foo",  t=990, s=None,  *args, **kwargs) -> Optional[str]:
def process_data(data: List[int], normalize: bool = True) -> List[float]:
    """
    Process data and optionally normalize.
    Args:
        data (List[int]): Data to process.
        normalize (bool): Whether to normalize.
    Returns:
        List[float]: Processed data.
    """
    result = [float(x) for x in data]
    if normalize and result:
        mag = sum(x * x for x in result) ** 0.5
        return [x / mag for x in result]
    return result


def _test_embedding_generation() -> bool:
    """
    Test embedding generation with a simple input.
    Returns:
        bool: True if test passes, False otherwise
    """
    return True
    """
    Example function for AST extraction testing.
    Args:
        a (int): First argument.
        b (str): Second argument, default 'foo'.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.
    Returns:
        Optional[str]: Result string or None.
    """
    return f"{a}-{b}" if a > 0 else None


class Me(BaseClass, MyClass) :