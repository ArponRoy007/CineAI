"""Bounded, grounded tool-calling agent for Ask Roy."""

import json
import logging
import re

from ai.llm import MODEL_NAME, get_groq_client
from rag.prompts import SYSTEM_PROMPT
from rag.retriever import build_context


MAX_TOOL_CALLS = 3

FALLBACK_ANSWER = "I couldn't find that in Roy's movie notes."

LOGGER = logging.getLogger("royreview.agent")

MOVIE_PROJECTION = {
    "_id": 0,
    "movie_id": 1,
    "title": 1,
    "year": 1,
    "genre": 1,
    "zone": 1,
    "roy_rating": 1,
    "verdict": 1,
    "review_text": 1,
}

movies_collection = None


AGENT_SYSTEM_PROMPT = SYSTEM_PROMPT + """

You are the tool-using assistant inside RoyReview.

You may use only the provided RoyReview tools before answering.

Choose the tool that best matches the user's request.

Important rules:

1. Never answer from general movie knowledge.
2. RoyReview tool results are the only source of truth.
3. If the user asks about a specific movie, first find that movie or retrieve
   its confirmed RoyReview review context.
4. If a tool call fails or returns nothing, say so instead of guessing.
5. If the requested information is not present in RoyReview, return exactly:
   "I couldn't find that in Roy's movie notes."
6. Keep answers concise and grounded in the returned review information.
7. Use at most three tool calls.
8. Do not invent ratings, verdicts, reviews, actors, directors, awards,
   box-office information, release facts, or other movie facts.
9. For movie-detail questions, respect the movie scope supplied by the
   application and do not retrieve information from unrelated movies.
"""


def _tool_response(data=None, sources=None, error=None):
    return {
        "data": data or [],
        "sources": sources or [],
        "error": error,
    }


def _movies():
    """Delay Atlas initialization until a Mongo-backed tool is actually used."""
    global movies_collection

    if movies_collection is None:
        from database.mongodb import movies_collection as collection

        movies_collection = collection

    return movies_collection


def search_movies(query):
    """Search confirmed RoyReview movies by title."""

    query = (query or "").strip()

    if not query:
        return _tool_response(
            error="A movie title is required."
        )

    try:
        movies = list(
            _movies()
            .find(
                {
                    "title": {
                        "$regex": re.escape(query),
                        "$options": "i",
                    },
                    "review_status": "CONFIRMED",
                },
                MOVIE_PROJECTION,
            )
            .limit(10)
        )

        return _tool_response(
            data=movies
        )

    except Exception as error:
        return _tool_response(
            error=(
                f"Movie search unavailable: "
                f"{type(error).__name__}"
            )
        )


def filter_by_verdict(verdict):
    """Return confirmed movies for one known verdict."""

    allowed = {
        "Must Watch",
        "Good Watch",
        "Don't Watch",
    }

    if verdict not in allowed:
        return _tool_response(
            error=(
                "Verdict must be Must Watch, Good Watch, "
                "or Don't Watch."
            )
        )

    try:
        movies = list(
            _movies()
            .find(
                {
                    "verdict": verdict,
                    "review_status": "CONFIRMED",
                },
                MOVIE_PROJECTION,
            )
            .sort(
                [
                    ("roy_rating", -1),
                    ("year", -1),
                ]
            )
        )

        return _tool_response(
            data=movies
        )

    except Exception as error:
        return _tool_response(
            error=(
                f"Verdict filter unavailable: "
                f"{type(error).__name__}"
            )
        )


def filter_by_rating(min_rating):
    """Return confirmed movies with Roy's rating at or above a threshold."""

    try:
        minimum = float(min_rating)
    except (TypeError, ValueError):
        return _tool_response(
            error="Minimum rating must be a number from 1 to 5."
        )

    if not 1 <= minimum <= 5:
        return _tool_response(
            error="Minimum rating must be between 1 and 5."
        )

    try:
        movies = list(
            _movies()
            .find(
                {
                    "roy_rating": {
                        "$gte": minimum
                    },
                    "review_status": "CONFIRMED",
                },
                MOVIE_PROJECTION,
            )
            .sort(
                [
                    ("roy_rating", -1),
                    ("year", -1),
                ]
            )
        )

        return _tool_response(
            data=movies
        )

    except Exception as error:
        return _tool_response(
            error=(
                f"Rating filter unavailable: "
                f"{type(error).__name__}"
            )
        )


