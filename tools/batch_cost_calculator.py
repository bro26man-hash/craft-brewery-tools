# batch_cost_calculator.py
#
# Craft Brewery Batch Cost Calculator
# Inspired by tfrayner/beerfestdb's CBF_beer_price_calculator.py
# (https://github.com/tfrayner/beerfestdb/blob/main/tool_dashboard/CBF_beer_price_calculator.py)
#
# The original tool calculates beer sale prices from cask cost and ABV-based pricing.
# This script adapts the concept for *batch-level* cost accounting: it takes ingredient
# unit costs, a batch size in barrels, and a configurable margin to produce the total
# batch cost, cost-per-barrel, and recommended selling price per barrel.

from dataclasses import dataclass
from typing import Optional
import json


# ---------------------------------------------------------------------------
# Configuration / inputs  (mirrors the `st.number_input` fields in the reference)
# ---------------------------------------------------------------------------

@dataclass
class BatchInputs:
    """All user-tunable inputs for a single batch calculation.

    Attributes:
        grain_cost_per_lb:     Price of grain per pound            ($/lb)
        hops_cost_per_oz:     Price of hops per ounce             ($/oz)
        yeast_cost_per_unit:  Price of yeast per unit (per pack)  ($/unit)
        packaging_cost_per_unit: Price of packaging per unit (per bottle/can)  ($/unit)
        barrels:              Batch size in barrels (1 barrel = 31 US gallons)
        oz_per_barrel:        Hops usage in ounces per barrel       (default 1.0)
        lb_per_barrel:        Grain usage in pounds per barrel      (default 20.0)
        yeast_units_per_batch: Number of yeast units per batch      (default 1)
        units_per_barrel:     Packaging units (bottles/cans) per barrel (default 325)
        margin_pct:           Markup percentage applied to cost      (e.g. 30 = 30%)
    """
    grain_cost_per_lb:        float = 0.60
    hops_cost_per_oz:         float = 1.00
    yeast_cost_per_unit:      float = 5.00
    packaging_cost_per_unit:  float = 0.10
    barrels:                  float = 5.0
    oz_per_barrel:            float = 1.0
    lb_per_barrel:            float = 20.0
    yeast_units_per_batch:    float = 1.0
    units_per_barrel:         float = 325.0
    margin_pct:               float = 30.0


# ---------------------------------------------------------------------------
# Calculation logic
# ---------------------------------------------------------------------------

def calculate_batch_cost(inputs: BatchInputs) -> dict:
    """Compute total cost, cost per barrel, and recommended sale price.

    Returns a dict with all intermediate and final values.
    """
    # --- Ingredient costs for the whole batch ---
    grain_cost_total    = inputs.grain_cost_per_lb   * inputs.lb_per_barrel   * inputs.barrels
    hops_cost_total     = inputs.hops_cost_per_oz    * inputs.oz_per_barrel   * inputs.barrels
    yeast_cost_total    = inputs.yeast_cost_per_unit * inputs.yeast_units_per_batch
    packaging_cost_total = inputs.packaging_cost_per_unit * inputs.units_per_barrel * inputs.barrels

    total_cost = grain_cost_total + hops_cost_total + yeast_cost_total + packaging_cost_total
    cost_per_barrel = total_cost / inputs.barrels if inputs.barrels else 0.0

    # --- Margin / selling price (same "cost + markup" principle as l_coefficient
    #     in the reference: cost_price * l_coefficient -> sale price) ---
    margin_multiplier = 1 + (inputs.margin_pct / 100.0)
    recommended_price_per_barrel = cost_per_barrel * margin_multiplier

    return {
        # raw inputs echoed back
        "grain_cost_per_lb":         inputs.grain_cost_per_lb,
        "hops_cost_per_oz":           inputs.hops_cost_per_oz,
        "yeast_cost_per_unit":        inputs.yeast_cost_per_unit,
        "packaging_cost_per_unit":    inputs.packaging_cost_per_unit,
        "barrels":                    inputs.barrels,
        "oz_per_barrel":              inputs.oz_per_barrel,
        "lb_per_barrel":              inputs.lb_per_barrel,
        "yeast_units_per_batch":      inputs.yeast_units_per_batch,
        "units_per_barrel":           inputs.units_per_barrel,
        "margin_pct":                 inputs.margin_pct,
        # computed values
        "grain_cost_total":           round(grain_cost_total, 2),
        "hops_cost_total":            round(hops_cost_total, 2),
        "yeast_cost_total":           round(yeast_cost_total, 2),
        "packaging_cost_total":       round(packaging_cost_total, 2),
        "total_cost":                 round(total_cost, 2),
        "cost_per_barrel":            round(cost_per_barrel, 2),
        "margin_multiplier":          round(margin_multiplier, 4),
        "recommended_price_per_barrel": round(recommended_price_per_barrel, 2),
    }


