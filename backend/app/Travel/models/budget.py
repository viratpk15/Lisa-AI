"""
Jarvis AIOS — Budget Breakdown Models
"""

from typing import List, Literal
from pydantic import BaseModel, Field


class BudgetCategory(BaseModel):
    """Itemized budget line item."""

    category: Literal["Flights", "Hotel", "Local transport", "Food", "Activities", "Other"] = Field(
        ..., description="Standard expense category"
    )
    verified_amount: float = Field(default=0.0, ge=0, description="Amount with verified provider or live rate")
    estimated_amount: float = Field(default=0.0, ge=0, description="Estimated approximate spending")
    currency: str = Field(default="INR", description="Currency code")
    is_verified: bool = Field(default=False, description="Whether line item is anchored on live verified data")
    notes: str = Field(default="", description="Category justification or breakdown details")


class TripBudget(BaseModel):
    """Aggregate budget calculation model strictly distinguishing verified vs estimated figures."""

    user_budget: float = Field(default=0.0, ge=0, description="Target budget provided by user (0 if unspecified)")
    currency: str = Field(default="INR", description="Currency code")
    categories: List[BudgetCategory] = Field(default_factory=list, description="Categorized budget lines")
    total_verified: float = Field(default=0.0, ge=0, description="Sum of verified bookings and fares")
    total_estimated: float = Field(default=0.0, ge=0, description="Sum of estimated discretionary costs")
    total_projected: float = Field(default=0.0, ge=0, description="total_verified + total_estimated")
    remaining_balance: float = Field(
        default=0.0,
        description="user_budget - total_projected (positive = savings, negative = deficit)",
    )
    status: Literal["within_budget", "exceeded", "unspecified"] = Field(
        default="within_budget",
        description="Budget compliance status against user limit",
    )
    disclaimer: str = Field(
        default="Verified amounts reflect selected options. Estimated costs are based on typical destination averages and may vary by season."
    )
