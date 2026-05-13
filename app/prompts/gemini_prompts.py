SYSTEM_PROMPT = """
You are a fitness analysis assistant.
Be concise, factual, and structured.
When summarizing workouts, focus on effort, pacing, changes over time, and notable peaks.
Avoid inventing missing data.
""".strip()


def build_workout_summary_prompt(workout_payload: dict) -> str:
    return (
        "Summarize the following cycling workout for a human athlete. "
        "Describe the overall session, notable phases, intensity trends, and any important peaks.\n\n"
        f"Workout data:\n{workout_payload}"
    )


def build_weight_loss_bike_prompt(workout_payload: dict) -> str:
    return (
        "Analyze this cycling workout for a 32-year-old man, 182 cm, 93 kg, whose main goal is losing weight.\n"
        "Write the answer as a short 5-line list.\n"
        "Include a score from 0 to 10 for the fat-loss goal, say whether it looks mainly Zone 2 or Zone 3 or mixed, "
        "briefly explain whether that intensity fits weight loss, and propose concrete improvements for the next workout.\n"
        "Keep the full answer to a maximum of 5 lines.\n"
        "Use one idea per line and keep each line concise.\n\n"
        f"Workout data:\n{workout_payload}"
    )
