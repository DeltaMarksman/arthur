from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class ControlVectors(BaseModel):
    throttle: int = Field(..., ge=-255, le=255, description="Motor speed (-255 to 255)")
    steering: int = Field(..., ge=-255, le=255, description="Turning bias (-255 to 255)")
    duration_ms: int = Field(default=500, description="How long to execute the command")
    mode: str = Field(default="standard")


class Reasoning(BaseModel):
    observation: str = Field(..., description="What the AI sees in the environment")
    intent: str = Field(..., description="The logic behind the movement")
    confidence_score: float = Field(..., ge=0.0, le=1.0)


class RobotCommand(BaseModel):
    # Header info
    status: int = Field(default=100, description="100 to continue, 200 to stop")
    timestamp: datetime = Field(default_factory=datetime.now)

    # Nested structures
    reasoning: Reasoning
    controls: ControlVectors

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
        command = RobotCommand.model_validate_json(raw_json_from_ai)

        print(f"Decision: {command.reasoning.intent}")
        print(f"To Arduino -> T: {command.controls.throttle}, S: {command.controls.steering}")

        return command
    except Exception as e:
        print(f"Invalid AI response: {e}")
        return None