default:
    just -l

# Generate doc notebooks from markdown sources (run locally)
[group('docs')]
doc_gen_notebooks:
    python doc/scripts/generate_doc_notebooks.py

# Build the doc as static HTML
[group('docs')]
doc_build:
    cd doc && jupyter-book build --html

# Build the doc as PDF
[group('docs')]
doc_build_pdf:
    cd doc && jupyter-book build --pdf

# Serve the doc interactively (for dev, with live reload)
[group('docs')]
doc_serve:
    cd doc && jupyter-book start

# Serve the notebooks
[group('docs')]
doc_notebook_edit:
    cd doc && jupyter notebook


# Serve the built static HTML
[group('docs')]
doc_serve_static:
    cd doc/_build/html && python -m http.server 7005

# View the generated PDF
[group('docs')]
doc_view_pdf:
    open doc/_build/exports/flgt.pdf
