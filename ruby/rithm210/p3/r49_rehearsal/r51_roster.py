"""Export one read-only SQLite snapshot of every R49 allocation."""

import argparse
from contextlib import closing
from hashlib import sha256
import json
from pathlib import Path
import sqlite3

from r49_model import PROTOCOL
from r49_store import Ledger

ROSTER_SCHEMA = "rithm-r51-roster-v1"


def group_ref(study):
    return sha256(("rithm-r51:" + study).encode()).hexdigest()


def export_roster(path):
    """Keep prefix records without exporting live study keys or receipt tokens."""
    uri = Path(path).resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as db, db:
        db.execute("BEGIN")
        groups = []
        for (study,) in db.execute("SELECT DISTINCT study FROM r49_events ORDER BY study"):
            events = [{k: v for k, v in event.items() if k != "receipt"}
                      for event in Ledger.load(db, study)]
            groups.append({"group": group_ref(study), "events": events})
    return {"schema": ROSTER_SCHEMA, "source_protocol": PROTOCOL, "groups": groups}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sqlite", type=Path)
    args = parser.parse_args()
    print(json.dumps(export_roster(args.sqlite), indent=2))
