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

    def _simulate(self, timeStep: float, mass: float, spring_constant: float, initial_displacement: float, damping_ratio: float = 0.0, g: float = 9.81):
        """
        Simulate a mass-spring system with a ball.
        Args:
            timeStep (float): Time step in seconds (e.g., 0.01 for smooth updates).
            mass (float): Mass of the ball in kg.
            spring_constant (float): Spring constant in N/m.
            initial_displacement (float): Initial displacement from equilibrium in meters.
            damping_ratio (float): Damping ratio (0 for no damping, typically 0-1).
            g (float): Gravitational acceleration in m/s^2 (default 9.81).
        """
        # Calculate natural frequency (ω = √(k/m))
        omega = math.sqrt(spring_constant / mass)
        
        # Calculate damping coefficient (c = 2 * damping_ratio * √(m * k))
        damping_coeff = 2 * damping_ratio * math.sqrt(mass * spring_constant)
        
        current_time = 0.0
        
        # For undamped or underdamped systems, use analytical solution
        if damping_ratio < 1:
            # Calculate damped frequency (ω_d = ω * √(1 - ζ²))
            damped_omega = omega * math.sqrt(1 - damping_ratio**2) if damping_ratio > 0 else omega
            
            # Initial conditions
            amplitude = initial_displacement
            
            while True:
                # Calculate position using x(t) = A * e^(-ζωt) * cos(ω_d * t)
                decay = math.exp(-damping_ratio * omega * current_time) if damping_ratio > 0 else 1.0
                position = amplitude * decay * math.cos(damped_omega * current_time)
                
                # Calculate velocity (derivative of position)
                velocity_term1 = -amplitude * decay * damped_omega * math.sin(damped_omega * current_time)
                velocity_term2 = -damping_ratio * omega * amplitude * decay * math.cos(damped_omega * current_time) if damping_ratio > 0 else 0
                velocity = velocity_term1 + velocity_term2
                
                # Calculate acceleration (F = -kx - cv, a = F/m)
                spring_force = -spring_constant * position
                damping_force = -damping_coeff * velocity
                acceleration = (spring_force + damping_force) / mass
                
                # Send data to clients (position in cm for display)
                data = {
                    "method": "data",
                    "time": round(current_time, 2),
                    "position": round(position * 100, 2),  # Convert to cm
                    "velocity": round(velocity * 100, 2),  # Convert to cm/s
                    "acceleration": round(acceleration * 100, 2),  # Convert to cm/s²
                    "spring_force": round(spring_force, 2),  # N
                    "damping_force": round(damping_force, 2)  # N
                }
                json_message = json.dumps(data)
                self.itexaWebSocketServer.send_data(json_message)
                
                if self.simulationBreakEvent.is_set():
                    self.simulationBreakEvent.clear()
                    return
                
                time.sleep(timeStep)
                current_time += timeStep
                
        else:
            # For critically damped or overdamped systems, simplified handling
            print("Critically damped or overdamped systems not fully implemented")
            return

    def simulate(self, limits, mass: float, spring_constant: float, initial_displacement: float, timeStep: float = 0.01, damping_ratio: float = 0.0, g: float = 9.81):
        """
        Start the spring-mass simulation.
        Args:
            limits (dict): Dictionary containing max values for parameters.
            mass (float): Mass of the ball in kg.
            spring_constant (float): Spring constant in N/m.
            initial_displacement (float): Initial displacement in meters.
            timeStep (float): Time step in seconds.
            damping_ratio (float): Damping ratio (0 for no damping).
            g (float): Gravitational acceleration in m/s^2.
        """
        # Send initialization data
        self.itexaWebSocketServer.send_data(
            json.dumps({
                "method": "init",
                "mass": mass,
                "spring_constant": spring_constant,
                "initial_displacement": initial_displacement,
                "damping_ratio": damping_ratio,
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
            args=(timeStep, mass, spring_constant, initial_displacement, damping_ratio, g)
        )
        self.simulationThread.start()