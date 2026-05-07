from fastapi.testclient import TestClient

from agent_slate.app import app


client = TestClient(app)


def test_catalog_has_core_roles() -> None:
    response = client.get("/api/wordup/catalog")
    assert response.status_code == 200
    roles = {item["role"] for item in response.json()}
    assert {"orchestrator", "builder", "qa"}.issubset(roles)


def test_launch_builds_team_and_workflow() -> None:
    response = client.post(
        "/api/wordup/launch",
        json={
            "product_name": "WordUp",
            "idea_name": "Founder launch builder",
            "prompt": "Build a productized service that turns founder ideas into launch plans with agents.",
            "template_choice": "service-offer",
            "constraints": ["Keep it lean"],
            "goals": ["Generate a runnable team"],
            "max_agents": 6,
            "execution_mode": "simulate",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["mission"]["challenge_type"] in {
        "product build",
        "growth launch",
        "operations system",
        "service offer",
        "general venture",
    }
    assert payload["mission"]["title"] == "WordUp"
    assert payload["mission"]["primary_idea_type"] == "offer"
    assert "offer" in payload["mission"]["idea_types"]
    assert len(payload["template_options"]) == 3
    assert payload["template_options"][0]["recommended"] is True
    assert len(payload["team"]) >= 4
    assert len(payload["workflow"]) == len(payload["team"])
    assert payload["execution"][0]["status"] == "done"
    assert "WordUp" in payload["next_prompt"]
    assert payload["output"]["product_name"] == "WordUp"
    assert payload["output"]["selected_template"] == "Service Offer"
    assert "commit" in payload["git_note"].lower()
    assert "push" in payload["git_note"].lower()


def test_ui_page_renders() -> None:
    response = client.get("/wordup")
    assert response.status_code == 200
    assert "Run WordFlow" in response.text
    assert "Input" in response.text
    assert "Logic" in response.text
    assert "Automation" in response.text
    assert "Output" in response.text
    assert "Built Artifact" in response.text


def test_broad_idea_type_classification_stays_grounded() -> None:
    cases = [
        (
            {
                "product_name": "Pocket Coach",
                "idea_name": "Golf improvement guide",
                "prompt": "Create a beginner golf guide with drills, lessons, and a printable practice plan.",
            },
            "guide",
            "Content Engine",
            "guide",
        ),
        (
            {
                "product_name": "Gridiron Rise",
                "idea_name": "Open world football game",
                "prompt": "Build an open world 3D football game with progression, mini-camp tryouts, and online buzz.",
            },
            "game",
            "Product Launch",
            "game",
        ),
        (
            {
                "product_name": "City Clash",
                "idea_name": "Fortnite map",
                "prompt": "Create a Fortnite map with custom island rules, progression, and replayable rounds.",
            },
            "map",
            "Product Launch",
            "map",
        ),
        (
            {
                "product_name": "Ops Spine",
                "idea_name": "Internal workflow",
                "prompt": "Build an internal system for team handoffs, approvals, and operations workflow automation.",
            },
            "operations workflow",
            "Operations System",
            "workflow",
        ),
        (
            {
                "product_name": "Midnight Kitchen",
                "idea_name": "Comfort food cookbook",
                "prompt": "Build a cookbook with recipes, kitchen storytelling, chapter sections, and a launch plan.",
            },
            "book",
            "Content Engine",
            "cookbook",
        ),
    ]

    for request, expected_type, expected_template, expected_term in cases:
        response = client.post(
            "/api/wordup/launch",
            json={**request, "max_agents": 6, "execution_mode": "simulate"},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["mission"]["primary_idea_type"] == expected_type
        assert payload["output"]["selected_template"] == expected_template
        assert expected_term in " ".join(payload["output"]["detected_inputs"]).lower()
        assert "detected inputs" in payload["output"]["positioning"].lower()
