# batch_cost_calculator.py
"""
Craft Brewery Batch Cost Calculator
====================================
Inspired by tfrayner/beerfestdb's CBF_beer_price_calculator.py
(https://github.com/tfrayner/beerfestdb/blob/main/tool_dashboard/CBF_beer_price_calculator.py)

The original tool calculates beer sale prices based on cask cost and ABV-based
pricing, using whichever is greater, then rounds up. This CLI adaptation focuses
on batch-level cost accounting for craft brewers: it tallies ingredient costs,
computes total batch cost and cost-per-barrel, then applies a configurable margin
to recommend a selling price per barrel.

Usage:
    python batch_cost_calculator.py
"""

from dataclasses import dataclass
from typing import Optional
import math


# -- Data Structures --

@dataclass
class IngredientCosts:
    """Per-unit cost inputs for a brewing batch."""
    grain_per_lb: float    # $/lb
    hops_per_oz: float     # $/oz
    yeast_per_unit: float  # $/unit
    packaging_per_unit: float  # $/unit (kegs, bottles, cans, etc.)


@dataclass
class BatchSpecs:
    """Batch sizing and quantity inputs."""
    batch_size_barrels: float   # volume in barrels (1 barrel = 31 US gallons)
    grain_lbs: float            # lbs of grain used
    hops_oz: float              # oz of hops used
    yeast_units: int = 1        # number of yeast units (packs/vials)
    packaging_units: int = 1    # number of packaging units (kegs, bottles, etc.)


@dataclass
class CostResult:
    """Computed cost and pricing results."""
    total_ingredient_cost: float
    total_packaging_cost: float
    total_batch_cost: float
    cost_per_barrel: float
    margin_percent: float
    recommended_price_per_barrel: float


# -- Calculator Engine --

class BatchCostCalculator:
    """
    Calculates total batch cost, cost-per-barrel, and recommended selling price.

    Pricing logic mirrors the reference implementation's "use whichever is
    greater" principle: the recommended price is the greater of
    (a) cost-per-barrel x (1 + margin)  [cost-plus pricing]
    (b) a minimum market-floor price per barrel (configurable, default $0.00)
    """

    BARREL_TO_GALLONS = 31.0  # US beer barrel

    def __init__(self, market_floor_per_barrel: float = 0.0):
        self.market_floor_per_barrel = market_floor_per_barrel

    def calculate(
        self,
        ingredients: IngredientCosts,
        batch: BatchSpecs,
        margin_percent: float,
    ) -> CostResult:
        # --- Ingredient costs ---
        grain_cost     = ingredients.grain_per_lb  * batch.grain_lbs
        hops_cost      = ingredients.hops_per_oz    * batch.hops_oz
        yeast_cost     = ingredients.yeast_per_unit * batch.yeast_units
        packaging_cost = ingredients.packaging_per_unit * batch.packaging_units

        total_ingredient_cost = grain_cost + hops_cost + yeast_cost
        total_packaging_cost   = packaging_cost
        total_batch_cost       = total_ingredient_cost + total_packaging_cost

        # --- Per-barrel metrics ---
        cost_per_barrel = total_batch_cost / batch.batch_size_barrels

        # --- Recommended selling price (greater of cost-plus or market floor) ---
        cost_plus_price = cost_per_barrel * (1.0 + margin_percent / 100.0)
        recommended_price = max(cost_plus_price, self.market_floor_per_barrel)

        # Round up to nearest cent (mirrors the reference's math.ceil rounding)
        recommended_price = math.ceil(recommended_price * 100) / 100

        return CostResult(
            total_ingredient_cost=round(total_ingredient_cost, 2),
            total_packaging_cost=round(total_packaging_cost, 2),
            total_batch_cost=round(total_batch_cost, 2),
            cost_per_barrel=round(cost_per_barrel, 2),
            margin_percent=margin_percent,
            recommended_price_per_barrel=recommended_price,
        )


# -- Pretty Printer --

def print_report(result: CostResult, batch: BatchSpecs):
    divider = "=" * 56
    print(f"\n{divider}")
    print("       CRAFT BREWERY BATCH COST REPORT")
    print(divider)
    print(f"  Batch Size          : {batch.batch_size_barrels:.1f} barrels "
          f"({batch.batch_size_barrels * BatchCostCalculator.BARREL_TO_GALLONS:.0f} gal)")
    print(f"  Grain               : {batch.grain_lbs:.1f} lbs")
    print(f"  Hops                : {batch.hops_oz:.1f} oz")
    print(f"  Yeast               : {batch.yeast_units} unit(s)")
    print(f"  Packaging           : {batch.packaging_units} unit(s)")
    print(f"  Margin              : {result.margin_percent:.1f}%")
    print("-" * 56)
    print(f"  Total Ingredient $  : ${result.total_ingredient_cost:>8.2f}")
    print(f"  Total Packaging $   : ${result.total_packaging_cost:>8.2f}")
    print(f"  ---------------------------")
    print(f"  TOTAL BATCH COST    : ${result.total_batch_cost:>8.2f}")
    print(f"  COST / BARREL       : ${result.cost_per_barrel:>8.2f}")
    print("-" * 56)
    print(f"  >> RECOMMENDED PRICE: ${result.recommended_price_per_barrel:>8.2f}")
    print(f"                     (per barrel, cost-plus with {result.margin_percent:.1f}% margin)")
    print(divider)


# -- Sample Run --

if __name__ == "__main__":
    print("\n==> Running sample batch calculation...\n")

    # Sample: 5-barrel all-grain homebrew / small-production batch
    ingredients = IngredientCosts(
        grain_per_lb=1.75,     # $1.75 / lb for base malt
        hops_per_oz=0.85,      # $0.85 / oz for Cascade
        yeast_per_unit=2.50,   # $2.50 / lab yeast pack
        packaging_per_unit=8.00, # $8.00 / 5-gal keg
    )

    batch = BatchSpecs(
        batch_size_barrels=5.0,
        grain_lbs=60.0,    # ~60 lbs of grain
        hops_oz=4.0,       # ~4 oz of hops
        yeast_units=2,     # 2 packs of yeast
        packaging_units=31, # 31 kegs (5 gal each = 155 gal = ~5 bbl)
    )

    calculator = BatchCostCalculator(market_floor_per_barrel=0.0)
    result = calculator.calculate(ingredients, batch, margin_percent=45.0)
    print_report(result, batch)

    # --> Second sample: larger production batch with a market floor
    print("\n==> Running production batch with market floor...\n")

    prod_ingredients = IngredientCosts(
        grain_per_lb=1.20,
        hops_per_oz=1.50,
        yeast_per_unit=2.00,
        packaging_per_unit=5.00,
    )

    prod_batch = BatchSpecs(
        batch_size_barrels=10.0,
        grain_lbs=120.0,
        hops_oz=15.0,
        yeast_units=2,
        packaging_units=62,  # 62 kegs (5 gal each) for 10 bbl
    )

    calc_with_floor = BatchCostCalculator(market_floor_per_barrel=85.0)
    prod_result = calc_with_floor.calculate(prod_ingredients, prod_batch, margin_percent=50.0)
    print_report(prod_result, prod_batch)

    print("\n[OK] Calculator executed successfully - no errors.\n")
