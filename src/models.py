"""Pydantic models for the call me meybe"""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

jsonType = Literal["string", "number", "boolean", "object", "array", "integer"]


class StrictModel(BaseModel):
    """Base model that rejects unknown fields."""

    model_config = ConfigDict(extra="forbid")


class PromptItem(StrictModel):
    """Represent one natural-language prompt."""

    prompt: str = Field(min_length=1)


class TypeDefinition(StrictModel):
    """Represent a Json type definition"""

    type: jsonType


class FunctionDefinition(StrictModel):
    """Represent one available function"""

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    parameters: dict[str, TypeDefinition]
    returns: TypeDefinition


class FunctionCallResult(StrictModel):
    """Represent one generated function call"""

    prompt: str = Field(min_length=1)
    name: str = Field(min_length=1)
    parameters: dict[str, object]


class InputData(StrictModel):
    """Group loaded project inputs"""
    prompts: list[PromptItem]
    functions: list[FunctionDefinition]
