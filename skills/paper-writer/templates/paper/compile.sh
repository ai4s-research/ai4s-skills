#!/bin/bash
set -e

# This script is meant to be run from within the paper output directory
# where main.tex, bibliography.bib, and sections/ already exist.

echo "First pdflatex run..."
pdflatex -interaction=nonstopmode main.tex || true

echo "Running bibtex..."
if [ -f bibliography.bib ]; then
    bibtex main || true
fi

echo "Second pdflatex run..."
pdflatex -interaction=nonstopmode main.tex || true

echo "Final pdflatex run..."
pdflatex -interaction=nonstopmode main.tex || true

echo "Compilation complete. PDF: main.pdf"
