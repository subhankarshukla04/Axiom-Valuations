import json
import logging
import os
import pickle
from datetime import datetime

from ml._config import SUBSECTOR_MULT
from ml.log import PREDICTION_LOG_PATH

logger = logging.getLogger(__name__)

ML_MODEL_PATH     = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml_calibration_model.pkl')
ML_METADATA_PATH  = ML_MODEL_PATH.replace('.pkl', '_metadata.json')
MIN_TRAINING_SAMPLES = 15

_COMPANY_TYPES = ['DISTRESSED', 'STORY', 'HYPERGROWTH', 'GROWTH_TECH',
                  'CYCLICAL', 'STABLE_VALUE', 'STABLE_VALUE_LOWGROWTH']
_EBITDA_METHODS  = ['em:single', 'em:zero', 'em:cyc3yr', 'em:secular_decline',
                    'em:recent', 'em:trend', 'em:3yavg', 'backtest']
_MARKET_REGIMES  = ['risk_on', 'transition', 'risk_off', 'unknown']

# Sector vol priors for inference — real vol computed during training
_TAG_VOL_DEFAULT = {
    'biotech_clinical': 0.55,  'growth_loss': 0.50,   'ev_auto': 0.45,
    'crypto_proxy': 0.60,      'cloud_saas': 0.35,    'rule40_saas': 0.35,
    'semiconductor': 0.32,     'consumer_internet': 0.30,
    'enterprise_software': 0.28, 'cloud_software': 0.30,
    'medical_device': 0.25,    'pharma_largecap': 0.22,
    'health_insurance': 0.20,  'commercial_bank': 0.22,
    'investment_bank': 0.28,   'oil_gas_major': 0.25,  'oil_gas_mid': 0.30,
    'auto_legacy': 0.22,       'defense': 0.18,
    'retail_discount': 0.22,   'retail_ecomm': 0.28,
    'industrial_cong': 0.20,   'telecom': 0.15,
    'consumer_staples': 0.15,  'utility_regulated': 0.12,
    'reit_office': 0.20,       'reit_residential': 0.18,
    'pc_insurance': 0.18,      'pharma': 0.22,
}
_VOL_DEFAULT = 0.25


def _tag_to_int(tag: str) -> int:
    tags = sorted(SUBSECTOR_MULT.keys())
    try:
        return tags.index(tag)
    except ValueError:
        return len(tags)


def _type_to_int(t: str) -> int:
    try:
        return _COMPANY_TYPES.index(t)
    except ValueError:
        return len(_COMPANY_TYPES)


def _method_to_int(m: str) -> int:
    try:
        return _EBITDA_METHODS.index(m)
    except ValueError:
        return len(_EBITDA_METHODS)


def _regime_to_int(r: str) -> int:
    try:
        return _MARKET_REGIMES.index(r)
    except ValueError:
        return len(_MARKET_REGIMES)


def _load_prediction_log() -> list:
    records = []
    if not os.path.exists(PREDICTION_LOG_PATH):
        return records
    with open(PREDICTION_LOG_PATH) as f:
        for line in f:
            try:
                records.append(json.loads(line.strip()))
            except Exception:
                pass
    return records


def _build_features(r: dict) -> list:
    """7-feature vector: [tag_int, type_int, wacc, growth_y1, ebitda_method_int, analyst_ratio, regime_int]"""
    predicted = float(r.get('predicted_price', 1) or 1)
    analyst   = float(r.get('analyst_target', 0) or 0)
    analyst_ratio = (analyst / predicted) if predicted > 0 and analyst > 0 else 1.0
    return [
        _tag_to_int(r.get('sub_sector_tag', '')),
        _type_to_int(r.get('company_type', '')),
        float(r.get('wacc', 0.10) or 0.10),
        float(r.get('growth_y1', 0.05) or 0.05),
        _method_to_int(r.get('ebitda_method', '')),
        analyst_ratio,
        _regime_to_int(r.get('market_regime', 'unknown')),
    ]


def _build_features_extended(r: dict, horizon_days: int = 365, month: int = None) -> list:
    """10-feature vector for walk-forward v2 models (adds horizon, month, volatility)."""
    if month is None:
        month = datetime.utcnow().month
    tag = r.get('sub_sector_tag', '')
    vol = _TAG_VOL_DEFAULT.get(tag, _VOL_DEFAULT)
    return _build_features(r) + [float(horizon_days), float(month), vol]


