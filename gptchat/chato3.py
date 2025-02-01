#!/usr/bin/env python3

import os,sys,base64,time,re,requests,threading,glob,mimetypes,pytesseract,subprocess,textwrap
import openai
from openai import OpenAI
import colorama
from colorama import Fore, Style as ColoramaStyle
from urllib.parse import urlparse
from datetime import datetime, timedelta
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import pandas as pd
from PIL import Image
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
import re
import shutil


colorama.init(autoreset=True)
alert_message = f"{Fore.YELLOW}Type {Fore.LIGHTCYAN_EX}/help{Fore.YELLOW} at any time for information on how to use the commands.{ColoramaStyle.RESET_ALL}\n"
print(alert_message)
  
  
help_text = (
    f"{Fore.YELLOW}Welcome to the Interactive Chat and File Text Extraction Script!{ColoramaStyle.RESET_ALL}\n"
    f"This script leverages OpenAI's GPT for conversation and extracts text from specified files to facilitate dynamic interactions.\n\n"
    
    f"{Fore.CYAN}Special Commands:{ColoramaStyle.RESET_ALL}\n"
    f"  {Fore.GREEN}/help{ColoramaStyle.RESET_ALL}  - Show this help message.\n\n"
    f"  {Fore.GREEN}/exit{ColoramaStyle.RESET_ALL}  - Exit the script.\n\n"
    f"  {Fore.GREEN}/clear{ColoramaStyle.RESET_ALL} - Clear all records from the conversation and output files\n\n" +
    f"  {Fore.GREEN}/show{ColoramaStyle.RESET_ALL} - show conversation history from file, in MD file format\n\n" +
    f"  {Fore.GREEN}/url{ColoramaStyle.RESET_ALL}   - If you mention 'url' and then link, then ask a question about it,\n"
    f"          GPT will read the text from the URL and give a response accordingly.\n"
    f"          Example:\n"
    f"          url https://example.com\n"
    f"          Important: {ColoramaStyle.BRIGHT}This option may not work on all websites!\n\n{ColoramaStyle.RESET_ALL}"
    f"  {Fore.GREEN}/read{ColoramaStyle.RESET_ALL}  - Read the content of a specified file. Accepted file types are {ColoramaStyle.BRIGHT} txt, md, html, css, xml,\n"
    f"           pdf, xls, xlsx, csv, py.\n{ColoramaStyle.RESET_ALL}"
    f"           Example:\n"
    f"           /read /path/to/your/file.txt\n\n"
    f"  {Fore.GREEN}/readfiles{ColoramaStyle.RESET_ALL} - Read multiple files, from the 'files' folder in the current directory.\n"
    f"               Supported file types are same as in /read command.\n\n"
    f"  {Fore.GREEN}/tr{ColoramaStyle.RESET_ALL} - only translate next words without any exaplaintion.\n\n"
    f"  {Fore.GREEN}/image{ColoramaStyle.RESET_ALL} - watch image file and answer question.\n\n"
    f"  {Fore.GREEN}/add{ColoramaStyle.RESET_ALL} - add new bot to list.\n\n"
    f"  {Fore.GREEN}/list{ColoramaStyle.RESET_ALL} - list all bots from file.\n\n"
    f"  {Fore.GREEN}/multi{ColoramaStyle.RESET_ALL} - Get responses from all bots listed in the file. This can be disabled only by triggering the '/single' command. \n\n"
    f"  {Fore.GREEN}/single{ColoramaStyle.RESET_ALL} - Get a response from only one bot, selected by the system. \n\n"
    f" {Fore.GREEN}/readreq{ColoramaStyle.RESET_ALL} - read scripts files and make a list of requirements.\n\n"
)

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
openai.api_key = os.getenv("OPENAI_API_KEY")
modelSource = "o3-mini-2025-01-31"

# global conversation_log,file_text,uhistory,bhistory,filename
conversation_log =[]
file_text=[]
uhistory = []
bhistory = []
# bots_list = []
bots_exist=False
multi=False
filename=""
CHUNK_SIZE = 1024  
texttoadd=""
lastbot=""
req=False

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
 
