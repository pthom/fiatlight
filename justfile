default:
    just -l

doc:
    python doc/scripts/generate_doc_notebooks.py

doc_pdf:
    python doc/scripts/generate_doc_notebooks.py pdf

doc_view_pdf:
    open doc/docs/flgt.pdf

