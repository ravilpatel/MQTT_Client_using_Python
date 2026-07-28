import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import paho.mqtt.client as mqtt
from datetime import datetime
import uuid
import queue


class MQTTGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MQTT Client")
        self.root.geometry("950x750")

        self.client = None
        self.connected = False
        self.message_queue = queue.Queue()
        self.subscribed_topics = set()

        self.create_widgets()
        self.poll_queue()  # start polling thread-safe queue

    # --------------------------- GUI BUILD --------------------------- #
    def create_widgets(self):
        # ---------- Connection Frame ----------
        conn_frame = ttk.LabelFrame(self.root, text="Broker Connection (unencrypted)", padding=10)
        conn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(conn_frame, text="Broker:").grid(row=0, column=0, sticky="w")
        self.broker_entry = ttk.Entry(conn_frame, width=25)
        self.broker_entry.insert(0, "test.mosquitto.org")
        self.broker_entry.grid(row=0, column=1, padx=5)

        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, sticky="w")
        self.port_entry = ttk.Entry(conn_frame, width=8)
        self.port_entry.insert(0, "1883")
        self.port_entry.grid(row=0, column=3, padx=5)

        ttk.Label(conn_frame, text="KeepAlive (s):").grid(row=0, column=4, sticky="w")
        self.keepalive_entry = ttk.Entry(conn_frame, width=5)
        self.keepalive_entry.insert(0, "60")
        self.keepalive_entry.grid(row=0, column=5, padx=5)

        ttk.Label(conn_frame, text="Client ID:").grid(row=1, column=0, sticky="w")
        self.clientid_entry = ttk.Entry(conn_frame, width=25)
        self.clientid_entry.insert(0, f"client_{uuid.uuid4().hex[:8]}")
        self.clientid_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(conn_frame, text="Username:").grid(row=1, column=2, sticky="w")
        self.username_entry = ttk.Entry(conn_frame, width=15)
        self.username_entry.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(conn_frame, text="Password:").grid(row=1, column=4, sticky="w")
        self.password_entry = ttk.Entry(conn_frame, width=15, show="*")
        self.password_entry.grid(row=1, column=5, padx=5, pady=5)

        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")

        self.status_label = ttk.Label(conn_frame, text="● Disconnected", foreground="red", font=("Segoe UI", 10, "bold"))
        self.status_label.grid(row=2, column=3, columnspan=3, padx=10)

        # ---------- Subscribe Frame ----------
        sub_frame = ttk.LabelFrame(self.root, text="Subscribe", padding=10)
        sub_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(sub_frame, text="Topic:").grid(row=0, column=0, sticky="w")
        self.topic_entry = ttk.Entry(sub_frame, width=40)
        self.topic_entry.insert(0, "test/topic")
        self.topic_entry.grid(row=0, column=1, padx=5)

        ttk.Label(sub_frame, text="QoS:").grid(row=0, column=2, sticky="w")
        self.qos_var = tk.IntVar(value=0)
        ttk.Combobox(sub_frame, textvariable=self.qos_var, values=[0, 1, 2],
                     width=5, state="readonly").grid(row=0, column=3, padx=5)

        self.subscribe_btn = ttk.Button(sub_frame, text="Subscribe", command=self.subscribe_topic, state="disabled")
        self.subscribe_btn.grid(row=0, column=4, padx=5)

        self.unsubscribe_btn = ttk.Button(sub_frame, text="Unsubscribe", command=self.unsubscribe_topic, state="disabled")
        self.unsubscribe_btn.grid(row=0, column=5, padx=5)

        ttk.Button(sub_frame, text="Unsubscribe All", command=self.unsubscribe_all, state="disabled").grid(row=0, column=6, padx=5)

        ttk.Label(sub_frame, text="Subscribed:").grid(row=1, column=0, sticky="w")
        self.subscribed_label = ttk.Label(sub_frame, text="None", foreground="blue", wraplength=700, justify="left")
        self.subscribed_label.grid(row=1, column=1, columnspan=6, sticky="w", pady=5)

        # ---------- Publish Frame ----------
        pub_frame = ttk.LabelFrame(self.root, text="Publish", padding=10)
        pub_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(pub_frame, text="Topic:").grid(row=0, column=0, sticky="w")
        self.pub_topic_entry = ttk.Entry(pub_frame, width=30)
        self.pub_topic_entry.grid(row=0, column=1, padx=5)

        ttk.Label(pub_frame, text="Message:").grid(row=0, column=2, sticky="w")
        self.pub_msg_entry = ttk.Entry(pub_frame, width=40)
        self.pub_msg_entry.grid(row=0, column=3, padx=5)

        ttk.Label(pub_frame, text="QoS:").grid(row=0, column=4, sticky="w")
        self.pub_qos_var = tk.IntVar(value=0)
        ttk.Combobox(pub_frame, textvariable=self.pub_qos_var, values=[0, 1, 2],
                     width=5, state="readonly").grid(row=0, column=5, padx=5)

        self.publish_btn = ttk.Button(pub_frame, text="Publish", command=self.publish_message, state="disabled")
        self.publish_btn.grid(row=0, column=6, padx=5)

        # ---------- Messages Frame ----------
        msg_frame = ttk.LabelFrame(self.root, text="Received Messages", padding=10)
        msg_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.message_text = scrolledtext.ScrolledText(msg_frame, wrap="word", height=15)
        self.message_text.pack(fill="both", expand=True)
        self.message_text.config(state="disabled")
        self.message_text.tag_config("timestamp", foreground="gray")
        self.message_text.tag_config("topic", foreground="blue", font=("Consolas", 10, "bold"))
        self.message_text.tag_config("payload", foreground="black", font=("Consolas", 10))

        ttk.Button(msg_frame, text="Clear Messages", command=self.clear_messages).pack(side="right", pady=5)

        # ---------- Log Frame ----------
        log_frame = ttk.LabelFrame(self.root, text="Log", padding=10)
        log_frame.pack(fill="x", padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap="word", height=5)
        self.log_text.pack(fill="both", expand=True)
        self.log_text.config(state="disabled")
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("info", foreground="darkgreen")

        ttk.Button(log_frame, text="Clear Log", command=self.clear_log).pack(side="right", pady=5)

    # --------------------------- HELPERS --------------------------- #
    def log(self, message, level="info"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"[{timestamp}] {message}\n", level)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    def clear_messages(self):
        self.message_text.config(state="normal")
        self.message_text.delete("1.0", "end")
        self.message_text.config(state="disabled")

    def update_subscribed_label(self):
        self.subscribed_label.config(text=", ".join(self.subscribed_topics) if self.subscribed_topics else "None")

    # --------------------------- CONNECTION --------------------------- #
    def toggle_connection(self):
        if self.connected:
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        broker = self.broker_entry.get().strip()
        if not broker:
            messagebox.showerror("Error", "Please enter broker address")
            return

        try:
            port = int(self.port_entry.get().strip())
            keepalive = int(self.keepalive_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Invalid port or keepalive value")
            return

        client_id = self.clientid_entry.get().strip() or f"client_{uuid.uuid4().hex[:8]}"
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        # Paho MQTT v2 API
        self.client = mqtt.Client(
            client_id=client_id,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )

        if username:
            self.client.username_pw_set(username, password)

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_subscribe = self._on_subscribe
        self.client.on_unsubscribe = self._on_unsubscribe
        self.client.on_publish = self._on_publish

        self.log(f"Connecting to {broker}:{port} ...")
        try:
            self.client.connect(broker, port, keepalive)
            self.client.loop_start()  # background network thread
        except Exception as e:
            self.log(f"Connection failed: {e}", "error")
            messagebox.showerror("Connection Error", str(e))
            self.client = None

    def disconnect(self):
        if self.client:
            self.subscribed_topics.clear()
            self.update_subscribed_label()
            self.client.loop_stop()
            self.client.disconnect()
            self.client = None
        self.connected = False
        self._set_ui_connected(False)
        self.log("Disconnected")

    # --------------------------- MQTT CALLBACKS (run in paho thread) --------------------------- #
    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        self.message_queue.put(("connect", reason_code))

    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties=None):
        self.message_queue.put(("disconnect", reason_code))

    def _on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode("utf-8", errors="replace")
        except Exception:
            payload = str(msg.payload)
        self.message_queue.put(("message", msg.topic, payload, msg.qos))

    def _on_subscribe(self, client, userdata, mid, reason_codes, properties=None):
        self.message_queue.put(("subscribe", mid))

    def _on_unsubscribe(self, client, userdata, mid, reason_codes, properties=None):
        self.message_queue.put(("unsubscribe", mid))

    def _on_publish(self, client, userdata, mid, reason_code, properties=None):
        self.message_queue.put(("publish", mid))

    # --------------------------- GUI QUEUE POLLING --------------------------- #
    def poll_queue(self):
        try:
            while True:
                self._handle_queue_item(self.message_queue.get_nowait())
        except queue.Empty:
            pass
        self.root.after(100, self.poll_queue)

    def _handle_queue_item(self, item):
        event = item[0]

        if event == "connect":
            rc = item[1]
            # Paho v2 uses ReasonCode objects. We check is_failure property.
            if not rc.is_failure:
                self.connected = True
                self._set_ui_connected(True)
                self.log("Connected to broker", "info")
            else:
                self.log(f"Connection failed (code: {rc})", "error")
                messagebox.showerror("Connection Failed", f"Reason code: {rc}")
                self.connected = False
                self._set_ui_connected(False)

        elif event == "disconnect":
            self.connected = False
            self._set_ui_connected(False)
            self.subscribed_topics.clear()
            self.update_subscribed_label()
            self.log("Disconnected from broker", "error")

        elif event == "message":
            topic, payload, qos = item[1], item[2], item[3]
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            self.message_text.config(state="normal")
            self.message_text.insert("end", f"[{timestamp}] ", "timestamp")
            self.message_text.insert("end", f"Topic: {topic}  (QoS:{qos})\n", "topic")
            self.message_text.insert("end", f"   {payload}\n\n", "payload")
            self.message_text.see("end")
            self.message_text.config(state="disabled")

        elif event == "subscribe":
            topic = self.topic_entry.get().strip()
            self.subscribed_topics.add(topic)
            self.update_subscribed_label()
            self.unsubscribe_btn.config(state="normal")
            self.log(f"Subscribed to: {topic}", "info")

        elif event == "unsubscribe":
            topic = self.topic_entry.get().strip()
            self.subscribed_topics.discard(topic)
            self.update_subscribed_label()
            if not self.subscribed_topics:
                self.unsubscribe_btn.config(state="disabled")
            self.log(f"Unsubscribed from: {topic}", "info")

        elif event == "publish":
            self.log("Message published", "info")

    # --------------------------- UI STATE --------------------------- #
    def _set_ui_connected(self, connected: bool):
        if connected:
            self.status_label.config(text="● Connected", foreground="green")
            self.connect_btn.config(text="Disconnect")
            self.subscribe_btn.config(state="normal")
            self.publish_btn.config(state="normal")
        else:
            self.status_label.config(text="● Disconnected", foreground="red")
            self.connect_btn.config(text="Connect")
            self.subscribe_btn.config(state="disabled")
            self.unsubscribe_btn.config(state="disabled")
            self.publish_btn.config(state="disabled")

    # --------------------------- ACTIONS --------------------------- #
    def subscribe_topic(self):
        if not self.connected or not self.client:
            return
        topic = self.topic_entry.get().strip()
        if not topic:
            messagebox.showerror("Error", "Please enter a topic")
            return
        qos = self.qos_var.get()
        self.client.subscribe(topic, qos)
        self.log(f"Subscribing to '{topic}' (QoS {qos}) ...")

    def unsubscribe_topic(self):
        if not self.connected or not self.client:
            return
        topic = self.topic_entry.get().strip()
        if not topic:
            return
        self.client.unsubscribe(topic)

    def unsubscribe_all(self):
        if not self.client:
            return
        for t in list(self.subscribed_topics):
            self.client.unsubscribe(t)

    def publish_message(self):
        if not self.connected or not self.client:
            return
        topic = self.pub_topic_entry.get().strip()
        message = self.pub_msg_entry.get()
        if not topic:
            messagebox.showerror("Error", "Please enter a topic to publish")
            return
        qos = self.pub_qos_var.get()
        self.client.publish(topic, message, qos=qos)
        self.log(f"Publishing to '{topic}': {message} (QoS {qos})")


def main():
    root = tk.Tk()
    app = MQTTGUI(root)

    def on_closing():
        try:
            if app.client:
                app.client.loop_stop()
                app.client.disconnect()
        except Exception:
            pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
