from pydantic import BaseModel, Field, HttpUrl
from datetime import date
from typing import List

class Finding(BaseModel):
    title: str = Field(..., description="Clear descriptive title of the finding")
    description: str = Field(..., description="Detailed description of the finding")
    source: HttpUrl | str = Field(..., description="Source URL or reference")
    relevance: int = Field(..., ge=1, le=10, description="Relevance score from 1–10")
    category: str = Field(..., description="Category or theme of the finding")

class ResearchOutput(BaseModel):
    topic: str = Field(..., description="Topic name researched")
    research_date: date = Field(..., description="Date when the research was conducted")
    findings: List[Finding] = Field(..., min_items=10, max_items=10, description="Exactly 10 research findings")
    executive_summary: str = Field(..., description="Executive summary of research")
    total_sources: int = Field(..., ge=0, description="Total number of sources found")

class Section(BaseModel):
    heading: str = Field(..., description="Title of section")
    content: str = Field(..., description="Detailed narrative for this section")
    key_points: List[str] = Field(..., description="List of key points in this section")

class FinalReport(BaseModel):
    professional_title: str = Field(..., description="Professional report title")
    executive_summary: str = Field(..., description="2–3 paragraph executive summary")
    sections: List[Section] = Field(..., min_items=3, max_items=5, description="3–5 detailed sections")
    conclusion: str = Field(..., description="Comprehensive conclusion")
    generation_date: date = Field(..., description="Date of report generation")
    word_count: int = Field(..., ge=0, description="Word count of the final report")
