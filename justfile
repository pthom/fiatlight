default:
    just -l

doc:
    python src/python/fiatlight/doc/scripts/generate_doc_notebooks.py

doc_view_pdf:
    open src/python/fiatlight/doc/_build/pdf/book.pdf

