from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

## Control flow:
## Observe the environment using vision and sensors
## Extract current and previous position
## Based on Context (Reasoning) decide to move, response, or move while responding
## Send movement commands based on current and previous position


class RobotPosition(BaseModel):
    """The Global State Estimation (The 'Where am I' data)"""
    x: float = Field(default=0.0, description="X coordinate in meters")
    y: float = Field(default=0.0, description="Y coordinate in meters")
    theta: float = Field(default=0.0, description="Heading in radians (0 to 2π)")


class TargetRobotPosition(BaseModel):
    """The Goal Coordinates (The 'Where am I going' data)"""
    target_x: float
    target_y: float
    distance_to_goal: Optional[float] = None
    bearing_to_goal: Optional[float] = Field(None, description="Angle error to target")

class ControlVectors(BaseModel):
    throttle: int = Field(..., ge=-255, le=255, description="Motor speed (-255 to 255)")
    steering: int = Field(..., ge=-255, le=255, description="Turning bias (-255 to 255)")
    duration_ms: int = Field(default=500, description="How long to execute the command")
    mode: str = Field(default="standard")


class Reasoning(BaseModel):
    observation: str = Field(..., description="What the AI sees in the environment")
    intent: str = Field(..., description="The logic behind the movement")
    confidence_score: float = Field(..., ge=0.0, le=1.0)


# --- The "Superclass" (Container Pattern) ---

class RobotBrainPacket(BaseModel):
    """
    This is the single object passed between Python and Gemini.
    It contains the full context (Telemetry + Intent + Action).
    """
    status: int = Field(default=100, description="100 to continue, 200 to stop")
    timestamp: datetime = Field(default_factory=datetime.now)

    # Composed Objects
    position: RobotPosition
    target: TargetRobotPosition
    controls: ControlVectors
    reasoning: Reasoning

    # Custom Validator for Safety
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: int) -> int:
        if v not in [100, 200]:
            raise ValueError("Status must be 100 (Active) or 200 (Stop)")
        return v


# --- Example Usage ---
def handle_gemini_output(raw_json_from_ai: str):
    try:
        # This parses and validates simultaneously
        command = RobotBrainPacket.model_validate_json(raw_json_from_ai)

        print(f"Decision: {command.reasoning.intent}")
        print(f"To Arduino -> T: {command.controls.throttle}, S: {command.controls.steering}")

        return command
    except Exception as e:
        print(f"Invalid AI response: {e}")
        return None