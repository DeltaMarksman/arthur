from google import genai
from api_header import API_KEY

client = genai.Client(api_key=API_KEY)

def gemini_api(prompt, response_count):
    # Request the stream
    response_stream = client.models.generate_content_stream(
        model="gemini-3-flash-preview",
        contents=f"{prompt}; keep this response to less than 3 sentences"
    )

    # Process the stream and print response
    for chunk in response_stream:
        print(chunk.text, end="")
    print() # New line after stream finishes

    # Increment counter
    response_count += 1

    # Logic: Continue if under 5 responses, else stop
    if response_count < 5:
        return 100, response_count
    else:
        print("\n--- Max conversation limit reached ---")
        return 200, response_count

if __name__ == "__main__":
    # Initialize status to start the loop
    status = 100
    count = 0
    print("System active. Enter '200' to stop.")

    while status == 100:
        user_input = input("Ask Gemini 3: ")
        status, count = gemini_api(user_input, count)
        # Try to convert input to an integer to match your condition
        try:
            int(user_input)
            status = int(user_input)
        except ValueError:
            continue

        if status == 100:
            print("Status remains 100. Continuing...")
        elif status == 200:
            print("Status 200 received. Shutting down.")
        else:
            continue



    print("Loop exited.")
