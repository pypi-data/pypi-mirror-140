from datetime import datetime, timedelta

import pytest

from ..conftest import MockStarletteRequest

STAC_CORE_ROUTES = [
    "GET /",
    "GET /collections",
    "GET /collections/{collectionId}",
    "GET /collections/{collectionId}/items",
    "GET /collections/{collectionId}/items/{itemId}",
    "GET /conformance",
    "GET /search",
    "POST /search",
]

STAC_TRANSACTION_ROUTES = [
    "DELETE /collections/{collectionId}",
    "DELETE /collections/{collectionId}/items/{itemId}",
    "POST /collections",
    "POST /collections/{collectionId}/items",
    "PUT /collections",
    "PUT /collections/{collectionId}/items",
]


def test_post_search_content_type(app_client):
    params = {"limit": 1}
    resp = app_client.post("search", json=params)
    assert resp.headers["content-type"] == "application/geo+json"


def test_get_search_content_type(app_client):
    resp = app_client.get("search")
    assert resp.headers["content-type"] == "application/geo+json"


def test_api_headers(app_client):
    resp = app_client.get("/api")
    assert (
        resp.headers["content-type"] == "application/vnd.oai.openapi+json;version=3.0"
    )
    assert resp.status_code == 200


@pytest.mark.skip(reason="not working")
def test_core_router(api_client):
    core_routes = set(STAC_CORE_ROUTES)
    api_routes = set(
        [f"{list(route.methods)[0]} {route.path}" for route in api_client.app.routes]
    )
    assert not core_routes - api_routes


@pytest.mark.skip(reason="not working")
def test_transactions_router(api_client):
    transaction_routes = set(STAC_TRANSACTION_ROUTES)
    api_routes = set(
        [f"{list(route.methods)[0]} {route.path}" for route in api_client.app.routes]
    )
    assert not transaction_routes - api_routes


def test_app_transaction_extension(app_client, load_test_data):
    item = load_test_data("test_item.json")
    resp = app_client.post(f"/collections/{item['collection']}/items", json=item)
    assert resp.status_code == 200


def test_app_search_response(load_test_data, app_client, mongo_transactions):
    item = load_test_data("test_item.json")
    mongo_transactions.create_item(item, request=MockStarletteRequest)

    resp = app_client.get("/search", params={"ids": ["test-item"]})
    assert resp.status_code == 200
    resp_json = resp.json()

    assert resp_json.get("type") == "FeatureCollection"
    # stac_version and stac_extensions were removed in v1.0.0-beta.3
    assert resp_json.get("stac_version") is None
    assert resp_json.get("stac_extensions") is None


def test_app_context_extension(load_test_data, app_client, mongo_transactions):
    item = load_test_data("test_item.json")
    mongo_transactions.create_item(item, request=MockStarletteRequest)

    resp = app_client.get("/search", params={"collections": ["test-collection"]})
    assert resp.status_code == 200
    resp_json = resp.json()
    assert "context" in resp_json
    assert resp_json["context"]["returned"] == resp_json["context"]["matched"] == 1


def test_app_fields_extension(load_test_data, app_client, mongo_transactions):
    item = load_test_data("test_item.json")
    mongo_transactions.create_item(item, request=MockStarletteRequest)

    resp = app_client.get("/search", params={"collections": ["test-collection"]})
    assert resp.status_code == 200
    resp_json = resp.json()
    assert list(resp_json["features"][0]["properties"]) == ["datetime"]


def test_app_query_extension_gt(load_test_data, app_client, mongo_transactions):
    test_item = load_test_data("test_item.json")
    mongo_transactions.create_item(test_item, request=MockStarletteRequest)

    params = {"query": {"proj:epsg": {"gt": test_item["properties"]["proj:epsg"]}}}
    resp = app_client.post("/search", json=params)
    assert resp.status_code == 200
    resp_json = resp.json()
    assert len(resp_json["features"]) == 0


def test_app_query_extension_gte(load_test_data, app_client, mongo_transactions):
    test_item = load_test_data("test_item.json")
    mongo_transactions.create_item(test_item, request=MockStarletteRequest)

    params = {"query": {"proj:epsg": {"gte": test_item["properties"]["proj:epsg"]}}}
    resp = app_client.post("/search", json=params)
    assert resp.status_code == 200
    resp_json = resp.json()
    assert len(resp_json["features"]) == 1


def test_app_query_extension_limit_lt0(load_test_data, app_client, mongo_transactions):
    item = load_test_data("test_item.json")
    mongo_transactions.create_item(item, request=MockStarletteRequest)

    params = {"limit": -1}
    resp = app_client.post("/search", json=params)
    assert resp.status_code == 400