def train_calibration_model() -> bool:
    try:
        import numpy as np
        from sklearn.pipeline import Pipeline
        from sklearn.compose import ColumnTransformer
        from sklearn.preprocessing import OrdinalEncoder, StandardScaler
        from sklearn.ensemble import GradientBoostingRegressor
    except ImportError:
        logger.warning('scikit-learn not installed — skipping ML training')
        return False

    records = _load_prediction_log()
    labeled = [r for r in records
               if r.get('actual_price_365d') and r.get('predicted_price')]

    # Sort chronologically for walk-forward split
    labeled.sort(key=lambda r: r.get('predicted_at', ''))

    if len(labeled) < MIN_TRAINING_SAMPLES:
        logger.info(f'Only {len(labeled)} labeled samples — need {MIN_TRAINING_SAMPLES}')
        return False

    X = np.array([_build_features(r) for r in labeled])
    y = np.array([
        max(0.2, min(r['actual_price_365d'] / r['predicted_price'], 5.0))
        for r in labeled
    ])

    # Walk-forward 80/20 split — no lookahead bias
    split = int(len(X) * 0.80)
    X_train, X_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]

    # Categorical cols: [0]=tag_int, [1]=type_int, [4]=ebitda_method_int, [6]=regime_int
    # Numeric cols:     [2]=wacc, [3]=growth_y1, [5]=analyst_ratio
    cat_cols = [0, 1, 4, 6]
    num_cols = [2, 3, 5]

    pipeline = Pipeline([
        ('features', ColumnTransformer([
            ('cat', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1), cat_cols),
            ('num', StandardScaler(), num_cols),
        ])),
        ('model', GradientBoostingRegressor(
            n_estimators=150, max_depth=3,
            learning_rate=0.05, subsample=0.8,
            random_state=42,
        )),
    ])

    pipeline.fit(X_train, y_train)

    mae_holdout = float(np.mean(np.abs(pipeline.predict(X_val) - y_val))) if len(X_val) > 0 else None

    with open(ML_MODEL_PATH, 'wb') as f:
        pickle.dump(pipeline, f)

    metadata = {
        'trained_at':   datetime.utcnow().isoformat(),
        'n_samples':    len(labeled),
        'n_train':      len(X_train),
        'n_val':        len(X_val),
        'mae_holdout':  round(mae_holdout, 4) if mae_holdout is not None else None,
        'features':     ['tag_int', 'type_int', 'wacc', 'growth_y1', 'ebitda_method_int', 'analyst_ratio', 'regime_int'],
        'framework':    'sklearn_pipeline_v2',
    }
    with open(ML_METADATA_PATH, 'w') as f:
        json.dump(metadata, f, indent=2)

    logger.info(f'ML pipeline trained: {len(labeled)} samples, holdout MAE={mae_holdout:.4f}')
    return True


def apply_ml_correction(predicted_price: float, company_data: dict) -> float:
    tag   = company_data.get('sub_sector_tag', '')
    ctype = company_data.get('company_type', '')

    if os.path.exists(ML_MODEL_PATH):
        try:
            import numpy as np
            with open(ML_MODEL_PATH, 'rb') as f:
                pipeline = pickle.load(f)
            from ml.log import _get_market_regime

            n_features = 7
            if os.path.exists(ML_METADATA_PATH):
                try:
                    with open(ML_METADATA_PATH) as _mf:
                        n_features = json.load(_mf).get('n_features', 7)
                except Exception:
                    pass

            record = {
                'sub_sector_tag':  tag,
                'company_type':    ctype,
                'wacc':            company_data.get('wacc', 0.10),
                'growth_y1':       company_data.get('growth_rate_y1', 0.05),
                'ebitda_method':   company_data.get('ebitda_method', ''),
                'analyst_target':  company_data.get('analyst_target', 0),
                'predicted_price': predicted_price,
                'market_regime':   _get_market_regime(),
            }
            if n_features >= 10:
                feat = _build_features_extended(record)
            elif n_features == 9:
                feat = _build_features(record) + [float(365), float(datetime.utcnow().month)]
            else:
                feat = _build_features(record)
            correction = float(pipeline.predict(np.array([feat]))[0])
            correction = max(0.4, min(correction, 2.0))
            return predicted_price * correction
        except Exception as e:
            logger.warning(f'ML correction failed: {e}')

    if company_data.get('_non_usd_reporting'):
        return predicted_price

    try:
        import sys
        scripts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts')
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        from calibration_corrections import get_correction
        return predicted_price * get_correction(tag, ctype)
    except Exception:
        pass

    return predicted_price
