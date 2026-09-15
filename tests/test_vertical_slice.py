import csv, json
from pathlib import Path
from ml_stack.artifacts import VersionManager
from ml_stack.compute import ExperimentCoordinator, audit_deliverable
from ml_stack.data import audit_file
from ml_stack.requirements import RequirementsCompiler
from ml_stack.validation import ValidationLock, ValidationError

def test_requirements_audit_experiments_and_immutable_version(tmp_path):
    data = tmp_path / "fixture.csv"
    with data.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["x", "y"]); writer.writeheader(); writer.writerows([{"x":1,"y":2},{"x":2,"y":4},{"x":3,"y":6}])
    compiler = RequirementsCompiler(tmp_path); lock = compiler.compile([compiler.capture("minimize MAE")]); compiler.write_visible(lock)
    assert audit_file(data, "y")[0 if False else "columns"] == ["x", "y"]
    results = ExperimentCoordinator(tmp_path).run_bounded(data, "y", ["baseline", "scale x", "drop x"])
    assert len(results) == 3 and all(r.provenance["target"] == "y" for r in results)
    source = tmp_path / "bundle"; source.mkdir(); (source / "model.json").write_text("{}")
    manager = VersionManager(tmp_path); version = manager.promote(source, lock.digest); assert manager.verify(version.name)
    try: manager.promote(source, lock.digest, version.name); assert False
    except FileExistsError: pass

def test_validation_rejects_invalid_metric(tmp_path):
    lock = ValidationLock(1, "holdout", 1, 42, "accuracy", 0.8, "fixed").seal(); lock.write(tmp_path / "lock.json")
    try: lock.validate_metric(2.0); assert False
    except ValidationError: pass

def test_deliverable_audit_rejects_missing_column(tmp_path):
    path = tmp_path / "out.csv"; path.write_text("id\\n1\\n")
    audit = audit_deliverable(path, ["prediction"]); assert not audit["valid"]
