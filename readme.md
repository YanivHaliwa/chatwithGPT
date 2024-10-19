# GPT-powered Tools Suite

This repository contains a suite of powerful Python-based tools that leverage OpenAI's GPT models for various tasks, including chat interactions, file processing, code generation, and Linux command assistance. Each tool is designed to provide a unique set of features for different use cases.

## Tools Overview

1. **Advanced GPT Chat (gptchat)**
2. **GPT for Python (gptpy)**
3. **Linux Command Expert ChatBot (gptshell)**

for more scripts using GPT for translation and subtitle check here: [Subtitle Management Tools section in the main README](https://github.com/YanivHaliwa/Linux-Stuff/tree/master?tab=readme-ov-file#subtitle-management-tools).


## Common Features

- Utilizes OpenAI's GPT-4 model for intelligent responses
- Maintains conversation history for context-aware interactions
- Colorized output for improved readability
- Error handling and graceful exit options

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/YanivHaliwa/chatwithGPT.git
   cd chatwithGPT
   ```

2. Install the required dependencies:
   ```
   pip install openai colorama requests beautifulsoup4 pandas pytesseract Pillow
   ```

3. Set your OpenAI API key as an environment variable:
   ```
   export OPENAI_API_KEY='your_api_key_here'
   ```

## Tool-specific Features and Usage

### 1. GPT Chat Advanced (gptchat)

A versatile chat interface with advanced file processing and image analysis capabilities.

#### Features:
- **Text extraction from URLs**: Fetch and process text content directly from web pages.
- **File reading and processing**: Supports a wide range of file formats including `txt`, `md`, `html`, `css`, `xml`, `pdf`, `xls`, `xlsx`, `csv`, `py`.
- **Bulk file reading**: Automatically process all supported files in a designated 'files' folder.
- **Image processing with OCR and GPT-4 Vision integration**: Analyze images and extract relevant information.
- **Custom bot creation with expertise and style**: Users can add special bots with custom expertise and communication styles. 
    GPT will automatically determine which bot should respond to the user's query based on the context.
- **multi bots**: default is that gpt decide which special bot to answer. but its possible to activate /multi so all bots exist will respond to same input



#### Usage:
```
python gptchat.py
```

#### Special Commands:
- `/help`: Show help message
- `/exit`: Exit the script
- `/clear`: Clear conversation history and output files
- `/url [URL]`: Extract and process text from a given URL
- `/read [file path]`: Read and process a specific file
- `/image [image path]`: Process an image for analysis
- `/readfiles`: Read all supported files from the 'files' folder
- `/tr [text]`: Translate the given text
- `/add`: add user in bot lists
- `/list`: list all existing bots in file
- `/multi`: Get responses from all bots listed in the file. This can be disabled only by triggering the '/single' command.
- `/single`:Get a response from only one bot, selected by the system.



### 2. GPT Python (gptpy)

A tool designed for generating, updating, and executing Python code snippets using GPT.

#### Features:
- Generate and execute Python code snippets based on user input
- Save and manage conversation histories
- Dynamic interaction with generated code, including running and capturing output

#### Usage:
```
python gptpy.py
```

#### Special Commands:
- `/help`: Show help message
- `/run`: Execute the last generated Python script
- `/clear`: Clear all records from the conversation and code output files
- `/read <file>`: Read and process the specified file's content
- `exit`: Exit the script


### 3. GPT for Linux Commands (gptshell)

A ChatBot specialized in providing expert-level Linux command suggestions and execution.

#### Features:
- Expert-level Linux command suggestions
- Concise command responses tailored to user queries
- Option to execute suggested commands with safety prompts
- Automatic inclusion of 'sudo' for commands requiring elevated permissions

#### Usage:
```
python gptshell.py
```

#### Special Commands:
- `/help`: Show help message
- `exit`: Exit the script


## Notes

- Ensure your OpenAI account has access to the GPT-4 model.
- Some features may require additional setup or dependencies (e.g., OCR capabilities for image processing).
- Use caution when executing suggested commands, especially those with 'sudo' privileges.

## Contributing

Contributions are welcome! Please feel free to submit pull requests, report bugs, or suggest new features for any of the tools in this suite.

## License

This project is open-source and available under the [MIT License](LICENSE).
