default:
    just -l

doc:
    python src/python/fiatlight/doc/scripts/generate_doc_notebooks.py

doc_pdf:
    python src/python/fiatlight/doc/scripts/generate_doc_notebooks.py pdf

doc_view_pdf:
    open src/python/fiatlight/doc/docs/flgt.pdf

