from backend.local_server import DEFAULT_HOST, DEFAULT_PORT, _port_open


def test_embedded_server_defaults() -> None:
    assert DEFAULT_HOST == "127.0.0.1"
    assert DEFAULT_PORT == 8000
    assert isinstance(_port_open(), bool)
