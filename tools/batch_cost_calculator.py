"""
Craft Brewery Batch Cost Calculator
====================================
Inspired by: tfrayner/beerfestdb CBF_beer_price_calculator.py

A standalone Python module for calculating craft brewery batch costs,
including ingredient costs (grain, hops, yeast, packaging), batch size
in barrels, total cost, cost-per-barrel, and a configurable margin-based
recommended selling price per barrel.
"""


def calculate_batch_cost(
    grain_cost_per_lb: float,
    hops_cost_per_oz: float,
    yeast_cost_per_unit: float,
    packaging_cost_per_unit: float,
    batch_size_barrels: float,
    margin_percent: float = 30.0,
    grain_lbs_per_barrel: float = 10.0,
    hops_oz_per_barrel: float = 1.5,
    yeast_units_per_barrel: float = 1.0,
    packaging_units_per_barrel: float = 1.0,
) -> dict:
    """
    Calculate total batch cost, cost per barrel, and recommended selling price.

    Args:
        grain_cost_per_lb: Cost of grain in dollars per pound.
        hops_cost_per_oz: Cost of hops in dollars per ounce.
        yeast_cost_per_unit: Cost of yeast per unit.
        packaging_cost_per_unit: Cost of packaging per unit.
        batch_size_barrels: Batch size in barrels.
        margin_percent: Desired profit margin as a percentage (default 30.0%).
        grain_lbs_per_barrel: Grain usage per barrel (default 10.0 lbs).
        hops_oz_per_barrel: Hops usage per barrel (default 1.5 oz).
        yeast_units_per_barrel: Yeast usage per barrel (default 1.0 unit).
        packaging_units_per_barrel: Packaging usage per barrel (default 1.0 unit).

    Returns:
        A dictionary containing:
            - batch_size_barrels: The batch size in barrels.
            - ingredients: Breakdown of each ingredient with quantities and costs.
            - total_cost: Total batch cost in dollars.
            - cost_per_barrel: Cost per barrel in dollars.
            - margin_percent: The margin percentage applied.
            - selling_price_per_barrel: Recommended selling price per barrel.
    """
    # Quantities for the full batch
    total_grain_lbs = grain_lbs_per_barrel * batch_size_barrels
    total_hops_oz = hops_oz_per_barrel * batch_size_barrels
    total_yeast_units = yeast_units_per_barrel * batch_size_barrels
    total_packaging_units = packaging_units_per_barrel * batch_size_barrels

    # Ingredient costs
    grain_cost = total_grain_lbs * grain_cost_per_lb
    hops_cost = total_hops_oz * hops_cost_per_oz
    yeast_cost = total_yeast_units * yeast_cost_per_unit
    packaging_cost = total_packaging_units * packaging_cost_per_unit

    # Totals
    total_cost = grain_cost + hops_cost + yeast_cost + packaging_cost
    cost_per_barrel = total_cost / batch_size_barrels
    selling_price_per_barrel = cost_per_barrel * (1 + margin_percent / 100)

    return {
        "batch_size_barrels": batch_size_barrels,
        "ingredients": {
            "grain": {
                "quantity_lbs": total_grain_lbs,
                "unit_cost": grain_cost_per_lb,
                "total_cost": round(grain_cost, 2),
            },
            "hops": {
                "quantity_oz": total_hops_oz,
                "unit_cost": hops_cost_per_oz,
                "total_cost": round(hops_cost, 2),
            },
            "yeast": {
                "quantity_units": total_yeast_units,
                "unit_cost": yeast_cost_per_unit,
                "total_cost": round(yeast_cost, 2),
            },
            "packaging": {
                "quantity_units": total_packaging_units,
                "unit_cost": packaging_cost_per_unit,
                "total_cost": round(packaging_cost, 2),
            },
        },
        "total_cost": round(total_cost, 2),
        "cost_per_barrel": round(cost_per_barrel, 2),
        "margin_percent": margin_percent,
        "selling_price_per_barrel": round(selling_price_per_barrel, 2),
    }


def print_report(result: dict) -> None:
    """Print a formatted, human-readable batch cost report."""
    print("=" * 56)
    print("  CRAFT BREWERY BATCH COST CALCULATOR")
    print("=" * 56)
    print(f"  Batch Size: {result['batch_size_barrels']} barrels")
    print("-" * 56)
    print("  INGREDIENT COSTS:")
    for name, data in result["ingredients"].items():
        qty = data["quantity_lbs"] if name == "grain" else (
            data["quantity_oz"] if name == "hops" else data["quantity_units"]
        )
        unit = "lbs" if name == "grain" else ("oz" if name == "hops" else "units")
        print(
            f"    {name.capitalize():12s} {qty:>8.2f} {unit:>4s}  "
            f"@ ${data['unit_cost']:.2f}/{unit:>3s}  =  ${data['total_cost']:>8.2f}"
        )
    print("-" * 56)
    print(f"  Total Cost:              ${result['total_cost']:>10.2f}")
    print(f"  Cost per Barrel:         ${result['cost_per_barrel']:>10.2f}")
    print(f"  Margin:                  {result['margin_percent']:>10.1f}%")
    print(f"  Recommended Sell/Barrel: ${result['selling_price_per_barrel']:>10.2f}")
    print("=" * 56)


if __name__ == "__main__":
    # Sample batch: 5 barrels, 30% margin, typical craft beer recipe rates
    sample = calculate_batch_cost(
        grain_cost_per_lb=2.50,
        hops_cost_per_oz=15.00,
        yeast_cost_per_unit=8.50,
        packaging_cost_per_unit=3.75,
        batch_size_barrels=5,
        margin_percent=30.0,
    )
    print_report(sample)

    # Validation:
    #   grain: 10 lbs/bbl * 5 bbl = 50 lbs * $2.50 = $125.00
    #   hops:  1.5 oz/bbl  * 5 bbl =  7.5 oz * $15.00 = $112.50
    #   yeast: 1.0 unit/bbl * 5 bbl =  5.0    * $8.50 = $ 42.50
    #   pkg:   1.0 unit/bbl * 5 bbl =  5.0    * $3.75 = $ 18.75
    #   total: $298.75
    #   cpb:   $298.75 / 5 = $59.75
    #   sell:  $59.75 * 1.30 = $77.675 -> $77.68
    assert sample["ingredients"]["grain"]["total_cost"] == 125.00
    assert sample["ingredients"]["hops"]["total_cost"] == 112.50
    assert sample["ingredients"]["yeast"]["total_cost"] == 42.50
    assert sample["ingredients"]["packaging"]["total_cost"] == 18.75
    assert sample["total_cost"] == 298.75
    assert sample["cost_per_barrel"] == 59.75
    assert sample["selling_price_per_barrel"] in (77.67, 77.68)
    assert sample["margin_percent"] == 30.0

    # Custom margin test
    custom = calculate_batch_cost(2.50, 15.00, 8.50, 3.75, 5, margin_percent=40.0)
    assert custom["selling_price_per_barrel"] == round(59.75 * 1.40, 2)

    print("\n[VALIDATION PASSED] All assertions successful.")