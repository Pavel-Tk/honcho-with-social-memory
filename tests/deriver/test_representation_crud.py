import datetime
from typing import cast

from src import models
from src.utils.representation import (
    DeductiveObservation,
    ExplicitObservation,
    ExplicitObservationBase,
    PromptRepresentation,
    Representation,
)


def test_representation_is_empty_and_diff():
    """is_empty and diff_representation behave per the new definitions."""
    now = datetime.datetime.now(datetime.timezone.utc)
    shared_time = now - datetime.timedelta(seconds=10)
    exp_shared_1 = ExplicitObservation(
        content="A",
        created_at=shared_time,
        message_ids=[1],
        session_name="s",
    )
    exp_shared_2 = ExplicitObservation(
        content="B",
        created_at=shared_time,
        message_ids=[1],
        session_name="s",
    )
    rep1 = Representation(explicit=[exp_shared_1], deductive=[])
    rep2 = Representation(
        explicit=[
            ExplicitObservation(
                content="A",
                created_at=shared_time,
                message_ids=[1],
                session_name="s",
            ),
            exp_shared_2,
        ]
    )

    assert not rep1.is_empty()
    assert Representation().is_empty()

    diff = rep1.diff_representation(rep2)
    assert [e.content for e in diff.explicit] == ["B"]
    assert diff.deductive == []


def test_representation_formatting_methods():
    """__str__ and format_as_markdown produce expected section headers and content."""
    now = datetime.datetime.now(datetime.timezone.utc)
    e = ExplicitObservation(
        content="has a dog",
        created_at=now,
        message_ids=[1],
        session_name="s",
    )
    d = DeductiveObservation(
        created_at=now,
        message_ids=[1],
        session_name="s",
        conclusion="owns a pet",
        premises=[e.content],
    )
    rep = Representation(explicit=[e], deductive=[d])

    s = str(rep)
    assert "EXPLICIT:" in s
    assert "DEDUCTIVE:" in s
    assert "owns a pet" in s

    md = rep.format_as_markdown()
    assert "## Explicit Observations" in md
    assert "## Deductive Observations" in md
    assert "owns a pet" in md
    assert "Premises:" in md


def test_prompt_representation_conversion():
    """PromptRepresentation.to_representation maps strings to observation objects.

    Note: In the current architecture, the Deriver only creates explicit observations.
    Deductive and inductive observations are created by the Dreamer agent.
    Therefore, from_prompt_representation only converts explicit observations.
    """
    pr = PromptRepresentation(
        explicit=[ExplicitObservationBase(content="A")],
        # Deductive observations in PromptRepresentation are ignored by from_prompt_representation
        # because the Deriver only produces explicit observations
        # deductive=[
        #     DeductiveObservationBase(
        #         conclusion="C", premises=["P1"], source_ids=["id1"]
        #     )
        # ],
    )
    timestamp = datetime.datetime(2025, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    rep = Representation.from_prompt_representation(
        pr,
        message_ids=[1],
        session_name="s",
        created_at=timestamp,
    )
    assert isinstance(rep, Representation)
    assert [e.content for e in rep.explicit] == ["A"]
    # Deductive observations from PromptRepresentation are not converted
    # (they would be created directly by the Dreamer via the create_observations tool)
    assert len(rep.deductive) == 0
    assert rep.explicit[0].created_at == timestamp


def test_social_memory_fields_survive_prompt_conversion_and_markdown():
    """Social-brain metadata from structured Deriver output is preserved."""
    pr = PromptRepresentation(
        explicit=[
            ExplicitObservationBase(
                content="Alice trusts Bob with launch planning",
                social_category="trust",
                subject="Alice",
                object="Bob",
                relation_type="trusts",
                confidence="high",
                perspective="Alice stated",
            )
        ]
    )
    timestamp = datetime.datetime(2025, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)

    rep = Representation.from_prompt_representation(
        pr,
        message_ids=[1],
        session_name="s",
        created_at=timestamp,
    )

    obs = rep.explicit[0]
    assert obs.social_category == "trust"
    assert obs.subject == "Alice"
    assert obs.object == "Bob"
    assert obs.relation_type == "trusts"
    assert obs.confidence == "high"
    assert obs.perspective == "Alice stated"
    assert obs.social_metadata() == {
        "social_category": "trust",
        "subject": "Alice",
        "object": "Bob",
        "relation_type": "trusts",
        "confidence": "high",
        "perspective": "Alice stated",
    }

    md = rep.format_as_markdown()
    assert "category=trust" in md
    assert "relation=trusts" in md
    assert "confidence=high" in md


def test_social_memory_fields_survive_document_conversion():
    """Stored document metadata hydrates social-brain fields on explicit observations."""
    timestamp = datetime.datetime(2025, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)

    class DocumentStub:
        id: str = "doc_social"
        created_at: datetime.datetime = timestamp
        content: str = "Alice believes Dana may be upset with them"
        level: str = "explicit"
        session_name: str = "s"
        source_ids: list[str] | None = None
        internal_metadata: dict[str, object] = {
            "message_ids": [1],
            "message_created_at": "2025-01-01T12:00:00+00:00",
            "social_category": "belief",
            "subject": "Alice",
            "object": "Dana",
            "relation_type": "believes",
            "confidence": "low",
            "perspective": "Alice believes",
        }

    rep = Representation.from_documents(cast("list[models.Document]", [DocumentStub()]))

    obs = rep.explicit[0]
    assert obs.social_category == "belief"
    assert obs.subject == "Alice"
    assert obs.object == "Dana"
    assert obs.relation_type == "believes"
    assert obs.confidence == "low"
    assert obs.perspective == "Alice believes"
