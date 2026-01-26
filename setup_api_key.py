from pathlib import Path

if Path("api_key.txt").exists():
    print("✅ api_key.txt already exists")
else:
    while True:
        api_key = input("Enter your GRADIENT_MODEL_ACCESS_KEY: ").strip()
        if api_key:
            Path("api_key.txt").write_text(api_key)
            print("✅ API key saved to api_key.txt")
            break
        else:
            print("❌ API key cannot be empty. Please try again.")
