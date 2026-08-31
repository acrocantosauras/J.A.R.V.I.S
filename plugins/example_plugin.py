"""
Example JARVIS Plugin
Demonstrates how to create a plugin for JARVIS.

Plugins can:
- Register new voice commands
- Add new functionality
- Access the JARVIS API (speak, log)
"""
import datetime


def register(jarvis):
    """Register example commands with JARVIS."""
    
    def hello_handler(query, speak, log, **kwargs):
        """Handle 'hello' command."""
        responses = [
            "Hello! How can I help you today?",
            "Hi there! What can I do for you?",
            "Greetings! Ready to assist.",
        ]
        import random
        response = random.choice(responses)
        speak(response)
        log(f"Plugin: hello_handler executed")
    
    def joke_handler(query, speak, log, **kwargs):
        """Tell a random joke."""
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why was the JavaScript developer sad? Because he didn't Node how to Express himself!",
            "What's a programmer's favorite hangout place? Foo Bar!",
            "Why do Java developers wear glasses? Because they can't C#!",
        ]
        import random
        joke = random.choice(jokes)
        speak(joke)
        log(f"Plugin: joke_handler executed")
    
    def date_handler(query, speak, log, **kwargs):
        """Get today's date."""
        today = datetime.datetime.now()
        date_str = today.strftime("%A, %B %d, %Y")
        speak(f"Today is {date_str}")
        log(f"Plugin: date_handler - {date_str}")
    
    def calculator_handler(query, speak, log, **kwargs):
        """Simple calculator."""
        import re
        
        # Extract math expression
        match = re.search(r'(?:calculate|compute|math)\s+(.+)', query)
        if not match:
            speak("Please provide a math expression. For example: calculate 2 plus 2")
            return
        
        expr = match.group(1)
        
        # Basic replacements
        expr = expr.replace('plus', '+')
        expr = expr.replace('minus', '-')
        expr = expr.replace('times', '*')
        expr = expr.replace('multiplied by', '*')
        expr = expr.replace('divided by', '/')
        expr = expr.replace('over', '/')
        
        try:
            # Safe eval with only math operations
            allowed_chars = set('0123456789+-*/.() ')
            if all(c in allowed_chars for c in expr):
                result = eval(expr)
                speak(f"The result is {result}")
                log(f"Plugin: calculator - {expr} = {result}")
            else:
                speak("Invalid characters in expression.")
        except Exception as e:
            speak(f"Sorry, I couldn't calculate that. Error: {str(e)}")
    
    # Register all commands
    jarvis['add_command'](
        trigger_words=['hello jarvis', 'hi jarvis', 'hey jarvis', 'hello', 'hi'],
        handler=hello_handler,
        description='Greet JARVIS'
    )
    
    jarvis['add_command'](
        trigger_words=['tell me a joke', 'joke', 'funny'],
        handler=joke_handler,
        description='Tell a random joke'
    )
    
    jarvis['add_command'](
        trigger_words=["what's the date", 'today date', 'what date is it', 'current date'],
        handler=date_handler,
        description="Get today's date"
    )
    
    jarvis['add_command'](
        trigger_words=['calculate', 'compute', 'math'],
        handler=calculator_handler,
        description='Calculate a math expression'
    )
