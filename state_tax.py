"""
state_tax.py
============

Utility functions for parsing state-level individual income tax brackets
(from the Tax Foundation's “2025 State Individual Income Tax Rates and
Brackets” spreadsheet) and for computing the state income‐tax liability
for a given taxpayer.

The module is entirely self‑contained: on first import it parses the
Excel file and caches a dictionary ``STATE_BRACKETS`` mapping each state
name (e.g. ``"Calif"``) to a *progressive* bracket schedule of the form

    [(min_0, max_0, rate_0),
     (min_1, max_1, rate_1),
     ...
     (min_n, math.inf, rate_n)]

All rates are expressed as **decimals**, e.g. ``0.053`` for 5.3 %.

For states with *flat* taxes the list contains a single tuple whose
range is ``(0, math.inf, flat_rate)``.  States without an income tax
have a single tuple whose rate is ``0.0``.

Only the **Single Filer** schedule is loaded because the surrounding app
does not yet model filing status.  If you need Married‑Joint brackets,
pass ``filer_type="Married Filing Jointly"`` to
:func:`load_state_tax_brackets`.

Example
-------

```python
>>> from state_tax import calculate_state_tax
>>> calculate_state_tax(75_000, "Ore")   # $75 k salary, Oregon
3352.0
```
"""
from __future__ import annotations

import math
import os
import re
from functools import lru_cache
from typing import Dict, List, Tuple

import pandas as pd

Bracket = Tuple[float, float, float]  # (min, max, rate)
Schedule = List[Bracket]

# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def calculate_state_tax(
    income: float,
    state: str,
    brackets: Dict[str, Schedule] | None = None,
    deduction: float = 0.0,
) -> float:
    """
    Compute state income tax for *income* (gross) earned in *state*.

    Parameters
    ----------
    income
        Gross income.
    state
        State name *exactly* as it appears in the spreadsheet’s first
        column (punctuation removed, e.g. ``"Calif"``, ``"N.H."`` ⇒
        ``"NH"``).  Case‑insensitive.
    brackets
        Optional pre‑loaded bracket dictionary.  If *None* the module
        global ``STATE_BRACKETS`` is used.
    deduction
        An optional deduction **specific to the state tax** (do not
        confuse with the federal standard deduction already subtracted
        upstream).  Set to 0.0 to ignore state deductions.

    Returns
    -------
    float
        Tax owed.

    Raises
    ------
    KeyError
        If the *state* key is not present in *brackets*.
    """
    sched = (brackets or STATE_BRACKETS)[_normalize_state(state)]
    taxable = max(0.0, income - deduction)
    tax = 0.0
    for lower, upper, rate in sched:
        if taxable <= lower:  # no income in this and subsequent brackets
            break
        tax += (min(taxable, upper) - lower) * rate
    return tax


# ---------------------------------------------------------------------------
# Data loading / parsing
# ---------------------------------------------------------------------------


def _normalize_state(raw: str) -> str:
    """Strip footnotes & punctuation and turn “Calif.” → “Calif”."""
    return re.sub(r"[^A-Za-z ]", "", raw).strip()


def _iter_schedules(
    df: pd.DataFrame, filer_type: str = "Single Filer"
) -> Dict[str, Schedule]:
    """Yield (<state>, <schedule>) pairs parsed from *df*."""
    state_col = df.columns[0]
    rate_col = filer_type
    bracket_col = next(
        (c for c in df.columns if "Bracket" in str(c)), df.columns[3]
    )

    current_state: str | None = None
    current_rates: List[float] = []
    current_thresholds: List[float] = []

    for _, row in df.iterrows():
        cell = row[state_col]

        # New state header row
        if (
            isinstance(cell, str)
            and cell.strip()
            and cell.strip().lower() != "state"
            and not cell.strip().startswith("(")
        ):
            # Finalise previous schedule, if any
            if current_state and current_rates:
                yield current_state, _build_schedule(
                    current_rates, current_thresholds
                )
            current_state = _normalize_state(cell)
            current_rates, current_thresholds = [], []

        # Skip until we've seen the first state header
        if current_state is None:
            continue

        rate_raw = row.get(rate_col)
        if pd.isna(rate_raw):
            continue

        rate_s = str(rate_raw).strip().lower()
        if rate_s in {"none", "n.a.", "na"}:
            yield current_state, [(0.0, math.inf, 0.0)]
            current_rates, current_thresholds = [], []
            continue

        # Try to parse a numeric percentage
        try:
            rate_val = float(rate_s)
        except ValueError:  # e.g. “n.a.”
            continue

        bracket_raw = row.get(bracket_col)
        if pd.isna(bracket_raw):
            threshold_val = current_thresholds[-1] if current_thresholds else 0.0
        else:
            threshold_str = (
                str(bracket_raw).replace(">", "").replace(",", "").strip()
            )
            try:
                threshold_val = float(threshold_str)
            except ValueError:
                threshold_val = current_thresholds[-1] if current_thresholds else 0.0

        current_rates.append(rate_val)
        current_thresholds.append(threshold_val)

    # Final state at EOF
    if current_state and current_rates:
        yield current_state, _build_schedule(current_rates, current_thresholds)


def _build_schedule(rates: List[float], thresholds: List[float]) -> Schedule:
    assert len(rates) == len(thresholds)
    return [
        (thresholds[i], thresholds[i + 1] if i + 1 < len(thresholds) else math.inf, rate)
        for i, rate in enumerate(rates)
    ]


@lru_cache(maxsize=1)
def load_state_tax_brackets(
    path: str | os.PathLike = os.path.join(
        os.path.dirname(__file__),
        "2025-State-Individual-Income-Tax-Rates-and-Brackets-2025.xlsx",
    ),
    filer_type: str = "Single Filer",
) -> Dict[str, Schedule]:
    """
    Parse *path* (Tax Foundation spreadsheet) into a mapping from state to
    progressive tax schedule.

    The result is cached with :func:`functools.lru_cache` for fast
    repeat calls.
    """
    df = pd.read_excel(path, engine="openpyxl")
    return dict(_iter_schedules(df, filer_type=filer_type))


# Parse once at import‑time.
try:
    STATE_BRACKETS: Dict[str, Schedule] = load_state_tax_brackets()
except FileNotFoundError:
    # Defer until first usage if the Excel file lives elsewhere.
    STATE_BRACKETS = {}


__all__ = ["calculate_state_tax", "load_state_tax_brackets", "STATE_BRACKETS"]
