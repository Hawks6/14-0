from app.simulation.calibrate import run_calibration

def test_calibration_distribution():
    results = run_calibration(2000)
    assert 154.0 <= results["mean_score"] <= 163.0, f"Mean score {results['mean_score']} outside [154, 163]"
    assert 25.0 <= results["std_score"] <= 35.0, f"Std dev {results['std_score']} outside [25, 35]"
    assert 5.5 <= results["mean_wickets"] <= 7.5, f"Mean wickets {results['mean_wickets']} outside [5.5, 7.5]"
