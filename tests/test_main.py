import polars as pl
import io
import os
import sys
import pytest
from datetime import datetime, timezone

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_path, ".."))
sys.path.append(parent_path)
from src.data_ingestion.data_consolidation import metar_to_parquet, MetarObservation

def test_metar_to_parquet_basic():
    sample_ingest_metar = [{
      "icaoId": "KDTW",
      "receiptTime": "2025-09-09T12:00:00.000Z",
      "obsTime": 1756946558,
      "reportTime": "2025-09-09T12:00:00.000Z",
      "temp": 20.0,
      "dewp": 10.0,
      "wdir": "NW",
      "wspd": 5,
      "wgst": 10,
      "visib": "10",
      "altim": 29.92,
      "slp": 1013.0,
      "wxString": "Clear",
      "presTend": 0.0,
      "maxT": 22.0,
      "minT": 18.0,
      "maxT24": 23.0,
      "minT24": 17.0,
      "precip": 0.0,
      "pcp3hr": 0.0,
      "pcp6hr": 0.0,
      "pcp24hr": 0.0,
      "snow": 0.0,
      "vertVis": 0,
      "metarType": "METAR",
      "rawOb": "KDTW 091200Z 32005KT 10SM CLR 20/10 A2992",
      "lat": 42.212,
      "lon": -83.353,
      "elev": 645,
      "name": "Detroit Metro",
      "clouds": ["test_cirrus", "test_stratus", "test_cumulus"],
      "fltCat": "VFR"
    }]
    sample_existing_metar = pl.DataFrame([{
        "icaoId": "KDTW",
        "receiptTime": "2025-09-09T13:00:00.000Z",
        "obsTime": 1756950158,
        "reportTime": "2025-09-09T13:00:00.000Z",
        "temp": 22.0,
        "dewp": 12.0,
        "wdir": "E",
        "wspd": 7,
        "wgst": 11,
        "visib": "9",
        "altim": 29.98,
        "slp": 1014.0,
        "wxString": "Partly Cloudy",
        "presTend": 0.05,
        "maxT": 24.0,
        "minT": 20.0,
        "maxT24": 25.0,
        "minT24": 19.0,
        "precip": 0.01,
        "pcp3hr": 0.0,
        "pcp6hr": 0.01,
        "pcp24hr": 0.03,
        "snow": 0.0,
        "vertVis": 0,
        "metarType": "METAR",
        "rawOb": "KDTW 091300Z 09007KT 9SM SCT025 22/12 A2998",
        "lat": 42.212,
        "lon": -83.353,
        "elev": 645,
        "name": "Detroit Metro",
        "fltCat": "VFR"
      },
      {
        "icaoId": "KDTW",
        "receiptTime": "2025-09-08T14:00:00.000Z",
        "obsTime": 1756953758,
        "reportTime": "2025-09-08T14:00:00.000Z",
        "temp": 19.0,
        "dewp": 11.0,
        "wdir": "S",
        "wspd": 10,
        "wgst": 15,
        "visib": "7",
        "altim": 29.90,
        "slp": 1011.0,
        "wxString": "Light Rain",
        "presTend": -0.1,
        "maxT": 20.0,
        "minT": 17.0,
        "maxT24": 21.0,
        "minT24": 16.0,
        "precip": 0.15,
        "pcp3hr": 0.05,
        "pcp6hr": 0.10,
        "pcp24hr": 0.20,
        "snow": 0.0,
        "vertVis": 0,
        "metarType": "METAR",
        "rawOb": "KDTW 091400Z 18010G15KT 7SM -RA 19/11 A2990",
        "lat": 42.212,
        "lon": -83.353,
        "elev": 645,
        "name": "Detroit Metro",
        "fltCat": "MVFR"
    }])
        
    sample_existing_metar = sample_existing_metar.with_columns(
      pl.col("reportTime").str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S%.3fZ")
    )

    sample_existing_metar_buffer = io.BytesIO()
    sample_existing_metar.write_parquet(sample_existing_metar_buffer)

    result_bytes = metar_to_parquet(city="detroit", ingested_metar=sample_ingest_metar, ingest_day=datetime(2025,9,5), existing_metar=sample_existing_metar_buffer.getvalue())

    assert isinstance(result_bytes, bytes)
    assert len(result_bytes) > 0

    compiled_metar_as_parquet = pl.read_parquet(io.BytesIO(result_bytes))

    expected_columns = [
        "icaoId", "receiptTime", "obsTime", "reportTime", "temp", "dewp", "wdir", "wspd", "wgst",
        "visib", "altim", "slp", "wxString", "presTend", "maxT", "minT", "maxT24", "minT24",
        "precip", "pcp3hr", "pcp6hr", "pcp24hr", "snow", "vertVis", "metarType", "rawOb",
        "lat", "lon", "elev", "name", "fltCat"
    ]
    for col in expected_columns:
        assert col in compiled_metar_as_parquet.columns

    assert compiled_metar_as_parquet.height == 2
    # Height should only be two because the logic in metar_to_parquet removes data from ingested reporting day to avoid repeated entries. So only the existing metar entry from 2025-09-04 will persist.