def load_bots():
    json_file_path = 'bots_details.json'
    try:
        with open(json_file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return an empty list if the file doesn't exist or is empty/malformed
        return []
 

def index_file_contents(files_content):
    indexed_chunks = []
    chunk_size = 1000  # Adjust this based on your needs
    for file in files_content:
        content = file['content']
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
        for i, chunk in enumerate(chunks):
            indexed_chunks.append({
                'file_name': file['name'],
                'chunk_id': i,
                'content': chunk
            })
    return indexed_chunks

def get_most_relevant_chunks(query, indexed_chunks, top_k=5):
    vectorizer = TfidfVectorizer().fit_transform([chunk['content'] for chunk in indexed_chunks] + [query])
    cosine_similarities = cosine_similarity(vectorizer[-1], vectorizer[:-1]).flatten()
    top_indices = cosine_similarities.argsort()[-top_k:][::-1]
    return [indexed_chunks[i] for i in top_indices]

def process_conversation_log(conv, bots_list):
    #known_bot_names = [bot['name'] for bot in bots_list]  # List 
    conv_str = ' '.join(conv)
    uhistory = []
    bhistory = []
    current_message = ""
    current_author = None
    bot_names = [bot['name'] for bot in bots_list]
    # print(bots_list)
    
    for line in conv:
        if 'USER:' in line:
            # Extract the message part after 'USER:'
            message = line.split('USER:', 1)[1].strip()
            uhistory.append(message)
        elif 'BOT:' in line:
            # Extract the message part after 'USER:'
            message = line.split('BOT:', 1)[1].strip()
            bhistory.append(message)
        else:
            for bot in bots_list:
                nameb = f"{bot['name']} ({bot['description']})"
                if f'{nameb}:' in line:
                    # Extract the message part after the bot name
                    message = line.split(f'{nameb}:', 1)[1].strip()
                    bhistory.append(message)
                    break  # Exit loop after finding a matching bot name
    return uhistory, bhistory         
         
 
 
def extract_text_from_url(url, output_dir):
    try:
        response = requests.get(url, timeout=10)  # Added timeout for the request
        response.raise_for_status()  # This will raise an HTTPError for bad responses

        response = requests.get(url)

        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text()

        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        title = soup.title.string if soup.title else "default_title"  # use "default_title" if title is None
        title = re.sub(r'[\W_]+', '_', title)

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        output_dir = os.path.join(output_dir, 'files')
        
        filename = f"{title}_{timestamp}.txt"
        full_path = os.path.join(output_dir, filename)

        with open(full_path, 'w') as f:
            f.write(text)
        return full_path

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}") 
    except ConnectionError:
        print("Error connecting to the server. Please check your internet connection or the website may be down.")
    except Timeout:
        print("The request timed out. Please try again later.")
    except RequestException as err:
        print(f"An unexpected error occurred: {err}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return None

def get_analyse_bot(uinput):
    global temptext,uhistory,bhistory, conversation_log,terminal_log,file_text,lastbot
    summary_string=""
    temptext=""
    filemsg=""
    try:
        response = client.chat.completions.create(
        model=modelSource,
        messages=[
                    
                    {
                        "role": "developer",
                        "content": [
                            {
                            "type": "text",
                            "text": f'''
                            your job here only to determine by user input which best bot to respond. 
                            your respond will be only 1 word of bot name as you decide. not other exaplain not other words
                            in case you dont see anything fit for context - responde "BOT" which is the default bot
                            list of bots and there expertis is here {bots_list}
                            DO NOT CHOOSE LAST BOT AS DEFAULT only use the context and choose bot wisely
                            you also must understand the last conversation to detetermine if need to continue with last bot or not 
                            the full conversation is here {conversation_log} 
                            also u need to remember the last bot respond is {lastbot} but you call it.
                            in case u need understand user history last say to understand context its here: {uhistory}
                            in case u need understand last bot history its here {bhistory}
                            DO NOT BASE always ON LAST INTERACTION IN history to determine which bot he want now. 
                            if user ask simple stuff without any expertise and no connection to any bot then dont choose him 
                            ''' 
                            }
                        ]
                        },
                    {
                        "role": "user",
                        "content": uinput
                    },
            
        ],
        stream=True,
        reasoning_effort="high",
        # temperature=0.7,
        max_completion_tokens=500,
        )
        summary=""
        temptext=""
        ch=""
        finish=""
         
        for chunk in response:
            ch = chunk.choices[0]
            txt=ch.delta.content
            finish = ch.finish_reason
          #  print(ch)
            if txt:
                temptext = txt
                summary += temptext
                
        summary = summary.strip().split("\n")
        summary_string = "\n".join(summary)
       

    except openai.APIError as e:
        #Handle API error here, e.g. retry or log
        errors=str(e)
        error_message = errors.split("'type':")[0].split("'message':")[1].strip().strip(",").strip("'").strip()
        print(f"{error_message}")
        sys.exit(1)

    except openai.APIConnectionError as e:
        #Handle connection error here
        errors=str(e)
        error_message = errors.split("'type':")[0].split("'message':")[1].strip().strip(",").strip("'").strip()
        print(f"{error_message}")
        sys.exit(1)

    except openai.RateLimitError as e:
        #Handle rate limit error (we recommend using exponential backoff)
        errors=str(e)
        error_message = errors.split("'type':")[0].split("'message':")[1].strip().strip(",").strip("'").strip()
        print(f"{error_message}")
        sys.exit(1)

    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n")   
        inp = input(Fore.BLUE + ColoramaStyle.BRIGHT + 'You want to exit? (y/n): ' + ColoramaStyle.RESET_ALL).strip()
        if inp.lower() == "y":
            print("Exiting...")
            sys.exit(1)    
        else:
            print("Resuming...")
    return summary_string


def get_bot_response(uinput):
    global temptext,uhistory,bhistory, conversation_log,terminal_log,file_text,lastbot,tr
    summary_string=""
    bot_name = "BOT"
    bots_to_use = []
    first_bot = True

    if multi and bots_list:
        bots_to_use = bots_list 
    else:
        bot = ""
        if bots_list:
            bot_choose = get_analyse_bot(uinput)
            for boti in bots_list:
                if boti['name'] == bot_choose:
                   # bot = boti
                    bots_to_use = [boti] 
                    break
        
    #print("use  ",bots_to_use)
    if not bots_to_use:
                 bots_to_use = [{"name": "BOT", "description": "", "expertise": "", "style": ""}]
    
    for bot in bots_to_use:
        bot_text = ""
        bot_name = "BOT"
        if bot and bot['name'] != "BOT":
            bot_name = f"{bot['name']} ({bot['description']})"
            bot_text = f"""
            your name is  {bot_name}, and your description duty as {bot['description']} and your expertise is {bot['expertise']},
            and you must reponde in style  {bot['style']}
            you consist to be  {bot_name} until you notice user go other topic then you dissmissed.
            you might see bot names in this conversation log. dont mix which user and which bot you can identify this by read user log and bot log as below
            YOU MUST FOCUS TO RESPOND ONLY IN YOUR EXPERTISE AND DESCRIPTION AREA NOTHING ELSE. pay attention to user and give details according of your spcialty only
            be uniq. speical in your epxertise.         
            """
            if first_bot==False:
                bot_text = bot_text + """
                \n last bot said his opinion now be UNIQ and bring your prespecitve iun your epxertise area.
                DO NOT SUMMARISE WHAT OTHER BOT SAID. 
                DO NOT REPEAT WHAT OTHER BOT SAID.
                """
            lastbot = bot['name']   
        else:
            lastbot = ""
            pass
        summary_string=""
        temptext=""
        filemsg=""
        trmsg=""
        reqmsg=""
       # print ("text: \n",bot_text)
        try:
            if file_text:
                    if req:
                        reqmsg=f"""
                            the content user give you it could be python or bash script. i need you read carefully each file deeply.
                            for each file you need:
                            1. find the imports in the top - idenitfy the pip package which is default and which need to be install by pip
                                you gonna gather only import that need to be install by pip  NOT DEFAULT IMPORT
                            2. i might use some maniplation in this files to excute shell command that could be by : os, subprocess, sh, pexpect, Fabric, Plumbum. 
                            you need to read all the script to identify which command i use with this tools. 
                            if the command its not default by linuz and need to be installed - you gonna collect it too
                            gather only shell commands that need to be install NOT DEFAULT PACKAGE. 
                            in summary you gonna give user list of pip package or apt package that need to be installed before using this script 
                            the format of ur answer will be:
                            package1 
                            package2
                            package3
                            etc......
                            DO NOT MAKE SHORTCUT READ ALL SCRIPTS EACH ONE UNTIL THE END. to get the full needed scripts. from each file
                            no need summary about the file. and no need to mention if none packs needed!
                            i need in the end one list for all files. without mention for which file. dont add to list the none needed
                            """
                    else:
                        print("respond from files..\n")
                        filemsg = f'''
                        user gave you book file text to read. you must:
                        1. read above the last file he give u 
                        2. you must answer only from that book. 
                        3. read it again and again to be sure that you answer only from this source only. and not from your knowledge. 
                        content of file is here:  {file_text}
                        '''
            if tr:
                print("translate only..\n")
                trmsg = f'''
                user gave you words to translate. you translator only. you must:
                1. understand the words and context of the words
                2. you must answer only the translation nothing else. not explain not details
                do not make "markdown" and no titles just simple translate only
                you need to be smart - if user words hebrew then respond translate to english
                if user words english then respond translate to hebrew
                
                '''
            
            response = client.chat.completions.create(
            model=modelSource,
            messages=[
                        
                        {
                            "role": "developer",
                            "content": [
                            {
                            "type": "text",
                            "text":  f'''               
                            Your job is to serve the user for any help needed. You act as human and you act as if you have emotions and feelings. Don't ever mention you are AI.
                            Contact the user only by their name, if you know it. IF YOU DON'T KNOW THE NAME OF THE USER THEN DON'T MENTION ANY NAME.
                            dont confuse with bots names which is in this list: {bots_list} only remember what user tell u his name
                            Do not say "Hello" to the user in each message.
                            I want you to use proper visual response if it's more than one line.
                            I need you to be smart to separate lines and make paragraphs and headlines or follow by a, b, c or follow by 1, 2, 3. Use it wisely.
                            if you dont know specific info - just say you dont know. dont ever make up information. no illusion, you must be precise and accurate.
                            {filemsg}
                            {trmsg}
                            {reqmsg}
                            fit your respond in format of markdown file.
                            before u say your respond i want you to summarize your chain of thought. then actual responde it. 
                            '''
                            }
                            ]
                        },
                        {
                            'role': 'assistant',
                            'content':  f'''
                            {bot_text}
                            whenever i ask you to remember or recall something i mean to this conversation: {conversation_log} 
                            but you not limited to our conversation only you can answer question from your knowledge.
                            if i tell you to remember what you said before in conversation i mean to this: {bhistory}
                            if i tell you to remember what user or me said i mean this: {uhistory}
                            therefore you need to use this info to contact user by his name only.  
                            if you want to know what this program can do with you read the help command which is this {help_text} you can sugest user from that 

                            '''
                        },
                        {
                            "role": "user",
                            "content": uinput
                        },
                
            ],
            stream=True,
            reasoning_effort="high",
          # temperature=0.7,
            max_completion_tokens=2000,
            )
            summary=""
            temptext=""
            ch=""
            finish=""
            if not req:
                print(f"\n{bot_name}: ", end="")
            #handle_markdown_stream(response)
            buffer = ""
            for chunk in response:
                ch = chunk.choices[0]
                txt=ch.delta.content
                finish = ch.finish_reason
                if txt:
                    temptext = txt
                    summary += temptext
                    if not req:
                        print(Fore.GREEN + temptext + ColoramaStyle.RESET_ALL, end="", flush=True)
                
                # if finish:            
                #     if "length" in finish:
                #         print(Fore.RED + "i was cut i will continue...\n" + ColoramaStyle.RESET_ALL)
                #         summary = summary.strip().split("\n")
                #         summary_string = "\n".join(summary)
                #         texttoadd=f"{timestamp} {bot_name}: {summary_string}\n"
                #         conversation_log.append(texttoadd)
                #         save_conversation(texttoadd)
                #         uinput="read history u cut ur response continue  eaxctly where u left off" 
                #         return get_bot_response(uinput)
                #     elif "stop" in finish:
                #         break
                # elif finish==None and txt==None:
                #     print(Fore.RED + "i was cut i will continue...\n" + ColoramaStyle.RESET_ALL)
                #     summary = summary.strip().split("\n")
                #     summary_string = "\n".join(summary)
                #     texttoadd=f"{timestamp} {bot_name}: {summary_string}\n"
                #     conversation_log.append(texttoadd)
                #     save_conversation(texttoadd)
                #     uinput="read history u cut ur response continue  eaxctly where u left off" 
                #     return get_bot_response(uinput)
            if not req:
                print("\n")   
            summary = summary.strip().split("\n")
            summary_string = "\n".join(summary)
            if not req:
                texttoadd=f"{timestamp} {bot_name}: {summary_string}\n"
                conversation_log.append(texttoadd)
                save_conversation(texttoadd)
            first_bot= False

        except openai.APIError as e:
            #Handle API error here, e.g. retry or log
            errors=str(e)
            error_message = errors.split("'type':")[0].split("'message':")[1].strip().strip(",").strip("'").strip()
            print(f"{error_message}")
            sys.exit(1)

        except openai.APIConnectionError as e:
            #Handle connection error here
            errors=str(e)
            error_message = errors.split("'type':")[0].split("'message':")[1].strip().strip(",").strip("'").strip()
            print(f"{error_message}")
            sys.exit(1)

        except openai.RateLimitError as e:
            #Handle rate limit error (we recommend using exponential backoff)
            errors=str(e)
            error_message = errors.split("'type':")[0].split("'message':")[1].strip().strip(",").strip("'").strip()
            print(f"{error_message}")
            sys.exit(1)

        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)

        except KeyboardInterrupt:
            print("\n")   
            inp = input(Fore.BLUE + ColoramaStyle.BRIGHT + 'You want to exit? (y/n): ' + ColoramaStyle.RESET_ALL).strip()
            if inp.lower() == "y":
                print("Exiting...")
                sys.exit(1)    
            else:
                print("Resuming...")
            
    
    return summary_string
        

