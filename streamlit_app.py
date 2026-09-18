import asyncio
from pathlib import Path
import time

import streamlit as st
import inngest
from dotenv import load_dotenv
import os
import requests

load_dotenv()

st.set_page_config(
    page_title="RAG Ingest PDF",
    page_icon="📄",
    layout="centered"
)


@st.cache_resource
def get_inngest_client() -> inngest.Inngest:
    return inngest.Inngest(
        app_id="rag_app",
        is_production=False
    )


def save_uploaded_pdf(file) -> Path:
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)

    file_path = uploads_dir / file.name
    file_path.write_bytes(file.getbuffer())

    return file_path


async def send_rag_ingest_event(pdf_path: Path) -> str:
    client = get_inngest_client()

    result = await client.send(
        inngest.Event(
            name="rag/inngest_pdf",
            data={
                "pdf_path": str(pdf_path.resolve()),
                "source_id": pdf_path.name,
            },
        )
    )

    return result[0]


async def send_rag_query_event(question: str, top_k: int) -> str:
    client = get_inngest_client()

    result = await client.send(
        inngest.Event(
            name="rag/query_pdf_ai",
            data={
                "question": question,
                "top_k": top_k,
            },
        )
    )

    return result[0]


def _inngest_api_base() -> str:
    return os.getenv(
        "INNGEST_API_BASE",
        "http://127.0.0.1:8288/v1"
    )


def fetch_runs(event_id: str) -> list[dict]:
    url = f"{_inngest_api_base()}/events/{event_id}/runs"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()
    return data.get("data", [])


def wait_for_run_output(
    event_id: str,
    timeout_s: float = 300.0,
    poll_interval_s: float = 0.5
) -> dict:
    start = time.time()
    last_status = None

    while True:
        runs = fetch_runs(event_id)

        if runs:
            for run in runs:
                status = run.get("status")

                if status in (
                    "Completed",
                    "Succeeded",
                    "Success",
                    "Finished"
                ):
                    return run.get("output") or {}

                if status:
                    last_status = status

        if time.time() - start >= timeout_s:
            raise TimeoutError(
                f"Timed out waiting for backend. "
                f"Last status: {last_status}"
            )

        time.sleep(poll_interval_s)


st.title("Upload a PDF to Ingest")

uploaded = st.file_uploader(
    "Choose a PDF",
    type=["pdf"],
    accept_multiple_files=False
)

if uploaded is not None:
    try:
        with st.spinner("Uploading and processing PDF..."):
            path = save_uploaded_pdf(uploaded)

            event_id = asyncio.run(
                send_rag_ingest_event(path)
            )

            wait_for_run_output(event_id)

        st.success(f"PDF successfully ingested: {path.name}")
        st.caption("You can upload another PDF if you like.")

    except TimeoutError:
        st.error(
            "PDF processing is taking too long. "
            "Please check the backend and try again."
        )

    except requests.exceptions.ConnectionError:
        st.error(
            "Could not connect to the Inngest server. "
            "Please make sure the Inngest development server is running."
        )

    except Exception:
        st.error(
            "The PDF could not be processed. "
            "Please check the backend logs."
        )


st.divider()

st.title("Ask a question about your PDFs")


with st.form("rag_query_form"):
    question = st.text_input("Your question")

    top_k = st.number_input(
        "How many chunks to retrieve",
        min_value=1,
        max_value=20,
        value=5,
        step=1
    )

    submitted = st.form_submit_button("Ask")


if submitted:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner(
                "Searching documents and generating answer..."
            ):
                event_id = asyncio.run(
                    send_rag_query_event(
                        question.strip(),
                        int(top_k)
                    )
                )

                output = wait_for_run_output(event_id)

                answer = output.get("answer", "")
                sources = output.get("sources", [])

            st.subheader("Answer")
            st.write(answer or "(No answer)")

            if sources:
                st.caption("Sources")

                for source in sources:
                    st.write(f"- {source}")

        except TimeoutError:
            st.error(
                "The backend took too long to generate an answer. "
                "Please try again."
            )

        except requests.exceptions.ConnectionError:
            st.error(
                "Could not connect to the Inngest server. "
                "Please make sure the Inngest development server is running."
            )

        except requests.exceptions.HTTPError:
            st.error(
                "The Inngest server returned an error. "
                "Please check the backend logs."
            )

        except Exception:
            st.error(
                "The question could not be processed. "
                "Please check the backend logs and try again."
            )