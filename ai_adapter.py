from __future__ import annotations

from requests.adapters import BaseAdapter


class GeminiAdapter(BaseAdapter):
    """
    Gemini adapter for Inngest AI calls.
    """

    def __init__(
        self,
        *,
        auth_key: str,
        base_url: str | None = None,
        headers: dict[str, str] | None = None,
        model: str,
    ) -> None:
        self._auth_key = auth_key
        self._headers = headers or {}
        self._model = model
        self._url = (
            base_url
            or "https://generativelanguage.googleapis.com/v1beta/"
        )

    def auth_key(self) -> str:
        return self._auth_key

    def format(self) -> str:
        return "gemini"

    def headers(self) -> dict[str, str]:
        return self._headers

    def on_call(self, body: dict[str, object]) -> None:
        if not body.get("model"):
            body["model"] = self._model

    def url_infer(self) -> str:
        return (
            self._url.rstrip("/")
            + f"/models/{self._model}:generateContent"
            f"?key={self._auth_key}"
        )