from fastapi import APIRouter

router = APIRouter()


@router.post("/whatsapp")
def whatsapp_inbound(payload: dict) -> dict[str, str]:
    return {"status": "accepted", "type": "whatsapp", "payload_keys": ",".join(sorted(payload.keys()))}


@router.post("/graph")
def graph_inbound(payload: dict) -> dict[str, str]:
    return {"status": "accepted", "type": "graph", "payload_keys": ",".join(sorted(payload.keys()))}
