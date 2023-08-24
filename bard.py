import requests
from pyrogram import Client, filters
from pyrogram.types import Message

BASE_URL = 'https://api.safone.me'

app = Client("my_bot", api_id=YOUR_API_ID, api_hash="YOUR_API_HASH", bot_token="YOUR_BOT_TOKEN")

def ask_bard(question, image=None):
    endpoint = f"{BASE_URL}/bard"
    headers = {'Content-Type': 'application/json'}
    body = {'message': question}

    files = None
    if image:
        files = {'image': open(image, 'rb')}

    try:
        response = requests.post(endpoint, json=body, headers=headers, files=files)
        response_data = response.json()

        if response.ok:
            choices = response_data.get('choices', [])
            image_url = response_data.get('image_url')
            if choices:
                content = choices[0]['content'][0]
            else:
                content = "Error: No response content found."

            return content, image_url
        else:
            error_message = f"Error: {response.status_code}, {response_data}"
            print(error_message)
            return error_message, None
    except requests.RequestException as e:
        return f"Error occurred: {e}", None

@app.on_message(filters.command("bard", prefixes="/"))
async def ask_command_handler(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply("Please reply to a message with an image or provide a question after the /bard command.")
        return

    question = " ".join(message.command[1:])
    image = message.reply_to_message.photo.file_id if message.reply_to_message else None

    if question or image:
        response_content, image_url = ask_bard(question, image)

        if image_url:
            await client.send_photo(message.chat.id, image_url, caption=response_content)
        else:
            await message.reply(response_content)
    else:
        await message.reply("Please provide a question after the /bard command.")

if __name__ == "__main__":
    app.run()
