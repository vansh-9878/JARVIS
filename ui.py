import tkinter as tk
from tkinter import font as tkfont
import threading
import time
import queue
import os
import speech_recognition as sr
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
from agent import getAgent
from voice import speak

load_dotenv()

WAKE_WORDS = ["hey assistant", "ok siri", "hi jarvis", "lucy"]


BG_DARK    = "#0d0f14"
BG_PANEL   = "#13161d"
BG_CARD    = "#1a1e27"
BG_INPUT   = "#1f2433"
ACCENT     = "#5e81f4"
ACCENT2    = "#8b5cf6"
GLOW       = "#5e81f420"
TEXT_PRI   = "#e8eaf0"
TEXT_SEC   = "#8b92a8"
TEXT_MUT   = "#4a5068"
USER_BUBBLE = "#2a3355"
AI_BUBBLE   = "#1e2535"
SUCCESS    = "#22d3a0"
DANGER     = "#f43f5e"
WARN       = "#f59e0b"

class AssistantApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Assistant")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("780x900")
        self.root.minsize(600, 700)

        self.is_listening    = False
        self.wake_listening  = True
        self.is_processing   = False
        self.msg_queue       = queue.Queue()
        self.wake_thread     = None
        self.dot_count       = 0
        self.dot_timer       = None

        self._load_fonts()
        self._build_ui()
        self._start_wake_listener()
        self._poll_queue()
        self._animate_status()

    def _load_fonts(self):
        self.font_title   = tkfont.Font(family="SF Pro Display", size=15, weight="bold")
        self.font_msg     = tkfont.Font(family="SF Pro Text",    size=13)
        self.font_sender  = tkfont.Font(family="SF Pro Text",    size=10, weight="bold")
        self.font_time    = tkfont.Font(family="SF Pro Text",    size=9)
        self.font_input   = tkfont.Font(family="SF Pro Text",    size=13)
        self.font_btn     = tkfont.Font(family="SF Pro Text",    size=12, weight="bold")
        self.font_status  = tkfont.Font(family="SF Pro Text",    size=11)
        self.font_wake    = tkfont.Font(family="SF Pro Text",    size=10)

    def _build_ui(self):
        topbar = tk.Frame(self.root, bg=BG_PANEL, height=64)
        topbar.pack(fill=tk.X, side=tk.TOP)
        topbar.pack_propagate(False)

        av_canvas = tk.Canvas(topbar, width=40, height=40, bg=BG_PANEL,
                              highlightthickness=0)
        av_canvas.place(x=18, y=12)
        av_canvas.create_oval(2, 2, 38, 38, fill=ACCENT, outline="")
        av_canvas.create_text(20, 20, text="A", fill="white",
                              font=tkfont.Font(family="SF Pro Display", size=16, weight="bold"))

        tk.Label(topbar, text="Assistant", bg=BG_PANEL, fg=TEXT_PRI,
                 font=self.font_title).place(x=68, y=12)

        self.status_dot = tk.Canvas(topbar, width=10, height=10, bg=BG_PANEL,
                                    highlightthickness=0)
        self.status_dot.place(x=68, y=48)
        self._dot_oval = self.status_dot.create_oval(1, 1, 9, 9,
                                                     fill=SUCCESS, outline="")

        self.status_label = tk.Label(topbar, text="Idle  •  Say a wake word to begin",
                                     bg=BG_PANEL, fg=TEXT_SEC,
                                     font=self.font_wake)
        self.status_label.place(x=82, y=40)

        wake_frame = tk.Frame(topbar, bg=BG_CARD, padx=8, pady=3)
        wake_frame.place(relx=1.0, x=-18, y=18, anchor="ne")
        tk.Label(wake_frame, text='🔊 Wake: "ok assistant"',
                 bg=BG_CARD, fg=TEXT_MUT,
                 font=tkfont.Font(family="SF Pro Text", size=9)).pack()

        tk.Frame(self.root, bg=BG_CARD, height=1).pack(fill=tk.X)

        chat_outer = tk.Frame(self.root, bg=BG_DARK)
        chat_outer.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self.chat_canvas = tk.Canvas(chat_outer, bg=BG_DARK,
                                     highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(chat_outer, orient=tk.VERTICAL,
                                 command=self.chat_canvas.yview)
        self.chat_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.chat_frame = tk.Frame(self.chat_canvas, bg=BG_DARK)
        self.chat_frame_id = self.chat_canvas.create_window(
            (0, 0), window=self.chat_frame, anchor="nw")

        self.chat_frame.bind("<Configure>", self._on_frame_configure)
        self.chat_canvas.bind("<Configure>", self._on_canvas_configure)
        self.chat_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self._add_system_message(
            '👋  Hello! I\'m ready to help.\n'
            'Type a message below, press 🎤 to speak, or say "ok assistant" anytime.'
        )

        bottom = tk.Frame(self.root, bg=BG_PANEL, pady=14)
        bottom.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Frame(self.root, bg=BG_CARD, height=1).pack(fill=tk.X, side=tk.BOTTOM)

        input_row = tk.Frame(bottom, bg=BG_PANEL)
        input_row.pack(fill=tk.X, padx=16)

        input_bg = tk.Frame(input_row, bg=BG_INPUT, padx=12, pady=10)
        input_bg.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.input_var = tk.StringVar()
        self.entry = tk.Entry(input_bg, textvariable=self.input_var,
                              font=self.font_input, bg=BG_INPUT,
                              fg=TEXT_PRI, insertbackground=ACCENT,
                              relief=tk.FLAT, bd=0,
                              highlightthickness=0)
        self.entry.pack(fill=tk.X)
        self.entry.bind("<Return>", lambda e: self._handle_text_send())
        self.entry.bind("<FocusIn>",  lambda e: input_bg.configure(bg="#252b3b"))
        self.entry.bind("<FocusOut>", lambda e: input_bg.configure(bg=BG_INPUT))

        self._placeholder = "Type a message…"
        self.entry.insert(0, self._placeholder)
        self.entry.config(fg=TEXT_MUT)
        self.entry.bind("<FocusIn>",  self._clear_placeholder)
        self.entry.bind("<FocusOut>", self._set_placeholder)

        btn_row = tk.Frame(bottom, bg=BG_PANEL)
        btn_row.pack(fill=tk.X, padx=16, pady=(10, 0))

        self.send_btn = self._make_button(
            btn_row, "Send ↵", ACCENT, self._handle_text_send, side=tk.LEFT)
        self.voice_btn = self._make_button(
            btn_row, "🎤  Speak", BG_CARD, self._handle_voice_click,
            side=tk.LEFT, padleft=10, fg=TEXT_PRI)
        self._make_button(btn_row, "✕  Clear", BG_CARD,
                          self._clear_chat, side=tk.RIGHT, fg=TEXT_SEC)

        self.proc_frame = tk.Frame(bottom, bg=BG_PANEL)
        self.proc_label = tk.Label(self.proc_frame,
                                   text="● ● ●  Thinking…",
                                   bg=BG_PANEL, fg=ACCENT,
                                   font=self.font_status)
        self.proc_label.pack()

    def _make_button(self, parent, text, bg, cmd,
                     side=tk.LEFT, padleft=0, fg="white"):
        btn = tk.Button(parent, text=text, bg=bg, fg=fg,
                        font=self.font_btn, relief=tk.FLAT,
                        padx=18, pady=8, cursor="hand2",
                        activebackground=ACCENT, activeforeground="white",
                        command=cmd, bd=0)
        btn.pack(side=side, padx=(padleft, 0))

        def on_enter(e):
            btn.configure(bg=ACCENT if bg == ACCENT else "#252b3b")
        def on_leave(e):
            btn.configure(bg=bg)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def _clear_placeholder(self, e):
        if self.entry.get() == self._placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=TEXT_PRI)

    def _set_placeholder(self, e):
        if not self.entry.get():
            self.entry.insert(0, self._placeholder)
            self.entry.config(fg=TEXT_MUT)

    def _on_frame_configure(self, e):
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))

    def _on_canvas_configure(self, e):
        self.chat_canvas.itemconfig(self.chat_frame_id, width=e.width)

    def _on_mousewheel(self, e):
        self.chat_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    def _scroll_bottom(self):
        self.root.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def _add_system_message(self, text):
        wrapper = tk.Frame(self.chat_frame, bg=BG_DARK)
        wrapper.pack(fill=tk.X, padx=24, pady=(16, 4))
        tk.Label(wrapper, text=text, bg=BG_CARD, fg=TEXT_SEC,
                 font=tkfont.Font(family="SF Pro Text", size=11, slant="italic"),
                 padx=14, pady=10, justify=tk.LEFT,
                 wraplength=600).pack(fill=tk.X)
        self._scroll_bottom()

    def _add_message(self, text, sender="User"):
        is_user = sender == "User"
        wrapper = tk.Frame(self.chat_frame, bg=BG_DARK)
        wrapper.pack(fill=tk.X, padx=20,
                     pady=(10, 2) if is_user else (2, 10))

        bubble_bg  = USER_BUBBLE if is_user else AI_BUBBLE
        align      = tk.E if is_user else tk.W
        anchor_dir = "e" if is_user else "w"

        meta_row = tk.Frame(wrapper, bg=BG_DARK)
        meta_row.pack(fill=tk.X)

        sender_color = ACCENT if is_user else ACCENT2
        sender_text  = "You" if is_user else "Assistant"
        ts = time.strftime("%H:%M")

        if is_user:
            tk.Label(meta_row, text=ts, bg=BG_DARK, fg=TEXT_MUT,
                     font=self.font_time).pack(side=tk.RIGHT, padx=(0, 4))
            tk.Label(meta_row, text=sender_text, bg=BG_DARK,
                     fg=sender_color, font=self.font_sender).pack(side=tk.RIGHT)
        else:
            tk.Label(meta_row, text=sender_text, bg=BG_DARK,
                     fg=sender_color, font=self.font_sender).pack(side=tk.LEFT)
            tk.Label(meta_row, text=ts, bg=BG_DARK, fg=TEXT_MUT,
                     font=self.font_time).pack(side=tk.LEFT, padx=(4, 0))

        bubble_wrap = tk.Frame(wrapper, bg=BG_DARK)
        bubble_wrap.pack(fill=tk.X)

        max_w = int(self.root.winfo_width() * 0.65) or 480
        bubble = tk.Label(bubble_wrap, text=text, bg=bubble_bg,
                          fg=TEXT_PRI, font=self.font_msg,
                          padx=14, pady=10, justify=tk.LEFT,
                          wraplength=max_w, anchor="w")
        bubble.pack(side=tk.RIGHT if is_user else tk.LEFT)
        self._scroll_bottom()

    def _show_typing(self):
        self.typing_frame = tk.Frame(self.chat_frame, bg=BG_DARK)
        self.typing_frame.pack(fill=tk.X, padx=20, pady=(2, 10), anchor="w")
        self.typing_label = tk.Label(self.typing_frame,
                                     text="Assistant  ●●●",
                                     bg=AI_BUBBLE, fg=TEXT_SEC,
                                     font=self.font_msg, padx=14, pady=10)
        self.typing_label.pack(side=tk.LEFT)
        self._animate_typing()
        self._scroll_bottom()

    def _animate_typing(self):
        dots = ["●○○", "●●○", "●●●", "○●●", "○○●"]
        self.dot_count = (self.dot_count + 1) % len(dots)
        try:
            self.typing_label.configure(
                text=f"Assistant  {dots[self.dot_count]}")
        except tk.TclError:
            return
        self.dot_timer = self.root.after(300, self._animate_typing)

    def _hide_typing(self):
        if self.dot_timer:
            self.root.after_cancel(self.dot_timer)
            self.dot_timer = None
        try:
            self.typing_frame.destroy()
        except Exception:
            pass

    def _clear_chat(self):
        for w in self.chat_frame.winfo_children():
            w.destroy()
        self._add_system_message("Chat cleared. Ready for a new conversation!")

    def _set_status(self, text, color=TEXT_SEC, dot=SUCCESS):
        self.status_label.configure(text=text, fg=color)
        self.status_dot.itemconfig(self._dot_oval, fill=dot)

    def _animate_status(self):
        """Pulse the dot when listening."""
        if self.is_listening:
            cur = self.status_dot.itemcget(self._dot_oval, "fill")
            nxt = DANGER if cur != DANGER else "#ff8099"
            self.status_dot.itemconfig(self._dot_oval, fill=nxt)
        self.root.after(500, self._animate_status)

    def _handle_text_send(self):
        text = self.input_var.get().strip()
        if text == self._placeholder or not text:
            return
        self.input_var.set("")
        self.entry.config(fg=TEXT_PRI)
        threading.Thread(target=self._run_agent, args=(text,),
                         daemon=True).start()

    def _handle_voice_click(self):
        if self.is_listening:
            return
        self.voice_btn.configure(bg=DANGER, text="⏹  Stop")
        threading.Thread(target=self._do_voice_query, daemon=True).start()

    def _do_voice_query(self, auto_send=True):
        self.is_listening = True
        self.msg_queue.put(("status", ("🎙  Listening…", DANGER, DANGER)))
        query = self._record_voice()
        self.is_listening = False
        self.root.after(0, lambda: self.voice_btn.configure(
            bg=BG_CARD, text="🎤  Speak"))
        if query:
            if auto_send:
                self._run_agent(query)
        else:
            self.msg_queue.put(("status", ("Idle  •  Ready", TEXT_SEC, SUCCESS)))

    def _record_voice(self) -> str:
        rec = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                rec.adjust_for_ambient_noise(source, duration=0.5)
                audio = rec.listen(source, timeout=8, phrase_time_limit=15)
            return rec.recognize_google(audio)
        except sr.WaitTimeoutError:
            self.msg_queue.put(("sys_msg", "⏱  No speech detected."))
            return ""
        except sr.UnknownValueError:
            self.msg_queue.put(("sys_msg", "🤷  Didn't catch that. Try again."))
            return ""
        except Exception as e:
            self.msg_queue.put(("sys_msg", f"Mic error: {e}"))
            return ""

    def _run_agent(self, query: str):
        self.is_processing = True
        self.msg_queue.put(("user_msg",  query))
        self.msg_queue.put(("show_typing", None))
        self.msg_queue.put(("status",   ("⚙  Thinking…", ACCENT, ACCENT)))

        try:
            messages = getAgent(query)
            reply = messages["messages"][-1].content
        except Exception as e:
            reply = f"Sorry, something went wrong: {e}"

        self.msg_queue.put(("hide_typing", None))
        self.msg_queue.put(("ai_msg",   reply))
        self.msg_queue.put(("status",   ("Idle  •  Ready", TEXT_SEC, SUCCESS)))
        self.is_processing = False

        threading.Thread(target=speak, args=(reply,), daemon=True).start()

    def _start_wake_listener(self):
        self.wake_thread = threading.Thread(
            target=self._wake_loop, daemon=True)
        self.wake_thread.start()

    def _wake_loop(self):
        rec = sr.Recognizer()
        rec.energy_threshold = 300
        rec.dynamic_energy_threshold = True
        while self.wake_listening:
            try:
                with sr.Microphone() as source:
                    audio = rec.listen(source, timeout=3, phrase_time_limit=4)
                try:
                    heard = rec.recognize_google(audio).lower()
                    if any(w in heard for w in WAKE_WORDS):
                        self.msg_queue.put(("wake_triggered", heard))
                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    time.sleep(2)
            except Exception:
                time.sleep(1)

    def _poll_queue(self):
        try:
            while True:
                kind, payload = self.msg_queue.get_nowait()
                if kind == "user_msg":
                    self._add_message(payload, "User")
                elif kind == "ai_msg":
                    self._add_message(payload, "AI")
                elif kind == "sys_msg":
                    self._add_system_message(payload)
                elif kind == "show_typing":
                    self._show_typing()
                elif kind == "hide_typing":
                    self._hide_typing()
                elif kind == "status":
                    self._set_status(*payload)
                elif kind == "wake_triggered":
                    self._on_wake(payload)
        except queue.Empty:
            pass
        self.root.after(80, self._poll_queue)

    def _on_wake(self, heard: str):
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(300, lambda: self.root.attributes("-topmost", False))
        self._add_system_message(f'🔔  Wake word detected: "{heard}"')
        self._set_status("🎙  Wake word heard — recording…", WARN, WARN)
        if not self.is_listening and not self.is_processing:
            self.voice_btn.configure(bg=DANGER, text="⏹  Recording")
            threading.Thread(target=self._do_voice_query,
                             daemon=True).start()

    def run(self):
        self.root.mainloop()
        self.wake_listening = False


if __name__ == "__main__":
    app = AssistantApp()
    app.run()