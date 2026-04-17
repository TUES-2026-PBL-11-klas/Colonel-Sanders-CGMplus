"""
Unit tests for src/business/store.py
"""
import copy
import threading
import time
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reset_store():
    """Return store to its canonical initial state between tests."""
    import src.business.store as store_module
    with store_module._lock:
        store_module._store.clear()
        store_module._store.update({
            "alerts": {"fetched_at": None, "header": {}, "entities": []},
            "trip_updates": {"fetched_at": None, "header": {}, "entities": []},
            "vehicle_positions": {
                "fetched_at": None,
                "header": {},
                "entities": []
            },
            "static": {
                "fetched_at": None,
                "agency":     [],
                "routes":     [],
                "stops":      [],
                "trips":      [],
                "calendar":   [],
            },
        })


@pytest.fixture(autouse=True)
def reset_store():
    """Restore the real _store to its initial state before each test."""
    _reset_store()
    yield
    _reset_store()


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------

class TestInitialState:

    def test_store_has_all_top_level_keys(self):
        import src.business.store as store_module
        assert set(store_module._store.keys()) == {
            "alerts", "trip_updates", "vehicle_positions", "static"
        }

    def test_realtime_feeds_have_correct_keys(self):
        import src.business.store as store_module
        for feed in ("alerts", "trip_updates", "vehicle_positions"):
            entry = store_module._store[feed]
            assert set(entry.keys()) == {"fetched_at", "header", "entities"}

    def test_realtime_feeds_fetched_at_is_none(self):
        import src.business.store as store_module
        for feed in ("alerts", "trip_updates", "vehicle_positions"):
            assert store_module._store[feed]["fetched_at"] is None

    def test_realtime_feeds_header_is_empty_dict(self):
        import src.business.store as store_module
        for feed in ("alerts", "trip_updates", "vehicle_positions"):
            assert store_module._store[feed]["header"] == {}

    def test_realtime_feeds_entities_is_empty_list(self):
        import src.business.store as store_module
        for feed in ("alerts", "trip_updates", "vehicle_positions"):
            assert store_module._store[feed]["entities"] == []

    def test_static_has_correct_keys(self):
        import src.business.store as store_module
        assert set(store_module._store["static"].keys()) == {
            "fetched_at", "agency", "routes", "stops", "trips", "calendar"
        }

    def test_static_fetched_at_is_none(self):
        import src.business.store as store_module
        assert store_module._store["static"]["fetched_at"] is None

    def test_static_collections_are_empty_lists(self):
        import src.business.store as store_module
        static = store_module._store["static"]
        for key in ("agency", "routes", "stops", "trips", "calendar"):
            assert static[key] == [], f"Expected static['{key}'] to be []"

    def test_lock_is_threading_lock(self):
        import src.business.store as store_module
        # threading.Lock() returns a _thread.lock or threading._RLock subtype;
        # the canonical check is that it has acquire/release.
        assert hasattr(store_module._lock, "acquire")
        assert hasattr(store_module._lock, "release")


# ---------------------------------------------------------------------------
# _snapshot — return value correctness
# ---------------------------------------------------------------------------

class TestSnapshotReturnValue:

    def test_snapshot_returns_dict(self):
        from src.business.store import _snapshot
        assert isinstance(_snapshot("alerts"), dict)

    def test_snapshot_alerts_initial_keys(self):
        from src.business.store import _snapshot
        snap = _snapshot("alerts")
        assert set(snap.keys()) == {"fetched_at", "header", "entities"}

    def test_snapshot_trip_updates_initial_keys(self):
        from src.business.store import _snapshot
        snap = _snapshot("trip_updates")
        assert set(snap.keys()) == {"fetched_at", "header", "entities"}

    def test_snapshot_vehicle_positions_initial_keys(self):
        from src.business.store import _snapshot
        snap = _snapshot("vehicle_positions")
        assert set(snap.keys()) == {"fetched_at", "header", "entities"}

    def test_snapshot_static_initial_keys(self):
        from src.business.store import _snapshot
        snap = _snapshot("static")
        assert set(snap.keys()) == {
            "fetched_at",
            "agency",
            "routes",
            "stops",
            "trips",
            "calendar"
        }

    def test_snapshot_initial_values_match_store(self):
        import src.business.store as store_module
        snap = store_module._snapshot("alerts")
        assert snap["fetched_at"] is None
        assert snap["header"] == {}
        assert snap["entities"] == []

    def test_snapshot_reflects_updated_store(self):
        import src.business.store as store_module
        with store_module._lock:
            store_module._store["alerts"]["fetched_at"] = (
                "2024-06-01T00:00:00Z"
            )
            store_module._store["alerts"]["entities"] = [{"id": "A1"}]

        snap = store_module._snapshot("alerts")
        assert snap["fetched_at"] == "2024-06-01T00:00:00Z"
        assert snap["entities"] == [{"id": "A1"}]

    def test_snapshot_unknown_key_raises_key_error(self):
        from src.business.store import _snapshot
        with pytest.raises(KeyError):
            _snapshot("does_not_exist")


