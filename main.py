"""
This scripts simulates the electrical circuit defined in Assignment.pdf for 10s. It prints out readings from the voltmeter V and ammeter A at regular intervals (100 ms and 300 ms respectively) together with the instantaneous resistance RL every 1s. Additionally, every 1s it outputs the 2s rolling average of RL.
"""

import asyncio
from classes import Application

# Run simulation
app = Application()
asyncio.run(app.run())