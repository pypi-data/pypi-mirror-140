import json
from typing import Dict, List, Optional, Tuple

from dbt_utils.dbt_runner import get_downstream_models
from parsers.manifest import Manifest
from parsers.run_result import RunResult, RunResultType

SlackMessageBody = Tuple[Dict[str, List[Dict[str, str]]], int]


def _build_slack_message_header(dag_name: str, len_results: int, fail_cnt: int) -> Dict:
    pass_cnt = len_results - fail_cnt
    return {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "dbt: Failures",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "plain_text",
                        "text": f":green-circle: Pass: {pass_cnt}",
                        "emoji": True,
                    },
                    {
                        "type": "plain_text",
                        "text": f":red_circle: Failures: {fail_cnt}",
                        "emoji": True,
                    },
                ],
            },
        ]
    }


def _build_slack_message_body(
    results: List[RunResult], dag_name: str
) -> SlackMessageBody:
    attachments = []
    failure_count = 0
    for result in results:
        if not result.is_success:
            failure_count += 1

            msg = {"color": "#90EE90" if result.is_success else "#FF0000"}

            team_ownership_text = (
                f"{result.manifest.owner} "
                f"( <!subteam^{result.manifest.slack_support_group_id}> )"
                if result.manifest.owner is not None
                else "WARNING: No assigned team"
            )

            if result.run_type == RunResultType.Model:
                downstream_models = get_downstream_models(result.table_name)
                msg[
                    "title"
                ] = f":redsiren: Critcal Model Failure: {result.table_name} :redsiren:\n\n:warning: Impacts {len(downstream_models)} models, which will not be updated until the error is resolved"
                msg["text"] = f"{result.message}"

            if result.run_type == RunResultType.Test:
                msg["title"] = (
                    f"Test Failure: {result.table_name}"
                    if result.test_name is not None
                    else f"Test Failure: {result.table_name}"
                )
                msg["text"] = (
                    f"Check: {result.test_name}\n{result.message}"
                    if result.test_name is not None
                    else f"{result.message}"
                )

            if result.run_type == RunResultType.Freshness:
                msg["title"] = f"Model Freshness: {result.table_name}"
                msg["text"] = f"Stale Data: {result.message}"

            msg["footer"] = (
                f"Execution time: {round(result.execution_time, 4)}s\n"
                f"Owner | {team_ownership_text}\n"
                f"DAG name | {dag_name}"  # how to pass in the dag name?
            )
            attachments.append(msg)

    return {
        "attachments": attachments,
    }, failure_count


def build_slack_message(
    dag_name: str, results: List[RunResult], invocation_id: str
) -> Optional[str]:
    """
    Build a slack message blob from the raw dbt results
    """
    body, failure_count = _build_slack_message_body(results, dag_name)
    header = _build_slack_message_header(dag_name, len(results), failure_count)

    return json.dumps({**header, **body}) if failure_count else None


def lookup_team_info(
    manifest: Dict[str, Manifest], unique_id: str
) -> Tuple[Optional[str], Optional[str]]:
    dbt_item = manifest[unique_id]
    return dbt_item.owner, dbt_item.slack_support_group_id
