"""Fetch test scores from an API, compute the average, draw a bar chart.

Start mock_api.py first, then: python problem2_scores/scores.py [--url URL]
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # write image files without needing a display
import matplotlib.pyplot as plt
import requests


def fetch_scores(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def clean_scores(records):
    """Split into valid (name, score) pairs and rejected records."""
    valid, rejected = [], []
    for record in records:
        score = record.get("score")
        is_number = isinstance(score, (int, float)) and not isinstance(score, bool)
        if record.get("name") and is_number and 0 <= score <= 100:
            valid.append((record["name"], score))
        else:
            rejected.append(record)
    return valid, rejected


def average(scores):
    if not scores:
        raise ValueError("No valid scores to average")
    return sum(score for _, score in scores) / len(scores)


def plot(scores, mean, output):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar([n for n, _ in scores], [s for _, s in scores], color="#2a78d6")
    ax.bar_label(bars, label_type="center", color="white")
    ax.axhline(mean, color="#333333", linestyle="--", label=f"Average: {mean:.2f}")
    ax.set(title="Student test scores", xlabel="Student", ylabel="Score", ylim=(0, 110))
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000/scores")
    parser.add_argument("--output", default=Path(__file__).with_name("scores.png"))
    args = parser.parse_args()
    try:
        scores, rejected = clean_scores(fetch_scores(args.url))
        mean = average(scores)
    except (requests.RequestException, ValueError) as exc:
        raise SystemExit(f"Error: {exc}")
    for record in rejected:
        print(f"Rejected: {record}")
    print(f"Valid scores: {len(scores)}, average: {mean:.2f}")
    plot(scores, mean, args.output)
    print(f"Chart saved to {args.output}")


if __name__ == "__main__":
    main()
