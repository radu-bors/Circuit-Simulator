"""
This scripts contains classes definitions for CircuitSimulator, Ammeter, Voltmeter, Ohmmeter and RollingAverageOhmmeter
"""

import asyncio # required to run tasks in parallel
import time # required for timestamps

# ============================================================
# Class: CircuitSimulator
# ============================================================
class CircuitSimulator:
    """
    The CircuitSimulator class simulates the behavior of the provided electrical circuit over time. The circuit diagram is:
        +-- R1 -+----- R2 ----+
        |       |             |
        |       +-- RL -- A --+
        |       |             |
        |       +----- V -----+
        |                     |
        +-------- VS ---------+
    where RL is a fixed resistor, VS is a DC voltage source (VS=10V), R1 and R2 are variable resistors, V is a voltmeter, and A is an ammeter.
    
    R1 and R2 change linearly over time, from start at t1=0s to end at t2=10s. The voltage and current values are calculated based on these and on RL, following the equation:
        IL = VS / (R1 + RL + (R1 * RL / R2))
        V  = IL * RL
    The equations represent the solution to the above circuit and were found by applying Kirchoff current and voltage laws.

    Parameters:
    R1_start (float): The initial resistance of R1 at the start of the simulation (t1=0s) in ohms. Default: 0.
    R1_end (float)  : The final resistance of R1 at the end of the simulation (t2=10s) in ohms. Default: 100_000.
    R2_start (float): The initial resistance of R2 at the start of the simulation (t1=0s) in ohms. Default: 100_000.
    R2_end (float)  : The final resistance of R2 at the end of the simulation (t2=10s) in ohms. Default: 0.
    RL (float)      : The fixed resistance of RL in ohms. Default: 30_000.
    VS (float)      : The voltage of VS in the circuit in volts. Default: 10.
    duration (float): The total duration of the simulation in seconds. Default: 10.

    Methods:
    start()                     : Starts the simulation by setting the start time to the current time.
    get_resistance(current_time): Calculates and returns the resistances R1 and R2 based on the current time.
    get_values(current_time)    : Returns the voltage and current values at the current time.
    """
    
    def __init__(self, R1_start=0, R1_end=100_000, R2_start=100_000, R2_end=0, RL=30_000, VS=10, duration=10):
        """Initialize the simulator with given parameters."""
        self.R1_start = R1_start
        self.R1_end = R1_end
        self.R2_start = R2_start
        self.R2_end = R2_end
        self.RL = RL
        self.VS = VS
        self.duration = duration
        self.start_time = None

    def start(self):
        """Start the simulation."""
        self.start_time = time.time()

    def get_resistance(self, current_time):
        """Calculate and return the resistances R1 and R2 based on the current time."""
        elapsed_time = current_time - self.start_time
        R1 = self.R1_start + (self.R1_end - self.R1_start) * (elapsed_time / self.duration)
        R2 = self.R2_start + (self.R2_end - self.R2_start) * (elapsed_time / self.duration)
        return R1, R2

    def get_values(self, current_time):
        """Return the voltage and current values at the current time."""
        R1, R2 = self.get_resistance(current_time)
        
        # Calculate the current through the ammeter based on the manually determined solution
        IL = self.VS / (R1 + self.RL + R1 * self.RL / R2)
        V = IL * self.RL
        
        return V, IL, current_time
    
# ============================================================
# Class: Ammeter
# ============================================================
class Ammeter:
    """
    The Ammeter class represents an ammeter device in the circuit. The ammeter measures the current through RL in the circuit at regular intervals. Whenever a reading is performed, the instance of Ohmmeter updates as well.

    Parameters:
    simulator (CircuitSimulator): The CircuitSimulator instance that simulates the circuit which this device measures.
    ohmmeter (Ohmmeter)         : The Ohmmeter instance that this device updates.
    interval (float)            : The interval at which the device takes measurements, in seconds. Default: 0.3.

    Attributes:
    last_value (float)      : The last measured value.
    last_timestamp (float)  : The timestamp of the last measurement.

    Methods:
    start()         : Starts the measurement process. This method is designed to be run as an asynchronous task.
    get_last_value(): Returns the last measured value and its timestamp.
    """
    
    def __init__(self, simulator, ohmmeter, interval=0.3):
        """Initialize the device with a reference to the simulator, the ohmmeter, and the measurement interval."""
        self.simulator = simulator
        self.ohmmeter = ohmmeter
        self.interval = interval
        self.last_value = None
        self.last_timestamp = None

    async def start(self):
        """Start the measurement."""
        while True:
            # Read the measurement and print the output
            _, self.last_value, self.last_timestamp = self.simulator.get_values(time.time())
            
            timestamp = self.last_timestamp - self.simulator.start_time
            print(f'{self.__class__.__name__} reading at timestamp {timestamp:.4f} s : {self.last_value:.5g} A')
            
            # Update the current inside the ohmmeter
            self.ohmmeter.set_current(self.last_value)
            
            # Pause running for the characteristic interval
            await asyncio.sleep(self.interval)

    def get_last_value(self):
        """Return the last measured value and its timestamp."""
        return self.last_value, self.last_timestamp
    
