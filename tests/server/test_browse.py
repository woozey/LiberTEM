import os
import pytest


pytestmark = [pytest.mark.functional]


@pytest.mark.asyncio
async def test_browse_localfs(default_raw, base_url, http_client):
    conn_url = "{}/api/config/connection/".format(base_url)
    conn_details = {
        'connection': {
            'type': 'local',
            'numWorkers': 2,
        }
    }
    async with http_client.put(conn_url, json=conn_details) as response:
        assert response.status == 200

    browse_path = os.path.dirname(default_raw._path)
    raw_ds_filename = os.path.basename(default_raw._path)
    url = "{}/api/browse/localfs/".format(base_url)
    async with http_client.get(url, params={"path": browse_path}) as resp:
        assert resp.status == 200
        listing = await resp.json()
        assert listing['status'] == 'ok'
        assert listing['messageType'] == 'DIRECTORY_LISTING'
        assert "drives" in listing
        assert "places" in listing
        assert "path" in listing
        assert "files" in listing
        assert "dirs" in listing
        assert listing["path"] == browse_path
        assert len(listing["files"]) >= 1
        defraw_found = False
        for entry in listing["files"]:
            assert set(entry.keys()) == set(["name", "size", "ctime", "mtime", "owner"])
            if entry["name"] == raw_ds_filename:
                defraw_found = True
            assert defraw_found


@pytest.mark.asyncio
async def test_browse_localfs_fail(default_raw, base_url, http_client):
    conn_url = "{}/api/config/connection/".format(base_url)
    conn_details = {
        'connection': {
            'type': 'local',
            'numWorkers': 2,
        }
    }
    async with http_client.put(conn_url, json=conn_details) as response:
        assert response.status == 200

    browse_path = os.path.join(
        os.path.dirname(default_raw._path),
        "does", "not", "exist"
    )
    url = "{}/api/browse/localfs/".format(base_url)
    async with http_client.get(url, params={"path": browse_path}) as resp:
        assert resp.status == 200
        listing = await resp.json()
        assert listing['status'] == 'error'
        assert listing['messageType'] == 'DIRECTORY_LISTING_FAILED'
