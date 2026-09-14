"""Example Haystack wiring for Paca task + document creation after extract.

Witdem instrumentation happens at app entry via ``witdem_sdk`` (do not reimplement
here). Pipeline outcomes should treat a non-empty ``error`` from either component
as a failed outcome (loud failure — do not swallow).

Typical flow after an extract / intake step:

1. ``CreatePacaTask`` — create a task in the target Paca project
2. ``CreatePacaDocument`` — attach markdown notes / extracted content as a document

Minimal wiring sketch (not a full production pipeline)::

    from haystack import Pipeline

    from integrations.haystack_paca.components import CreatePacaDocument, CreatePacaTask
    from integrations.paca_client import PacaClient

    client = PacaClient(base_url=..., api_key=...)
    project_id = "proj-1"

    pipe = Pipeline()
    pipe.add_component("create_task", CreatePacaTask(client=client, project_id=project_id))
    pipe.add_component("create_doc", CreatePacaDocument(client=client, project_id=project_id))

    # After extract: feed title/description into create_task, then title/markdown into create_doc.
    # Inspect result["create_task"]["error"] and result["create_doc"]["error"];
    # if either is non-empty → failed outcome.
    result = pipe.run(
        {
            "create_task": {"title": extracted_title, "description": extracted_description},
            "create_doc": {"title": doc_title, "markdown": extracted_markdown},
        }
    )
"""