# ============================================================
# Class: Voltmeter
# ============================================================
class Voltmeter:
    """
    The Voltmeter class represents a voltmeter device in the circuit. The voltmeter measures the voltage across RL in the circuit at regular intervals. Whenever a reading is performed, the instance of Ohmmeter updates as well.

    Parameters:
    simulator (CircuitSimulator): The CircuitSimulator instance that simulates the circuit which this device measures.
    ohmmeter (Ohmmeter)         : The Ohmmeter instance that this device updates.
    interval (float)            : The interval at which the device takes measurements, in seconds. Default: 0.1.

    Attributes:
    last_value (float)      : The last measured value.
    last_timestamp (float)  : The timestamp of the last measurement.

    Methods:
    start()         : Starts the measurement process. This method is designed to be run as an asynchronous task.
    get_last_value(): Returns the last measured value and its timestamp.
    """
    
    def __init__(self, simulator, ohmmeter, interval=0.1):
        """Initialize the device with the simulator, the ohmmeter, and the measurement interval."""
        self.simulator = simulator
        self.ohmmeter = ohmmeter
        self.interval = interval
        self.last_value = None
        self.last_timestamp = None

    async def start(self):
        """Start the measurement."""
        while True:
            # Read the measurement and print the output
            self.last_value, _, self.last_timestamp = self.simulator.get_values(time.time())
            
            timestamp = self.last_timestamp - self.simulator.start_time
            print(f'{self.__class__.__name__} reading at timestamp {timestamp:.4f} s : {self.last_value:.5g} V')
            
            # Update the voltage inside the ohmmeter
            self.ohmmeter.set_voltage(self.last_value)
            
            # Pause running for the characteristic interval until next reading
            await asyncio.sleep(self.interval)

    def get_last_value(self):
        """Return the last measured value and its timestamp."""
        return self.last_value, self.last_timestamp
    
# ============================================================
# Class: Ohmmeter
# ============================================================
class Ohmmeter:
    """
    The Ohmmeter class calculates the resistance RL in the circuit at regular intervals, based on the latest voltage and current measurements which it stores. The stored values are updated in the Ammeter and Voltmeter whenever a measurement is performed.

    Parameters:
    simulator (CircuitSimulator): The CircuitSimulator instance that simulates the circuit which this device measures.
    interval (float)            : The interval at which the device calculates the resistance, in seconds. Default: 1.0.

    Attributes:
    voltage (float)         : The last voltage measurement.
    current (float)         : The last current measurement.
    last_timestamp (float)  : The timestamp of the last calculation.

    Methods:
    start()          : Starts the resistance calculation process. This method is designed to be run as an asynchronous task.
    set_voltage(val) : Sets the voltage value.
    set_current(val) : Sets the current value.
    """
    
    def __init__(self, simulator, interval=1.0):
        """Initialize the device with the calculation interval."""
        self.simulator = simulator
        self.interval = interval
        self.voltage = None
        self.current = None
        self.last_timestamp = None

    async def start(self):
        """Start the resistance calculation."""
        while True:
            if self.voltage is not None and self.current is not None:
                # Calculate the resistance and print the output
                resistance = self.voltage / self.current if self.current != 0 else float('inf')
                
                self.last_timestamp = time.time()
                timestamp = time.time() - self.simulator.start_time
                print(f'{self.__class__.__name__} reading at timestamp {timestamp:.4f} s : {resistance:.4f} \u03A9')
            
            # Pause running for the characteristic interval until next reading
            await asyncio.sleep(self.interval)

    def set_voltage(self, value):
        """Set the voltage value."""
        self.voltage = value

    def set_current(self, value):
        """Set the current value."""
        self.current = value
            