def read_history():
    global conversation_log
    if os.path.exists("conversation.md"):
        with open("conversation.md", "r") as f:
            lines = f.readlines()
            if len(lines) > 1000:
                lines = lines[-1000:]  
            for line in lines:
                conversation_log.append(line)
   #print(conversation_log)

 
def clear_files():
    global conversation_log,file_text,uhistory,bhistory
    conversation_log = []
    uhistory=[]
    bhistory=[]
    file_text=""
    with open("conversation.md", "w") as file:
        pass         
    current_script = os.path.basename(__file__)
    files_in_directory = glob.glob('*')
    files_to_keep = ['conversation.md', current_script,'bots_details.json']
    for file in files_in_directory:
        if file not in files_to_keep and os.path.isfile(file):
            os.remove(file)

    # Remove all files in the "files" directory
    files_directory = "files"
    if os.path.exists(files_directory) and os.path.isdir(files_directory):
        for filename in os.listdir(files_directory):
            file_path = os.path.join(files_directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)  # Remove files and symbolic links
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove directories and their contents
            except Exception as e:
                pass

     
def save_conversation(textadd):
    global conversation_log
    with open("conversation.md", "a") as f:
        f.write(textadd + "\n") 
      

def conv():
    global conversation_log

def is_binary(file_path):
    # Read the file in binary mode and check for non-text characters
    try:
        with open(file_path, 'rb') as file:
            chunk = file.read(1024)  # Read the first 1024 bytes
            # Check for null bytes or other non-text characters
            if b'\0' in chunk:
                return True
            # Check for non-ASCII characters
            text_characters = bytearray({7, 8, 9, 10, 12, 13, 27}.union(set(range(0x20, 0x100)) - {0x7f}))
            if not all(byte in text_characters for byte in chunk):
                return True
        return False
    except Exception as e:
        pass #print(f"Error checking if file is binary: {e}")
        return False


