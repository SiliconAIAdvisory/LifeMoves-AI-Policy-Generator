from agent import ask_agent

print("🧾  Assistant")
print("Type 'exit' to quit.\n")

# Interactive loop for CLI conversation
while True:
    user_input = input("👤 You: ")
    if user_input.strip().lower() in ["exit", "quit"]:
        print("👋 Goodbye!")
        break

    try:
        response = ask_agent(user_input)
        print(f"\n🧠 Agent:\n{response}\n")
    except Exception as e:
        print(f"❌ Error: {e}")
