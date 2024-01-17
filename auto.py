from keep_alive import keep_alive
import http.client
import json
import random
import sys
from time import sleep
from http.client import HTTPSConnection

# Open file containing user information
with open("info.txt", "r") as file:
    text = file.read().splitlines()


def configure_info():
    try:
        user_id = input("User-ID: ")
        token = input("Discord token: ")
        channel_url = input("Discord channel URL: ")
        channel_id = input("Discord channel ID: ")
        with open("info.txt", "w") as file:
            file.write(f"{user_id}\n{token}\n{channel_url}\n{channel_id}")
    except Exception as e:
        print(f"Error configuring user information: {e}")
        exit()


def set_channel():
    user_id = text[0]
    token = text[1]
    channel_url = input("Discord channel URL: ")
    channel_id = input("Discord channel ID: ")
    with open("info.txt", "w") as file:
        file.write(f"{user_id}\n{token}\n{channel_url}\n{channel_id}")


def show_help():
    print("Showing help for discord-auto-messenger")
    print("Usage:")
    print(
        "  'python3 auto.py'               :  Runs the automessenger. Type in the wait time and take a back seat."
    )
    print("  'python3 auto.py --config'      :  Configure settings.")
    print(
        "  'python3 auto.py --setC'  :  Set channel to send message to. Including Channel ID and Channel URL"
    )
    print("  'python3 auto.py --help'        :  Show help")


if len(sys.argv) > 1:
    if sys.argv[1] == "--config" and input("Configure? (y/n)") == "y":
        configure_info()
        exit()
    elif sys.argv[1] == "--setC" and input("Set channel? (y/n)") == "y":
        set_channel()
        exit()
    elif sys.argv[1] == "--help":
        show_help()
        exit()

if len(text) != 4:
    print(
        "An error inside the user information file. Please ensure the file contains the following information in order: User agent, Discord token, Discord channel URL, and Discord channel ID and try again ->python3 auto.py"
    )
    configure_info()
    exit()

header_data = {
    "content-type": "application/json",
    "user-id": text[0],
    "authorization": text[1],
    "host": "discordapp.com",
    "referrer": text[2],
}

print("Messages will be sent to " + header_data["referrer"] + ".")


def get_connection():
    return HTTPSConnection("discordapp.com", 443)


def send_message(conn, channel_id, message_data):
    try:
        conn.request(
            "POST", f"/api/v6/channels/{channel_id}/messages", message_data, header_data
        )
        resp = conn.getresponse()

        if 199 < resp.status < 300:
            print("Message sent!")
    except Exception as e:
        print(f"Error sending message: {e}")


def get_latest_message(conn, channel_id):
    try:
        conn.request(
            "GET",
            f"/api/v6/channels/{channel_id}/messages?limit=1",
            headers=header_data,
        )
        resp = conn.getresponse()

        if 199 < resp.status < 300:
            data = json.loads(resp.read().decode("utf-8"))
            return data[0]["id"]
        return ""
    except Exception as e:
        print(f"Error fetching latest message: {e}")
        return ""


# Read messages from file
with open("messages.txt", "r", encoding="utf8") as file:
    messages = file.read().splitlines()

# Read wait times from user
wait_time = int(input("Seconds between messages: "))
keep_alive()
# Loop through messages and send them
for message in messages:
    message_data = json.dumps({"content": message})
    conn = get_connection()
    latest_id = get_latest_message(conn, text[3])
    if latest_id != "":
        message_data = json.dumps(
            {"content": message, "message_reference": {"message_id": latest_id}}
        )
    send_message(conn, text[3], message_data)
    conn.close()

    print(f"Waiting {wait_time} seconds...")
    sleep(wait_time)
