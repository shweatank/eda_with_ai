"""
gate_analysis.py

Uses an LLM (Gemini by default, via llm_client.py) to explain and analyze
logic gate behavior in natural language.

Assumes you already have gate logic elsewhere in your project (e.g.
and_gate.py, or_gate.py) that produces truth tables or simulation results
as plain Python data structures (lists, dicts, etc.).

Usage:
    from gate_analysis import explain_truth_table, summarize_gate_results

    truth_table = {
        ("0", "0"): "0",
        ("0", "1"): "0",
        ("1", "0"): "0",
        ("1", "1"): "1",
    }
    print(explain_truth_table("AND", truth_table))
"""

from llm_client import ask_llm


def explain_truth_table(gate_name: str, truth_table: dict) -> str:
    """
    Ask the LLM to explain a gate's truth table in plain English.

    Args:
        gate_name: e.g. "AND", "OR", "XOR", "NAND"
        truth_table: dict mapping input tuples -> output, e.g.
                      {("0","0"): "0", ("0","1"): "0", ...}

    Returns:
        Natural-language explanation as a string.
    """
    table_str = "\n".join(
        f"Inputs: {inputs} -> Output: {output}"
        for inputs, output in truth_table.items()
    )

    prompt = (
        f"Here is the truth table for a {gate_name} gate:\n\n"
        f"{table_str}\n\n"
        f"Explain in plain English what this gate does and how the "
        f"output is determined by the inputs."
    )

    return ask_llm(
        prompt,
        system_prompt="You are an expert in digital logic and circuit design. "
                       "Explain concepts clearly and concisely.",
    )


def summarize_gate_results(results: list) -> str:
    """
    Ask the LLM to summarize a batch of gate simulation/test results
    (e.g. from a test suite or randomized simulation run).

    Args:
        results: list of dicts, each describing one test case, e.g.
                 [{"gate": "AND", "inputs": (1,0), "output": 0, "expected": 0, "pass": True}, ...]

    Returns:
        Natural-language summary as a string.
    """
    results_str = "\n".join(str(r) for r in results)

    prompt = (
        f"Here are logic gate test results:\n\n{results_str}\n\n"
        f"Summarize the overall pass/fail rate, flag any unexpected or "
        f"failing results, and note any patterns you see."
    )

    return ask_llm(
        prompt,
        system_prompt="You are a QA engineer reviewing digital logic test results. "
                       "Be precise and highlight anomalies.",
    )


def explain_circuit(gate_sequence: list) -> str:
    """
    Ask the LLM to explain a composed circuit (sequence/combination of gates).

    Args:
        gate_sequence: list describing how gates are chained, e.g.
                       [{"gate": "AND", "inputs": ["A", "B"], "output": "X"},
                        {"gate": "OR", "inputs": ["X", "C"], "output": "Y"}]

    Returns:
        Natural-language explanation of the overall circuit behavior.
    """
    circuit_str = "\n".join(str(step) for step in gate_sequence)

    prompt = (
        f"Here is a circuit described as a sequence of gates:\n\n{circuit_str}\n\n"
        f"Explain what this circuit computes overall, step by step."
    )

    return ask_llm(
        prompt,
        system_prompt="You are an expert in digital logic and circuit design.",
    )


if __name__ == "__main__":
    # quick manual test: python gate_analysis.py
    sample_truth_table = {
        ("0", "0"): "0",
        ("0", "1"): "0",
        ("1", "0"): "0",
        ("1", "1"): "1",
    }
    print(explain_truth_table("AND", sample_truth_table))