import sqlite3
import unittest

from downtime_tracker import (
    add_event,
    calculate_duration_minutes,
    init_db,
    list_events,
    total_downtime,
)


class DowntimeTrackerTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        init_db(self.connection)

    def tearDown(self):
        self.connection.close()

    def test_calculate_duration_minutes(self):
        result = calculate_duration_minutes(
            "2026-09-23 14:20",
            "2026-09-23 14:47",
        )
        self.assertEqual(result, 27)

    def test_end_time_must_be_after_start(self):
        with self.assertRaises(ValueError):
            calculate_duration_minutes(
                "2026-09-23 14:20",
                "2026-09-23 14:20",
            )

    def test_add_and_list_event(self):
        event_id = add_event(
            self.connection,
            "CNC-01",
            "Hydraulic fault",
            "2026-09-23 14:20",
            "2026-09-23 14:47",
        )

        events = list_events(self.connection)

        self.assertEqual(event_id, 1)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["machine_name"], "CNC-01")
        self.assertEqual(events[0]["duration_minutes"], 27)

    def test_total_downtime(self):
        add_event(
            self.connection,
            "CNC-01",
            "Hydraulic fault",
            "2026-09-23 10:00",
            "2026-09-23 10:30",
        )
        add_event(
            self.connection,
            "CNC-01",
            "Tool change issue",
            "2026-09-23 11:00",
            "2026-09-23 11:15",
        )
        add_event(
            self.connection,
            "Pump-02",
            "Pressure loss",
            "2026-09-23 12:00",
            "2026-09-23 12:10",
        )

        self.assertEqual(total_downtime(self.connection), 55)
        self.assertEqual(total_downtime(self.connection, "cnc-01"), 45)

    def test_invalid_machine_and_reason(self):
        with self.assertRaises(ValueError):
            add_event(
                self.connection,
                "",
                "Fault",
                "2026-09-23 10:00",
                "2026-09-23 10:05",
            )

        with self.assertRaises(ValueError):
            add_event(
                self.connection,
                "Motor-01",
                "",
                "2026-09-23 10:00",
                "2026-09-23 10:05",
            )


if __name__ == "__main__":
    unittest.main()