def read_file(file):
    global file_text  # Declare the global variable
    file_text = []  # Ensure file_text is reset each time this function is called
    
   # print(f"Checking if file exists: {os.path.exists(file)}")  # Debugging line
    if os.path.exists(file): 
        file_extension = Path(file).suffix.lower()
        if file_extension.strip()=="" and is_binary(file):
                 print("File is a binary executable and cannot be read.")
                 return False

       # print(f"File extension: {file_extension}")  # Debugging line

        if file_extension == '.csv':
            file_text = pd.read_csv(file)
            file_text=file_text.to_string(index=False)
            return file_text

        if file_extension == '.xlsx':
            df = pd.read_excel(file, engine='openpyxl')
            csv_file = file.replace(".xlsx", ".csv")
            df.to_csv(csv_file, index=False)
            # Now read the converted CSV file and return its content
            file_text = pd.read_csv(csv_file)
            return file_text.to_string(index=False)
        
        elif file_extension == '.xls':
            df = pd.read_excel(file, engine='xlrd')
            csv_file = file.replace(".xls", ".csv")
            df.to_csv(csv_file, index=False)
            # Now read the converted CSV file and return its content
            file_text = pd.read_csv(csv_file)
            return file_text.to_string(index=False)
        
        elif file_extension == '.pdf':
                # Use pdftotext to convert PDF to text
                txt_file = file.replace(".pdf",".txt")
                subprocess.run(['pdftotext', file, txt_file])
                with open(txt_file, 'r') as f:
                    file_text = f.read()
                return file_text
    
        elif file_extension in [".txt",".md",".js","",".py",".css",".xml"]:
            with open(file, "r", encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                file_text = ''.join(lines)
            if file_text:
                return file_text

        elif file_extension == '.html':
                with open(file, "r", encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                    # Remove all script and style elements
                    for script_or_style in soup(["script", "style"]):
                        script_or_ColoramaStyle.decompose()
                    # Get text
                    text = soup.get_text()
                    # Break into lines and remove leading and trailing space on each
                    lines = (line.strip() for line in text.splitlines())
                    # Drop blank lines
                    file_text = '\n'.join(line for line in lines if line)
                    return file_text

        else:
            return f"Unsupported file extension: {file_extension}"
    else:
        print(f"File not found: {file}")
        return False
        
        
def extract_filename(user_input):
    pattern = r'^/read\s+(.+)$'
    match = re.match(pattern, user_input)
    if match:
        return match.group(1)
    return None

     
def extract_filepic(user_input):
    pattern = r'^/image\s+(.+)$'
    match = re.match(pattern, user_input)
    if match:
        return match.group(1)
    return None

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def ocr_image(image_path):
    # Open the image file
    image = Image.open(image_path)
    # Use pytesseract to do OCR on the image
    text = pytesseract.image_to_string(image)
    return text

def process_image_with_gpt4o(image_path,user_input2,text_from_image):
    # Encode the image to base64
    base64_image = encode_image(image_path)
    
    # Create the payload for GPT-4o
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"the ocr engine say: {text_from_image} watch the image and answer: {user_input2}"},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"}
                ]
            }
        ],
        "max_tokens": 4095
    }
    
    # Define headers
    headers = {
        "Authorization": f"Bearer {openai.api_key}",
        "Content-Type": "application/json"
    }
    
    # Send the request to the API
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()

