from keep_alive import run
import http.client
import json
import random
import sys
from time import sleep
from http.client import HTTPSConnection
from threading import Thread
import certifi
import ssl

# Open file containing user information
with open("info.txt", "r") as file:
    text = file.read().splitlines()


def configure_info():
    try:
        user_id = input("User-ID: ")
        token = input("Discord token: ")
        channel_url = input("Discord channel URL: ")
        channel_cn_id = input("Discord channel CN ID: ")
        channel_jp_id = input("Discord channel JP ID: ")
        channel_vn_id = input("Discord channel VN ID: ")
        with open("info.txt", "w") as file:
            file.write(
                f"{user_id}\n{token}\n{channel_url}\n{channel_cn_id}\n{channel_jp_id}\n{channel_vn_id}"
            )
    except Exception as e:
        print(f"Error configuring user information: {e}")
        exit()


def set_channel():
    user_id = text[0]
    token = text[1]
    channel_url = input("Discord channel URL: ")
    channel_cn_id = input("Discord channel ID: ")
    channel_jp_id = input("Discord channel ID: ")
    channel_vn_id = input("Discord channel ID: ")
    with open("info.txt", "w") as file:
        file.write(
            f"{user_id}\n{token}\n{channel_url}\n{channel_cn_id}\n{channel_jp_id}\n{channel_vn_id}"
        )


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

if len(text) != 6:
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
    return HTTPSConnection(
        "discordapp.com",
        443,
        context=ssl.create_default_context(cafile=certifi.where()),
    )


def send_message(conn, channel_id, message_data):
    try:
        conn.request(
            "POST", f"/api/v6/channels/{channel_id}/messages", message_data, header_data
        )
        resp = conn.getresponse()

        if 199 < resp.status < 300:
            print("Message sent on channel " + channel_id)
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


def send_messages_in_thread(channel_id, message_file_name):
    print(f"Reading file {message_file_name}")
    with open(message_file_name, "r", encoding="utf8") as file:
        messages = file.read().splitlines()
        # Loop through messages and send them
        for message in messages:
            random_wait_time_coefficient = random.random()
            message_data = json.dumps({"content": message})
            conn = get_connection()
            latest_id = get_latest_message(conn, channel_id)
            if latest_id != "":
                message_data = json.dumps(
                    {"content": message, "message_reference": {"message_id": latest_id}}
                )
            send_message(conn, channel_id, message_data)
            conn.close()

            print(f"Waiting {wait_time*(1+random_wait_time_coefficient)} seconds...")
            sleep(wait_time * (1 + random_wait_time_coefficient))


# Read messages from file
def keep_alive(n, file_names):
    threads = []
    for i in range(n):
        t = Thread(
            target=send_messages_in_thread,
            args=(
                text[3 + i],
                file_names[i],
            ),
        )
        threads.append(t)
        t.start()
        sleep(wait_time)

    for t in threads:
        t.join()


# Read wait times from user
wait_time = int(input("Seconds between messages: "))
keep_alive(3, ["messages_cn.txt", "messages_jp.txt", "messages_vn.txt"])
# keep_alive(2, ["messages_jp.txt","messages_vn.txt"])
