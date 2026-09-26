from api.gemini import ask_gemini


def main():
    prompt = "Hello! Please introduce yourself briefly."
    print(f"Prompt: {prompt}\n")

    try:
        response = ask_gemini(prompt)
        print("Response:")
        print(response)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
