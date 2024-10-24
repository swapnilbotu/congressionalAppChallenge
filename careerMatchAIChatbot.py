import google.generativeai as genai

# Configure the API key directly (not recommended for production)
genai.configure(api_key="AIzaSyAPLEHp-EgmbZgMxhQXZ1LVrd5BcFBhMFo")

class CareerChatbot:
    def __init__(self):
        self.history = []
        self.current_state = "ask_career"  # Initial state to ask for career
        self.career_of_interest = None
        self.zipcode = None
        self.initial_message = "Hi there! Please enter the career that you are interested in learning more about?"

    def get_response(self, user_input):
        if self.current_state == "ask_career":
            self.career_of_interest = user_input.strip()
            self.current_state = "ask_zipcode"
            return f"Great! You're interested in {self.career_of_interest}. Now, could you provide your zip code? If you don't want to, just type 'no'."

        elif self.current_state == "ask_zipcode":
            if user_input.lower() == 'no':
                self.zipcode = None  # No zip code provided
                self.current_state = "provide_info"
                return f"Got it! I'll gather general information about {self.career_of_interest} for you."
            else:
                self.zipcode = user_input.strip()
                self.current_state = "provide_info"
                return f"Thank you! Let me gather information about {self.career_of_interest} in your area (zip code {self.zipcode})."

        elif self.current_state == "provide_info":
            # Combine history with current input to create the chatbot prompt
            if self.zipcode:
                prompt = f"User is considering a career in {self.career_of_interest} and lives in {self.zipcode}. "
            else:
                prompt = f"User is considering a career in {self.career_of_interest}. "

            prompt += """Write in a direct, personable, casual tone. Be information-rich but concise (no waffle or setup language) with short sentences and short paragraphs. Use jargon-free, clear language. Clarity is key. Use bullet points, numbered lists, tables to improve readability. Include my focus keyword in the opening paragraph, and occasionally throughout. Use active voice; avoid passive voice. Address the reader with 'you' and 'your'. Minimise the use of adjectives and adverbs. DO NOT use unnecessary words like: ensure, crucial, etc."""

            for entry in self.history:
                prompt += f"{entry}\n"
            prompt += f"You: {user_input}\nChatbot: "

            # Use the Generative AI model to generate the response
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)

            # Store user input and chatbot response in history
            self.history.append(f"You: {user_input}")
            self.history.append(f"Chatbot: {response.text}")

            self.current_state = "ask_career"  # Reset to ask for a new career after providing info
            return response.text

def main():
    print("\n\n\n\n\n\n\n\n\nWelcome to the Career Advisor Chatbot!")
    print("Type 'exit' to end the conversation.")

    # Create an instance of the chatbot
    chatbot = CareerChatbot()

    # Start the conversation with a predefined message
    print("Chatbot:", chatbot.initial_message)
    chatbot.history.append(f"Chatbot: {chatbot.initial_message}")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Chatbot: Goodbye!")
            break

        # Generate chatbot response
        response = chatbot.get_response(user_input)
        print("Chatbot:", response)

if __name__ == "__main__":
    main()
