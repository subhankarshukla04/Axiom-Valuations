from typing import Optional, Tuple

_ANCHOR_WEIGHTS = {
    'STORY':                 0.70,
    'HYPERGROWTH':           0.20,
    'GROWTH_TECH':           0.15,
    'DISTRESSED':            0.20,
    'CYCLICAL':              0.10,
    'STABLE_VALUE':          0.15,
    'STABLE_VALUE_LOWGROWTH': 0.15,
}


def apply_sanity_guardrail(final_price: float, analyst_target: Optional[float],
                           current_price: Optional[float]) -> Tuple[float, bool]:
    flagged = False

    if analyst_target and analyst_target > 0:
        if final_price > analyst_target * 4.0:
            final_price = analyst_target * 0.90
            flagged = True
        elif final_price < analyst_target * 0.25:
            final_price = analyst_target * 0.70
            flagged = True

    if current_price and current_price > 0 and not flagged:
        if final_price > current_price * 10.0:
            final_price = current_price * 1.10
            flagged = True

    return final_price, flagged


def apply_analyst_anchor(model_price: float, analyst_target: Optional[float],
                         company_type: str, company_data: dict = None) -> float:
    if not analyst_target or analyst_target <= 0:
        return model_price

    if company_data and company_data.get('_forced_anchor_weight'):
        anchor_weight = company_data['_forced_anchor_weight']
    else:
        anchor_weight = _ANCHOR_WEIGHTS.get(company_type, 0.15)

    return (1 - anchor_weight) * model_price + anchor_weight * analyst_target
