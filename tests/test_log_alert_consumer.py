from collections import deque
from http_monitor.log_alert_consumer import LogAlertConsumer
import unittest


class TestLogAlertConsumer(unittest.TestCase):

    def setUp(self):
        self.time_window = 6
        threshold = 5
        self.consumer = LogAlertConsumer(self.time_window, threshold, deque())

        # (10 / 6) = 1.6 - no alert
        times = [1549573860] * 3 + [1549573861] * 7
        [self.consumer.alert_queue.append(t) for t in times]
        self.consumer._LogAlertConsumer__should_alert_or_recover(1549573861)

    def tearDown(self):
        self.consumer = None

    def test_alert_state(self):
        alert_data = self.consumer.updated_alert_data()

        self.assertEqual(alert_data.get('type'), None)
        self.assertEqual(alert_data['alert_count'], 0)

        # (27 / 6) = 6.1 > threshold - alert
        breach_threshold_times = [1549573862] * 27
        [self.consumer.alert_queue.append(t) for t in breach_threshold_times]
        self.consumer._LogAlertConsumer__should_alert_or_recover(1549573862)
        alert_data = self.consumer.updated_alert_data()

        self.assertEqual(alert_data['type'], 'alert')
        self.assertEqual(alert_data['alert_count'], 1)

    def test_recovered_state(self):
        breach_threshold_times = [1549573862] * 27
        [self.consumer.alert_queue.append(t) for t in breach_threshold_times]
        self.consumer._LogAlertConsumer__should_alert_or_recover(1549573862)

        push_out = breach_threshold_times[0] + 2
        for _ in range(self.time_window):
            push_out += 1
            self.consumer.alert_queue.append(push_out)

        self.consumer._LogAlertConsumer__should_alert_or_recover(push_out)
        alert_data = self.consumer.updated_alert_data()

        # (6 / 6) = 1 - recovered
        self.assertEqual(alert_data['type'], 'recovered')
        self.assertEqual(alert_data['alert_count'], 1)

    def test_recover_then_alert_state(self):
        breach_threshold_times = [1549573862] * 27
        [self.consumer.alert_queue.append(t) for t in breach_threshold_times]
        self.consumer._LogAlertConsumer__should_alert_or_recover(1549573862)

        push_out = breach_threshold_times[0] + 2
        for _ in range(self.time_window):
            push_out += 1
            self.consumer.alert_queue.append(push_out)

        self.consumer._LogAlertConsumer__should_alert_or_recover(push_out)

        # (55 / 6) - alert again
        breach = [push_out] * 50

        [self.consumer.alert_queue.append(t) for t in breach]
        self.consumer._LogAlertConsumer__should_alert_or_recover(breach[0])
        alert_data = self.consumer.updated_alert_data()

        self.assertEqual(alert_data['type'], 'alert')
        self.assertEqual(alert_data['alert_count'], 2)


if __name__ == '__main__':
    unittest.main()
