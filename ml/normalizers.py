from typing import Dict, Optional, Tuple

from ml._config import (
    CYCLICAL_TAGS, SECULAR_DECLINE_TAGS,
    SUBSECTOR_MULT, SECTOR_CAPEX_NORM, CAPEX_NORM_DEFAULT,
    BLEND_WEIGHTS,
)


def smart_ebitda(ebitda_history: list, tag: str) -> Tuple[float, str]:
    if not ebitda_history or len(ebitda_history) < 2:
        val = ebitda_history[0] if ebitda_history else 0
        return val, 'em:single'

    eb = [float(x) for x in ebitda_history if x is not None and x != 0]
    if not eb:
        return 0, 'em:zero'

    if tag in CYCLICAL_TAGS:
        return sum(eb[:3]) / len(eb[:3]), 'em:cyc3yr'

    if tag in SECULAR_DECLINE_TAGS:
        return eb[0], 'em:secular_decline'

    if len(eb) < 3:
        return eb[0], 'em:recent'

    improving = eb[0] > eb[1] > eb[2]
    declining = eb[0] < eb[1] < eb[2]

    if improving or declining:
        return eb[0], 'em:trend'

    return sum(eb[:3]) / 3, 'em:3yavg'


def normalize_capex(actual_pct: float, tag: str) -> float:
    norm = SECTOR_CAPEX_NORM.get(tag, CAPEX_NORM_DEFAULT)
    return min(actual_pct, norm)


def get_multiples(tag: str, company_growth: float) -> Tuple[Optional[float], Optional[float]]:
    entry = SUBSECTOR_MULT.get(tag)
    if not entry:
        return 12.0, 20.0

    base_ev, base_pe, sector_median_g = entry

    if base_ev is None:
        return None, None

    if sector_median_g and sector_median_g > 0 and company_growth and company_growth > 0:
        adj = (company_growth / sector_median_g) ** 0.4
        adj = max(0.5, min(adj, 1.5))
    else:
        adj = 1.0

    return base_ev * adj, base_pe * adj


def get_blend_weights(company_type: str, dcf_value: float) -> Dict[str, float]:
    weights = dict(BLEND_WEIGHTS.get(company_type, BLEND_WEIGHTS['STABLE_VALUE']))

    if dcf_value is not None and dcf_value < 0:
        weights['dcf'] = 0.0
        total = weights['ev'] + weights['pe']
        if total > 0:
            weights['ev'] = weights['ev'] / total
            weights['pe'] = weights['pe'] / total

    return weights
