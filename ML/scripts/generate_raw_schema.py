"""Sprint 4 (Backend Integration) support artifact.

Writes ML/saved_models/raw_schema.json: the ordered list of raw NHAMCS
column names PreprocessingPipeline.transform() expects to find present
(even if empty) in any DataFrame passed to it. Several cleaning steps
(e.g. ML.cleaning.dtype_correction.convert_boolean_columns) index a fixed,
previously-learned column list without an existence check, so a raw
record with a column *missing entirely* -- as opposed to present but
null -- raises a KeyError at transform time.

The backend's PatientRecordAssembler (Backend/app/services/) uses this
artifact to build a full-width raw record from a curated, human-sized
request payload, leaving every column the client didn't supply as null so
the pipeline's own fitted median / "Missing"-category imputation fills it
in exactly as it would for any other missing value.

This performs no training and no preprocessing -- it only records column
names, which is why it is a lightweight standalone script rather than
something recomputed at backend startup (loading the raw ~16k-row SAS
dataset takes several seconds and the backend should not depend on the
raw dataset being present at runtime).
"""

import json

from ML.ingestion.config import load_config, resolve_repo_path
from ML.ingestion.loader import load_dataset

OUTPUT_PATH = resolve_repo_path("ML/saved_models/raw_schema.json")


def main() -> None:
    config = load_config()
    dataframe, _metadata = load_dataset(config)

    payload = {
        "columns": list(dataframe.columns),
        "column_count": dataframe.shape[1],
        "source": config["dataset"]["raw_path"],
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {payload['column_count']} raw columns to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
