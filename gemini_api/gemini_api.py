from google import genai
from api_header import API_KEY
import control_defaults as cd
import json
import time

client = genai.Client(api_key=API_KEY)


# --- Existing API Functions ---

def gemini_api(prompt, response_count):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{prompt}; keep this response shorter than 5 sentences"
    )
    print(f"\nGemini: {response.text}")
    response_count += 1
    return (100 if response_count < 10 else 200), response_count


def gemini_api_movement(pos: cd.RobotPosition, target: cd.TargetRobotPosition, prompt, response_count):
    context = (
        f"Position: {pos.model_dump()}, Target: {target.model_dump()}. "
        f"Task: {prompt}"
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=context,
        config={
            "response_mime_type": "application/json",
            "response_schema": cd.RobotBrainPacket,
        }
    )

    try:
        command = cd.RobotBrainPacket.model_validate_json(response.text)
        print(f"\n[AI Reasoning]: {command.reasoning}")
        print(f"[Action]: T:{command.controls.throttle} S:{command.controls.steering}")

        # Update our local position for simulation purposes
        # (Ideally, this would be replaced by actual Arduino feedback)
        pos.x += (command.controls.throttle / 255.0)
        pos.theta += (command.controls.steering / 255.0)

        status = command.status
    except Exception as e:
        print(f"Error parsing movement JSON: {e}")
        status = 100

    response_count += 1
    return status, response_count


# --- Main Execution ---

if __name__ == "__main__":
    status = 100
    count = 0

    current_pos = cd.RobotPosition(x=0.0, y=0.0, theta=0.0)
    target_pos = cd.TargetRobotPosition(target_x=10.0, target_y=10.0)

    print("System active.")
    print("100: Chat | 150: Run 5-Movement Test | 200: Stop")

    while status != 200:
        user_input = input("\nInput Command/Code: ")

        # 1. Check for Stop Code
        if user_input == "200":
            print("Shutting down...")
            break

        # 2. Check for 5-Movement Test Code
        elif user_input == "150":
            print("\n--- Starting 5-Movement Autonomous Test ---")
            test_prompt = "Navigate toward the target safely."

            for i in range(5):
                print(f"\n--- Test Step {i + 1}/5 ---")
                status, count = gemini_api_movement(current_pos, target_pos, test_prompt, count)

                if status == 200:
                    print("AI requested stop during test.")
                    break

                time.sleep(0.5)  # Brief pause for readability
            print("\n--- Test Sequence Complete ---")

        # 3. Handle General Chat or Manual "Move"
        else:
            try:
                # If they just entered 100 or something else, treat as chat
                if user_input == "100":
                    user_input = input("Chat Message: ")

                if "move" in user_input.lower():
                    status, count = gemini_api_movement(current_pos, target_pos, user_input, count)
                else:
                    status, count = gemini_api(user_input, count)
            except Exception as e:
                print(f"Error: {e}")

    print("Loop exited.")