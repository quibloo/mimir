# mimir

"rips out" the table of contents of a pdf to assist w/ studying.

- [x] We want to take the table of contents for a textbook
- [] We want to mark down when we have read a chapter or subsection
- [] We want to calculate expected completion time
- [] We want to auto-generate the best times to go back and re-study certain sections
- [] We want to create a "bank" of useful exercises from the books


# Setup & Install


```bash
# Setup virtual environment
python3 -m venv .venv

# Use it
source .venv/bin/activate

# Install pymupdf
pip install pymupdf

# Run the pdf script on the pdf you want
python3 pdf.py <PATH_TO_PDF_FILE>.pdf
```
