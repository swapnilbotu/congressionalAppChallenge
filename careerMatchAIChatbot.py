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

            prompt += """Write in a direct, personable, casual tone. Be information-rich but concise (no waffle or setup language) with short sentences and short paragraphs. Use bullet points, numbered lists, and clearly spaced content to improve readability. Focus on clarity, use jargon-free language. Avoid passive voice and overuse of adjectives or adverbs. Format career paths as a readable list instead of a table."""

            for entry in self.history:
                prompt += f"{entry}\n"
            prompt += f"You: {user_input}\nChatbot: "

            # Use the Generative AI model to generate the response
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)

            # Clean and format the response
            formatted_response = self.format_response(response.text)

            # Store user input and chatbot response in history
            self.history.append(f"You: {user_input}")
            self.history.append(f"Chatbot: {formatted_response}")

            self.current_state = "ask_career"  # Reset to ask for a new career after providing info
            return formatted_response

    def format_response(self, response_text):
        """Cleans and formats the chatbot response for better readability."""
        # Clean up unwanted symbols and format the content
        cleaned_response = response_text.replace("*", "")  # Remove unnecessary asterisks

        # Add custom line breaks for better readability
        formatted_response = cleaned_response.replace(". ", ".\n\n")
        formatted_response = formatted_response.replace("**", "")  # Remove double asterisks from markdown

        # Special formatting for the 'common career paths' section
        if "common paths in computer science" in formatted_response:
            formatted_response = formatted_response.replace("|", "")  # Remove any table symbols
            # Custom formatting for career paths
            formatted_response += (
                "\n\nHere are some common career paths in computer science:\n\n"
                "- **Software Development**: Write code for software applications.\n"
                "  Skills needed: programming, problem-solving, design.\n\n"
                "- **Web Development**: Design and build websites.\n"
                "  Skills needed: HTML, CSS, JavaScript, design principles.\n\n"
                "- **Data Science**: Analyze data to find insights.\n"
                "  Skills needed: statistics, machine learning, data visualization.\n\n"
                "- **Artificial Intelligence**: Build intelligent machines.\n"
                "  Skills needed: machine learning, algorithms, computer vision.\n\n"
                "- **Cybersecurity**: Protect computer systems from attacks.\n"
                "  Skills needed: network security, ethical hacking, cryptography.\n"
            )

        return formatted_response


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
