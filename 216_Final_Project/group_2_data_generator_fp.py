# group_2_data_generator_fp.py
# Based on Lab Assignment 8/9 group2_data_generator.py

import random
import math
import time

class SensorDataGenerator:
    """
    Generates simulated sensor data with a configurable pattern and randomness.
    Adapted to run indefinitely as per project requirements[Bonus: 37].
    """
    def __init__(self,
                 sensor_id="Sensor_01",
                 sensor_type="temperature",
                 min_value=18,
                 max_value=30,
                 base_frequency=0.05,
                 noise_level=0.1,
                 trend_strength=0.5,
                 seasonal_strength=0.8,
                 wild_data_chance=0.005, # Chance to generate wild data
                 wild_data_factor=5):
        """
        Initialize the sensor data generator.
        """
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.min_value = min_value
        self.max_value = max_value
        self.base_frequency = base_frequency
        self.noise_level = noise_level
        self.trend_strength = trend_strength
        self.seasonal_strength = seasonal_strength
        self.wild_data_chance = wild_data_chance
        self.wild_data_factor = wild_data_factor

        # Internal state
        self._counter = 0
        self._packet_id = 0 # Project requirement [Bonus: 39]
        self._phase_shift = random.uniform(0, 2 * math.pi)
        self._trend_direction = random.choice([-1, 1])
        self._trend_change_point = random.randint(100, 300)

    def _generate_normalized_value(self):
        """Generate a normalized value between 0 and 1."""
        self._counter += 1
        if self._counter % self._trend_change_point == 0:
            self._trend_direction *= -1
            self._trend_change_point = random.randint(100, 300)

        trend = (math.sin(self._counter * 0.002) + 1) / 2 * self._trend_direction * self.trend_strength
        seasonal = math.sin(self._counter * self.base_frequency + self._phase_shift)
        seasonal = (seasonal + 1) / 2 * self.seasonal_strength
        secondary = math.sin(self._counter * self.base_frequency * 2.7 + self._phase_shift * 1.5)
        secondary = (secondary + 1) / 2 * 0.3
        noise = random.uniform(0, 1) * self.noise_level

        value = (trend + seasonal + secondary + noise) / (1 + self.trend_strength + self.seasonal_strength + 0.3)
        return max(0, min(1, value))

    def get_value(self):
        """Get the next sensor reading, potentially 'wild'."""
        normalized_value = self._generate_normalized_value()
        value = self.min_value + normalized_value * (self.max_value - self.min_value)

        # Introduce wild data occasionally
        if random.random() < self.wild_data_chance:
             value = self.min_value + (self.max_value - self.min_value) * random.uniform(-self.wild_data_factor, self.wild_data_factor)
             print(f"--- Generated Wild Data: {value:.2f} ---")

        return value

    def package_data(self):
        """Package data as JSON object with timestamp and packet ID[Bonus: 39]."""
        self._packet_id += 1
        value = self.get_value()
        data = {
            'packet_id': self._packet_id,
            'sensor_id': self.sensor_id,
            'sensor_type': self.sensor_type,
            'timestamp': time.time(), # Using epoch time for easier processing
            'value': round(value, 2),

        }
        return data

# Example usage (for testing this module)
if __name__ == "__main__":
    gen = SensorDataGenerator(sensor_id="TestSensor")
    for _ in range(10):
        print(gen.package_data())
        time.sleep(0.1)