# ============================================================
# Class: RollingAverageOhmmeter
# ============================================================
class RollingAverageOhmmeter(Ohmmeter):
    """
    The RollingAverageOhmmeter class represents a device for calculating the resistance RL in the circuit with a rolling average. This class takes the latest readings from V and A, calculates RL based on those readings, and computes the rolling average of the calculated values over the last 2 seconds. The class inherits from the Ohmmeter class and overrides the start() method for calculating the rolling average resistance.
    
    Parameters:
    simulator (CircuitSimulator): The CircuitSimulator instance that simulates the circuit which this device measures.

    Attributes:
    values (list) : List to store values of RL from the past 2 seconds

    Methods:
    start()          : Starts the rolling average calculation of RL using voltage and current values recorded in the past 2 s. It overwrites the start() method from Ohmmeter class
    """

    def __init__(self, simulator, voltmeter, ammeter):
        super().__init__(simulator)
        self.voltmeter = voltmeter
        self.ammeter = ammeter
        self.values = []

    async def start(self):
        """Start the calculation of the resistance with a rolling average."""
        while True:
            # Read latest measurements from voltmeter and ammeter
            V, _ = self.voltmeter.get_last_value()
            I, _ = self.ammeter.get_last_value()
            
            # Check if voltage or current values have updated
            if self.voltage != V or self.current != I:
                # Calculate the resistance RL and add it to a list
                RL = V / I if I != 0 else float('inf')
                self.values.append((RL, time.time()))
                self.voltage = V
                self.current = I
            
            # Store only readings from the last 2 s and use them to calculate the rolling average
            self.values = [(v, t) for v, t in self.values if time.time() - t <= 2]
            RL_avg = sum(v for v, t in self.values) / len(self.values) if self.values else float('inf')
            
            print(f'{self.__class__.__name__} calculated RL (rolling average): {RL_avg:.4f} \u03A9')
            
            # Pause execution for the specified interval (inherited from the Ohmmeter class)
            await asyncio.sleep(self.interval)
            
# ============================================================
# Class: Application
# ============================================================
class Application:
    """
    The Application class represents the entire application. It includes the circuit simulator, the measurement devices, and the ohmmeters. It's meant to start the simulation of the circuit and the measurement and calculation processes of the devices. Then it stops these processes after a specified duration in the circuit simulator (default is 10 s).

    Attributes:
    simulator (CircuitSimulator)                        : CircuitSimulator instance that simulates the circuit.
    voltmeter (Voltmeter)                               : Voltmeter instance that measures the voltage in the circuit.
    ammeter (Ammeter)                                   : Ammeter instance that measures the current in the circuit.
    ohmmeter (Ohmmeter)                                 : Ohmmeter instance that calculates the resistance RL.
    rolling_average_ohmmeter (RollingAverageOhmmeter)   : RollingAverageOhmmeter instance that calculates the rolling average of RL.

    Methods:
    run(): Run the application.
    """
    
    def __init__(self):
        """Initialize the application with a circuit simulator, a voltmeter, an ammeter, and two ohmmeters."""
        self.simulator = CircuitSimulator()
        self.ohmmeter = Ohmmeter(self.simulator)
        self.voltmeter = Voltmeter(self.simulator, self.ohmmeter)
        self.ammeter = Ammeter(self.simulator, self.ohmmeter)
        self.rolling_average_ohmmeter = RollingAverageOhmmeter(self.simulator, self.voltmeter, self.ammeter)

    async def run(self):
        """Run the application."""
        self.simulator.start()
        
        # Create a list of asyncio tasks from each start() routine of devices to be run concurrently
        tasks = [asyncio.create_task(t.start()) for t in [self.voltmeter, self.ammeter, self.ohmmeter, self.rolling_average_ohmmeter]]
        
        # Sleep for 10 seconds before cancelling the tasks
        await asyncio.sleep(10)
        for task in tasks:
            # Cancel all tasks
            task.cancel()
            
        # Run all the tasks concurrently and wait for them to complete
        await asyncio.gather(*tasks, return_exceptions=True)