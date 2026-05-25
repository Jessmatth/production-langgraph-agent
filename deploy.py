#!/usr/bin/env python3
"""Deploy, query, and delete a LangGraph agent on Vertex AI Agent Engine."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
AGENT_ID_FILE = ROOT / ".agent_engine_id"
SRC_DIR = ROOT / "src"


def load_config() -> dict[str, str]:
    load_dotenv(ROOT / ".env")
    project = os.getenv("GOOGLE_CLOUD_PROJECT", "").strip()
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1").strip()
    staging_bucket = os.getenv("AGENT_ENGINE_STAGING_BUCKET", "").strip()
    display_name = os.getenv(
        "AGENT_DISPLAY_NAME", "production-langgraph-agent"
    ).strip()
    description = os.getenv(
        "AGENT_DESCRIPTION",
        "LangGraph product agent on Vertex Agent Engine",
    ).strip()

    missing = []
    if not project:
        missing.append("GOOGLE_CLOUD_PROJECT")
    if not staging_bucket:
        missing.append("AGENT_ENGINE_STAGING_BUCKET")
    if missing:
        print(
            f"Missing required env vars: {', '.join(missing)}. "
            "Copy .env.example to .env and fill in values.",
            file=sys.stderr,
        )
        sys.exit(1)

    return {
        "project": project,
        "location": location,
        "staging_bucket": staging_bucket,
        "display_name": display_name,
        "description": description,
    }


def ensure_src_on_path() -> None:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))


def get_client(config: dict[str, str]):
    import vertexai

    vertexai.init(
        project=config["project"],
        location=config["location"],
        staging_bucket=config["staging_bucket"],
    )
    return vertexai.Client(project=config["project"], location=config["location"])


def extract_content(response: dict) -> str:
    messages = response.get("messages", [])
    if not messages:
        return str(response)
    last = messages[-1]
    if isinstance(last, dict):
        kwargs = last.get("kwargs", {})
        if "content" in kwargs:
            return kwargs["content"]
        return str(last)
    return str(last)


def read_agent_id(resource_name: str | None) -> str:
    if resource_name:
        return resource_name
    if not AGENT_ID_FILE.exists():
        print(
            "No .agent_engine_id file. Run `python deploy.py deploy` first, "
            "or pass --resource-name.",
            file=sys.stderr,
        )
        sys.exit(1)
    return AGENT_ID_FILE.read_text().strip()


def cmd_deploy(config: dict[str, str]) -> None:
    ensure_src_on_path()
    from src.agent import create_agent

    agent = create_agent()
    client = get_client(config)

    print("Deploying agent to Vertex AI Agent Engine...")
    remote_agent = client.agent_engines.create(
        agent=agent,
        config={
            "staging_bucket": config["staging_bucket"],
            "requirements": [
                "google-cloud-aiplatform[agent_engines,langchain]",
            ],
            "extra_packages": ["src"],
            "display_name": config["display_name"],
            "description": config["description"],
        },
    )
    resource_name = remote_agent.api_resource.name
    AGENT_ID_FILE.write_text(resource_name)
    print(f"Deployed: {resource_name}")
    print(f"Saved resource name to {AGENT_ID_FILE}")


def cmd_query(config: dict[str, str], prompt: str, resource_name: str | None) -> None:
    name = read_agent_id(resource_name)
    client = get_client(config)
    remote_agent = client.agent_engines.get(name=name)

    print(f"Querying agent: {name}")
    response = remote_agent.query(
        input={"messages": [("user", prompt)]},
    )
    print(extract_content(response))


def cmd_delete(config: dict[str, str], resource_name: str | None) -> None:
    name = read_agent_id(resource_name)
    client = get_client(config)

    print(f"Deleting agent: {name}")
    client.agent_engines.delete(name=name)
    if AGENT_ID_FILE.exists():
        AGENT_ID_FILE.unlink()
    print("Deleted.")


def cmd_local(config: dict[str, str], prompt: str) -> None:
    ensure_src_on_path()
    from src.agent import create_agent

    get_client(config)
    agent = create_agent()
    print("Running local query...")
    response = agent.query(input={"messages": [("user", prompt)]})
    print(extract_content(response))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Manage a LangGraph agent on Vertex AI Agent Engine.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("deploy", help="Deploy agent to Agent Engine")

    query_p = sub.add_parser("query", help="Query deployed agent")
    query_p.add_argument(
        "--prompt",
        default="Get product details for shoes",
        help="User message to send",
    )
    query_p.add_argument(
        "--resource-name",
        default=None,
        help="Agent Engine resource name (overrides .agent_engine_id)",
    )

    delete_p = sub.add_parser("delete", help="Delete deployed agent")
    delete_p.add_argument(
        "--resource-name",
        default=None,
        help="Agent Engine resource name (overrides .agent_engine_id)",
    )

    local_p = sub.add_parser("local", help="Run a local query (no deploy)")
    local_p.add_argument(
        "--prompt",
        default="Get product details for headphones",
        help="User message to send",
    )

    args = parser.parse_args()
    config = load_config()

    if args.command == "deploy":
        cmd_deploy(config)
    elif args.command == "query":
        cmd_query(config, args.prompt, args.resource_name)
    elif args.command == "delete":
        cmd_delete(config, args.resource_name)
    elif args.command == "local":
        cmd_local(config, args.prompt)


if __name__ == "__main__":
    main()
