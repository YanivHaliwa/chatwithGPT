# 1. Linux Command Expert ChatBot - GPTCODE

This Python script powers a ChatBot designed to provide expert-level, concise, and precise Linux command responses to user queries. Utilizing OpenAI's GPT-4, the ChatBot offers accurate and context-aware command suggestions, tailoring its responses to the needs of Linux enthusiasts and professionals alike.

## Features

- **Expert in Linux Commands**: Specializes in Linux commands, delivering concise command examples directly relevant to user queries.
- **Concise Command Responses**: Focuses on delivering the exact commands needed without unnecessary detail.
- **Environment-Specific Commands**: Generates commands tailored to specific environment variables for enhanced compatibility.
- **Precise File Locations**: Includes commands to determine file locations or names when uncertain, ensuring accuracy.
- **Error Handling**: Redirects error output to null for clean command output presentation.
- **Sudo Permissions**: Automatically includes 'sudo' for commands that likely require elevated permissions.
- **Conversation History**: Maintains a log of interactions, allowing for context recall in ongoing conversations.
- **Command Execution**: Offers an option to execute commands directly, with confirmation prompts for safety.
- **Command Output Display**: Shows the results of executed commands in the terminal, providing immediate feedback.
- **Persistent Conversation Logs**: Stores conversation history in "conversation.txt" to resume conversations across sessions.
- **Terminal Result Logging**: Logs executed commands and outputs in "terminal_result.txt" for future reference.
- **Keyboard Interrupt Handling**: Gracefully manages Ctrl+C interrupts, allowing users to exit or resume conversations smoothly.


 
# 2. Advanced GPT in the shell - GPTCHAT

This Python script utilizes the OpenAI GPT model to offer a versatile text processing tool capable of handling various tasks, including extracting text from URLs and engaging in conversational interactions. It leverages OpenAI's powerful GPT-4 model to understand and generate responses based on the user's input, making it an invaluable asset for automating responses and processing textual data.

## Features

- **Text Extraction from URLs**: Automatically fetches and cleans text from any provided URL, making it easy to process web content.
- **Conversational Interface**: Engages users in a conversational manner, utilizing OpenAI's GPT-4 for generating responses.
- **Customizable Responses**: Tailored responses based on user input, conversation history, and specific instructions coded within the script.
- **Error Handling and Logging**: Efficiently handles errors and logs conversation history for review and continuation of sessions.
- **Dynamic Content Processing**: Adapts responses based on dynamic inputs and previous interactions, ensuring relevant and context-aware outputs.


# 3. GPT for python - GPTPY

GPTpy is a Python utility designed to facilitate interaction with the Generative Pre-trained Transformer (GPT) models. It simplifies generating responses, managing conversation logs, and executing dynamically generated Python code snippets.

## Features

- Generate and execute Python code snippets based on GPT model responses.
- Save and manage conversation histories for review and auditing.
- Allow dynamic interaction with generated code, **including running and capturing output**.



# Requirements

- Python 3.x
- An OpenAI API key
- Python packages: `openai`, `colorama`, `requests`, `beautifulsoup4`


# Installation

1. Clone the repository or download the script to your local machine.
2. Install the required dependencies by running:

```sh
pip install openai colorama requests beautifulsoup4
```

3. Set your OpenAI API key as an environment variable:

```sh
export OPENAI_API_KEY='your_api_key_here'
```

# Usage

1. Run the Python script to initiate the ChatBot.
2. To exit, either type "exit" or use the keyboard interrupt (Ctrl+C).


# License

This project is made available under the MIT License - see the LICENSE file for details.

# Contributing

Contributions are welcome! Feel free to fork the project, make changes, and submit pull requests. For bugs, feature requests, or feedback, please open an issue.

 