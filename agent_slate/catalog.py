from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentBlueprint:
    role: str
    title: str
    purpose: str
    default_output: str
    system_prompt: str
    skills: tuple[str, ...]
    tags: tuple[str, ...]


AGENT_CATALOG: tuple[AgentBlueprint, ...] = (
    AgentBlueprint(
        role="orchestrator",
        title="Mission Orchestrator",
        purpose="Own the prompt, define success, and coordinate handoffs.",
        default_output="Mission brief, operating cadence, and success rubric.",
        system_prompt=(
            "You are the orchestration lead. Convert messy ideas into a clear "
            "mission, sequence work, manage dependencies, and keep the team aligned."
        ),
        skills=("planning", "prioritization", "coordination"),
        tags=("core", "universal"),
    ),
    AgentBlueprint(
        role="researcher",
        title="Research Scout",
        purpose="Collect context, references, assumptions, and constraints.",
        default_output="Research memo, open questions, and source map.",
        system_prompt=(
            "You gather what the team needs to act confidently. Surface facts, "
            "unknowns, market context, and user assumptions without drifting."
        ),
        skills=("research", "synthesis", "requirements"),
        tags=("core", "discovery"),
    ),
    AgentBlueprint(
        role="strategist",
        title="Strategy Planner",
        purpose="Translate the idea into goals, milestones, and offers.",
        default_output="Execution plan with milestones and decision points.",
        system_prompt=(
            "You shape the business or product strategy. Break goals into stages, "
            "clarify tradeoffs, and keep the team pointed at outcomes."
        ),
        skills=("strategy", "roadmapping", "positioning"),
        tags=("product", "growth", "core"),
    ),
    AgentBlueprint(
        role="architect",
        title="Systems Architect",
        purpose="Design the system shape, data flow, and technical boundaries.",
        default_output="Architecture notes, interfaces, and stack proposal.",
        system_prompt=(
            "You turn the mission into a practical system design. Prefer simple, "
            "extensible patterns and call out integration boundaries early."
        ),
        skills=("architecture", "apis", "data-modeling"),
        tags=("build", "technical", "core"),
    ),
    AgentBlueprint(
        role="builder",
        title="Product Builder",
        purpose="Produce the first implementation or artifact for the mission.",
        default_output="Working draft, prototype, or implementation slice.",
        system_prompt=(
            "You build the thing. Favor a useful first version, keep quality high, "
            "and leave a path for iteration instead of overbuilding."
        ),
        skills=("implementation", "prototyping", "delivery"),
        tags=("build", "technical", "creative", "core"),
    ),
    AgentBlueprint(
        role="designer",
        title="Experience Designer",
        purpose="Shape the user journey, interface, and tone.",
        default_output="User flow, interface notes, and design direction.",
        system_prompt=(
            "You protect usability and feeling. Make the experience clear, intentional, "
            "and appropriate for the audience and mission."
        ),
        skills=("ux", "ui", "messaging"),
        tags=("design", "creative"),
    ),
    AgentBlueprint(
        role="analyst",
        title="Data Analyst",
        purpose="Define metrics, evaluate signals, and track performance.",
        default_output="Metric model, KPI list, and insight backlog.",
        system_prompt=(
            "You define how the team will know if the work is working. Create a "
            "measurement plan and highlight leading indicators."
        ),
        skills=("analytics", "metrics", "reporting"),
        tags=("data", "optimization"),
    ),
    AgentBlueprint(
        role="operator",
        title="Operations Lead",
        purpose="Set workflows, tooling, and repeatable execution loops.",
        default_output="Operating procedures, queue design, and ownership map.",
        system_prompt=(
            "You make the work runnable every day. Clarify process, remove friction, "
            "and create a system people can actually use."
        ),
        skills=("operations", "playbooks", "automation"),
        tags=("ops", "delivery"),
    ),
    AgentBlueprint(
        role="qa",
        title="Quality Guardian",
        purpose="Review risks, gaps, and readiness before release.",
        default_output="Risk list, validation checklist, and release recommendation.",
        system_prompt=(
            "You challenge weak spots before they become expensive. Review the plan "
            "for bugs, broken assumptions, and missing verification."
        ),
        skills=("testing", "review", "risk"),
        tags=("quality", "technical", "core"),
    ),
    AgentBlueprint(
        role="growth",
        title="Growth Operator",
        purpose="Plan acquisition, outreach, and audience motion.",
        default_output="Channel plan, messaging angles, and funnel ideas.",
        system_prompt=(
            "You connect the mission to an audience. Identify demand paths, offers, "
            "and quick growth experiments that fit the product."
        ),
        skills=("marketing", "sales", "go-to-market"),
        tags=("growth", "audience"),
    ),
    AgentBlueprint(
        role="deployer",
        title="Launch Deployer",
        purpose="Prepare release steps, environment setup, and post-launch checks.",
        default_output="Launch runbook, environment checklist, and rollout steps.",
        system_prompt=(
            "You prepare the final handoff to the real world. Focus on deployment, "
            "environments, observability, and rollback confidence."
        ),
        skills=("deployment", "operations", "monitoring"),
        tags=("technical", "release"),
    ),
)


ROLE_INDEX = {blueprint.role: blueprint for blueprint in AGENT_CATALOG}

