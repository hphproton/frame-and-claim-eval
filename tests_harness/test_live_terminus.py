"""The live Terminus class must complete one model turn.

`make test-harness` uses system Python, which does not have Harbor. This file
skips there. With the venv from `make setup`, it builds a LiveTerminus and asks
it for one turn. Before the fix that raised TypeError, because the method was
copied from ScriptedTerminus and its zero-arg super() is not valid for a
LiveTerminus. After the fix the same call returns the parent turn.
"""
import asyncio, pathlib, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))


def test_live_terminus_returns_the_model_turn():
    from harbor.agents.terminus_2.terminus_2 import Terminus2
    from harbor.llms.base import LLMResponse
    from harness.terminus_runner import LiveTerminus

    logs = pathlib.Path(tempfile.mkdtemp())
    agent = LiveTerminus(
        logs_dir=logs,
        model_name="openai/live-smoke",
        api_base="http://127.0.0.1:9/v1",
        llm_kwargs={"api_key": "local-smoke"},
        max_turns=2,
        enable_summarize=False,
        proactive_summarization_threshold=0,
        record_terminal_session=False,
        suppress_max_turns_warning=True,
        temperature=0,
    )
    seen = {}

    async def parent_turn(self, *args, **kwargs):
        seen["self_type"] = type(self).__name__
        return ([], True, "", "analysis", "plan", LLMResponse(content="{}"))

    async def parent_exec(self, commands, session):
        seen["exec"] = [command.keystrokes for command in commands]
        return False, "ran"

    saved = (Terminus2._handle_llm_interaction, Terminus2._execute_commands)
    Terminus2._handle_llm_interaction = parent_turn
    Terminus2._execute_commands = parent_exec
    try:
        turn = asyncio.run(agent._handle_llm_interaction(None, "prompt"))
        assert turn[1] is True and turn[3] == "analysis", turn
        assert seen.get("self_type") == "LiveTerminus", seen

        class Command:
            keystrokes = "true\n"
            duration_sec = 0.1

        ran = asyncio.run(agent._execute_commands([Command()], None))
        assert ran == (False, "ran"), ran
        assert seen.get("exec") == ["true\n"]
    finally:
        Terminus2._handle_llm_interaction, Terminus2._execute_commands = saved


if __name__ == "__main__":
    try:
        import harbor  # noqa: F401
    except ModuleNotFoundError:
        print("live terminus checks: SKIP (harbor is not installed)")
        raise SystemExit(0)
    test_live_terminus_returns_the_model_turn()
    print("live terminus checks: OK")
