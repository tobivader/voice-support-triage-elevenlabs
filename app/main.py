from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Voice Support Triage")


def load_customers() -> dict[str, dict[str, Any]]:
    data_path = Path(__file__).resolve().parent / "data" / "customers.json"
    with data_path.open("r", encoding="utf-8") as file:
        customers = json.load(file)
    return {customer["customer_id"]: customer for customer in customers}


CUSTOMERS = load_customers()
ESCALATIONS: list[dict[str, Any]] = []


class EscalationCreate(BaseModel):
    customer_id: str = Field(..., min_length=1)
    issue: str = Field(..., min_length=1)
    finding: str = Field(..., min_length=1)
    troubleshooting_performed: list[str] = Field(..., min_length=1)

    @field_validator("troubleshooting_performed")
    @classmethod
    def validate_steps(cls, value: list[str]) -> list[str]:
        if not value or any(not step.strip() for step in value):
            raise ValueError("Each troubleshooting step must be a non-empty string.")
        return value


class EscalationResponse(EscalationCreate):
    status: str = "created"
    escalation_id: str
    recommended_team: str = "Engineering"


@app.get("/")
def home() -> HTMLResponse:
    html_path = Path(__file__).resolve().parent / "static" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/customers/{customer_id}")
def get_customer(customer_id: str) -> dict[str, Any]:
    customer = CUSTOMERS.get(customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer {customer_id} was not found.",
        )
    return customer


@app.post("/escalations", status_code=status.HTTP_201_CREATED, response_model=EscalationResponse)
def create_escalation(payload: EscalationCreate) -> EscalationResponse:
    next_number = len(ESCALATIONS) + 1
    escalation_id = f"ESC-{next_number:04d}"
    response = EscalationResponse(
        escalation_id=escalation_id,
        customer_id=payload.customer_id,
        issue=payload.issue,
        finding=payload.finding,
        troubleshooting_performed=payload.troubleshooting_performed,
        recommended_team="Engineering",
    )
    ESCALATIONS.append(response.model_dump())
    return response
