import re

from prompts.registry import PROMPT_MAPPINGS, get_system_prompt
from prompts.types import Stack


def test_registry_covers_all_stacks():
    stacks = list(Stack.__args__)
    for kind, mapping in PROMPT_MAPPINGS.items():
        for stack in stacks:
            assert stack in mapping, f"{kind} missing stack {stack}"
            prompt = mapping[stack]
            assert isinstance(prompt, str) and prompt.strip()


def test_prompts_do_not_contain_fenced_code_blocks():
    stacks = list(Stack.__args__)
    fenced = re.compile(r"(?m)^```")
    for kind in PROMPT_MAPPINGS.keys():
        for stack in stacks:
            prompt = get_system_prompt(kind, stack)  # type: ignore[arg-type]
            assert fenced.search(prompt) is None, f"{kind}/{stack} contains fenced block"


def test_svg_stacks_use_svg_tags_in_return_instructions():
    for kind in ("screenshot", "text", "imported_code"):
        prompt = get_system_prompt(kind, "svg")
        assert "<svg>" in prompt and "</svg>" in prompt

