from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class ProtocolSpec(BaseModel):
	name: str = Field(..., description="Original protocol name")
	endpoint: Optional[str] = None
	auth_token: Optional[str] = None
	config: Dict[str, Any] = Field(default_factory=dict)


class ConvertRequest(BaseModel):
	source: ProtocolSpec
	target: str = Field(..., pattern="^(streamable-http|sse|stdio)$")
	custom_script: Optional[str] = None


class ConvertResponse(BaseModel):
	result: Dict[str, Any]
