#!/usr/bin/env python

"""Tests for `opensea` package."""

import json
import pytest
import os
from opensea import OpenseaAPI, utils

@pytest.fixture
def api():
    old_key = "989fc3e2f28a40d88b6939d5da699bef"
    # new_key = "8e6b3a19779f439188118f94401b6da7"
    return OpenseaAPI(apikey=old_key)


@pytest.fixture
def api_without_key():
    return OpenseaAPI()


@pytest.fixture
def export_folder():
    test_path = "tests/exports/"
    # create dir if not exists
    if not os.path.isdir(test_path):
        os.mkdir(test_path)
    return test_path


@pytest.fixture
def asset_contract_address():
    return "0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb"


@pytest.fixture
def collection_slug():
    return "cryptopunks"


pytest.mark.skip(reason="Works, but runs for a long time so test separately!")
def test_events_backfill(api: OpenseaAPI, export_folder):
    backfill_until = utils.datetime_utc(2022, 2, 17, 8, 59)
    start_backfilling_from_here = utils.datetime_utc(2022, 2, 17, 10, 0)
    
    event_generator = api.events_backfill(start=start_backfilling_from_here,
                                          until=backfill_until,
                                          event_type="successful")
    i = 0
    for event in event_generator:
        i += 1
        print("----------\nDownloading data from OpenSea...")
        if event is not None:
            utils.export_file(json.dumps(event).encode(), export_folder + f"{i}_pagination_export.json")
            print(f"Data downloaded until this time: {event['asset_events'][-1]['created_date']}")
    print("All rows have been ingested from the defined time period!")


# it should return ConnectionError as non apikey requests get blocked
def test_apikey_none(api_without_key: OpenseaAPI, export_folder):
    export_file = export_folder + "test_no_apikey.json"
    with pytest.raises(ConnectionError):
        api_without_key.events(limit=1, export_file_name=export_file)


def test_make_request_no_args(api: OpenseaAPI):
    with pytest.raises(ValueError):
        api._make_request()


def test_events(api: OpenseaAPI, export_folder):
    export_file = export_folder + "test_events.json"
    result = api.events(limit=1, export_file_name=export_file)
    assert isinstance(result, dict)
    assert os.path.exists(export_file)


def test_asset(api: OpenseaAPI, asset_contract_address, export_folder):
    export_file = export_folder + "test_asset.json"
    result = api.asset(
        asset_contract_address=asset_contract_address,
        token_id="1",
        export_file_name=export_file,
    )
    result = api.events(limit=1)
    assert isinstance(result, dict)
    assert os.path.exists(export_file)


def test_assets(api: OpenseaAPI, export_folder):
    export_file = export_folder + "test_assets.json"
    result = api.assets(limit=1, export_file_name=export_file)
    assert isinstance(result, dict)
    assert os.path.exists(export_file)


def test_contract(api: OpenseaAPI, asset_contract_address, export_folder):
    export_file = export_folder + "test_contract.json"
    result = api.contract(
        asset_contract_address=asset_contract_address, export_file_name=export_file
    )
    assert isinstance(result, dict)
    assert os.path.exists(export_file)


def test_collection(api: OpenseaAPI, collection_slug, export_folder):
    export_file = export_folder + "test_collection.json"
    result = api.collection(
        collection_slug=collection_slug, export_file_name=export_file
    )
    assert isinstance(result, dict)
    assert os.path.exists(export_file)


def test_collection_stats(api: OpenseaAPI, collection_slug, export_folder):
    export_file = export_folder + "test_collection_stats.json"
    result = api.collection_stats(
        collection_slug=collection_slug, export_file_name=export_file
    )
    assert isinstance(result, dict)
    assert os.path.exists(export_file)


def test_collections(api: OpenseaAPI, export_folder):
    export_file = export_folder + "test_collections.json"
    result = api.collections(limit=1, export_file_name=export_file)
    assert isinstance(result, dict)
    assert os.path.exists(export_file)


def test_bundles(api: OpenseaAPI, export_folder):
    export_file = export_folder + "test_bundles.json"
    result = api.collections(limit=1, export_file_name=export_file)
    assert isinstance(result, dict)
    assert os.path.exists(export_file)


@pytest.mark.skip(reason="TODO")
def test_collections_by_date(api: OpenseaAPI, export_folder):
    export_file = export_folder + "test_coll_by_time.json"
    result = api.collections(limit=1, export_file_name=export_file)
    assert isinstance(result, dict)
    assert os.path.exists(export_file)
