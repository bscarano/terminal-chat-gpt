#!/usr/bin/env python
import openai
import os
import pyperclip
import curses
from colorama import Fore, Style
from rich.console import Console
from rich.markdown import Markdown

class Chatbot:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')

        self.MODEL = "gpt-4"
        self.default_history = [{'role': 'system', 'content': 'You are a helpful assistant.'}]
        self.messages = self.default_history.copy()
        self.count = 1
        self.request = ""
        self.blank_lines = 0

    def chat_completion(self):
        response = openai.ChatCompletion.create(model=self.MODEL, messages=self.messages, stream=True)

        print(Fore.WHITE)
        console = Console()

        answer = ""
        for chunk in response:
            finish_reason = chunk['choices'][0]['finish_reason']
            if finish_reason == 'stop':
                break

            content = chunk['choices'][0]['delta']['content']
            answer = answer + content

            console.print(content, end="")

        print(Style.RESET_ALL)
        return answer

    def process_query(self, query):
        new_messages = self.messages
        new_messages.append({'role': 'user', 'content': query})
        answer = self.chat_completion()

        self.messages = new_messages
        self.messages.append({'role': 'assistant', 'content': answer})
        self.count = self.count + 1

        print()

    def paste(self):
        try:
            text = pyperclip.paste()
            print(text)
            self.request = self.request + text + '\n'
        except Exception as e:
            print(e)

    def reset(self):
        self.messages = self.default_history.copy()
        self.count = 1
        self.request = ""

    def add_line(self, line):
        self.request = self.request + line + '\n'

    def get_input(self):
        try:
            print(Fore.WHITE + f"[{self.count}]> " + Fore.YELLOW, end="")
            line = input()

            if line == "/help" or line == "/?":
                help()
                return True

            if line == "/new" or line == "/":
                self.reset()
                os.system('clear')
                return True

            if line == "/paste" or line == "/p":
                self.paste()
                self.blank_lines = 0
                return True

            if line == "/exit" or line == '/quit' or line == '/q':
                return False

            if line == ".":
                self.process_query(self.request.strip()) # strip trailing empty lines before processing
                self.blank_lines = 0
                return True

            if line.strip() == "" and self.request.strip() != "":
                self.blank_lines += 1
                if self.blank_lines >= 2:
                    self.process_query(self.request.strip())
                    self.blank_lines = 0
            else:
                self.blank_lines = 0

            self.add_line(line)
            return True
        except Exception as e:
            print(e)
            return True
    
def help():
    print()
    print("Enter a multi-line prompt")
    print("Enter two blank lines or '.' to process the prompt")
    print("")
    print("commands:")
    print("/new or / - reset the history")
    print("/quit /exit /q - to exit")
    print("/paste - paste from clipboard")
    print()

if __name__ == '__main__':
    bot = Chatbot()

    running = True
    while (running):
        running = bot.get_input()
