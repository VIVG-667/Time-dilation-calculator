"""
Time Dilation Calculator (Exact + Approx) with simplified reference frames

Reference frames:
- Relative Motion Only (no astronomical motion)
- CMB (Cosmic Microwave Background) with selectable speeds:
    350 km/s, 600 km/s, 850 km/s

Speed combination:
    v_total = sqrt(v_user^2 + v_frame^2)

Time dilation:
    Exact: γ = 1 / sqrt(1 - v^2/c^2)
    Approx: Δt ≈ t0 * v^2 / (2 c^2)

UI preserved from original design.
"""

import math
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

C = 299_792_458.0  

TIME_UNITS = {
    "Seconds": 1.0,
    "Minutes": 60.0,
    "Hours": 3600.0,
    "Days": 86400.0,
    "Years": 365 * 86400.0,
}

SPEED_UNITS = ["m/s", "km/s", "km/h", "fraction of c", "c"]

PRESETS = {
    "Walking": (1.4, "m/s"),
    "Car 100 km/h": (100.0, "km/h"),
    "Plane 900 km/h": (900.0, "km/h"),
    "ISS": (7.66, "km/s"),
    "0.1 c": (0.1, "fraction of c"),
    "0.5 c": (0.5, "fraction of c"),
    "0.9 c": (0.9, "fraction of c"),
}

REFERENCE_FRAMES = ["Relative Motion Only", "CMB"]

CMB_CHOICES = {
    "CMB 350 km/s": 350_000.0,
    "CMB 600 km/s": 600_000.0,
    "CMB 850 km/s": 850_000.0,
}


def to_m_per_s(value: float, unit: str) -> float:
    """Convert a speed value to meters per second."""
    if unit == "m/s":
        return value
    if unit == "km/s":
        return value * 1000.0
    if unit == "km/h":
        return value * 1000.0 / 3600.0
    if unit == "fraction of c":
        return value * C
    if unit == "c":
        return value * C
    return value


def approx_delta_t(t0_seconds: float, v_m_s: float) -> float:
    """Approximation for small v: Δt ≈ t0 * v^2 / (2 c^2)."""
    beta2 = (v_m_s / C) ** 2
    return t0_seconds * beta2 / 2.0


def lorentz_gamma(v_m_s: float) -> float:
    """Exact Lorentz factor γ."""
    beta = v_m_s / C
    if beta >= 1.0:
        beta = 0.999999999999
    return 1.0 / math.sqrt(1.0 - beta * beta)


def short_time(sec: float) -> str:
    """Return a short human-friendly time string."""
    if sec < 0:
        return "0 s"
    if sec < 1e-6:
        return f"{sec*1e9:.3f} ns"
    if sec < 1e-3:
        return f"{sec*1e6:.3f} µs"
    if sec < 1:
        return f"{sec*1e3:.3f} ms"
    if sec < 60:
        return f"{sec:.6f} s"
    if sec < 3600:
        return f"{sec/60:.6f} min"
    if sec < 86400:
        return f"{sec/3600:.6f} h"
    if sec < 365 * 86400:
        return f"{sec/86400:.6f} d"
    return f"{sec/(365*86400):.6f} yr"


class TimeDilationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Time Dilation — CMB Reference Frame")
        self.geometry("1000x640")
        self.configure(bg="#121212")
        self._style()
        self._vars()
        self._build_ui()
        self._bind_events()
        self._update_all()

    def _style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure(".", background="#121212", foreground="#eaeaea", fieldbackground="#1b1b1b")
        style.configure("TLabel", background="#121212", foreground="#eaeaea")
        style.configure("TButton", background="#1b1b1b", foreground="#eaeaea")
        style.configure("TEntry", fieldbackground="#1b1b1b", foreground="#eaeaea")
        style.configure("TCombobox", fieldbackground="#1b1b1b", foreground="#eaeaea")

    def _vars(self):
        self.time_value = tk.StringVar(value="1")
        self.time_unit = tk.StringVar(value="Years")
        self.speed_value = tk.StringVar(value="0.0")
        self.speed_unit = tk.StringVar(value="km/s")
        self.reference_frame = tk.StringVar(value="Relative Motion Only")
        self.cmb_choice = tk.StringVar(value="CMB 600 km/s")
        self.precision = tk.IntVar(value=6)
        self.calc_mode = tk.StringVar(value="Exact (Lorentz factor)")

        self.delta_str = tk.StringVar(value="0 s")
        self.traveler_str = tk.StringVar(value="")
        self.observer_str = tk.StringVar(value="")
        self.speed_str = tk.StringVar(value="0 m/s")
        self.gamma_str = tk.StringVar(value="γ = 1.000000")

    def _build_ui(self):
        left = ttk.Frame(self)
        left.pack(side="left", fill="y", padx=12, pady=12)

        ttk.Label(left, text="Inputs", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0,6))
        frm = ttk.Frame(left)
        frm.pack(fill="x")

        ttk.Label(frm, text="Time").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.time_value, width=12).grid(row=0, column=1, padx=6)
        ttk.Combobox(frm, textvariable=self.time_unit, values=list(TIME_UNITS.keys()), width=12).grid(row=0, column=2)

        ttk.Label(frm, text="Your speed").grid(row=1, column=0, sticky="w", pady=(8,0))
        ttk.Entry(frm, textvariable=self.speed_value, width=12).grid(row=1, column=1, padx=6, pady=(8,0))
        ttk.Combobox(frm, textvariable=self.speed_unit, values=SPEED_UNITS, width=12).grid(row=1, column=2, pady=(8,0))

        ttk.Label(left, text="Reference frame", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10,6))
        ttk.Combobox(left, textvariable=self.reference_frame,
                     values=REFERENCE_FRAMES, width=28).pack(anchor="w")

        ttk.Label(left, text="CMB speed", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10,6))
        ttk.Combobox(left, textvariable=self.cmb_choice,
                     values=list(CMB_CHOICES.keys()), width=28).pack(anchor="w")

        ttk.Label(left, text="Calculation mode", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10,6))
        ttk.Combobox(left, textvariable=self.calc_mode,
                     values=["Exact (Lorentz factor)", "Approximation (v << c)"],
                     width=28).pack(anchor="w")

        ttk.Label(left, text="Presets", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10,0))
        pf = ttk.Frame(left)
        pf.pack(fill="x", pady=(6,8))
        r = 0
        c = 0
        for name, (val, unit) in PRESETS.items():
            b = ttk.Button(pf, text=name, width=18,
                           command=lambda v=val, u=unit: self._apply_preset(v, u))
            b.grid(row=r, column=c, padx=4, pady=4)
            c += 1
            if c >= 2:
                c = 0
                r += 1

        ttk.Label(left, text="Precision (decimals)").pack(anchor="w", pady=(8,0))
        ttk.Spinbox(left, from_=3, to=12, textvariable=self.precision, width=6).pack(anchor="w", pady=(4,0))

        ttk.Button(left, text="Reset", command=self._reset).pack(fill="x", pady=(12,0))

        center = ttk.Frame(self)
        center.pack(side="left", fill="both", expand=True, padx=8, pady=12)

        ttk.Label(center, text="Results", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        res = ttk.Frame(center)
        res.pack(fill="x", pady=(6,0))

        ttk.Label(res, text="Lorentz factor γ:").grid(row=0, column=0, sticky="w")
        ttk.Label(res, textvariable=self.gamma_str).grid(row=0, column=1, sticky="w", padx=8)

        ttk.Label(res, text="Traveler proper time:").grid(row=1, column=0, sticky="w")
        ttk.Label(res, textvariable=self.traveler_str).grid(row=1, column=1, sticky="w", padx=8)

        ttk.Label(res, text="Observer time:").grid(row=2, column=0, sticky="w")
        ttk.Label(res, textvariable=self.observer_str).grid(row=2, column=1, sticky="w", padx=8)

        ttk.Label(res, text="Time difference Δt:").grid(row=3, column=0, sticky="w")
        ttk.Label(res, textvariable=self.delta_str).grid(row=3, column=1, sticky="w", padx=8)

        ttk.Label(res, text="Speed relative to selected reference frame:").grid(row=4, column=0, sticky="w")
        ttk.Label(res, textvariable=self.speed_str).grid(row=4, column=1, sticky="w", padx=8)

        ttk.Label(center, text="Short explanation (plain)", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(12,0))
        self.explain = ScrolledText(center, height=6, bg="#0f0f0f", fg="#eaeaea", insertbackground="#eaeaea")
        self.explain.pack(fill="x", pady=(6,0))

        ttk.Label(center, text="Step-by-step details", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(12,0))
        self.details = ScrolledText(center, height=12, bg="#0f0f0f", fg="#eaeaea", insertbackground="#eaeaea")
        self.details.pack(fill="both", expand=True, pady=(6,0))

        right = ttk.Frame(self)
        right.pack(side="right", fill="y", padx=12, pady=12)

        ttk.Label(right, text="Reference frame info", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.info = ScrolledText(right, width=36, height=18, bg="#121212", fg="#eaeaea", insertbackground="#eaeaea")
        self.info.pack(fill="both", pady=(6,0))

    def _bind_events(self):
        for var in (
            self.time_value,
            self.time_unit,
            self.speed_value,
            self.speed_unit,
            self.reference_frame,
            self.cmb_choice,
            self.precision,
            self.calc_mode,
        ):
            var.trace_add("write", lambda *a: self._update_all())

    def _apply_preset(self, val, unit):
        self.speed_value.set(f"{val:.6g}")
        self.speed_unit.set(unit)
        self._update_all()

    def _reset(self):
        self.time_value.set("1")
        self.time_unit.set("Years")
        self.speed_value.set("0.0")
        self.speed_unit.set("km/s")
        self.reference_frame.set("Relative Motion Only")
        self.cmb_choice.set("CMB 600 km/s")
        self.precision.set(6)
        self.calc_mode.set("Exact (Lorentz factor)")
        self._update_all()

    def _update_all(self):
        try:
            tval = float(self.time_value.get())
            if tval < 0:
                raise ValueError
            tsec = tval * TIME_UNITS.get(self.time_unit.get(), 1.0)
        except Exception:
            tsec = 0.0

        try:
            sval = float(self.speed_value.get())
        except Exception:
            sval = 0.0

        v_user = to_m_per_s(sval, self.speed_unit.get())

        frame = self.reference_frame.get()
        if frame == "Relative Motion Only":
            v_frame = 0.0
        else:
            v_frame = CMB_CHOICES.get(self.cmb_choice.get(), 600_000.0)

        v_total = math.sqrt(v_user**2 + v_frame**2)
        if v_total >= C:
            v_total = C * 0.999999999999

        mode = self.calc_mode.get()
        if mode == "Exact (Lorentz factor)":
            gamma = lorentz_gamma(v_total)
            traveler = tsec
            observer = gamma * tsec
            delta = observer - traveler
        else:
            delta = approx_delta_t(tsec, v_total)
            traveler = tsec
            observer = tsec + delta
            gamma = observer / traveler if traveler > 0 else 1.0

        prec = max(0, min(12, int(self.precision.get())))
        self.gamma_str.set(f"γ = {gamma:.{prec}f}")
        self.delta_str.set(short_time(delta))
        self.traveler_str.set(short_time(traveler))
        self.observer_str.set(short_time(observer))
        self.speed_str.set(f"{v_total:.6g} m/s")

        self.info.delete("1.0", "end")
        lines = [
            f"Reference frame: {frame}",
            "",
        ]
        if frame == "Relative Motion Only":
            lines.append("No astronomical motion included.")
        else:
            lines.append("CMB reference frame selected.")
            lines.append(f"CMB speed used: {v_frame:.6g} m/s")

        lines.append("")
        lines.append(f"Your speed: {v_user:.6g} m/s")
        lines.append(f"Combined speed (quadrature): {v_total:.6g} m/s")

        self.info.insert("1.0", "\n".join(lines))

        expl = [
            "Plain and short:",
            "- Your speed is combined with the CMB speed (if selected).",
            "- Exact mode uses γ = 1 / sqrt(1 - v^2/c^2).",
            "- Approx mode uses Δt ≈ t0 × v^2 / (2 c^2).",
            "",
            f"Reference frame: {frame}",
        ]
        self.explain.delete("1.0", "end")
        self.explain.insert("1.0", "\n".join(expl))

        det = []
        det.append("Step-by-step:")
        det.append(f"1) Input time: {self.time_value.get()} {self.time_unit.get()} = {tsec:.6g} s")
        det.append(f"2) Your speed: {v_user:.6g} m/s")
        det.append(f"3) Frame speed: {v_frame:.6g} m/s")
        det.append(f"4) Combined speed: v = sqrt(v_user^2 + v_frame^2) = {v_total:.6g} m/s")
        det.append(f"5) v/c = {v_total/C:.6g}")
        det.append(f"6) Mode: {mode}")

        if mode == "Exact (Lorentz factor)":
            det.append(f"   - γ = {gamma:.6g}")
            det.append(f"   - Observer time = γ × t0 = {observer:.6g} s")
            det.append(f"   - Δt = {delta:.6g} s")
        else:
            det.append("   - Approx: Δt ≈ t0 × v^2 / (2 c^2)")
            det.append(f"   - Δt = {delta:.6g} s")
            det.append(f"   - Observer time = t0 + Δt = {observer:.6g} s")

        self.details.delete("1.0", "end")
        self.details.insert("1.0", "\n".join(det))


if __name__ == "__main__":
    app = TimeDilationApp()
    app.mainloop()