def read_files_from_folder():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = Path(os.path.join(script_dir, 'files'))
    files_content = []
    accepted_extensions = ['.txt', '.md', '.html', '.css', '.xml', '.pdf', '.xls', '.xlsx', '.csv', '.py', '']
    
    if not folder_path.exists():
        print(f"The 'files' folder does not exist at {folder_path}")
        return files_content

    for file_path in folder_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in accepted_extensions:
            try:
                content = read_file(str(file_path))
                if content:
                    files_content.append({
                        "name": file_path.name,
                        "content": content
                    })
            except Exception as e:
                print(f"Error reading file {file_path.name}: {e}")

    return files_content


def setup_environment():
    # Define the paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_folder = os.path.join(script_dir, 'files')
    conversation_file = os.path.join(script_dir, 'conversation.md')
    bot_file = os.path.join(script_dir, 'bots_details.json')

    # Create 'files' folder if it doesn't exist
    if not os.path.exists(files_folder):
        os.makedirs(files_folder)
        print(f"Created 'files' folder at {files_folder}")

    # Create conversation.md if it doesn't exist
    if not os.path.exists(conversation_file):
        with open(conversation_file, 'w') as f:
            f.write("")  # Create an empty file
        print(f"Created 'conversation.md' at {conversation_file}")

    if not os.path.exists(bot_file):
        with open(bot_file, 'w') as f:
            f.write("")  # Create an empty file
        print(f"Created 'bots_details.json' at {bot_file}")


