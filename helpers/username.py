import os, requests

IG_ACCESS_TOKEN = os.environ["IG_ACCESS_TOKEN"]

def username_ig(ig_id: str) -> str:
    res = requests.get(
        f"https://graph.instagram.com/v25.0/{ig_id}",
        headers={"Authorization": f"Bearer {IG_ACCESS_TOKEN}"},
        params={"fields": "username"},
        timeout=20,
    )

    res.raise_for_status()
    return res.json()["username"]
