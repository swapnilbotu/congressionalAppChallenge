import google.generativeai as genai

# Configure the API key directly (not recommended for production)
genai.configure(api_key="AIzaSyAPLEHp-EgmbZgMxhQXZ1LVrd5BcFBhMFo")

# Example variables (replace with actual user input from your application)
selected_career = "Software Engineer"  # Example career chosen by the user
user_zipcode = "95678"  # Example zip code provided by the user

def chatbot_response(user_input, career, zipcode, history):
    # Combine history with current input
    prompt = f"User is considering a career in {career} and lives in {zipcode}. Write in a direct, personable, casual tone. Not upbeat or exuberant but straightforward and helpful. Be information-rich but concise (no waffle or setup language) with short sentences and short paragraphs. Use jargon-free, clear language. Clarity is key. Use bullet points, numbered lists, tables to improve readability. Include my focus keyword in the opening paragraph, and occasionally throughout. Use active voice; avoid passive voice. Address the reader with 'you' and 'your'. Don't overexplain your work, just provide the requested writing. Minimise the use of adjectives and adverbs DO NOT use these words: ensure, crucial, vital, nestled, uncover, journey, embark, unleash, dive, world, delve, discover, plethora, whether, indulge, crucial, more than just, not just, unlock, unveil, look no further, world of, realm, elevate, whether you're, landscape, navigate, daunting, both style, tapestry, unique blend, blend, more than just, enhancing, game changer, stand out, stark, contrast.Also:Acknowledge and correct any past errors.Use the metric system for measurements and calculations.Search the web to research your answer before responding.It's OK to be negative, to criticise or push back on ideas I have. You only need to be positive when it's necessary, appropriate. Be concise with answering the user's questions, always leave the user with a relevant question they need to answer."
    for entry in history:
        prompt += f"{entry}\n"
    prompt += f"You: {user_input}\nChatbot: "
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

def main():
    print("\n\n\n\n\n\n\n\n\nWelcome to the Career Advisor Chatbot!")
    print("Type 'exit' to end the conversation.")
    
    # List to hold the conversation history
    history = []

    # Start the conversation with a predefined message
    initial_message = "Wondering if this is the right career for you?"
    print("Chatbot:", initial_message)
    history.append(f"Chatbot: {initial_message}")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Chatbot: Goodbye!")
            break

        # Generate chatbot response
        response = chatbot_response(user_input, selected_career, user_zipcode, history)
        
        # Store user input and chatbot response in history
        history.append(f"You: {user_input}")
        history.append(f"Chatbot: {response}")
        
        print("Chatbot:", response)

if __name__ == "__main__":
    main()
