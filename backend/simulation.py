from websocket_server import ItexaWebSocketServer
import json
import threading
import time
import math


class Simulation:
    def __init__(self, itexaWebSocketServer: ItexaWebSocketServer):
        self.simulationThread = None
        self.simulationBreakEvent = threading.Event()
        self.itexaWebSocketServer = itexaWebSocketServer
        self.__g = 9.81  # Default gravitational acceleration in m/s^2
        self.__timeStep = 0.1  # Default time step in seconds
        self.__epsilon = 1e-8  # Small value to avoid division by zero

    def _sendData(self, time: float, position: float):
        data = {
            "method": "data",
            "time": round(time, 2),
            "position": round(position * 100, 2),  # Convert to cm
        }
        json_message = json.dumps(data)
        self.itexaWebSocketServer.send_data(json_message)

    def _simulate(self, mass: float, spring_constant: float, initial_displacement: float, damping: float):
        """
        Simulate a mass-spring system with a ball.
        Args:
            timeStep (float): Time step in seconds (e.g., 0.1 for smooth updates).
            mass (float): Mass of the ball in kg.
            spring_constant (float): Spring constant in N/m.
            initial_displacement (float): Initial displacement from equilibrium in meters.
            damping (float): (0 for no damping).
        """
        w0 = math.sqrt(spring_constant / mass)                      # Natural frequency
        zeta = damping / (math.sqrt(2.0 * spring_constant * mass))  # Damping ratio
        current_time = 0.0
        while True:
            if zeta > 1.0 + self.__epsilon:
                r1 = -w0 * (zeta + math.sqrt(zeta ** 2 - 1))
                r2 = -w0 * (zeta - math.sqrt(zeta ** 2 - 1))
                A = (-r2 * initial_displacement) / (r1 - r2)
                B = initial_displacement - A
                cur_displacement = A * math.exp(r1 * current_time) + B * math.exp(r2 * current_time)
            elif zeta < 1.0 - self.__epsilon:
                wd = w0 * math.sqrt(1.0 - zeta ** 2)  # Damped frequency
                cur_displacement = math.exp(-zeta * w0 * current_time) * ((initial_displacement * math.cos(wd * current_time)) + (zeta * initial_displacement * w0 * math.sin(wd * current_time) / wd))
            else:
                cur_displacement = (initial_displacement + (w0 * initial_displacement * current_time)) * math.exp(-w0 * current_time) # critical zeta == 1

            self._sendData(current_time, cur_displacement)
            if self.simulationBreakEvent.is_set():
                self.simulationBreakEvent.clear()
                return

            time.sleep(self.__timeStep)
            current_time += self.__timeStep

    def simulate(self, limits, mass: float, spring_constant: float, initial_displacement: float, damping: float):
        # Send initialization data
        self.itexaWebSocketServer.send_data(
            json.dumps({
                "method": "init",
                "mass": mass,
                "spring_constant": spring_constant,
                "initial_displacement": initial_displacement,
                "max_mass": limits["MAX_MASS"],
                "max_spring_constant": limits["MAX_SPRING_CONSTANT"],
                "max_displacement": limits["MAX_DISPLACEMENT"]
            })
        )

        # Stop any existing simulation
        if self.simulationThread is not None and self.simulationThread.is_alive():
            self.simulationBreakEvent.set()
            self.simulationThread.join()

        # Start new simulation thread
        self.simulationThread = threading.Thread(
            target=self._simulate,
            args=(mass, spring_constant, initial_displacement, damping)
        )
        self.simulationThread.start()
    