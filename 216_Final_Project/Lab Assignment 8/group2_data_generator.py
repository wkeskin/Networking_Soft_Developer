import random
import math
import matplotlib.pyplot as plt

class SensorDataGenerator:
    """
    A class to generate simulated sensor data with realistic patterns.
    This generator produces values that follow a pattern with some randomness,
    similar to real-world sensor readings.
    """
    
    def __init__(self, 
                 sensor_type="temperature", 
                 min_value=18, 
                 max_value=30, 
                 base_frequency=0.05, 
                 noise_level=0.1,
                 trend_strength=0.5,
                 seasonal_strength=0.8):
        """
        Initialize the sensor data generator.
        
        Parameters:
        -----------
        sensor_type : str
            Type of sensor being simulated (e.g., "temperature", "humidity")
        min_value : float
            Minimum value in the desired range
        max_value : float
            Maximum value in the desired range
        base_frequency : float
            Base frequency of the pattern (lower values create longer patterns)
        noise_level : float
            Amount of random noise to add (0.0 to 1.0)
        trend_strength : float
            Strength of the long-term trend component (0.0 to 1.0)
        seasonal_strength : float
            Strength of the seasonal component (0.0 to 1.0)
        """
        self.sensor_type = sensor_type
        self.min_value = min_value
        self.max_value = max_value
        self.base_frequency = base_frequency
        self.noise_level = noise_level
        self.trend_strength = trend_strength
        self.seasonal_strength = seasonal_strength
        
        # Internal state
        self._counter = 0
        self._phase_shift = random.uniform(0, 2 * math.pi)
        self._trend_direction = random.choice([-1, 1])
        self._trend_change_point = random.randint(100, 300)
        
    def _generate_normalized_value(self):
        """
        Generate a normalized value between 0 and 1 with realistic patterns.
        
        Returns:
        --------
        float
            A normalized value between 0 and 1
        """
        # Increment the counter
        self._counter += 1
        
        # Change trend direction occasionally
        if self._counter % self._trend_change_point == 0:
            self._trend_direction *= -1
            self._trend_change_point = random.randint(100, 300)
        
        # Calculate trend component (long-term direction)
        trend = (math.sin(self._counter * 0.002) + 1) / 2 * self._trend_direction * self.trend_strength
        
        # Calculate seasonal component (repeating pattern)
        seasonal = math.sin(self._counter * self.base_frequency + self._phase_shift)
        seasonal = (seasonal + 1) / 2 * self.seasonal_strength
        
        # Add some secondary patterns
        secondary = math.sin(self._counter * self.base_frequency * 2.7 + self._phase_shift * 1.5)
        secondary = (secondary + 1) / 2 * 0.3
        
        # Add noise
        noise = random.uniform(0, 1) * self.noise_level
        
        # Combine components
        value = (trend + seasonal + secondary + noise) / (1 + self.trend_strength + self.seasonal_strength + 0.3)
        
        # Ensure value is between 0 and 1
        return max(0, min(1, value))
    
    @property
    def value(self):
        """
        Get the next sensor reading.
        
        Returns:
        --------
        float
            A sensor reading in the specified range
        """
        normalized_value = self._generate_normalized_value()
        # Scale to the desired range
        return self.min_value + normalized_value * (self.max_value - self.min_value)
    
    def plot_values(self, num_points=500):
        """
        Generate and plot sensor values.
        
        Parameters:
        -----------
        num_points : int
            Number of data points to generate and plot
        """
        # Generate values
        values = [self.value for _ in range(num_points)]
        
        # Create a time axis
        time = list(range(num_points))
        
        # Plot
        plt.figure(figsize=(10, 6))
        plt.plot(time, values)
        plt.title(f'Simulated {self.sensor_type.capitalize()} Readings')
        plt.xlabel('Time')
        plt.ylabel(f'{self.sensor_type.capitalize()} Value')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()


# Example usage
if __name__ == "__main__":
    # Create a temperature sensor
    temp_sensor = SensorDataGenerator(
        sensor_type="temperature",
        min_value=18,
        max_value=30,
        base_frequency=0.05,
        noise_level=0.1,
        trend_strength=0.5,
        seasonal_strength=0.8
    )
    
    # Plot 500 readings
    temp_sensor.plot_values(500)
    
    # Example of getting individual readings
    print(f"Current temperature: {temp_sensor.value:.2f}°C")
    print(f"Next temperature: {temp_sensor.value:.2f}°C")
    print(f"Next temperature: {temp_sensor.value:.2f}°C")
    
    
    # Usage example (Generalization)
    
    # Create a humidity sensor
    humidity_sensor = SensorDataGenerator(
        sensor_type="humidity",
        min_value=30,
        max_value=80,
        base_frequency=0.04,
        noise_level=0.15
    )
    
    # Get individual readings
    for _ in range(10):
        print(f"Current humidity: {humidity_sensor.value:.2f}%")
    
    # Plot 500 readings
    humidity_sensor.plot_values(500)
