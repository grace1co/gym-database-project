# gym_gui.py
# ITC 341 — Gym Membership Database
# Grace Okoro & Amrita Penke

import tkinter as tk
from tkinter import ttk, messagebox
import oracledb

# ─── DATABASE CONNECTION ──────────────────────────────────────────────
DB_USER = "OKORO1GC"
DB_PASSWORD = "KqCma4fh9lBYJmbl"
DB_DSN = "cps-orcl4.se.cmich.edu/orcl4"

def get_connection():
    """Return a live Oracle connection, or None on failure."""
    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        return conn
    except oracledb.Error as e:
        messagebox.showerror("Connection Error", f"Could not connect to Oracle:\n\n{e}")
        return None

# ─── COLOURS & FONTS ──────────────────────────────────────────────────
BG = "#ffffff"
SIDEBAR = "#fafafa"
CARD = "#ffffff"
ACCENT = "#2563eb"
FG = "#111827"
FG_DIM = "#6b7280"
GREEN = "#10b981"
RED = "#ef4444"
BLUE = "#2563eb"
BTN_BG = "#2563eb"
BTN_FG = "#ffffff"

FONT_HEAD = ("Segoe UI", 18, "bold")
FONT_SUB = ("Segoe UI", 11)
FONT_LABEL = ("Segoe UI", 9)
FONT_MONO = ("Courier New", 10)
FONT_BTN = ("Segoe UI", 10, "bold")

# ─── HELPERS ──────────────────────────────────────────────────────────
def styled_label(parent, text, font=FONT_SUB, fg=FG, bg=BG, **kw):
    return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, **kw)

def styled_entry(parent, width=28):
    e = tk.Entry(
        parent,
        width=width,
        bg="#ffffff",
        fg=FG,
        insertbackground=FG,
        relief="flat",
        font=FONT_MONO,
        bd=1,
        highlightbackground="#e5e7eb",
        highlightthickness=1,
    )
    return e

def styled_button(parent, text, cmd, color=BTN_BG, fg=BTN_FG, width=20):
    return tk.Button(
        parent,
        text=text,
        command=cmd,
        bg=color,
        fg=fg,
        font=FONT_BTN,
        relief="flat",
        padx=12,
        pady=7,
        cursor="hand2",
        width=width,
        activebackground=color,
        activeforeground=fg,
        bd=0,
    )

def separator(parent, bg=ACCENT):
    return tk.Frame(parent, height=2, bg=bg)

