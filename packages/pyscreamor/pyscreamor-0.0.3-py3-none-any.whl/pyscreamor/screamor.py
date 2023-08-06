import os
import paho.mqtt.client as mqtt
import json
import base64
import threading
import platform


players = {
    "Darwin": "afplay",
    "Linux": "mplayer"
}


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    print("Quit the server with CONTROL-C.")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("message/voice/request")


def on_message(client, userdata, msg):
    payload = json.loads(msg.payload)
    msg_id, b64_voice = payload.popitem()

    if not os.path.exists("./voice"):
        os.makedirs("voice")

    m4a = f"./voice/{msg_id}.m4a"

    with open(m4a, "wb") as f:
        f.write(base64.decodebytes(b64_voice.encode()))
        f.close()

    threading.Thread(target=lambda: os.system(f"{players.get(platform.system(), 'aplay')} {m4a}")).start()

    client.publish("message/voice/response", msg_id, 2)


if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set("ubuntu", "#czf786459117")

    client.connect("socks.devecor.cn", 1883, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()
