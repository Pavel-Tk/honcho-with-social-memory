"""
Minimal prompts for the deriver module optimized for speed.

This module contains simplified prompt templates focused only on observation extraction.
NO peer card instructions, NO working representation - just extract observations.
"""

from functools import cache
from inspect import cleandoc as c

from src.utils.tokens import estimate_tokens


def _normalized_custom_instructions(custom_instructions: str | None) -> str | None:
    """Return stripped custom instructions, if any."""
    if custom_instructions is None:
        return None

    normalized = custom_instructions.strip()
    return normalized or None


def _custom_instructions_section(custom_instructions: str | None) -> str:
    """Render optional custom instructions for the deriver prompt."""
    normalized_custom_instructions = _normalized_custom_instructions(
        custom_instructions
    )
    if normalized_custom_instructions is None:
        return ""

    return c(
        f"""
        CUSTOM INSTRUCTIONS:
        {normalized_custom_instructions}
        """
    )


def minimal_deriver_prompt(
    peer_id: str,
    messages: str,
    custom_instructions: str | None = None,
) -> str:
    """
    Generate minimal prompt for fast observation extraction.

    Args:
        peer_id: The ID of the user being analyzed.
        messages: All messages in the range (interleaving messages and new turns combined).

    Returns:
        Formatted prompt string for observation extraction.
    """
    custom_instructions_section = _custom_instructions_section(custom_instructions)
    return c(
        f"""
Analyze messages from {peer_id} to extract **explicit atomic facts** about them, including social-brain facts.

[EXPLICIT] DEFINITION: Facts about {peer_id} that can be derived directly from their messages.
   - Transform statements into one or multiple conclusions
   - Each conclusion must be self-contained with enough context
   - Use absolute dates/times when possible (e.g. "June 26, 2025" not "yesterday")

[SOCIAL-BRAIN] DEFINITION: Explicit facts about identities, preferences, goals, emotions, intentions, beliefs, commitments, roles, relationships, trust/affinity/conflict, and group context.
   - Use social_category when a conclusion fits one of these categories: identity, preference, relationship, emotion, intention, belief, commitment, role, trust, conflict, group_context, other.
   - Use subject for who/what the observation is about, object for the other peer/entity involved, relation_type for the social edge, confidence for high/medium/low certainty, and perspective for theory-of-mind qualifiers.
   - Preserve perspective: if {peer_id} reports or believes something about someone else, state it as {peer_id}'s report/belief, not as objective truth about the other person.

RULES:
- Properly attribute observations to the correct subject: if it is about {peer_id}, say so. If {peer_id} is referencing someone or something else, make that clear.
- Observations should make sense on their own. Each observation will be used in the future to better understand {peer_id}.
- Extract ALL observations from {peer_id} messages, using others as context.
- Contextualize each observation sufficiently (e.g. "Ann is nervous about the job interview at the pharmacy" not just "Ann is nervous")
- Do not overstate social facts: use "{peer_id} believes/reported/perceived..." when the message only provides {peer_id}'s perspective.
- Do not infer hidden motives, emotions, or relationships unless directly supported by the message text.

EXAMPLES:
- EXPLICIT: "I just had my 25th birthday last Saturday" → "{peer_id} is 25 years old", "{peer_id}'s birthday is June 21st"
- EXPLICIT: "I took my dog for a walk in NYC" → "{peer_id} has a dog", "{peer_id} lives in NYC"
- EXPLICIT: "{peer_id} attended college" + general knowledge → "{peer_id} completed high school or equivalent"
- SOCIAL-BRAIN: "Bob is my manager and I trust him with launches" → "Bob is {peer_id}'s manager" (social_category=relationship, object=Bob, relation_type=manager), "{peer_id} trusts Bob with launches" (social_category=trust, object=Bob, relation_type=trusts)
- SOCIAL-BRAIN: "I think Dana is upset with me" → "{peer_id} believes Dana may be upset with them" (social_category=belief, object=Dana, confidence=low, perspective="{peer_id} believes")
- SOCIAL-BRAIN: "Remind me to send Priya the contract Friday" → "{peer_id} intends to send Priya the contract on Friday" (social_category=commitment, object=Priya, relation_type=send_contract)

{custom_instructions_section}

Messages to analyze:
<messages>
{messages}
</messages>
"""
    )


@cache
def estimate_minimal_deriver_prompt_tokens() -> int:
    """Estimate the static minimal deriver prompt without custom instructions."""
    prompt = minimal_deriver_prompt(
        peer_id="",
        messages="",
        custom_instructions=None,
    )
    return estimate_tokens(prompt)


def estimate_deriver_prompt_tokens(custom_instructions: str | None) -> int:
    """Estimate minimal deriver prompt tokens, including custom instructions if present."""
    normalized_custom_instructions = _normalized_custom_instructions(
        custom_instructions
    )
    if normalized_custom_instructions is None:
        return estimate_minimal_deriver_prompt_tokens()

    prompt = minimal_deriver_prompt(
        peer_id="",
        messages="",
        custom_instructions=normalized_custom_instructions,
    )
    return estimate_tokens(prompt)
