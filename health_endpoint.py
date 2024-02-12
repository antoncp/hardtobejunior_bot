from threading import Event, Thread

from flask import Flask

from utilities import get_time

# Flask health check endpoint
app = Flask(__name__)
shutdown_event = Event()


@app.route("/", methods=["GET"])
def webhook():
    if not shutdown_event.is_set():
        now = get_time(1)
        intro = "The server time now is:"
        time = now.strftime("%m/%d/%Y, %H:%M:%S")
        message = [intro, time]
        return "<br><br>".join(message)


def run_flask_app():
    app.run(host="0.0.0.0", port=1400)


flask_thread = Thread(target=run_flask_app)
