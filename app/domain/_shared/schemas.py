from pydantic import BaseModel, ConfigDict

class RequestSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

class ResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)