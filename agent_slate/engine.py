from __future__ import annotations

import re
from textwrap import shorten

from .catalog import ROLE_INDEX, AgentBlueprint
from .models import (
    AgentCard,
    AgentSlateRequest,
    AgentSlateResponse,
    BuildOutput,
    ExecutionEvent,
    MissionBrief,
    TemplateOption,
    WorkflowStep,
)


DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "saas": ("app", "software", "saas", "platform", "dashboard", "tool"),
    "automation": ("automate", "workflow", "agent", "pipeline", "system"),
    "content": ("content", "write", "newsletter", "video", "podcast", "script"),
    "sales": ("sales", "leads", "outreach", "prospect", "close", "offer"),
    "ecommerce": ("ecommerce", "shop", "store", "product", "checkout"),
    "service": ("agency", "service", "consulting", "clients", "appointments"),
    "data": ("data", "analytics", "report", "dashboard", "metrics"),
    "operations": ("process", "ops", "team", "hire", "handoff", "standardize"),
    "education": ("course", "teach", "training", "lesson", "community"),
    "creative": ("brand", "design", "experience", "visual", "creative"),
}


IDEA_TYPE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "app": ("app", "application", "mobile app", "web app", "platform"),
    "game": ("game", "gameplay", "level up", "open world", "multiplayer", "mini-camp"),
    "map": ("map", "fortnite map", "uefn", "zone wars", "island"),
    "book": ("book", "ebook", "cookbook", "chapters", "manuscript"),
    "guide": ("guide", "playbook", "manual", "training guide", "field guide"),
    "offer": ("offer", "service", "agency", "consulting", "done-for-you", "package"),
    "internal system": ("internal system", "internal tool", "back office", "team process", "operating system"),
    "saas/product launch": ("saas", "software", "launch", "product launch", "mvp", "beta"),
    "operations workflow": ("workflow", "process", "ops", "handoff", "automation", "standard operating procedure"),
}


CHALLENGE_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("product build", ("build", "app", "platform", "tool", "software")),
    ("growth launch", ("launch", "grow", "audience", "marketing", "sales")),
    ("operations system", ("process", "workflow", "automation", "team")),
    ("knowledge engine", ("research", "knowledge", "library", "assistant")),
    ("service offer", ("agency", "service", "consulting", "delivery")),
)


TEMPLATE_LIBRARY: dict[str, dict[str, object]] = {
    "product-launch": {
        "name": "Product Launch",
        "fit": "Best for apps, tools, SaaS ideas, and digital products.",
        "use_case": "Turn a named concept into a launch-ready product plan.",
        "outputs": ["product scope", "feature stack", "launch plan", "agent workflow"],
        "tags": ("saas", "automation", "ecommerce", "data"),
    },
    "service-offer": {
        "name": "Service Offer",
        "fit": "Best for agencies, consulting offers, and done-for-you services.",
        "use_case": "Package an idea into an offer, fulfillment flow, and sales path.",
        "outputs": ["offer design", "delivery system", "pricing angle", "outreach plan"],
        "tags": ("service", "sales", "operations"),
    },
    "content-engine": {
        "name": "Content Engine",
        "fit": "Best for media, personal brands, newsletters, and educational ideas.",
        "use_case": "Build a repeatable engine for creation, publishing, and growth.",
        "outputs": ["content plan", "production workflow", "distribution plan", "agent roles"],
        "tags": ("content", "creative", "education"),
    },
    "ops-system": {
        "name": "Operations System",
        "fit": "Best for internal workflows, automation layers, and team operating systems.",
        "use_case": "Convert a rough process idea into a repeatable operating model.",
        "outputs": ["workflow map", "automation plan", "handoff rules", "measurement loop"],
        "tags": ("operations", "automation", "data"),
    },
}


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def contains_phrase(haystack: str, phrase: str) -> bool:
    normalized_haystack = normalize_text(haystack).lower()
    normalized_phrase = normalize_text(phrase).lower()
    pattern = r"\b" + re.escape(normalized_phrase).replace(r"\ ", r"\s+") + r"\b"
    return re.search(pattern, normalized_haystack) is not None


