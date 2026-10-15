import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
MIN_DWELLS_PER_PUBLIC_BIN = 5


@pytest.mark.parametrize("split_name", ["S2_to_S3", "S3_to_S2"])
@pytest.mark.parametrize("component_name, reference_key", [("axial", "rmse_fx_N"), ("vertical", "rmse_fv_N")])
def test_grouped_statistics_preserve_validation_and_hide_individual_dwells(split_name, component_name, reference_key):
    measurements = json.loads((ROOT / "data/validation_bins.json").read_text())
    summary = json.loads((ROOT / "data/characterization_summary.json").read_text())
    split = measurements["splits"][split_name]
    component = split["components"][component_name]
    bins = component["bins"]
    reference = summary["map_validation"][split_name]

    dwell_count = sum(group["n_dwells"] for group in bins)
    squared_error_sum = sum(group["squared_error_sum_N2"] for group in bins)
    recovered_rmse_newtons = np.sqrt(squared_error_sum / dwell_count)

    assert dwell_count == reference["n"] == split["n_dwells"]
    assert recovered_rmse_newtons == pytest.approx(reference[reference_key], rel=1e-12)
    assert component["rmse_N"] == pytest.approx(recovered_rmse_newtons, rel=1e-12)
    assert all(group["n_dwells"] >= MIN_DWELLS_PER_PUBLIC_BIN for group in bins)
    for group in bins:
        expected_residual_newtons = group["mean_predicted_N"] - group["mean_measured_N"]
        assert group["mean_residual_N"] == pytest.approx(expected_residual_newtons, abs=1e-12)
