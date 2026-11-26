# AI Security Engineer Trainee Assignment

Submission by Arin.

- `Arin_assignment.pdf`: written answers to all three assignments
- `problem1_books`: 1.1, books from a REST API stored in SQLite
- `problem2_scores`: 1.2, student scores, average and bar chart
- `problem3_csv`: 1.3, CSV import into SQLite
- `code_samples`: 1.4 and 1.5, code from Mukham
- `tests`: unit tests for 1.1 to 1.3

## Run (from this folder)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python tests/test_all.py -v
python problem1_books/books.py
python problem2_scores/mock_api.py   # terminal 1, keep running
python problem2_scores/scores.py     # terminal 2
python problem3_csv/import_users.py
```

## AI assistance
With the hiring team's permission, I used an AI coding assistant for the code in 1.1 to 1.3, the diagrams and drafting the written answers. I have reviewed the work and can explain it. Sources and assumptions are listed in the PDF.

## code_samples
Excerpts from Mukham, a team project. They show the code but do not run alone.
- `1.4_presence_service.py`: written by Arin.
- `1.5_refresh_token_rotation.py`: 161 of 176 lines by Arin, 15 by a teammate (Git blame).
