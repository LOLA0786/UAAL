# Demo that simulates pushing agent outputs into the UAAL pipeline without network calls.
import pprint
from app import (
    ACTIONS,
    WEBHOOKS,
    receive_action,
    approve_action,
    undo_action,
)
import asyncio


async def run_demo():
    print("Registering a fake webhook...")
    WEBHOOKS["demo_app"] = {"url": "https://example.app/webhook", "name": "DemoApp"}
    # agent output examples
    oa = {
        "assistant_id": "openai-123",
        "intent": "create_calendar_event",
        "target": {
            "type": "calendar_event",
            "attributes": {
                "title": "Sync with UAAL",
                "start": "2026-01-05T10:00:00",
                "end": "2026-01-05T11:00:00",
            },
        },
        "explanation": "User asked to schedule a sync meeting.",
        "confidence": 0.92,
    }
    ca = {
        "agent": "salesbot",
        "action": "update_crm",
        "payload": {
            "object_type": "lead",
            "id": "L-556",
            "fields": {"status": "contacted", "owner": "alice"},
        },
        "note": "Follow-up after demo.",
        "confidence": 0.83,
    }
    print("Sending openai-style action (auto-execute)...")
    r1 = await receive_action.__call__(
        type(
            "P",
            (),
            {
                "adapter": "openai_assistant",
                "agent_output": oa,
                "require_approval": False,
            },
        )
    )
    print("Result:", r1)
    print("Sending custom agent action (requires approval)...")
    r2 = await receive_action.__call__(
        type(
            "P",
            (),
            {"adapter": "simple_chat", "agent_output": ca, "require_approval": True},
        )
    )
    print("Result:", r2)
    print("\nCurrent ACTIONS:")
    pprint.pprint(list(ACTIONS.values()))
    # approve the pending action
    pending = [a for a in ACTIONS.values() if a["state"] == "pending"][0]
    print("\nApproving pending action:", pending["action_id"])
    await approve_action.__call__(pending["action_id"])
    print("\nACTIONS after approval:")
    pprint.pprint(list(ACTIONS.values()))
    # undo an action
    print("\nUndoing first action:")
    aid = list(ACTIONS.keys())[0]
    await undo_action.__call__(aid)
    pprint.pprint(ACTIONS[aid])


if __name__ == "__main__":
    asyncio.run(run_demo())