# ---------------------------------------------------------------------------
# _snapshot — deep-copy isolation
# ---------------------------------------------------------------------------

class TestSnapshotIsolation:

    def test_snapshot_is_not_same_object_as_store(self):
        import src.business.store as store_module
        snap = store_module._snapshot("alerts")
        assert snap is not store_module._store["alerts"]

    def test_mutating_snapshot_dict_does_not_affect_store(self):
        import src.business.store as store_module
        snap = store_module._snapshot("alerts")
        snap["fetched_at"] = "mutated"
        assert store_module._store["alerts"]["fetched_at"] is None

    def test_mutating_snapshot_list_does_not_affect_store(self):
        import src.business.store as store_module
        with store_module._lock:
            store_module._store["alerts"]["entities"] = [{"id": "A1"}]

        snap = store_module._snapshot("alerts")
        snap["entities"].append({"id": "INJECTED"})

        assert store_module._store["alerts"]["entities"] == [{"id": "A1"}]

    def test_mutating_nested_object_does_not_affect_store(self):
        import src.business.store as store_module
        with store_module._lock:
            store_module._store["alerts"]["entities"] = [
                {
                    "id": "A1",
                    "nested": {"x": 1}
                }
            ]

        snap = store_module._snapshot("alerts")
        snap["entities"][0]["nested"]["x"] = 999

        assert store_module._store["alerts"]["entities"][0]["nested"]["x"] == 1

    def test_two_snapshots_are_independent_copies(self):
        import src.business.store as store_module
        snap1 = store_module._snapshot("alerts")
        snap2 = store_module._snapshot("alerts")
        snap1["fetched_at"] = "snap1-only"
        assert snap2["fetched_at"] is None

    def test_snapshot_static_list_is_independent(self):
        import src.business.store as store_module
        with store_module._lock:
            store_module._store["static"]["routes"] = [{"route_id": "R1"}]

        snap = store_module._snapshot("static")
        snap["routes"].append({"route_id": "INJECTED"})

        assert store_module._store["static"]["routes"] == [{"route_id": "R1"}]


# ---------------------------------------------------------------------------
# _snapshot — thread safety
# ---------------------------------------------------------------------------

class TestSnapshotThreadSafety:

    def test_concurrent_reads_all_succeed(self):
        import src.business.store as store_module
        results = []
        errors = []
        n_threads = 20

        def reader():
            try:
                results.append(store_module._snapshot("alerts"))
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=reader) for _ in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Threads raised exceptions: {errors}"
        assert len(results) == n_threads
        assert all(isinstance(r, dict) for r in results)

    def test_concurrent_write_then_read_sees_consistent_data(self):
        import src.business.store as store_module

        ENTITY = {"id": "X", "data": list(range(100))}
        errors = []
        stop_event = threading.Event()

        def writer():
            while not stop_event.is_set():
                with store_module._lock:
                    store_module._store["alerts"]["entities"] = [
                        copy.deepcopy(ENTITY)
                    ]
                time.sleep(0)  # yield

        def reader():
            for _ in range(50):
                try:
                    snap = store_module._snapshot("alerts")
                    entities = snap["entities"]
                    assert entities == [] or entities == [ENTITY], (
                        f"Unexpected entities: {entities}"
                    )
                except Exception as exc:
                    errors.append(exc)
                time.sleep(0)

        w = threading.Thread(target=writer, daemon=True)
        r = threading.Thread(target=reader)
        w.start()
        r.start()
        r.join()
        stop_event.set()
        w.join()

        assert errors == [], f"Reader saw inconsistent state: {errors}"

    def test_snapshot_blocks_while_lock_held(self):
        """_snapshot must wait until the lock is released before returning."""
        import src.business.store as store_module

        results = []
        lock_released_at = None

        def hold_lock():
            nonlocal lock_released_at
            with store_module._lock:
                time.sleep(0.05)          # hold for 50 ms
                lock_released_at = time.monotonic()

        def do_snapshot():
            snap = store_module._snapshot("alerts")
            results.append((time.monotonic(), snap))

        holder = threading.Thread(target=hold_lock)
        reader = threading.Thread(target=do_snapshot)

        holder.start()
        time.sleep(0.005)   # ensure holder acquires lock first
        reader.start()

        holder.join()
        reader.join()

        assert results, "Snapshot thread never completed"
        snapshot_at = results[0][0]
        assert snapshot_at >= lock_released_at, (
            "Snapshot returned before the lock was released"
        )
