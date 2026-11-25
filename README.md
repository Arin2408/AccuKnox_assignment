# Run (from this folder)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python tests/test_all.py -v
python problem1_books/books.py
python problem2_scores/mock_api.py   # terminal 1, keep running
python problem2_scores/scores.py     # terminal 2
python problem3_csv/import_users.py
```
AI assistance: built with Claude Code. Sources and assumptions are in the assignment document.

# code_samples
Excerpts from Mukham, a team project. They show the code but do not run alone.
- `1.4_presence_service.py`: written by Arin.
- `1.5_refresh_token_rotation.py`: 161 of 176 lines by Arin, 15 by a teammate (Git blame).

The AI assistance note above applies to the problem folders and tests.
