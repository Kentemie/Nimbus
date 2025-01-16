from pydantic import BaseModel, Field


class BearerResponse(BaseModel):
    access_token: str = Field(
        ...,
        example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1"
        "c2VyX2lkIjoiOTIyMWZmYzktNjQwZi00MzcyLTg2Z"
        "DMtY2U2NDJjYmE1NjAzIiwiYXVkIjoiZmFzdGFwaS"
        "11c2VyczphdXRoIiwiZXhwIjoxNTcxNTA0MTkzfQ."
        "M10bjOe45I5Ncu_uXvOmVV8QxnL-nZfcH96U90JaocI",
    )
    token_type: str = Field(..., example="Bearer")
