from ml.pipeline import calibrate
from ml.alt_models import run_alternative_model, bank_model, reit_model, growth_loss_model
from ml.anchoring import apply_analyst_anchor, apply_sanity_guardrail
from ml.calibrator import apply_ml_correction, train_calibration_model, ML_MODEL_PATH
from ml.log import log_prediction, PREDICTION_LOG_PATH
from ml.normalizers import get_blend_weights, get_multiples, smart_ebitda, normalize_capex
from ml.tagging import get_sub_sector_tag, classify_company
from ml.backtest import run_backtest
from ml._config import (
    TICKER_TAG_MAP, SUBSECTOR_MULT, CYCLICAL_TAGS, SECULAR_DECLINE_TAGS,
    TERMINAL_GROWTH_BY_TAG, TERMINAL_GROWTH_DEFAULT,
    SECTOR_CAPEX_NORM, CAPEX_NORM_DEFAULT,
    SECTOR_PB, TICKER_PB, SECTOR_PFFO, TICKER_PFFO,
    BLEND_WEIGHTS,
)

MIN_TRAINING_SAMPLES = 15