def retrieve_review(movie_id, question):
    """Retrieve RAG context scoped to one confirmed movie."""

    try:
        movie = _movies().find_one(
            {
                "movie_id": str(movie_id),
                "review_status": "CONFIRMED",
            },
            MOVIE_PROJECTION,
        )

        if not movie:
            return _tool_response(
                error=(
                    "No confirmed RoyReview movie matches "
                    "that identifier."
                )
            )

        context, sources = build_context(
            question=question,
            top_k=5,
            movie_title=movie["title"],
        )

        if not context:
            return _tool_response(
                error=(
                    "No grounded review context was found "
                    "for that movie."
                )
            )

        return _tool_response(
            data={
                "movie": movie,
                "context": context,
            },
            sources=sources,
        )

    except Exception as error:
        return _tool_response(
            error=(
                f"Review retrieval unavailable: "
                f"{type(error).__name__}"
            )
        )


def general_semantic_search(question):
    """Retrieve general grounded RAG context from Roy's review notes."""

    try:
        context, sources = build_context(
            question=question,
            top_k=5,
        )

        if not context:
            return _tool_response(
                error="No grounded review context was found."
            )

        return _tool_response(
            data={
                "context": context
            },
            sources=sources,
        )

    except Exception as error:
        return _tool_response(
            error=(
                f"Semantic search unavailable: "
                f"{type(error).__name__}"
            )
        )


TOOL_FUNCTIONS = {
    "search_movies": search_movies,
    "filter_by_verdict": filter_by_verdict,
    "filter_by_rating": filter_by_rating,
    "retrieve_review": retrieve_review,
    "general_semantic_search": general_semantic_search,
}


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_movies",
            "description": (
                "Search RoyReview movies by title. "
                "Use this when the user wants to find a specific movie."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string"
                    }
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "filter_by_verdict",
            "description": (
                "List confirmed movies with one verdict."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "verdict": {
                        "type": "string",
                        "enum": [
                            "Must Watch",
                            "Good Watch",
                            "Don't Watch",
                        ],
                    }
                },
                "required": ["verdict"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "filter_by_rating",
            "description": (
                "List confirmed movies rated at or above "
                "a threshold."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "min_rating": {
                        "type": "number",
                        "minimum": 1,
                        "maximum": 5,
                    }
                },
                "required": ["min_rating"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_review",
            "description": (
                "Retrieve grounded review context for one "
                "confirmed movie using its movie ID."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "movie_id": {
                        "type": "string"
                    },
                    "question": {
                        "type": "string"
                    },
                },
                "required": [
                    "movie_id",
                    "question",
                ],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "general_semantic_search",
            "description": (
                "Retrieve grounded context when the question "
                "is not a structured movie search."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string"
                    }
                },
                "required": ["question"],
                "additionalProperties": False,
            },
        },
    },
]


def select_initial_tool(question):
    """
    Deterministic routing hint.

    This is retained for compatibility/tests, but the live agent
    does not force this tool_choice. The model is allowed to select
    the appropriate registered tool.
    """

    query = (question or "").lower()

    if (
        "must watch" in query
        or "good watch" in query
        or "don't watch" in query
        or "dont watch" in query
    ):
        return "filter_by_verdict"

    if (
        re.search(
            r"(?:rated|rating|at least|above|higher)\s*(?:a )?"
            r"(?:[1-5](?:\.5)?)",
            query,
        )
        or "5 out of 5" in query
    ):
        return "filter_by_rating"

    if query.startswith(
        (
            "find ",
            "search ",
            "look up ",
        )
    ):
        return "search_movies"

    return "general_semantic_search"


def _log_tool_call(name, arguments, result):
    LOGGER.info(
        "Ask Roy tool call %s",
        json.dumps(
            {
                "tool": name,
                "input": arguments,
                "returned": result,
            },
            default=str,
        ),
    )