def test_app_query_extension_limit_gt10000(
    load_test_data, app_client, mongo_transactions
):
    item = load_test_data("test_item.json")
    mongo_transactions.create_item(item, request=MockStarletteRequest)

    params = {"limit": 10001}
    resp = app_client.post("/search", json=params)
    assert resp.status_code == 400


def test_app_query_extension_limit_10000(
    load_test_data, app_client, mongo_transactions
):
    item = load_test_data("test_item.json")
    mongo_transactions.create_item(item, request=MockStarletteRequest)

    params = {"limit": 10000}
    resp = app_client.post("/search", json=params)
    assert resp.status_code == 200


def test_app_sort_extension(load_test_data, app_client, mongo_transactions):
    first_item = load_test_data("test_item.json")
    item_date = datetime.strptime(
        first_item["properties"]["datetime"], "%Y-%m-%dT%H:%M:%SZ"
    )
    mongo_transactions.create_item(first_item, request=MockStarletteRequest)

    second_item = load_test_data("test_item.json")
    second_item["id"] = "another-item"
    another_item_date = item_date - timedelta(days=1)
    second_item["properties"]["datetime"] = another_item_date.strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    mongo_transactions.create_item(second_item, request=MockStarletteRequest)

    params = {
        "collections": [first_item["collection"]],
        "sortby": [{"field": "datetime", "direction": "desc"}],
    }
    resp = app_client.post("/search", json=params)
    assert resp.status_code == 200
    resp_json = resp.json()
    assert resp_json["features"][0]["id"] == first_item["id"]
    assert resp_json["features"][1]["id"] == second_item["id"]


def test_search_invalid_date(load_test_data, app_client, mongo_transactions):
    item = load_test_data("test_item.json")
    mongo_transactions.create_item(item, request=MockStarletteRequest)

    params = {
        "datetime": "2020-XX-01/2020-10-30",
        "collections": [item["collection"]],
    }

    resp = app_client.post("/search", json=params)
    assert resp.status_code == 400


def test_search_point_intersects(load_test_data, app_client, mongo_transactions):
    item = load_test_data("test_item.json")
    mongo_transactions.create_item(item, request=MockStarletteRequest)

    point = [150.04, -33.14]
    intersects = {"type": "Point", "coordinates": point}

    params = {
        "intersects": intersects,
        "collections": [item["collection"]],
    }
    resp = app_client.post("/search", json=params)
    assert resp.status_code == 200
    resp_json = resp.json()
    assert len(resp_json["features"]) == 1


def test_datetime_non_interval(load_test_data, app_client, mongo_transactions):
    item = load_test_data("test_item.json")
    mongo_transactions.create_item(item, request=MockStarletteRequest)
    alternate_formats = [
        "2020-02-12T12:30:22+00:00",
        "2020-02-12T12:30:22.00Z",
        "2020-02-12T12:30:22Z",
        "2020-02-12T12:30:22.00+00:00",
    ]
    for date in alternate_formats:
        params = {
            "datetime": date,
            "collections": [item["collection"]],
        }

        resp = app_client.post("/search", json=params)
        assert resp.status_code == 200
        resp_json = resp.json()
        # datetime is returned in this format "2020-02-12T12:30:22+00:00"
        assert resp_json["features"][0]["properties"]["datetime"][0:19] == date[0:19]


def test_bbox_3d(load_test_data, app_client, mongo_transactions):
    item = load_test_data("test_item.json")
    mongo_transactions.create_item(item, request=MockStarletteRequest)

    australia_bbox = [106.343365, -47.199523, 0.1, 168.218365, -19.437288, 0.1]
    params = {
        "bbox": australia_bbox,
        "collections": [item["collection"]],
    }
    resp = app_client.post("/search", json=params)
    assert resp.status_code == 200
    resp_json = resp.json()
    assert len(resp_json["features"]) == 1


def test_search_line_string_intersects(load_test_data, app_client, mongo_transactions):
    item = load_test_data("test_item.json")
    mongo_transactions.create_item(item, request=MockStarletteRequest)

    line = [[150.04, -33.14], [150.22, -33.89]]
    intersects = {"type": "LineString", "coordinates": line}

    params = {
        "intersects": intersects,
        "collections": [item["collection"]],
    }
    resp = app_client.post("/search", json=params)
    assert resp.status_code == 200
    resp_json = resp.json()
    assert len(resp_json["features"]) == 1