def title_case_phrase(prompt: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", prompt)
    if not words:
        return "WordUp Mission"
    preview = " ".join(words[:6]).title()
    return preview[:64]


def effective_prompt(request: AgentSlateRequest) -> str:
    pieces = [
        normalize_text(request.product_name),
        normalize_text(request.idea_name),
        normalize_text(request.prompt),
    ]
    joined = " ".join(piece for piece in pieces if piece)
    return normalize_text(joined)


def effective_product_name(request: AgentSlateRequest, prompt_text: str) -> str:
    if normalize_text(request.product_name):
        return normalize_text(request.product_name)
    return title_case_phrase(prompt_text)


def effective_idea_name(request: AgentSlateRequest, prompt_text: str) -> str:
    if normalize_text(request.idea_name):
        return normalize_text(request.idea_name)
    if normalize_text(request.product_name):
        return normalize_text(request.product_name)
    return title_case_phrase(prompt_text)


def infer_domain_tags(prompt: str) -> list[str]:
    haystack = normalize_text(prompt).lower()
    matches = [tag for tag, keywords in DOMAIN_KEYWORDS.items() if any(contains_phrase(haystack, word) for word in keywords)]
    return matches or ["general"]


def infer_idea_types(prompt: str) -> list[str]:
    haystack = normalize_text(prompt).lower()
    scored: list[tuple[int, str]] = []
    for idea_type, keywords in IDEA_TYPE_KEYWORDS.items():
        score = sum(1 for keyword in keywords if contains_phrase(haystack, keyword))
        if score:
            scored.append((score, idea_type))

    if not scored:
        return ["general concept"]

    scored.sort(key=lambda item: (-item[0], item[1]))
    return [idea_type for _, idea_type in scored[:3]]


def infer_challenge_type(prompt: str) -> str:
    haystack = normalize_text(prompt).lower()
    for label, keywords in CHALLENGE_PATTERNS:
        if any(contains_phrase(haystack, word) for word in keywords):
            return label
    return "general venture"


def make_summary(prompt: str) -> str:
    clean = normalize_text(prompt)
    return shorten(clean or "Build a new idea with WordUp.", width=180, placeholder="...")


def article_for(word: str) -> str:
    return "an" if word[:1].lower() in {"a", "e", "i", "o", "u"} else "a"


def make_outcome(tags: list[str], product_name: str) -> str:
    focus = tags[0] if tags else "general"
    article = article_for(focus)
    return f"Ship a usable first version of {product_name} as {article} {focus}-oriented concept with a clear path from prompt to execution."


def detect_inputs(prompt_text: str, idea_name: str) -> list[str]:
    haystack = normalize_text(f"{prompt_text} {idea_name}").lower()
    phrase_candidates = [
        "app",
        "game",
        "map",
        "book",
        "guide",
        "offer",
        "internal system",
        "operations workflow",
        "saas",
        "cookbook",
        "recipes",
        "recipe",
        "chapter sections",
        "chapters",
        "launch plan",
        "digital product",
        "service offer",
        "fortnite map",
        "fortnite",
        "island",
        "workflow",
        "automation",
        "audience",
        "brand",
        "course",
        "newsletter",
        "community",
        "dashboard",
        "content",
        "sales",
    ]
    matches = [phrase for phrase in phrase_candidates if contains_phrase(haystack, phrase)]
    if matches:
        return matches[:6]

    fallback_words = re.findall(r"[A-Za-z][A-Za-z\-]{3,}", haystack)
    stop_words = {
        "build",
        "with",
        "that",
        "this",
        "from",
        "into",
        "your",
        "idea",
        "product",
        "name",
        "prompt",
        "create",
        "make",
        "would",
        "could",
        "should",
    }
    detected: list[str] = []
    for word in fallback_words:
        if word in stop_words or word in detected:
            continue
        detected.append(word)
        if len(detected) == 6:
            break
    return detected or ["general concept"]


def template_score(tags: list[str], template_key: str) -> int:
    library_tags = TEMPLATE_LIBRARY[template_key]["tags"]
    return sum(1 for tag in tags if tag in library_tags)


def idea_type_template_score(idea_types: list[str], template_key: str) -> int:
    weights = {
        "product-launch": {"app", "game", "map", "saas/product launch"},
        "service-offer": {"offer"},
        "content-engine": {"book", "guide"},
        "ops-system": {"internal system", "operations workflow"},
    }
    relevant_types = weights.get(template_key, set())
    return sum(2 for idea_type in idea_types if idea_type in relevant_types)


def build_template_options(tags: list[str], idea_types: list[str], forced_choice: str | None) -> list[TemplateOption]:
    options: list[tuple[int, str, TemplateOption]] = []
    normalized_choice = normalize_text(forced_choice or "").lower()
    for key, template in TEMPLATE_LIBRARY.items():
        recommended = False
        score = template_score(tags, key) + idea_type_template_score(idea_types, key)
        if normalized_choice and normalized_choice == key:
            score += 100
            recommended = True
        option = TemplateOption(
            key=key,
            name=str(template["name"]),
            fit=str(template["fit"]),
            use_case=str(template["use_case"]),
            outputs=list(template["outputs"]),
            recommended=recommended,
        )
        options.append((score, key, option))

    options.sort(key=lambda item: (-item[0], item[1]))
    if options and not any(item[2].recommended for item in options):
        top_score = options[0][0]
        options[0][2].recommended = True
        if top_score == 0 and len(options) > 1:
            options[1][2].recommended = False
    return [item[2] for item in options[:3]]


def choose_roles(tags: list[str], max_agents: int) -> list[str]:
    roles = ["orchestrator", "researcher", "strategist", "architect", "builder", "qa"]

    if any(tag in tags for tag in ("creative", "content", "ecommerce")):
        roles.append("designer")
    if any(tag in tags for tag in ("sales", "service", "ecommerce")):
        roles.append("growth")
    if any(tag in tags for tag in ("automation", "operations", "service")):
        roles.append("operator")
    if "data" in tags:
        roles.append("analyst")
    if any(tag in tags for tag in ("saas", "automation", "data")):
        roles.append("deployer")

    deduped: list[str] = []
    for role in roles:
        if role not in deduped:
            deduped.append(role)
    return deduped[:max_agents]


def kickoff_task_for(role: str, brief: MissionBrief, selected_template: str) -> str:
    action_map = {
        "orchestrator": f"Turn the prompt into a scoped WordUp mission for {brief.title} using the {selected_template} template.",
        "researcher": "List assumptions, gaps, audience context, and references needed before building.",
        "strategist": "Define the offer, audience, milestones, and fastest path to traction.",
        "architect": "Sketch the system shape, inputs, outputs, and integration boundaries.",
        "builder": "Produce the first implementation slice or packaged output that proves the idea can work.",
        "designer": "Shape the user journey and tone so the first version feels intentional.",
        "analyst": "Define the KPI model and feedback loops for early validation.",
        "operator": "Create the repeatable workflow, ownership model, and execution queue.",
        "qa": "Review the plan for risks, missing validation, and release blockers.",
        "growth": "Plan demand capture, messaging, and channel experiments for the first launch.",
        "deployer": "Prepare the launch checklist, environment setup, and post-release monitoring steps.",
    }
    return action_map.get(role, "Move the mission forward with a concrete deliverable.")


def build_team(brief: MissionBrief, max_agents: int, selected_template: str) -> list[AgentCard]:
    roles = choose_roles(brief.domain_tags, max_agents)
    team: list[AgentCard] = []
    for role in roles:
        blueprint: AgentBlueprint = ROLE_INDEX[role]
        team.append(
            AgentCard(
                role=blueprint.role,
                title=blueprint.title,
                purpose=blueprint.purpose,
                skills=list(blueprint.skills),
                system_prompt=blueprint.system_prompt,
                kickoff_task=kickoff_task_for(role, brief, selected_template),
                expected_output=blueprint.default_output,
            )
        )
    return team


def build_workflow(team: list[AgentCard], selected_template: str) -> list[WorkflowStep]:
    workflow: list[WorkflowStep] = []
    previous_step: int | None = None
    for index, agent in enumerate(team, start=1):
        depends_on = [previous_step] if previous_step else []
        workflow.append(
            WorkflowStep(
                step=index,
                owner=agent.role,
                action=agent.kickoff_task,
                deliverable=f"{selected_template}: {agent.expected_output}",
                depends_on=depends_on,
            )
        )
        previous_step = index
    return workflow


def build_execution(workflow: list[WorkflowStep], execution_mode: str) -> list[ExecutionEvent]:
    events: list[ExecutionEvent] = []
    for step in workflow:
        if execution_mode == "plan":
            status = "queued"
            note = "Planned but not executed."
        elif step.step == 1:
            status = "done"
            note = "WordUp initialized the mission from the submitted idea."
        elif step.step == 2:
            status = "active"
            note = "Current focus in the simulated run."
        else:
            status = "queued"
            note = "Waiting on upstream deliverables."
        events.append(
            ExecutionEvent(
                stage=f"Step {step.step}",
                owner=step.owner,
                status=status,
                note=note,
            )
        )
    return events


def first_recommended_template(options: list[TemplateOption]) -> TemplateOption:
    for option in options:
        if option.recommended:
            return option
    return options[0]


def build_scope_from_template(template_key: str) -> list[str]:
    if template_key == "product-launch":
        return ["Clarify core user problem", "Define MVP features", "Map user flow", "Prepare launch checklist"]
    if template_key == "service-offer":
        return ["Define offer promise", "Package delivery workflow", "Draft pricing angle", "Outline lead capture flow"]
    if template_key == "content-engine":
        return ["Choose content pillars", "Map production cadence", "Design distribution loop", "Assign specialist roles"]
    return ["Map workflow stages", "Identify automation points", "Define ownership handoffs", "Set measurement checkpoints"]


def format_detected_inputs(detected_inputs: list[str]) -> str:
    return ", ".join(detected_inputs[:3])


def build_scope(product_name: str, idea_name: str, selected_option: TemplateOption, detected_inputs: list[str]) -> list[str]:
    focus = format_detected_inputs(detected_inputs)
    if selected_option.key == "product-launch":
        return [
            f"Define the core promise for {product_name}",
            f"Outline the main feature or section set around {focus}",
            "Map the user or customer journey from first touch to delivery",
            "Prepare the launch checklist using only stated requirements",
        ]
    if selected_option.key == "service-offer":
        return [
            f"Define the client-facing promise for {product_name}",
            f"Package the delivery flow around {focus}",
            "Draft pricing and positioning without inventing unsupported claims",
            "Outline lead capture and fulfillment handoffs",
        ]
    if selected_option.key == "content-engine":
        return [
            f"Define the core themes for {idea_name or product_name}",
            f"Outline the main content sections around {focus}",
            "Create the production and review workflow",
            "Plan distribution based on the channels explicitly mentioned",
        ]
    return [
        f"Map the operating flow for {product_name}",
        f"Identify automation or handoff points tied to {focus}",
        "Define owner responsibilities and review checkpoints",
        "Set a measurement loop from the stated goals",
    ]


def build_output_packet(
    product_name: str,
    idea_name: str,
    selected_option: TemplateOption,
    brief: MissionBrief,
) -> BuildOutput:
    detected_inputs = detect_inputs(brief.summary, idea_name)
    focus = format_detected_inputs(detected_inputs)

    if selected_option.key == "service-offer":
        offer = f"{product_name} packages {idea_name} into a structured offer centered on {focus}."
        first_deliverable = f"A service blueprint covering {focus}, delivery steps, and launch language."
    elif selected_option.key == "content-engine":
        offer = f"{product_name} turns {idea_name} into a structured content system built around {focus}."
        first_deliverable = f"A content blueprint with sections, workflow, and launch guidance grounded in {focus}."
    elif selected_option.key == "ops-system":
        offer = f"{product_name} turns {idea_name} into an execution system organized around {focus}."
        first_deliverable = f"An operations map covering {focus}, handoffs, and review checkpoints."
    else:
        offer = f"{product_name} turns {idea_name} into a launch-ready concept built around {focus}."
        first_deliverable = f"An MVP blueprint covering {focus}, core structure, and release steps."

    positioning = (
        f"{product_name} is a WordUp-built concept based on detected inputs from your prompt: {', '.join(detected_inputs)}."
    )
    output_summary = (
        f"Recommended template: {selected_option.name}. WordUp classified this as {brief.primary_idea_type} and is grounding the build in the terms you supplied: {', '.join(detected_inputs)}."
    )

    return BuildOutput(
        product_name=product_name,
        idea_name=idea_name,
        selected_template=selected_option.name,
        detected_inputs=detected_inputs,
        positioning=positioning,
        offer=offer,
        build_scope=build_scope(product_name, idea_name, selected_option, detected_inputs),
        first_deliverable=first_deliverable,
        output_summary=output_summary,
    )


def build_next_prompt(brief: MissionBrief, team: list[AgentCard], selected_template: str, output: BuildOutput) -> str:
    roles = ", ".join(agent.role for agent in team)
    return (
        f"Use WordUp with the {selected_template} template for {output.product_name}. "
        f"Team: {roles}. Build around this outcome: {brief.outcome} "
        f"First deliverable: {output.first_deliverable}"
    )


def build_git_note(brief: MissionBrief) -> str:
    return f"Git handoff: after WordUp starts work for {brief.title}, create a focused commit and push the branch so the build has a shareable checkpoint."


def create_mission_brief(request: AgentSlateRequest) -> MissionBrief:
    prompt_text = effective_prompt(request)
    product_name = effective_product_name(request, prompt_text)
    tags = infer_domain_tags(prompt_text)
    idea_types = infer_idea_types(prompt_text)
    return MissionBrief(
        title=product_name,
        summary=make_summary(prompt_text),
        outcome=make_outcome(tags, product_name),
        primary_idea_type=idea_types[0],
        idea_types=idea_types,
        challenge_type=infer_challenge_type(prompt_text),
        domain_tags=tags,
        constraints=request.constraints,
        goals=request.goals,
    )


def launch_agent_slate(request: AgentSlateRequest) -> AgentSlateResponse:
    prompt_text = effective_prompt(request)
    brief = create_mission_brief(request)
    product_name = effective_product_name(request, prompt_text)
    idea_name = effective_idea_name(request, prompt_text)
    template_options = build_template_options(brief.domain_tags, brief.idea_types, request.template_choice)
    selected_option = first_recommended_template(template_options)
    team = build_team(brief, request.max_agents, selected_option.name)
    workflow = build_workflow(team, selected_option.name)
    execution = build_execution(workflow, request.execution_mode)
    output = build_output_packet(product_name, idea_name, selected_option, brief)
    return AgentSlateResponse(
        mission=brief,
        template_options=template_options,
        team=team,
        workflow=workflow,
        execution=execution,
        output=output,
        next_prompt=build_next_prompt(brief, team, selected_option.name, output),
        git_note=build_git_note(brief),
    )