def _execute_tool(name, arguments):
    """Execute a registered tool and always log the result."""

    tool = TOOL_FUNCTIONS.get(name)

    if not tool:
        result = _tool_response(
            error=f"Unknown tool: {name}"
        )

    else:
        try:
            result = tool(**arguments)

        except Exception as error:
            result = _tool_response(
                error=(
                    f"Tool execution failed: "
                    f"{type(error).__name__}"
                )
            )

    _log_tool_call(
        name,
        arguments,
        result,
    )

    return result


def _force_movie_scope(call, movie_id, question):
    """
    Enforce movie-detail scope.

    When Ask Roy is opened from a movie detail page,
    retrieval must remain scoped to that movie.
    """

    if not movie_id:
        return call

    name = call.function.name

    if name == "retrieve_review":
        arguments = json.loads(
            call.function.arguments or "{}"
        )

        arguments["movie_id"] = str(movie_id)
        arguments.setdefault(
            "question",
            question,
        )

        return name, arguments

    # If the model attempts an unrelated search while inside
    # a movie-detail page, replace it with the scoped retrieval.
    return (
        "retrieve_review",
        {
            "movie_id": str(movie_id),
            "question": question,
        },
    )


def answer_with_agent(
    question,
    movie_id=None,
    max_tool_calls=MAX_TOOL_CALLS,
):
    """
    Answer one Ask Roy turn with a hard cap on local function calls.
    """

    question = (question or "").strip()

    if not question:
        return {
            "answer": "Please ask a movie question.",
            "sources": [],
            "tool_calls": [],
        }

    max_tool_calls = max(
        1,
        min(
            int(max_tool_calls),
            MAX_TOOL_CALLS,
        ),
    )

    messages = [
        {
            "role": "system",
            "content": AGENT_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": question,
        },
    ]

    executed = []
    sources = []
    had_grounded_result = False

    try:
        client = get_groq_client()

        while len(executed) < max_tool_calls:

            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=TOOL_SCHEMAS,

                # IMPORTANT:
                # Never force a particular tool here.
                # The model can choose the correct registered tool.
                tool_choice="auto",

                parallel_tool_calls=False,
                temperature=0.1,
                max_completion_tokens=400,
            )

            message = response.choices[0].message
            calls = message.tool_calls or []

            # -------------------------------------------------
            # Model produced its final answer
            # -------------------------------------------------
            if not calls:

                answer = (
                    message.content or ""
                ).strip()

                if answer and had_grounded_result:
                    return {
                        "answer": answer,
                        "sources": sources,
                        "tool_calls": executed,
                    }

                return {
                    "answer": FALLBACK_ANSWER,
                    "sources": sources,
                    "tool_calls": executed,
                }

            messages.append(message)

            # -------------------------------------------------
            # Execute tool calls
            # -------------------------------------------------
            for call in calls:

                if len(executed) >= max_tool_calls:
                    return {
                        "answer": FALLBACK_ANSWER,
                        "sources": sources,
                        "tool_calls": executed,
                    }

                try:
                    arguments = json.loads(
                        call.function.arguments or "{}"
                    )

                except json.JSONDecodeError:
                    arguments = {}

                tool_name = call.function.name

                # -------------------------------------------------
                # Movie detail scope
                # -------------------------------------------------
                if movie_id:

                    tool_name, arguments = _force_movie_scope(
                        call,
                        movie_id,
                        question,
                    )

                result = _execute_tool(
                    tool_name,
                    arguments,
                )

                executed.append(
                    {
                        "tool": tool_name,
                        "input": arguments,
                        "returned": result,
                    }
                )

                sources.extend(
                    result.get(
                        "sources",
                        [],
                    )
                )

                if result.get("data"):
                    had_grounded_result = True

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "name": tool_name,
                        "content": json.dumps(
                            result,
                            default=str,
                        ),
                    }
                )

        return {
            "answer": FALLBACK_ANSWER,
            "sources": sources,
            "tool_calls": executed,
        }

    except Exception as error:

        print(
            f"[Ask Roy Agent Error] "
            f"{type(error).__name__}: {error}"
        )

        return {
            "answer": FALLBACK_ANSWER,
            "sources": sources,
            "tool_calls": executed,
        }
