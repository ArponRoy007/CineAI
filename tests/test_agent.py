from types import SimpleNamespace

from ai.agent import (
    AGENT_SYSTEM_PROMPT,
    FALLBACK_ANSWER,
    answer_with_agent,
    filter_by_rating,
    filter_by_verdict,
    general_semantic_search,
    retrieve_review,
    search_movies,
    select_initial_tool,
)
from rag.prompts import SYSTEM_PROMPT


class Cursor(list):
    def limit(self, _count):
        return self

    def sort(self, _order):
        return self


class Movies:
    def find(self, _query, _projection):
        return Cursor([{"movie_id": "darr", "title": "Darr", "review_status": "CONFIRMED", "roy_rating": 5.0}])

    def find_one(self, _query, _projection):
        return {"movie_id": "darr", "title": "Darr", "review_status": "CONFIRMED"}


def test_agent_tool_selection_routes_structured_questions():
    assert select_initial_tool("Which movies are Must Watch?") == "filter_by_verdict"
    assert select_initial_tool("Which movies are rated 4 or higher?") == "filter_by_rating"
    assert select_initial_tool("Search Darr") == "search_movies"
    assert select_initial_tool("Why did Roy like Darr?") == "general_semantic_search"


def test_agent_prompt_preserves_existing_grounding_rules_verbatim():
    assert SYSTEM_PROMPT in AGENT_SYSTEM_PROMPT
    normalized = " ".join(AGENT_SYSTEM_PROMPT.lower().split())
    assert "if a tool call fails or returns nothing, say so instead of guessing" in normalized


def test_mongodb_tools_return_structured_grounded_results(monkeypatch):
    import ai.agent as agent

    monkeypatch.setattr(agent, "movies_collection", Movies())
    assert search_movies("Darr")["data"][0]["title"] == "Darr"
    assert filter_by_verdict("Must Watch")["data"][0]["movie_id"] == "darr"
    assert filter_by_rating(4)["data"][0]["roy_rating"] == 5.0
    assert filter_by_verdict("Excellent")["error"]


def test_rag_tools_return_context_and_sources(monkeypatch):
    import ai.agent as agent

    monkeypatch.setattr(agent, "movies_collection", Movies())
    monkeypatch.setattr(agent, "build_context", lambda **_kwargs: ("Movie: Darr\nRoy's Review: Memorable.", [{"metadata": {"title": "Darr"}}]))
    assert retrieve_review("darr", "Why?")["sources"][0]["metadata"]["title"] == "Darr"
    assert general_semantic_search("Why?")["data"]["context"].startswith("Movie: Darr")


class FakeCompletions:
    def __init__(self, messages):
        self.messages = iter(messages)

    def create(self, **_kwargs):
        return SimpleNamespace(choices=[SimpleNamespace(message=next(self.messages))])


class FakeClient:
    def __init__(self, messages):
        self.chat = SimpleNamespace(completions=FakeCompletions(messages))


def _tool_message(name, arguments, call_id="call-1"):
    call = SimpleNamespace(id=call_id, function=SimpleNamespace(name=name, arguments=arguments))
    return SimpleNamespace(tool_calls=[call], content=None)


def _final_message(content):
    return SimpleNamespace(tool_calls=[], content=content)


def test_agent_executes_selected_tool_and_returns_grounded_answer(monkeypatch):
    import ai.agent as agent

    client = FakeClient([_tool_message("filter_by_verdict", '{"verdict":"Must Watch"}'), _final_message("Roy's confirmed Must Watch movies include Darr.")])
    monkeypatch.setattr(agent, "get_groq_client", lambda: client)
    monkeypatch.setattr(agent, "filter_by_verdict", lambda verdict: {"data": [{"title": "Darr"}], "sources": [], "error": None})
    monkeypatch.setitem(agent.TOOL_FUNCTIONS, "filter_by_verdict", agent.filter_by_verdict)

    result = answer_with_agent("Which movies are Must Watch?")

    assert result["answer"].startswith("Roy's confirmed")
    assert result["tool_calls"][0]["tool"] == "filter_by_verdict"


def test_agent_uses_scoped_retrieve_tool_for_movie_detail_question(monkeypatch):
    import ai.agent as agent

    client = FakeClient([_tool_message("retrieve_review", '{"movie_id":"wrong","question":"Why?"}'), _final_message("Roy calls Darr memorable.")])
    captured = {}

    def retrieve(movie_id, question):
        captured.update(movie_id=movie_id, question=question)
        return {"data": {"context": "Darr memorable"}, "sources": [{"metadata": {"title": "Darr"}}], "error": None}

    monkeypatch.setattr(agent, "get_groq_client", lambda: client)
    monkeypatch.setitem(agent.TOOL_FUNCTIONS, "retrieve_review", retrieve)
    result = answer_with_agent("Why did Roy like it?", movie_id="darr")

    assert captured["movie_id"] == "darr"
    assert result["sources"][0]["metadata"]["title"] == "Darr"


def test_agent_returns_fallback_when_tool_returns_empty(monkeypatch):
    import ai.agent as agent

    client = FakeClient([_tool_message("general_semantic_search", '{"question":"Unknown"}'), _final_message("I will guess anyway.")])
    monkeypatch.setattr(agent, "get_groq_client", lambda: client)
    monkeypatch.setitem(agent.TOOL_FUNCTIONS, "general_semantic_search", lambda question: {"data": [], "sources": [], "error": "No grounded context"})
    assert answer_with_agent("Unknown question")["answer"] == FALLBACK_ANSWER


def test_agent_returns_fallback_when_tool_raises_and_logs_call(monkeypatch, caplog):
    import ai.agent as agent

    client = FakeClient([_tool_message("general_semantic_search", '{"question":"Broken"}'), _final_message("I will guess anyway.")])
    monkeypatch.setattr(agent, "get_groq_client", lambda: client)
    monkeypatch.setitem(agent.TOOL_FUNCTIONS, "general_semantic_search", lambda question: (_ for _ in ()).throw(RuntimeError("down")))

    with caplog.at_level("INFO", logger="royreview.agent"):
        result = answer_with_agent("Broken question")

    assert result["answer"] == FALLBACK_ANSWER
    assert "general_semantic_search" in caplog.text


def test_agent_caps_tool_calls(monkeypatch):
    import ai.agent as agent

    messages = [_tool_message("general_semantic_search", '{"question":"Q"}', f"call-{number}") for number in range(4)]
    client = FakeClient(messages)
    monkeypatch.setattr(agent, "get_groq_client", lambda: client)
    monkeypatch.setitem(agent.TOOL_FUNCTIONS, "general_semantic_search", lambda question: {"data": {"context": "Q"}, "sources": [], "error": None})
    result = answer_with_agent("Q", max_tool_calls=99)

    assert result["answer"] == FALLBACK_ANSWER
    assert len(result["tool_calls"]) == 3
