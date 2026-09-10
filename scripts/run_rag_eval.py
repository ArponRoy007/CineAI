"""Manual, API-costing RAG evaluation runner. Run before deploying Ask Roy changes."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rag.evaluation import evaluate_case, hallucination_rate
from rag.retriever import build_context


EVAL_SET_PATH = ROOT / "tests" / "rag_eval" / "eval_set.json"


def main():
    use_agent = "--agent" in sys.argv
    if use_agent:
        from ai.agent import answer_with_agent
    else:
        from rag.qa import answer_question
    cases = json.loads(EVAL_SET_PATH.read_text(encoding="utf-8"))
    results = []
    for case in cases:
        context, sources = build_context(case["question"], top_k=5, movie_title=case.get("movie_title"))
        if use_agent:
            answer = answer_with_agent(case["question"]).get("answer", "")
        else:
            answer = answer_question(case["question"], top_k=5, movie_title=case.get("movie_title")).get("answer", "")
        result = evaluate_case(case, context, sources, answer)
        results.append(result)
        status = "PASS" if (answer == case["expected_answer"] if case["expect_fallback"] else result["answer_correctness"] >= 0.35) else "CHECK"
        print(f"{status:5} {case['id']}: retrieval={result['retrieval_recall']:.0f} faithfulness={result['answer_faithfulness']:.2f} correctness={result['answer_correctness']:.2f}")

    answerable = [item for item in results if not item["expect_fallback"]]
    average = lambda key, items: sum(item[key] for item in items) / len(items) if items else 0.0
    print(f"\nRAG evaluation summary ({'agent' if use_agent else 'baseline'} path)")
    print(f"Cases: {len(results)} | Answerable: {len(answerable)} | Unsupported: {len(results) - len(answerable)}")
    print(f"Retrieval recall:    {sum(item['retrieval_recall'] == 1 for item in answerable)}/{len(answerable)} pass")
    print(f"Context relevance:   {sum(item['context_relevance'] == 1 for item in answerable)}/{len(answerable)} pass")
    print(f"Faithfulness:        {sum(item['answer_faithfulness'] >= 0.5 for item in results)}/{len(results)} pass")
    print(f"Answer correctness:  {sum(item['answer_correctness'] >= 0.35 for item in answerable)}/{len(answerable)} pass")
    print(f"Fallback avoidance:  {sum(item['answer'] == case['expected_answer'] for item, case in zip(results, cases) if case['expect_fallback'])}/{len(results) - len(answerable)} pass")
    print(f"Retrieval precision: {average('retrieval_precision', answerable):.2%}")
    print(f"Retrieval recall:    {average('retrieval_recall', answerable):.2%}")
    print(f"Context relevance:   {average('context_relevance', answerable):.2%}")
    print(f"Faithfulness:        {average('answer_faithfulness', results):.2%}")
    print(f"Answer correctness:  {average('answer_correctness', answerable):.2%}")
    print(f"Hallucination rate:  {hallucination_rate(results):.2%}")


if __name__ == "__main__":
    main()
