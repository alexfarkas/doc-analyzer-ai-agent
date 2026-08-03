from itertools import zip_longest

from tests.consts.files import DEFAULT_FILENAME_WITH_EXT, DEFAULT_FILE_EXT
from tests.factories.agent import make_council_analyze_doc, make_agent_analyze_doc


def make_expected_agent_analyze_doc_response():
    """
    Expected response of POST /doc/analyze for single agent

    Returns:
        JSON object based on data set in agent mock
    """
    data = make_agent_analyze_doc()
    return {
        "result": [
            {
                "answer_seq": {
                    "answers": [
                        {
                            "answer": data.answer_item.answer,
                            "author": data.answer_item.author.value,
                            "status": data.answer_item.status.value,
                            "init_status": data.answer_item.init_status.value,
                        }
                    ]
                },
            },
        ],
        "consumption_data": {
            "token_usage": {
                "input_tokens": data.consumption_data.token_usage.input_tokens,
                "output_tokens": data.consumption_data.token_usage.output_tokens,
                "total_tokens": data.consumption_data.token_usage.total_tokens,
            }
            if data.consumption_data.token_usage
            else None,
            "elapsed": data.consumption_data.elapsed,
            "cost": data.consumption_data.cost,
        },
    }


def make_expected_council_analyze_doc_response():
    """
    Expected response of POST /doc/analyze for council

    Returns:
        JSON object based on data set in council mock
    """
    data = make_council_analyze_doc()
    return {
        "result": [
            {
                "answer_seq": {
                    "answers": [
                        {
                            "answer": answer.answer,
                            "author": answer.author.value,
                            "status": answer.status.value,
                            "init_status": answer.init_status.value,
                        }
                        for answer in answer_seq.answers
                    ]
                },
                "judgement": judgement,
                "score": score,
            }
            for answer_seq, judgement, score in zip_longest(
                data.answer_seqs,
                data.judgements,
                data.scores,
            )
        ],
        "consumption_data": {
            "token_usage": {
                "input_tokens": data.consumption_data.token_usage.input_tokens,
                "output_tokens": data.consumption_data.token_usage.output_tokens,
                "total_tokens": data.consumption_data.token_usage.total_tokens,
            }
            if data.consumption_data.token_usage
            else None,
            "elapsed": data.consumption_data.elapsed,
            "cost": data.consumption_data.cost,
        },
    }


def make_expected_file_preview_response(
    filename: str = DEFAULT_FILENAME_WITH_EXT,
    ext: str = DEFAULT_FILE_EXT,
) -> dict:
    return {
        "status": "success",
        "filename": filename,
        "format": ext,
        "metadata": {"encoding": "utf-8"},
        "blocks": [
            {"type": "heading", "level": 1, "content": "header"},
            {"type": "text", "content": "test content"},
        ],
    }
