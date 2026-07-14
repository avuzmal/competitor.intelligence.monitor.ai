from enum import Enum
from pydantic import BaseModel, Field
from typing import List

class ThreatLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class InsightItem(BaseModel):
    category: str = Field(description="The category of the change (e.g., Pricing, Hiring, Product Feature)")
    description: str = Field(description="A concise description of the factual change or insight")

class CompetitorInsight(BaseModel):
    executive_summary: str = Field(description="A 2-sentence TL;DR of the most important strategic updates.")
    what_changed: List[InsightItem] = Field(description="Factual observations of what changed in the competitor's data.")
    what_it_means: List[InsightItem] = Field(description="Strategic interpretation of the changes.")
    what_to_do: List[InsightItem] = Field(description="Actionable recommendations for our client based on these insights.")
    threat_level: ThreatLevel = Field(description="Overall threat level indicated by these changes.")
