import os
import random
import time
import requests
import telebot

# Enter your bot token here
bot = telebot.TeleBot('7776576163:AAHgaUg19RV8kSVM610lBaInIXsTKM3vLV4')

# Function to check if a card number is valid using the Luhn algorithm
def luhn_check(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]

    odd_digits = digits_of(card_number)[::2]
    even_digits = digits_of(card_number)[1::2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10 == 0

# Function to generate a random card number based on a BIN prefix
def generate_card_number(bin_prefix):
    card_number = str(bin_prefix)  # Start with the provided BIN
    while len(card_number) < 16:  # Visa and MasterCard usually have 16 digits
        card_number += str(random.randint(0, 9))

    while not luhn_check(card_number):
        card_number = str(bin_prefix)
        while len(card_number) < 16:
            card_number += str(random.randint(0, 9))

    return card_number

# Function to generate a random expiry date
def generate_expiry_date():
    month = random.randint(1, 12)
    year = random.randint(23, 25)  # Generate years within the next 2-3 years
    return f"{month:02d}/{year}"

# Function to generate a random CVV
def generate_cvv():
    return str(random.randint(100, 999))

# Command to ping and check network speed
@bot.message_handler(commands=['ping'])
def ping(message):
    start_time = time.time()
    response = requests.get('https://www.google.com/', timeout=5)
    end_time = time.time()
    latency = (end_time - start_time) * 1000  # Convert to milliseconds
    bot.reply_to(message, f"Ping: {latency:.2f} ms")

# Command to show user info
@bot.message_handler(commands=['info'])
def info(message):
    user_info = f"User ID: {message.from_user.id}\nUsername: @{message.from_user.username}\nFirst Name: {message.from_user.first_name}\nLast Name: {message.from_user.last_name}"
    bot.reply_to(message, user_info)

# Command to register user and send details to owner
@bot.message_handler(commands=['register'])
def register(message):
    owner_chat_id = '-1002169397567'  # Replace with your owner's chat ID
    user_info = f"User ID: {message.from_user.id}\nUsername: @{message.from_user.username}\nFirst Name: {message.from_user.first_name}\nLast Name: {message.from_user.last_name}"
    bot.send_message(owner_chat_id, f"New Registration:\n{user_info}")
    bot.reply_to(message, "Registration successful!")

# Command to generate a random IP address
@bot.message_handler(commands=['ip'])
def generate_ip(message):
    ip = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
    bot.reply_to(message, f"Generated IP: {ip}")

# Command to check if an IP address is live
@bot.message_handler(commands=['ip_check'])
def check_ip(message):
    ip = message.text.split()[1] if len(message.text.split()) > 1 else None
    if not ip:
        bot.reply_to(message, "Please provide an IP address to check. Usage: /ip_check <IP_ADDRESS>")
        return
    try:
        response = os.system(f"ping -c 1 {ip}")  # For Linux
        # response = os.system(f"ping -n 1 {ip}")  # For Windows
        if response == 0:
            bot.reply_to(message, f"{ip} is reachable.")
        else:
            bot.reply_to(message, f"{ip} is not reachable.")
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

# Command to generate a fake user
@bot.message_handler(commands=['fake'])
def fake_user(message):
    nat = message.text.split()[1] if len(message.text.split()) > 1 else None
    if not nat:
        bot.reply_to(message, "Please provide a nationality code. Usage: /fake <country_code>")
        return
    fake_api = requests.get(f"https://randomuser.me/api/?nat={nat}")
    if not fake_api.ok:
        bot.reply_to(message, "Error: Country wasn't found!")
        return
    fake = fake_api.json()['results'][0]
    name = fake['name']
    loc = fake['location']
    country = loc['country']
    
    msg = f"Name: {name['title']} {name['first']} {name['last']}\nEmail: {fake['email']}\nPhone: {fake['phone']}\nStreet: {loc['street']['number']} {loc['street']['name']}\nCity: {loc['city']}\nState: {loc['state']}\nPostal Code: {loc['postcode']}\nCountry: {country}"
    bot.reply_to(message, msg)

# Command to scrape credit cards
@bot.message_handler(commands=['scrape'])
def scrape_ccs(message):
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "Please provide both username and limit. Usage: /scrape username limit")
        return
    username = args[1]
    limit = args[2]
    start_time = time.time()
    msg = bot.send_message(message.chat.id, 'Scraping...')
    try:
        response = requests.get(f'https://scrd-3c14ab273e76.herokuapp.com/scr', params={'username': username, 'limit': limit}, timeout=120)
        raw = response.json()
        if 'error' in raw:
            bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"Error: {raw['error']}")
        else:
            cards = raw['cards']
            found = str(raw['found'])
            file = f'x{found}_Scrapped_by_@{message.from_user.username}.txt'
            
            if cards:
                with open(file, "w") as f:
                    f.write(cards)
                with open(file, "rb") as f:
                    bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
                    end_time = time.time()
                    time_taken = end_time - start_time
                    cap = f'<b>Scrapped Successfully ✅\nTarget -» <code>{username}</code>\nFound -» <code>{found}</code>\nTime Taken -» <code>{time_taken:.2f} seconds</code>\nREQ BY -» <code>{message.from_user.first_name}</code></b>'
                    bot.send_document(chat_id=message.chat.id, document=f, caption=cap, parse_mode='HTML')
                try:
                    os.remove(file)
                except PermissionError as e:
                    bot.send_message(message.chat.id, f"Error deleting file: {e}")
            else:
                bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="No cards found.")
    except requests.exceptions.RequestException as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"Request error: {e}")
    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"An error occurred: {e}")

# Command to look up BIN information using binlist.net
@bot.message_handler(commands=['bin'])
def bin_lookup(message):
    data = message.text.split()[1] if len(message.text.split()) > 1 else None
    if not data or len(data) < 6:
        bot.reply_to(message, "Please provide a valid BIN number (at least 6 digits). Usage: /bin <BIN>")
        return

    bin_info = requests.get(f"https://lookup.binlist.net/{data}").json()
    
    if 'error' in bin_info:
        bot.reply_to(message, "Error: BIN wasn't found!")
        return

    msg = f"[📟] <b>Bin</b> ↯ (<code>{data}</code>) <code>{bin_info['scheme']}</code> - <code>{bin_info['type']}</code> - <code>{bin_info['brand']}</code>\n" \
          f"[🏦] <b>Bank</b> ↯ <i>{bin_info['bank']['name']}</i>\n" \
          f"[🗺] <b>Country</b> ↯ <i>{bin_info['country']['name']}</i> [<code>{bin_info['country']['emoji']}</code>]\n" \
          f"[⛔] <b>Banned</b> ↯ <i>{bin_info.get('banned', 'False ✅')}</i>"
    
    bot.reply_to(message, msg, parse_mode='HTML')

# Command to generate random credit cards
@bot.message_handler(commands=['gen'])
def generate_cards(message):
    args = message.text.split()
    
    if len(args) < 2:
        bot.reply_to(message, "Please provide a BIN prefix (6 digits). Usage: /gen <BIN>")
        return

    bin_prefix = args[1]

    if not bin_prefix.isdigit() or len(bin_prefix) < 6:
        bot.reply_to(message, "Invalid BIN prefix! Please provide at least 6 digits.")
        return

    card_number = generate_card_number(bin_prefix)
    expiry_date = generate_expiry_date()
    cvv = generate_cvv()

    msg = f"Generated Card Details:\n" \
          f"Card Number: {card_number}\n" \
          f"Expiry Date: {expiry_date}\n" \
          f"CVV: {cvv}"

    bot.reply_to(message, msg)
