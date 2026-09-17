# batch_cost_calculator.py
# Craft Brewery Batch Cost Calculator
# Inspired by: tfrayner/beerfestdb - CBF_beer_price_calculator.py
#
# This script calculates the total cost of a brewing batch, the cost per barrel,
# and the recommended selling price per barrel based on a configurable margin.

from dataclasses import dataclass, field
from typing import Optional
import json


# ──────────────────────────────────────────────────────────
#  Data structures  (mirroring the reference code's model
#  of input parameters → computed cost fields)
# ──────────────────────────────────────────────────────────

@dataclass
class IngredientCosts:
    """Cost per unit for each ingredient category."""
    grain_per_lb: float = 0.0       # $ / lb
    hops_per_oz: float = 0.0        # $ / oz
    yeast_per_unit: float = 0.0     # $ / packet/unit
    packaging_per_unit: float = 0.0 # $ / keg, bottle, can, etc.


@dataclass
class BatchInputs:
    """All user-supplied values for a single brew batch."""
    batch_size_barrels: float            # barrels (1 bbl = 31 US gal)
    grain_lbs: float                     # total lbs of grain used
    hops_oz: float                       # total oz of hops used
    yeast_units: float                   # number of yeast packets/units
    packaging_units: float               # number of kegs/bottles/cans
    margin_percent: float = 20.0         # markup % on top of cost
    # ingredient unit costs
    grain_cost_per_lb: float = 0.0
    hops_cost_per_oz: float = 0.0
    yeast_cost_per_unit: float = 0.0
    packaging_cost_per_unit: float = 0.0


@dataclass
class BatchResult:
    """Computed cost breakdown and recommended pricing."""
    grain_cost: float
    hops_cost: float
    yeast_cost: float
    packaging_cost: float
    total_cost: float
    cost_per_barrel: float
    margin_amount: float
    recommended_price_per_barrel: float

    def to_dict(self) -> dict:
        return {
            "grain_cost": round(self.grain_cost, 2),
            "hops_cost": round(self.hops_cost, 2),
            "yeast_cost": round(self.yeast_cost, 2),
            "packaging_cost": round(self.packaging_cost, 2),
            "total_cost": round(self.total_cost, 2),
            "cost_per_barrel": round(self.cost_per_barrel, 2),
            "margin_amount": round(self.margin_amount, 2),
            "recommended_price_per_barrel": round(self.recommended_price_per_barrel, 2),
        }


# ──────────────────────────────────────────────────────────
#  Core calculation engine
# ──────────────────────────────────────────────────────────

def calculate_batch_cost(inputs: BatchInputs) -> BatchResult:
    """
    Compute the full cost breakdown for a brew batch.

    Logic mirrors the reference calculator:
      1. Multiply each ingredient quantity × unit cost → line-item costs
      2. Sum all line items → total production cost
      3. Divide by barrel count → cost per barrel
      4. Apply margin → recommended selling price per barrel
    """
    # Line-item costs (analogous to the reference's cask_price / lpc / cost_price chain)
    grain_cost = inputs.grain_lbs * inputs.grain_cost_per_lb
    hops_cost = inputs.hops_oz * inputs.hops_cost_per_oz
    yeast_cost = inputs.yeast_units * inputs.yeast_cost_per_unit
    packaging_cost = inputs.packaging_units * inputs.packaging_cost_per_unit

    total_cost = grain_cost + hops_cost + yeast_cost + packaging_cost

    if inputs.batch_size_barrels <= 0:
        raise ValueError("batch_size_barrels must be greater than 0")

    cost_per_barrel = total_cost / inputs.batch_size_barrels
    margin_amount = total_cost * (inputs.margin_percent / 100.0)
    recommended_price = cost_per_barrel + (margin_amount / inputs.batch_size_barrels)

    return BatchResult(
        grain_cost=grain_cost,
        hops_cost=hops_cost,
        yeast_cost=yeast_cost,
        packaging_cost=packaging_cost,
        total_cost=total_cost,
        cost_per_barrel=cost_per_barrel,
        margin_amount=margin_amount,
        recommended_price_per_barrel=recommended_price,
    )


def display_results(result: BatchResult) -> None:
    """Pretty-print the calculation results."""
    print("=" * 55)
    print("       CRAFT BREWERY BATCH COST CALCULATOR")
    print("=" * 55)
    print()
    print("  ── Cost Breakdown ──────────────────────────────")
    print(f"  Grain cost:        ${result.grain_cost:>10,.2f}")
    print(f"  Hops cost:         ${result.hops_cost:>10,.2f}")
    print(f"  Yeast cost:        ${result.yeast_cost:>10,.2f}")
    print(f"  Packaging cost:    ${result.packaging_cost:>10,.2f}")
    print(f"  ─────────────────────────────────────────")
    print(f"  TOTAL BATCH COST:  ${result.total_cost:>10,.2f}")
    print()
    print("  ── Per-Barrel Pricing ──────────────────────────")
    print(f"  Cost / barrel:          ${result.cost_per_barrel:>10,.2f}")
    print(f"  Margin added:           ${result.margin_amount:>10,.2f}")
    print(f"  RECOMMENDED SELL PRICE: ${result.recommended_price_per_barrel:>10,.2f}")
    print()
    print("=" * 55)


# ──────────────────────────────────────────────────────────
#  Sample batch execution  (validation)
# ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    # ── Sample: 5-barrel all-grain IPA batch ──────────
    sample = BatchInputs(
        batch_size_barrels=5.0,       # 5 bbl batch
        grain_lbs=155.0,              # ~31 lb/bbl × 5 bbl
        hops_oz=12.0,                 # dual-hop additions
        yeast_units=2.0,              # 2 packets of London Ale III
        packaging_units=4.0,          # 4 Cornelius kegs
        margin_percent=25.0,          # 25 % margin
        grain_cost_per_lb=1.85,       # ~$1.85/lb Maris Otter
        hops_cost_per_oz=8.50,        # ~$8.50/oz Citra & Simcoe
        yeast_cost_per_unit=3.25,     # ~$3.25/packet
        packaging_cost_per_unit=6.00, # ~$6.00/keg
    )

    result = calculate_batch_cost(sample)
    display_results(result)

    # ── JSON output for programmatic use ──────────────
    print("\nJSON:")
    print(json.dumps(result.to_dict(), indent=2))

    # ── Assertions to validate correctness ────────────
    assert abs(result.grain_cost - (155.0 * 1.85)) < 0.01, "Grain cost mismatch"
    assert abs(result.hops_cost - (12.0 * 8.50)) < 0.01, "Hops cost mismatch"
    assert abs(result.yeast_cost - (2.0 * 3.25)) < 0.01, "Yeast cost mismatch"
    assert abs(result.packaging_cost - (4.0 * 6.00)) < 0.01, "Packaging cost mismatch"
    assert abs(result.total_cost - (155.0*1.85 + 12.0*8.50 + 2.0*3.25 + 4.0*6.00)) < 0.01, "Total cost mismatch"
    assert abs(result.cost_per_barrel - result.total_cost / 5.0) < 0.01, "Cost per barrel mismatch"
    expected_price = result.cost_per_barrel * 1.25
    assert abs(result.recommended_price_per_barrel - expected_price) < 0.01, "Recommended price mismatch"

    print("\n✅ All validation assertions passed!")
