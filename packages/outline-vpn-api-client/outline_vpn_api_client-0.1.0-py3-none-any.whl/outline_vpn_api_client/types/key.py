from typing import Optional

from pydantic import BaseModel, Field


class OutlineKey(BaseModel):
    id: Optional[int] = Field(None)
    name: Optional[str] = Field(None)
    password: Optional[str] = Field(None)
    port: Optional[int] = Field(None)
    method: Optional[str] = Field(None)
    access_url: Optional[str] = Field(None, alias="accessUrl")
    used_bytes: Optional[int] = Field(None)
