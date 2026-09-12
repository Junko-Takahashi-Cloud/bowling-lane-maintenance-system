# app/services/member_gear_client.py
import os
import requests

MEMBER_GEAR_CALLBACK_URL = os.getenv("MEMBER_GEAR_CALLBACK_URL")
MEMBER_GEAR_CALLBACK_API_KEY = os.getenv("MEMBER_GEAR_CALLBACK_API_KEY")


def notify_gear_maintenance_completed(gear_id: int, action_type: str, note: str | None) -> None:
    if not MEMBER_GEAR_CALLBACK_URL:
        return
    try:
        requests.post(
            f"{MEMBER_GEAR_CALLBACK_URL}/api/v1/gears/{gear_id}/maintenance/complete",
            json={"action_type": action_type, "note": note},
            headers={"X-API-Key": MEMBER_GEAR_CALLBACK_API_KEY},
            timeout=5,
        )
    except requests.RequestException:
        pass  # 第四弾が落ちていても拡張①側の処理は止めない