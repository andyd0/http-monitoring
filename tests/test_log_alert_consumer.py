from collections import deque
from http_monitor.log_alert_consumer import LogAlertConsumer
import unittest


class TestLogAlertConsumer(unittest.TestCase):

    def setUp(self):
        time_window = 6
        threshold = 5
        self.consumer = LogAlertConsumer(time_window, threshold, deque())

        times = [1549573860] * 3 + [1549573861] * 7
        [self.consumer.alert_queue.append(t) for t in times]
        self.consumer.should_alert_or_recover(1549573861)

    def tearDown(self):
        self.consumer = None

    def test_alert_state(self):
        alert_data = self.consumer.updated_alert_data()

        self.assertEqual(alert_data.get('type'), None)
        self.assertEqual(alert_data['alert_count'], 0)

        breach_threshold_times = [1549573862] * 27
        [self.consumer.alert_queue.append(t) for t in breach_threshold_times]
        self.consumer.should_alert_or_recover(1549573862)
        alert_data = self.consumer.updated_alert_data()

        self.assertEqual(alert_data['type'], 'alert')
        self.assertEqual(alert_data['alert_count'], 1)

    def test_recovered_state(self):
        breach_threshold_times = [1549573862] * 27
        [self.consumer.alert_queue.append(t) for t in breach_threshold_times]
        self.consumer.should_alert_or_recover(1549573862)

        push_out_time = breach_threshold_times[0] + 2
        for _ in range(5):
            push_out_time += 1
            self.consumer.alert_queue.append(push_out_time)

        self.consumer.should_alert_or_recover(push_out_time)
        alert_data = self.consumer.updated_alert_data()

        self.assertEqual(alert_data['type'], 'recovered')
        self.assertEqual(alert_data['alert_count'], 1)

    def test_recover_then_alert_state(self):
        breach_threshold_times = [1549573862] * 27
        [self.consumer.alert_queue.append(t) for t in breach_threshold_times]
        self.consumer.should_alert_or_recover(1549573862)

        push_out_time = breach_threshold_times[0] + 2
        for _ in range(5):
            push_out_time += 1
            self.consumer.alert_queue.append(push_out_time)

        self.consumer.should_alert_or_recover(push_out_time)

        push_out_time += 1
        breach_again = [push_out_time] * 50

        [self.consumer.alert_queue.append(t) for t in breach_again]
        self.consumer.should_alert_or_recover(breach_again[0])
        alert_data = self.consumer.updated_alert_data()

        self.assertEqual(alert_data['type'], 'alert')
        self.assertEqual(alert_data['alert_count'], 2)


if __name__ == '__main__':
    unittest.main()
