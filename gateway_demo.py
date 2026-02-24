"""HIL Gateway demo: simulate an SLM→LLM neuro-compression workflow.

This script demonstrates the commercial value of pre-inference optimization:
1) Local SLM side compresses verbose user requests into compact HIL commands.
2) Cloud LLM side expands HIL into executable high-precision prompts.
3) Benchmark reports token savings to quantify cost/latency impact.
"""

from __future__ import annotations

from dataclasses import dataclass

from transcoder import HILTranscoder


@dataclass
class DemoArtifacts:
    original_request: str
    hil_command: str
    executable_prompt: str
    original_tokens: int
    hil_tokens: int
    saved_tokens: int
    saving_rate: float


def _format_panel(artifacts: DemoArtifacts) -> str:
    """Render an ASCII dashboard for terminal visualization."""

    line = "=" * 92
    small_line = "-" * 92

    def pct(v: float) -> str:
        return f"{v * 100:.2f}%"

    target_badge = "✅ In target range (35%–62%)" if 0.35 <= artifacts.saving_rate <= 0.62 else "⚠️ Out of target range"

    return (
        f"\n{line}\n"
        f" HIL-Gateway Demo · SLM→LLM Neuro-compression Pipeline\n"
        f"{line}\n"
        f"[Original Request]\n{artifacts.original_request}\n"
        f"{small_line}\n"
        f"[HIL Command | Local SLM Simulation]\n{artifacts.hil_command}\n"
        f"{small_line}\n"
        f"[Final Executable Prompt | Cloud LLM Simulation]\n{artifacts.executable_prompt}\n"
        f"{small_line}\n"
        f"[Savings Report]\n"
        f"- Original Tokens : {artifacts.original_tokens}\n"
        f"- HIL Tokens      : {artifacts.hil_tokens}\n"
        f"- Tokens Saved    : {artifacts.saved_tokens}\n"
        f"- Saving Rate     : {pct(artifacts.saving_rate)}\n"
        f"- Target Check    : {target_badge}\n"
        f"{line}\n"
    )


def run_demo() -> None:
    """Run end-to-end gateway simulation.

    Pre-optimization explanation:
    - We compress the request BEFORE expensive cloud inference.
    - This addresses enterprise pain points where token cost pressure is severe (85/100)
      and latency pressure is also high (70/100).
    """

    # ~200-token style verbose request for RAG competitor analysis simulation.
    original_request = (
        "for our strategy review, compare Apple and Tesla using retrieved annual-report context, earnings "
        "commentary, and r-and-d investment notes, then evaluate innovation efficiency, long-cycle product "
        "momentum, and moat durability across both firms. i also need a practical interpretation for enterprise "
        "decision-making: where each company is likely to sustain competitive advantage, where execution risk "
        "is rising, and which signals should be monitored in upcoming quarters. please return the result in "
        "chinese, keep it compact but information-dense, and output 5 bullet points that summarize key "
        "competitive strengths so leadership can quickly compare strategic positioning and feed the findings "
        "into an internal investment and partnership memo."
    )

    transcoder = HILTranscoder()

    # Step 1: Local SLM simulation -> reverse translate verbose NL into compact HIL.
    hil_command = transcoder.reverse_translate(original_request)

    # Step 2: Cloud LLM simulation -> decode HIL back into executable instruction.
    executable_prompt = transcoder.decode(hil_command)

    # Step 3: Quantification via existing HILBenchmark class.
    try:
        from benchmark import HILBenchmark

        benchmark = HILBenchmark()
        original_tokens = benchmark.token_count(original_request)
        hil_tokens = benchmark.token_count(hil_command)
    except SystemExit:
        # If tiktoken is unavailable, keep demo usable with a clear, deterministic fallback.
        # Fallback token estimation (word-level) is only for local demo continuity.
        original_tokens = len(original_request.split())
        hil_tokens = len(hil_command.split())
        print("⚠️ tiktoken not available; using rough word-based estimate for token counts.")

    saved_tokens = original_tokens - hil_tokens
    saving_rate = (saved_tokens / original_tokens) if original_tokens else 0.0

    artifacts = DemoArtifacts(
        original_request=original_request,
        hil_command=hil_command,
        executable_prompt=executable_prompt,
        original_tokens=original_tokens,
        hil_tokens=hil_tokens,
        saved_tokens=saved_tokens,
        saving_rate=saving_rate,
    )

    print(_format_panel(artifacts))


if __name__ == "__main__":
    run_demo()
