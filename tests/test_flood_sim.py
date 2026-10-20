import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from flood_sim import (make_terrain, risk_summary, simulate_parallel,  # noqa: E402
                       simulate_serial)


def test_terrain_shape_and_nonnegative():
    t = make_terrain(50)
    assert t.shape == (50, 50)
    assert (t >= 0).all()


def test_serial_equals_parallel():
    t = make_terrain(40)
    ps, _ = simulate_serial(t, 400)
    pp, _ = simulate_parallel(t, 400, workers=2)
    assert np.allclose(ps, pp)


def test_probability_range_and_coast_more_risky():
    t = make_terrain(40)
    p, _ = simulate_serial(t, 400)
    assert p.min() >= 0 and p.max() <= 1
    assert p[:5].mean() > p[-5:].mean()   # dekat pantai lebih rawan


def test_risk_summary_sums_to_one():
    t = make_terrain(40)
    p, _ = simulate_serial(t, 200)
    s = risk_summary(p)
    assert abs(s["tinggi"] + s["sedang"] + s["rendah"] - 1) < 1e-9