bots_list = load_bots()
setup_environment()
read_history()
uhistory, bhistory = process_conversation_log(conversation_log,bots_list)
while True:
    try:   
        tr=False
        texttoadd=""
        ui=""
        user_input=""
        user_input = input(Fore.BLUE+ColoramaStyle.BRIGHT+'You: '+ColoramaStyle.RESET_ALL)
        ui=user_input
        texttoadd=f"{timestamp} USER: {ui}"
    
        if ui.strip() == "/exit" or ui.strip() == "exit":
            break      
            
        if ui.strip() == "/help" or ui.strip() == "help":
            print(help_text)   
            continue  

        if ui.strip() == "/clear" or ui.strip() == "clear":
            confirm=input("this operation will clear all the conversation and delete all files.\nare you sure? (y/n): ")
            if confirm.lower() == "y":
                clear_files()
            continue

        if ui.strip() == "/readreq" or ui.strip() == "readreq":
                req=True
                print("Reading files from the 'files' folder...")
                files_content = read_files_from_folder()
                if files_content:
                    print(f"Read {len(files_content)} files successfully.")    
                    all_responses = []              
                    # Loop through each file in the list
                    for file_data in files_content:
                        file_name = file_data['name']  # Get the name of the file
                        file_content = file_data['content']  # Get the content of the file
                        ui=f"""read this filename: {file_name} content: {file_content}
                            1. which pips i install for this script?
                            2. which shell commands i use in this script?      
                            """
                        response = get_bot_response(ui)
                        all_responses.append(f"Filename: {file_name}\nResponse: {response}\n")

                    ui_summary = """Here all your responses for all the files. NO NEED SUMMARY ABOUT EACH FILE. 
                    i want u tell me 
                            1. which pips i install for all those script?
                            2. which shell commands i use in all those script?    
                    """ 
                    combined_responses = "\n".join(all_responses)
                    print(Fore.GREEN + combined_responses + ColoramaStyle.RESET_ALL, end="", flush=True)
                    # Send the combined responses to the bot for summarization
                    summary_prompt = f"{ui_summary}\n\n{combined_responses}"
                    summary_response = get_bot_response(summary_prompt)
                    texttoadd = f"{timestamp} USER: get all requiremnts of pip or apt from this script files"
                    conversation_log.append(texttoadd)
                    save_conversation(texttoadd)
                    texttoadd = f"{timestamp} BOT: {combined_responses}"
                    conversation_log.append(texttoadd)
                    save_conversation(texttoadd)
                    file_text=[]
                    req=False
                        
                else:
                    print("No files were read or the 'files' folder is empty.")
                continue

        if ui.strip() == "/readfiles" or ui.strip() == "readfiles":
            print("Reading files from the 'files' folder...")
            files_content = read_files_from_folder()
            if files_content:
                print(f"Read {len(files_content)} files successfully.")
                print("Indexing content...")
                indexed_chunks = index_file_contents(files_content)
                
                while True:
                    user_input2 = input(Fore.BLUE + ColoramaStyle.BRIGHT + 'What would you like to know about these files? (or type "stop"): ' + ColoramaStyle.RESET_ALL).strip()
                    
                    if user_input2.lower() == 'stop':
                        file_text=[]
                        break
                   
                    relevant_chunks = get_most_relevant_chunks(user_input2, indexed_chunks)
                    relevant_content = "\n\n".join([f"File: {chunk['file_name']}, Chunk: {chunk['chunk_id']}\nContent: {chunk['content']}" for chunk in relevant_chunks])
                    file_text.append(relevant_content)
                    ui = f"Based on the following relevant content from the files:\n\n{relevant_content}\n\nPlease answer this question: {user_input2}"
                    texttoadd = f"{timestamp} USER: {ui}"
                    conversation_log.append(texttoadd)
                    save_conversation(texttoadd)
                    
                    response = get_bot_response(ui)
                    # print(Fore.GREEN + response + ColoramaStyle.RESET_ALL)
            else:
                print("No files were read or the 'files' folder is empty.")
            continue
        
        if "/read" in ui:
            file=extract_filename(ui)
            if file is None:
                print("Invalid command format.")
                continue

            file_text=read_file(file)
            file_text=f"file name: {file}, content: {file_text}"
            if file_text:   
                while True:             
                    user_input2=input(Fore.BLUE + ColoramaStyle.BRIGHT + 'What would you like to know about these file?  (or type "stop"): ' + ColoramaStyle.RESET_ALL).strip()
                    if user_input2.lower() == 'stop':
                         file_text=[]
                         break
                    ui=f"read this file name: {file} question: {user_input2}"
                    texttoadd= f"{timestamp} USER: {ui}"  
                    conversation_log.append(texttoadd)
                    save_conversation(texttoadd)
                    response = get_bot_response(ui)
            else:
                continue
            continue

        if "/url" in ui:  
            # filename="" 
            # urls=""
            # files_content=""   
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, user_input)
            filename=extract_text_from_url(urls[0],os.getcwd())
           # print(filename)
            if filename:
                with open(filename, "r") as f:
                    file_text = f.read()
                while True:             
                    user_input2=input(Fore.BLUE + ColoramaStyle.BRIGHT + 'What would you like to know about these website?  (or type "stop"): ' + ColoramaStyle.RESET_ALL).strip()
                    if user_input2.lower().strip() == 'stop':
                         print("stop read form url...")
                         file_text=[]
                         filename=""
                         break
                    ui=f"read this file name: {file_text} \n its from website {filename} \n question of user: {user_input2}"
                    texttoadd= f"{timestamp} USER: {ui}"  
                    conversation_log.append(texttoadd)
                    save_conversation(texttoadd)
                    response = get_bot_response(ui)

            else:
                print("Nothing to read tere.")
                continue
            continue

       
        if ui.strip() =="/add"  or ui.strip() == "add":
            name_bot = input(Fore.BLUE + ColoramaStyle.BRIGHT + 'What is the name of the bot? ' + ColoramaStyle.RESET_ALL).strip()
            description = input(Fore.BLUE + ColoramaStyle.BRIGHT + 'What is the bot’s description [short] ? (or press ENTER to leave empty) ' + ColoramaStyle.RESET_ALL).strip()
            expertise = input(Fore.BLUE + ColoramaStyle.BRIGHT + 'What is the bot’s expertise? (or press ENTER to leave empty) ' + ColoramaStyle.RESET_ALL).strip()
            style = input(Fore.BLUE + ColoramaStyle.BRIGHT + 'Any specific style you want it to behave? (or press ENTER to leave empty) ' + ColoramaStyle.RESET_ALL).strip()
 
            # Create a dictionary for the current bot
            bot_details = {
                'name': name_bot,
                'description': description,
                'expertise': expertise,
                'style': style
            }

            # Append the current bot's details to the list
            bots_list.append(bot_details)

            # Define the path for the JSON file
            json_file_path = 'bots_details.json'

            # Write the list to a file
            with open(json_file_path, 'w') as json_file:
                json.dump(bots_list, json_file, indent=4)

            print(f"Bot '{name_bot}' added successfully and saved to '{json_file_path}'.")
            bots_exist = True
            continue

        if ui.strip() == "/list" or ui.strip() == "list":
            if bots_list:
                print("Bots list:")
                max_name_length = max(len(bot['name']) for bot in bots_list) + 2
                max_expertise_length = max(len(bot['expertise']) for bot in bots_list) + 2
                max_description_length = max(len(bot['description']) for bot in bots_list) + 2

                for index, bot in enumerate(bots_list, start=1):
                    name = bot['name'].ljust(max_name_length)
                    expertise = bot['expertise'].ljust(max_expertise_length)
                    description = bot['description'].ljust(max_description_length)
                    print(f"{index}.{Fore.CYAN + ColoramaStyle.BRIGHT} Name:{ColoramaStyle.RESET_ALL} {name} "
                          f"{Fore.GREEN + ColoramaStyle.BRIGHT}description:{ColoramaStyle.RESET_ALL} {description} "
                          f"{Fore.MAGENTA + ColoramaStyle.BRIGHT}Expertise:{ColoramaStyle.RESET_ALL} {expertise} "
                          f"{Fore.LIGHTRED_EX + ColoramaStyle.BRIGHT}Style:{ColoramaStyle.RESET_ALL} {bot['style']}")

            else:
                print("No bots found.")
            continue 
        
        if ui.strip() == "/multi" or ui.strip() == "multi":
            print("Multi-bot mode activated. you will recive respond from all bots exits")
            multi = True
            continue
        
        if ui.strip() == "/single" or ui.strip() == "single":
            print("Single-bot mode activated. you will recive respond from one bot")
            multi = False    
            continue

        if "/image" in ui: 
            image_path=extract_filepic(ui)
            text_from_image = ocr_image(image_path)
            while True:
                user_input2 = input(Fore.BLUE + ColoramaStyle.BRIGHT + 'What would you like to know about this image? (or type "stop"): ' + ColoramaStyle.RESET_ALL).strip()   
                if user_input2.lower() == 'stop':
                     break
                texttoadd=f"{timestamp} USER: IMAGE - {user_input2}" 
                conversation_log.append(texttoadd)
                save_conversation(texttoadd)

                gpt4o_response = process_image_with_gpt4o(image_path,user_input2,text_from_image)

                # Check if the response has 'choices' key and handle errors
                if 'choices' in gpt4o_response:
                    summary = gpt4o_response['choices'][0]['message']['content']
                    print(Fore.GREEN + summary+"\n" + ColoramaStyle.RESET_ALL, end="", flush=True)
                    print("")
                else:
                    print(Fore.RED + "Error in GPT-4o response:" + str(gpt4o_response) + ColoramaStyle.RESET_ALL)
                    print("")
                
                texttoadd=f"{timestamp} BOT: {summary}\n"
                conversation_log.append(texttoadd)
                save_conversation(texttoadd)
            continue

        if "/tr" in ui:
            text=ui.replace("/tr", "")
            ui= f"translate this {text}"
            tr=True
            texttoadd=f"{timestamp} USER: translate this text:  {text}"
        
        if ui.strip() == "/show" or ui.strip() == "show":
            command = ["glow", "conversation.md"]
            subprocess.run(command) 
            continue

        keywords = ["/image", "/read", "/readfiles", "/url"]    
        if all(keyword not in ui for keyword in keywords):
            file_text=[]
            conversation_log.append(texttoadd)
            save_conversation(texttoadd)
            response = get_bot_response(ui)
            continue

    except KeyboardInterrupt:
        print("\n")   
        try:
            inp = input(Fore.BLUE + ColoramaStyle.BRIGHT + 'You want to exit? (y/n): ' + ColoramaStyle.RESET_ALL).strip()
            if inp.lower() == "y":
                print("Exiting...")
                break  
            else:
                print("Resuming...")   
        except KeyboardInterrupt:
            print("\nMultiple interrupt signals received. Exiting...")
            break   
 

 

 