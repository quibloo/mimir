import pickle
import hashlib
import os
import glob
import time
from typing import Dict, List
import subprocess
from subprocess import PIPE
import datetime
import sys

import fitz  # pip install pymupdf


class Section:
    def __init__(self, name, idx, page, reviews: List[datetime]):
        self.name = name
        self.idx = idx
        self.page = page
        self.reviews = reviews
        self.last_review = reviews[-1] if len(reviews) > 1 else None


def compute_file_hash(file_path, algorithm='sha256'):
    """Compute the hash of a file using the specified algorithm."""
    hash_func = hashlib.new(algorithm)

    with open(file_path, 'rb') as file:
        # Read the file in chunks of 8192 bytes
        while chunk := file.read(8192):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def open_mupdf_at_page(page: int):
    process = subprocess.Popen(
        ['mupdf', sys.argv[1], '&'], stdin=PIPE, text=True)
    window_id = None
    while not window_id:
        try:
            # Use xdotool to search for the MuPDF window (by class name 'mupdf')
            window_id = subprocess.check_output(
                ["xdotool", "search", "--onlyvisible", "--class", "mupdf"]).strip()
        except subprocess.CalledProcessError:
            # If no window is found, keep waiting
            time.sleep(0.1)
    # Type the page number
    subprocess.run(["xdotool", "type", "--window",
                   window_id, str(page)])
    # Press Enter to go to the page
    subprocess.run(["xdotool", "key", "--window", window_id, "g"])
    # Press Enter to go to the page
    subprocess.run(["xdotool", "key", "--window", window_id, "Return"])
    return process


def get_bookmarks(filepath: str) -> Dict[int, str]:
    # WARNING! One page can have multiple bookmarks!
    bookmarks = {}
    with fitz.open(filepath) as doc:
        toc = doc.get_toc()  # [[lvl, title, page, …], …]
        for level, title, page in toc:
            bookmarks[page] = title
    return bookmarks


# hash file and check to see if there is already a hashed folder
hash = compute_file_hash(sys.argv[1])

secs = []
if os.path.isfile(f"{hash}.pkl"):
    with open(f"{hash}.pkl", 'rb') as file:
        secs = pickle.load(file)
else:
    bookmarks = get_bookmarks(sys.argv[1])
    for i, key in enumerate(bookmarks):
        sec = Section(bookmarks[key], i, key, [])
        secs.append(sec)
    with open(f"{hash}.pkl", 'wb') as file:
        pickle.dump(secs, file)


for sec in secs:
    print(sec.idx, sec.name, sec.page, sec.reviews)
current_review_section = 1
desired_section = int(input("Which section would you like to review?"))
process = open_mupdf_at_page(secs[desired_section].page)

user_input = input("Are you satisfied with your review session?")
if user_input == 'y':
    secs[desired_section].reviews.append(datetime.datetime.today())
    with open(f"{hash}.pkl", 'wb') as file:
        pickle.dump(secs, file)
    process.terminate()
else:
    print("Sorry you feel that way, we won't be adding today's review to your history...")
    process.terminate()