# ─── MAIN APPLICATION ─────────────────────────────────────────────────
class GymApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gym Management System — ITC 341")
        self.geometry("1100x680")
        self.configure(bg=BG)
        self.resizable(True, True)

        self.current_view = "dashboard"

        self._build_ui()
        self.show_view("dashboard")

    def _build_ui(self):
        # ── Sidebar ──────────────────────────────────────────────────
        self.sidebar = tk.Frame(self, bg=SIDEBAR, width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="GYM SYSTEM",
            font=("Segoe UI", 13, "bold"),
            fg=FG,
            bg=SIDEBAR,
        ).pack(pady=(20, 2))

        tk.Label(
            self.sidebar,
            text="ITC 341 · Admin",
            font=FONT_LABEL,
            fg=FG_DIM,
            bg=SIDEBAR,
        ).pack(pady=(0, 18))

        separator(self.sidebar, bg="#e5e7eb").pack(fill="x", padx=16, pady=4)

        self.nav_buttons = {}
        nav_items = [
            ("Dashboard", "dashboard"),
            ("Members", "members"),
            ("Plans", "plans"),
            ("Check-ins", "checkins"),
        ]

        for label, key in nav_items:
            btn = tk.Button(
                self.sidebar,
                text=label,
                font=FONT_BTN,
                bg=SIDEBAR,
                fg=FG_DIM,
                relief="flat",
                anchor="w",
                padx=20,
                pady=10,
                bd=0,
                cursor="hand2",
                width=18,
                command=lambda k=key: self.show_view(k),
                activebackground="#f3f4f6",
                activeforeground=ACCENT,
            )
            btn.pack(fill="x")
            self.nav_buttons[key] = btn

        separator(self.sidebar, bg="#e5e7eb").pack(fill="x", padx=16, pady=12)

        tk.Label(
            self.sidebar,
            text="ACTIONS",
            font=("Segoe UI", 8, "bold"),
            fg="#6b7280",
            bg=SIDEBAR,
            anchor="w",
        ).pack(fill="x", padx=20)

        actions = [
            ("↻ Refresh", lambda: self.show_view(self.current_view)),
            ("＋ Add Member", self.open_add_member),
            ("＋ Add Check-in", self.open_add_checkin),
            ("✎ Update Status", self.open_update_status),
            ("✕ Delete Member", self.open_delete_member),
        ]

        for label, cmd in actions:
            btn = tk.Button(
                self.sidebar,
                text=label,
                font=("Segoe UI", 9, "bold"),
                bg=SIDEBAR,
                fg=FG_DIM,
                relief="flat",
                anchor="w",
                padx=20,
                pady=8,
                bd=0,
                cursor="hand2",
                width=18,
                command=cmd,
                activebackground="#f3f4f6",
                activeforeground=ACCENT,
            )
            btn.pack(fill="x")

        # ── Main content area ─────────────────────────────────────────
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="right", fill="both", expand=True)

        self.title_bar = tk.Frame(self.content, bg="#ffffff", pady=12, padx=24)
        self.title_bar.pack(fill="x")

        self.page_title = tk.Label(
            self.title_bar,
            text="",
            font=FONT_HEAD,
            fg=FG,
            bg="#ffffff",
        )
        self.page_title.pack(side="left")

        # --- GLOBAL SEARCH BAR ---
        self.search_var = tk.StringVar()
        self.search_entry = styled_entry(self.title_bar, width=35)
        self.search_entry.configure(textvariable=self.search_var)
        self.search_entry.pack(side="right", padx=(5, 0), ipady=3)
        self.search_entry.insert(0, "Search members by name or ID...")

        def on_search_click(e):
            if self.search_entry.get() == "Search members by name or ID...":
                self.search_entry.delete(0, 'end')
                
        def on_search_leave(e):
            if not self.search_entry.get():
                self.search_entry.insert(0, "Search members by name or ID...")

        self.search_entry.bind("<FocusIn>", on_search_click)
        self.search_entry.bind("<FocusOut>", on_search_leave)
        self.search_entry.bind("<Return>", self.perform_search)

        btn_search = tk.Button(
            self.title_bar, text="🔍", font=("Segoe UI", 10), bg="#ffffff", 
            fg=FG_DIM, relief="flat", command=lambda: self.perform_search(None), bd=0, cursor="hand2"
        )
        btn_search.pack(side="right")

        separator(self.content, bg="#e5e7eb").pack(fill="x")

        outer = tk.Frame(self.content, bg=BG)
        outer.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scroll_frame = tk.Frame(self.canvas, bg=BG)
        win_id = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(win_id, width=e.width),
        )

        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self.log_bar = tk.Label(
            self.content,
            text="",
            font=FONT_MONO,
            fg=GREEN,
            bg="#fafafa",
            anchor="w",
            padx=16,
            pady=6,
        )
        self.log_bar.pack(fill="x", side="bottom")
        separator(self.content, bg="#e5e7eb").pack(fill="x", side="bottom")

    def perform_search(self, event=None):
        query = self.search_var.get().strip()
        if not query or query == "Search members by name or ID...":
            return
        self.show_view("search_results")

    def set_log(self, msg, ok=True):
        self.log_bar.configure(text=msg, fg=GREEN if ok else RED)

    def show_view(self, key):
        self.current_view = key

        for k, b in self.nav_buttons.items():
            b.configure(bg=SIDEBAR, fg=FG_DIM)

        if key in self.nav_buttons:
            self.nav_buttons[key].configure(bg="#f3f4f6", fg=ACCENT)

        titles = {
            "dashboard": "Dashboard",
            "members": "Members",
            "plans": "Plans",
            "checkins": "Check-in Log",
            "search_results": "Search Results"
        }
        self.page_title.configure(text=titles.get(key, ""))

        for w in self.scroll_frame.winfo_children():
            w.destroy()

        # Fixes the "blank page" bug by scrolling back to the top of the canvas
        self.canvas.yview_moveto(0)

        dispatch = {
            "dashboard": self._view_dashboard,
            "members": self._view_members,
            "plans": self._view_plans,
            "checkins": self._view_checkins,
            "search_results": self._view_search_results,
        }

        if key in dispatch:
            dispatch[key]()

    # ── SEARCH RESULTS ───────────────────────────────────────────────
    def _view_search_results(self):
        query = self.search_var.get().strip()
        
        frame = tk.Frame(self.scroll_frame, bg=BG, padx=28, pady=24)
        frame.pack(fill="both", expand=True)

        styled_label(frame, f"Results for '{query}'", fg=FG_DIM).pack(anchor="w", pady=(0, 14))

        conn = get_connection()
        if not conn: return

        try:
            cur = conn.cursor()
            sql = """
                SELECT m.MemberID, m.Name, g.GymName, ms.Status
                FROM Member m
                LEFT JOIN GymLocation g ON m.HomeGymID = g.GymID
                LEFT JOIN Membership ms ON m.MemberID = ms.MemberID
                WHERE LOWER(m.Name) LIKE :1 OR TO_CHAR(m.MemberID) LIKE :2
                ORDER BY m.MemberID
            """
            search_term = f"%{query.lower()}%"
            # Pass the search term twice to satisfy both :1 and :2 placeholders
            cur.execute(sql, (search_term, search_term))
            rows = cur.fetchall()
            cur.close()

            desc = ["MemberID", "Name", "HomeGym", "Status"]
            styled_label(frame, f"{len(rows)} matching members found", font=("Segoe UI", 9), fg=FG_DIM).pack(anchor="w", pady=(0, 8))

            self._render_table(
                frame, desc, rows, color_col=3,
                color_map={"ACTIVE": GREEN, "EXPIRED": RED, "CANCELLED": "#f59e0b"},
            )
        except Exception as e:
            styled_label(frame, f"Error: {e}", fg=RED).pack(anchor="w")

        conn.close()

    # ── DASHBOARD ────────────────────────────────────────────────────
    def _view_dashboard(self):
        frame = tk.Frame(self.scroll_frame, bg=BG, padx=28, pady=24)
        frame.pack(fill="both", expand=True)

        styled_label(frame, "Gym Management System", font=("Segoe UI", 14, "bold"), fg=FG).pack(anchor="w")
        styled_label(frame, "ITC 341 · Oracle SQL Class Project", font=FONT_LABEL, fg=FG_DIM).pack(anchor="w", pady=(0, 18))

        conn = get_connection()
        stats = [
            ("TOTAL MEMBERS", "SELECT COUNT(*) FROM Member", FG),
            ("ACTIVE MEMBERSHIPS", "SELECT COUNT(*) FROM Membership WHERE Status='ACTIVE'", FG),
            ("EXPIRED / CANCELLED", "SELECT COUNT(*) FROM Membership WHERE Status IN ('EXPIRED','CANCELLED')", FG),
            ("TOTAL CHECK-INS", "SELECT COUNT(*) FROM CheckIn", FG),
        ]

        row = tk.Frame(frame, bg=BG)
        row.pack(fill="x", pady=(0, 20))

        for label, sql, color in stats:
            val = "—"
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute(sql)
                    val = str(cur.fetchone()[0])
                    cur.close()
                except Exception: pass

            card = tk.Frame(row, bg=CARD, padx=22, pady=16, relief="flat", highlightbackground="#e5e7eb", highlightthickness=1)
            card.pack(side="left", padx=8, expand=True, fill="x")

            tk.Label(card, text=label, font=("Segoe UI", 8, "bold"), fg="#6b7280", bg=CARD).pack(anchor="w")
            tk.Label(card, text=val, font=("Segoe UI", 28, "bold"), fg=color, bg=CARD).pack(anchor="w")

        if conn:
            styled_label(frame, "Membership Status Breakdown", font=("Segoe UI", 11, "bold"), fg=FG).pack(anchor="w", pady=(8, 4))

            try:
                cur = conn.cursor()
                cur.execute("SELECT Status, COUNT(*) AS Total FROM Membership GROUP BY Status ORDER BY Status")
                rows = cur.fetchall()
                cur.close()

                tbl = tk.Frame(frame, bg=CARD, padx=20, pady=14, highlightbackground="#e5e7eb", highlightthickness=1)
                tbl.pack(fill="x", pady=(0, 14))

                for col, hdr in enumerate(["STATUS", "COUNT"]):
                    tk.Label(tbl, text=hdr, font=("Segoe UI", 8, "bold"), fg="#6b7280", bg=CARD, width=20, anchor="w").grid(row=0, column=col, padx=8, pady=4, sticky="w")

                for i, (status, cnt) in enumerate(rows):
                    c = GREEN if status == "ACTIVE" else (RED if status == "EXPIRED" else "#f59e0b")
                    tk.Label(tbl, text=status, font=FONT_MONO, fg=c, bg=CARD, width=20, anchor="w").grid(row=i + 1, column=0, padx=8, pady=3, sticky="w")
                    tk.Label(tbl, text=str(cnt), font=FONT_MONO, fg=FG, bg=CARD, width=20, anchor="w").grid(row=i + 1, column=1, padx=8, pady=3, sticky="w")
            except Exception as e:
                styled_label(frame, f"Error: {e}", fg=RED).pack(anchor="w")

            styled_label(frame, "ActiveMembers View  (SELECT * FROM ActiveMembers)", font=("Segoe UI", 11, "bold"), fg=FG).pack(anchor="w", pady=(8, 4))

            try:
                cur = conn.cursor()
                # ROWNUM is used here to ensure compatibility with CMU's older Oracle servers
                cur.execute("""
                    SELECT * FROM (
                        SELECT MemberID, Name, PlanName, Status 
                        FROM ActiveMembers
                    ) WHERE ROWNUM <= 10
                """)
                rows = cur.fetchall()
                desc = [d[0] for d in cur.description]
                cur.close()
                self._render_table(frame, desc, rows)
            except Exception as e:
                styled_label(frame, f"Note: {e}", fg=FG_DIM).pack(anchor="w")

            conn.close()
        else:
            styled_label(
                frame,
                "Not connected to Oracle. Update DB_USER, DB_PASSWORD, DB_DSN at the top of this file.",
                fg=RED, bg=BG,
            ).pack(anchor="w", pady=20)

    # ── MEMBERS ──────────────────────────────────────────────────────
    def _view_members(self):
        frame = tk.Frame(self.scroll_frame, bg=BG, padx=28, pady=24)
        frame.pack(fill="both", expand=True)

        styled_label(frame, "Manage active and expired gym memberships.", fg=FG_DIM).pack(anchor="w", pady=(0, 14))

        conn = get_connection()
        if not conn: return

        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT m.MemberID, m.Name, g.GymName, ms.Status
                FROM Member m
                LEFT JOIN GymLocation g ON m.HomeGymID = g.GymID
                LEFT JOIN Membership ms ON m.MemberID = ms.MemberID
                ORDER BY m.MemberID
            """)
            rows = cur.fetchall()
            cur.close()

            desc = ["MemberID", "Name", "HomeGym", "Status"]
            styled_label(frame, f"{len(rows)} members found", font=("Segoe UI", 9), fg=FG_DIM).pack(anchor="w", pady=(0, 8))

            self._render_table(frame, desc, rows, color_col=3, color_map={"ACTIVE": GREEN, "EXPIRED": RED, "CANCELLED": "#f59e0b"})
        except Exception as e:
            styled_label(frame, f"Error: {e}", fg=RED).pack(anchor="w")

        conn.close()

    # ── PLANS ────────────────────────────────────────────────────────
    def _view_plans(self):
        frame = tk.Frame(self.scroll_frame, bg=BG, padx=28, pady=24)
        frame.pack(fill="both", expand=True)

        styled_label(frame, "Overview of available membership tiers and access levels.", fg=FG_DIM).pack(anchor="w", pady=(0, 14))

        conn = get_connection()
        if not conn: return

        try:
            cur = conn.cursor()
            cur.execute("SELECT PlanID, PlanName, AllowsGuest FROM Plan ORDER BY PlanID")
            rows = cur.fetchall()
            cur.close()

            desc = ["PlanID", "PlanName", "AllowsGuest"]
            self._render_table(frame, desc, rows, color_col=2, color_map={"Y": ACCENT, "N": FG_DIM})

            styled_label(frame, "Subscriber Counts per Plan", font=("Segoe UI", 11, "bold"), fg=FG).pack(anchor="w", pady=(20, 6))

            cur = conn.cursor()
            cur.execute("""
                SELECT p.PlanName, ms.Status, COUNT(*) AS Total
                FROM Plan p
                JOIN Membership ms ON p.PlanID = ms.PlanID
                GROUP BY p.PlanName, ms.Status
                ORDER BY p.PlanName, ms.Status
            """)
            rows2 = cur.fetchall()
            cur.close()

            desc2 = ["Plan", "Status", "Count"]
            self._render_table(frame, desc2, rows2)
        except Exception as e:
            styled_label(frame, f"Error: {e}", fg=RED).pack(anchor="w")

        conn.close()

    # ── CHECK-INS ────────────────────────────────────────────────────
    def _view_checkins(self):
        frame = tk.Frame(self.scroll_frame, bg=BG, padx=28, pady=24)
        frame.pack(fill="both", expand=True)

        styled_label(frame, "Real-time facility access log.", fg=FG_DIM).pack(anchor="w", pady=(0, 14))

        conn = get_connection()
        if not conn: return

        try:
            cur = conn.cursor()
            # ROWNUM used for compatibility instead of FETCH FIRST
            cur.execute("""
                SELECT * FROM (
                    SELECT c.CheckInID, m.Name, g.GymName,
                           TO_CHAR(c.CheckInTime,'YYYY-MM-DD HH24:MI') AS CheckInTime
                    FROM CheckIn c
                    JOIN Member m ON c.MemberID = m.MemberID
                    JOIN GymLocation g ON c.GymID = g.GymID
                    ORDER BY c.CheckInTime DESC
                ) WHERE ROWNUM <= 50
            """)
            rows = cur.fetchall()
            cur.close()

            total_cur = conn.cursor()
            total_cur.execute("SELECT COUNT(*) FROM CheckIn")
            total = total_cur.fetchone()[0]
            total_cur.close()

            desc = ["CheckInID", "Member Name", "Gym", "Time"]
            styled_label(frame, f"Showing most recent 50 of {total} total check-ins", font=("Segoe UI", 9), fg=FG_DIM).pack(anchor="w", pady=(0, 8))

            self._render_table(frame, desc, rows)
        except Exception as e:
            styled_label(frame, f"Error: {e}", fg=RED).pack(anchor="w")

        conn.close()

    # ── TABLE RENDERER ───────────────────────────────────────────────
    def _render_table(self, parent, headers, rows, color_col=None, color_map=None):
        container = tk.Frame(parent, bg=CARD, highlightbackground="#e5e7eb", highlightthickness=1)
        container.pack(fill="x", pady=(0, 12))

        for col, hdr in enumerate(headers):
            tk.Label(container, text=hdr, font=("Segoe UI", 8, "bold"), fg="#6b7280", bg=CARD, anchor="w", padx=12, pady=6, width=20).grid(row=0, column=col, sticky="w")

        sep = tk.Frame(container, height=1, bg="#e5e7eb")
        sep.grid(row=1, column=0, columnspan=len(headers), sticky="ew")

        for r, row in enumerate(rows):
            bg = CARD if r % 2 == 0 else "#f9fafb"
            for col, val in enumerate(row):
                text = str(val) if val is not None else "null"
                fg = FG
                if color_col is not None and col == color_col and color_map:
                    fg = color_map.get(str(val), FG)
                tk.Label(container, text=text, font=FONT_MONO, fg=fg, bg=bg, anchor="w", padx=12, pady=5, width=20).grid(row=r + 2, column=col, sticky="w")

        if not rows:
            tk.Label(container, text="No rows returned.", font=FONT_MONO, fg=FG_DIM, bg=CARD, padx=12, pady=8).grid(row=2, column=0, columnspan=len(headers), sticky="w")

    # ── MODAL HELPER ─────────────────────────────────────────────────
    def _modal(self, title, width=420, height=400):
        win = tk.Toplevel(self)
        win.title(title)
        win.configure(bg=BG)
        win.geometry(f"{width}x{height}")
        # Allows vertical resizing in case buttons are cut off on smaller laptop screens
        win.resizable(False, True)
        win.grab_set()

        tk.Label(win, text=title, font=("Segoe UI", 14, "bold"), fg=FG, bg=BG).pack(pady=(20, 4), padx=24, anchor="w")
        separator(win, bg="#e5e7eb").pack(fill="x", padx=24, pady=(0, 14))
        return win

    def _field(self, win, label, hint=""):
        row = tk.Frame(win, bg=BG)
        row.pack(fill="x", padx=24, pady=4)

        tk.Label(row, text=label.upper(), font=("Segoe UI", 8, "bold"), fg="#6b7280", bg=BG).pack(anchor="w")
        e = styled_entry(row, width=38)
        e.pack(fill="x", pady=(2, 0))

        if hint:
            tk.Label(row, text=hint, font=("Segoe UI", 8), fg="#9ca3af", bg=BG).pack(anchor="w")

        return e

    def _log_label(self, win):
        lbl = tk.Label(win, text="", font=FONT_MONO, fg=GREEN, bg=BG, wraplength=370, justify="left", padx=24)
        lbl.pack(fill="x", padx=0, pady=8)
        return lbl

    # ── ADD MEMBER ───────────────────────────────────────────────────
    def open_add_member(self):
        win = self._modal("Add Member", height=450)

        e_mid = self._field(win, "MemberID", "e.g. 1103")
        e_name = self._field(win, "Name", "e.g. Jordan Hayes")
        e_gym = self._field(win, "HomeGymID", "1 = Downtown   2 = Westside")
        e_msid = self._field(win, "MembershipID", "e.g. 5103")
        e_plan = self._field(win, "PlanID", "1 = Basic   2 = Black Card")

        status_var = tk.StringVar(value="ACTIVE")
        row = tk.Frame(win, bg=BG)
        row.pack(fill="x", padx=24, pady=4)

        tk.Label(row, text="STATUS", font=("Segoe UI", 8, "bold"), fg="#6b7280", bg=BG).pack(anchor="w")
        for v in ("ACTIVE", "EXPIRED", "CANCELLED"):
            tk.Radiobutton(row, text=v, variable=status_var, value=v, bg=BG, fg=FG, selectcolor=BG, activebackground=BG, font=FONT_BTN).pack(side="left", padx=6)

        log = self._log_label(win)

        def do_add():
            conn = get_connection()
            if not conn: return
            try:
                cur = conn.cursor()
                cur.execute("INSERT INTO Member (MemberID, Name, HomeGymID) VALUES (:1, :2, :3)", (int(e_mid.get()), e_name.get().strip(), int(e_gym.get())))
                cur.execute("INSERT INTO Membership (MembershipID, MemberID, PlanID, Status) VALUES (:1, :2, :3, :4)", (int(e_msid.get()), int(e_mid.get()), int(e_plan.get()), status_var.get()))
                conn.commit()
                cur.close()
                conn.close()

                log.configure(text=f"✓ Member {e_mid.get()} ({e_name.get()}) added successfully.", fg=GREEN)
                self.set_log(f"Added member {e_mid.get()} — {e_name.get()}")
                self.show_view("members")
            except oracledb.Error as e:
                conn.rollback()
                conn.close()
                log.configure(text=f"✗ {e}", fg=RED)

        styled_button(win, "Add Member", do_add, width=24).pack(pady=(6, 0))

    # ── ADD CHECK-IN ─────────────────────────────────────────────────
    def open_add_checkin(self):
        win = self._modal("Add Check-in", height=300)

        e_cid = self._field(win, "CheckInID", "e.g. 500")
        e_mid = self._field(win, "MemberID", "Active = 1001   Expired = 1002")
        e_gid = self._field(win, "GymID", "1 = Downtown   2 = Westside")

        log = self._log_label(win)

        def do_checkin():
            conn = get_connection()
            if not conn: return
            try:
                cur = conn.cursor()
                cur.execute("INSERT INTO CheckIn (CheckInID, MemberID, GymID, CheckInTime) VALUES (:1, :2, :3, SYSTIMESTAMP)", (int(e_cid.get()), int(e_mid.get()), int(e_gid.get())))
                conn.commit()
                cur.close()
                conn.close()

                log.configure(text=f"✓ Check-in {e_cid.get()} recorded for member {e_mid.get()}.", fg=GREEN)
                self.set_log(f"Check-in recorded — member {e_mid.get()}")
                self.show_view("checkins")
            except oracledb.Error as e:
                conn.rollback()
                conn.close()
                msg = str(e)
                if "ORA-20001" in msg:
                    msg = "ORA-20001: Member does not have an active membership\n(Trigger trg_active_checkin blocked this request)"
                log.configure(text=f"✗ {msg}", fg=RED)
                self.set_log("Trigger blocked check-in — no active membership", ok=False)

        styled_button(win, "Process Check-in", do_checkin, width=24).pack(pady=(6, 0))

    # ── UPDATE MEMBERSHIP STATUS ──────────────────────────────────────
    def open_update_status(self):
        win = self._modal("Update Membership Status", height=280)

        tk.Label(win, text="Update a member's account status below:", font=FONT_LABEL, fg="#6b7280", bg=BG).pack(anchor="w", padx=24)

        e_mid = self._field(win, "MemberID", "e.g. 1001")
        status_var = tk.StringVar(value="EXPIRED")

        row = tk.Frame(win, bg=BG)
        row.pack(fill="x", padx=24, pady=6)

        tk.Label(row, text="NEW STATUS", font=("Segoe UI", 8, "bold"), fg="#6b7280", bg=BG).pack(anchor="w")
        for v in ("ACTIVE", "EXPIRED", "CANCELLED"):
            tk.Radiobutton(row, text=v, variable=status_var, value=v, bg=BG, fg=FG, selectcolor=BG, activebackground=BG, font=FONT_BTN).pack(side="left", padx=8)

        log = self._log_label(win)

        def do_update():
            conn = get_connection()
            if not conn: return
            try:
                cur = conn.cursor()
                cur.execute("UPDATE Membership SET Status = :1 WHERE MemberID = :2", (status_var.get(), int(e_mid.get())))
                rows_updated = cur.rowcount
                conn.commit()
                cur.close()
                conn.close()

                if rows_updated == 0:
                    log.configure(text=f"No membership found for MemberID {e_mid.get()}.", fg=RED)
                else:
                    log.configure(text=f"✓ Member {e_mid.get()} status updated to {status_var.get()}.", fg=GREEN)
                    self.set_log(f"Status updated — member {e_mid.get()} → {status_var.get()}")
                    self.show_view("members")
            except oracledb.Error as e:
                conn.rollback()
                conn.close()
                log.configure(text=f"✗ {e}", fg=RED)

        styled_button(win, "Update Status", do_update, width=24).pack(pady=(4, 0))

    # ── DELETE MEMBER ─────────────────────────────────────────────────
    def open_delete_member(self):
        win = self._modal("Delete Member", height=260)

        tk.Label(win, text="Warning: This completely removes the member and their history.", font=("Segoe UI", 9, "bold"), fg=RED, bg=BG).pack(anchor="w", padx=24, pady=(0, 6))

        e_mid = self._field(win, "MemberID to delete", "e.g. 1001")
        log = self._log_label(win)

        def do_delete():
            mid_str = e_mid.get().strip()
            if not mid_str:
                log.configure(text="Enter a MemberID.", fg=RED)
                return

            if not messagebox.askyesno("Confirm Delete", f"Delete member {mid_str} and all their check-ins and membership records?\n\nThis cannot be undone."):
                return

            conn = get_connection()
            if not conn: return

            try:
                mid = int(mid_str)
                cur = conn.cursor()
                cur.execute("DELETE FROM CheckIn WHERE MemberID = :1", (mid,))
                ci = cur.rowcount
                cur.execute("DELETE FROM Membership WHERE MemberID = :1", (mid,))
                ms = cur.rowcount
                cur.execute("DELETE FROM Member WHERE MemberID = :1", (mid,))
                m = cur.rowcount
                conn.commit()
                cur.close()
                conn.close()

                if m == 0:
                    log.configure(text=f"No member found with ID {mid}.", fg=RED)
                else:
                    log.configure(text=f"✓ Deleted member {mid}.\nCheckIn rows removed: {ci}\nMembership rows removed: {ms}", fg=GREEN)
                    self.set_log(f"Deleted member {mid} — {ci} check-ins, {ms} memberships removed")
                    self.show_view("members")
            except oracledb.Error as e:
                conn.rollback()
                conn.close()
                log.configure(text=f"✗ {e}", fg=RED)

        styled_button(win, "Delete Member", do_delete, color="#dc2626", width=24).pack(pady=(4, 0))

# ─── ENTRY POINT ──────────────────────────────────────────────────────
if __name__ == "__main__":
    app = GymApp()
    app.mainloop()