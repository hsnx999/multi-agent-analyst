# Run with: python analyst.py
# Terminal version — shows the full debate with colours

from dotenv import load_dotenv
load_dotenv()

from src.debate import run_debate

COLOURS = {
    "Planner":    "\033[94m",   # blue
    "Researcher": "\033[92m",   # green
    "Critic":     "\033[91m",   # red
    "System":     "\033[93m",   # yellow
    "RESET":      "\033[0m",
}

def coloured(agent: str, text: str) -> str:
    c = COLOURS.get(agent, "")
    return f"{c}[{agent}]{COLOURS['RESET']} {text}"

if __name__ == "__main__":
    topic = input("Enter analysis topic: ").strip()
    if not topic:
        topic = "The impact of AI on software engineering jobs in 2026"

    print(f"\n{'='*60}")
    print(f"  Multi-Agent Analysis: {topic}")
    print(f"{'='*60}\n")

    for event in run_debate(topic, max_rounds=3):
        print(coloured(event.agent, f"[{event.stage.upper()}]"))
        print(event.content)
        print()

    print(f"\n{'='*60}")
    print("Debate complete. Check the reports/ folder for the full report.")