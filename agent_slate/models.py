from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AgentSlateRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    prompt: str = Field(default="", description="Any idea or mission the agent team should build.")
    product_name: str = Field(default="", description="Name of the product, company, or idea.")
    idea_name: str = Field(default="", description="Optional name for the idea if different from the product.")
    template_choice: str | None = Field(default=None, description="Optional template family to force.")
    constraints: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    max_agents: int = Field(default=6, ge=3, le=10)
    execution_mode: Literal["plan", "simulate"] = "simulate"


class MissionBrief(BaseModel):
    title: str
    summary: str
    outcome: str
    primary_idea_type: str
    idea_types: list[str]
    challenge_type: str
    domain_tags: list[str]
    constraints: list[str]
    goals: list[str]


class AgentCard(BaseModel):
    role: str
    title: str
    purpose: str
    skills: list[str]
    system_prompt: str
    kickoff_task: str
    expected_output: str


class WorkflowStep(BaseModel):
    step: int
    owner: str
    action: str
    deliverable: str
    depends_on: list[int] = Field(default_factory=list)


class ExecutionEvent(BaseModel):
    stage: str
    owner: str
    status: Literal["queued", "active", "done"]
    note: str


class TemplateOption(BaseModel):
    key: str
    name: str
    fit: str
    use_case: str
    outputs: list[str]
    recommended: bool = False


class BuildOutput(BaseModel):
    product_name: str
    idea_name: str
    selected_template: str
    detected_inputs: list[str]
    positioning: str
    offer: str
    build_scope: list[str]
    first_deliverable: str
    output_summary: str


class AgentSlateResponse(BaseModel):
    mission: MissionBrief
    template_options: list[TemplateOption]
    team: list[AgentCard]
    workflow: list[WorkflowStep]
    execution: list[ExecutionEvent]
    output: BuildOutput
    next_prompt: str
    git_note: str
