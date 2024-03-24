from dataclasses import dataclass


@dataclass
class FiatExceptionConfig:
    catch_function_exceptions: bool = True
