"""Benchmark token efficiency between HIL commands and natural-language prompts."""

from __future__ import annotations

from dataclasses import dataclass

from transcoder import HILTranscoder

try:
    import tiktoken
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "tiktoken is required. Install with: pip install tiktoken"
    ) from exc


@dataclass
class BenchmarkResult:
    hil_command: str
    natural_prompt: str
    hil_tokens: int
    prompt_tokens: int

    @property
    def saved_tokens(self) -> int:
        return self.prompt_tokens - self.hil_tokens

    @property
    def saving_rate(self) -> float:
        if self.prompt_tokens == 0:
            return 0.0
        return self.saved_tokens / self.prompt_tokens


class HILBenchmark:
    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.encoding = tiktoken.encoding_for_model(model)
        self.transcoder = HILTranscoder()

    def token_count(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def compare(self, hil_command: str) -> BenchmarkResult:
        prompt = self.transcoder.decode(hil_command)
        hil_tokens = self.token_count(hil_command)
        prompt_tokens = self.token_count(prompt)
        return BenchmarkResult(
            hil_command=hil_command,
            natural_prompt=prompt,
            hil_tokens=hil_tokens,
            prompt_tokens=prompt_tokens,
        )


if __name__ == "__main__":
    sample = "? : $ {z, b} (3)"
    benchmark = HILBenchmark()
    result = benchmark.compare(sample)

    print("HIL command:", result.hil_command)
    print("Decoded prompt:", result.natural_prompt)
    print(f"HIL tokens: {result.hil_tokens}")
    print(f"Prompt tokens: {result.prompt_tokens}")
    print(f"Saved tokens: {result.saved_tokens}")
    print(f"Saving rate: {result.saving_rate:.2%}")

    if result.saving_rate >= 0.40:
        print("✅ Target met: token cost reduction exceeds 40%.")
    else:
        print("⚠️ Target not met for this sample; refine grammar or prompt style.")
