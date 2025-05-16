from fastapi import FastAPI
from pydantic import BaseModel, field_validator, Field
from typing import Dict, Any

fastApi = FastAPI(title="Spring-Mass Simulation API")

# Hardcoded maximum values for spring-mass system
limits = {
    "MAX_MASS": 10.0,  # Maximum mass in kg
    "MAX_SPRING_CONSTANT": 1000.0,  # Maximum spring constant in N/m
    "MAX_DISPLACEMENT": 1.0,  # Maximum initial displacement in meters
}


class SpringMassParameters(BaseModel):
    mass: float = Field(..., description="Mass of the ball in kg")
    spring_constant: float = Field(..., description="Spring constant in N/m")
    initial_displacement: float = Field(..., description="Initial displacement from equilibrium in meters")
    damping: float = Field(0.0, description="Damping")

    @field_validator('mass')
    @classmethod
    def mass_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Mass must be positive")
        if v > limits["MAX_MASS"]:
            raise ValueError(f"Mass cannot exceed {limits['MAX_MASS']} kg")
        return v

    @field_validator('spring_constant')
    @classmethod
    def spring_constant_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Spring constant must be positive")
        if v > limits["MAX_SPRING_CONSTANT"]:
            raise ValueError(f"Spring constant cannot exceed {limits['MAX_SPRING_CONSTANT']} N/m")
        return v

    @field_validator('initial_displacement')
    @classmethod
    def displacement_must_be_valid(cls, v):
        if abs(v) > limits["MAX_DISPLACEMENT"]:
            raise ValueError(f"Initial displacement cannot exceed {limits['MAX_DISPLACEMENT']} meters")
        return v

    @field_validator('damping')
    @classmethod
    def damping__must_be_valid(cls, v):
        if v < 0:
            raise ValueError("Damping cannot be negative")
        if v > 100:
            raise ValueError("Damping this is highest supported dumping constant")
        return v


@fastApi.post("/spring/simulate", response_model=Dict[str, Any])
async def simulate_spring(params: SpringMassParameters):
    """
    Simulate spring-mass system based on parameters

    - mass: Mass of the ball in kg
    - spring_constant: Spring constant in N/m
    - initial_displacement: Initial displacement from equilibrium in meters
    - damping_ratio: Damping ratio (0 for no damping)

    Returns a status message indicating simulation start
    """
    fastApi.state.simulation.simulate(
        limits,
        params.mass,
        params.spring_constant,
        params.initial_displacement,
        damping=params.damping
    )
    return {"status": "new simulation started"}


@fastApi.get("/spring/limits", response_model=Dict[str, float])
async def get_spring_limits():
    """
    Get the maximum limits for spring-mass parameters
    
    Returns:
        Dict[str, float]: Dictionary containing the maximum limits for spring-mass parameters
    """
    return limits