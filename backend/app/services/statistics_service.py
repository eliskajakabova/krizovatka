class StatisticsService:
    @staticmethod
    def create_initial_statistics() -> dict:
        return {
            "total_vehicles_generated": 0,
            "total_vehicles_passed": 0,
            "total_vehicles_waiting": 0,
            "average_wait_time": 0.0,
            "max_wait_time": 0.0,
            "average_queue_length": 0.0,
            "max_queue_length": 0,
            "intersection_utilization": 0.0,
        }