def display_results(result: dict) -> None:
    """Pretty-print the calculation results."""
    print("=" * 55)
    print("       CRAFT BREWERY BATCH COST CALCULATOR")
    print("=" * 55)

    print("\n--- Batch Parameters ---")
    print(f"  Batch size          : {result['barrels']:.1f} barrels")
    print(f"  Grain usage         : {result['lb_per_barrel']:.1f} lb/barrel")
    print(f"  Hops usage          : {result['oz_per_barrel']:.2f} oz/barrel")
    print(f"  Yeast units/batch   : {result['yeast_units_per_batch']:.0f}")
    print(f"  Packaging units     : {result['units_per_barrel']:.0f}/barrel")
    print(f"  Margin              : {result['margin_pct']:.0f}%")

    print("\n--- Ingredient Cost Breakdown ---")
    print(f"  Grain   ({result['grain_cost_per_lb']:.2f} $/lb x {result['lb_per_barrel']} lb x {result['barrels']} bbl)   = ${result['grain_cost_total']:>8.2f}")
    print(f"  Hops    ({result['hops_cost_per_oz']:.2f} $/oz  x {result['oz_per_barrel']} oz  x {result['barrels']} bbl)   = ${result['hops_cost_total']:>8.2f}")
    print(f"  Yeast   ({result['yeast_cost_per_unit']:.2f} $/unit x {result['yeast_units_per_batch']:.0f} unit            = ${result['yeast_cost_total']:>8.2f}")
    print(f"  Packaging ({result['packaging_cost_per_unit']:.2f} $/unit x {result['units_per_barrel']:.0f}/bbl x {result['barrels']} bbl)  = ${result['packaging_cost_total']:>8.2f}")

    print("\n--- Summary ---")
    print(f"  Total batch cost            : ${result['total_cost']:>8.2f}")
    print(f"  Cost per barrel             : ${result['cost_per_barrel']:>8.2f}")
    print(f"  Recommended sell price/bbl  : ${result['recommended_price_per_barrel']:>8.2f}")
    print("\n" + "=" * 55)


# ---------------------------------------------------------------------------
# Sample run (executed on import / direct script run)
# ---------------------------------------------------------------------------

def main():
    # Sample batch: 5-barrel batch with the default inputs above
    sample_inputs = BatchInputs(
        grain_cost_per_lb=0.60,        # $0.60 / lb of grain
        hops_cost_per_oz=1.00,         # $1.00  / oz of hops
        yeast_cost_per_unit=5.00,      # $5.00  / yeast unit
        packaging_cost_per_unit=0.10,  # $0.10  / bottle
        barrels=5.0,                   # 5 barrels
        oz_per_barrel=1.0,             # 1 oz hops per barrel
        lb_per_barrel=20.0,            # 20 lb grain per barrel
        yeast_units_per_batch=1.0,
        units_per_barrel=325.0,        # ~325 bottles per barrel
        margin_pct=30.0,               # 30% margin
    )

    result = calculate_batch_cost(sample_inputs)
    display_results(result)
    return result


if __name__ == "__main__":
    main()
