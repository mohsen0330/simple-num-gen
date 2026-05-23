#!/usr/bin/env python3
"""
A lightweight GUI application for generating random numbers from a given range.

This app provides a simple and intuitive user interface for selecting a
minimum and maximum integer range, choosing how many numbers to generate,
enabling or disabling repeats, and optionally supplying a base64‑encoded
sentence as a seed.  The generated numbers are saved alongside their
inputs to a text file, using ISO‑8601 timestamps for reproducibility.

Key features:

* Range inputs: specify the lower and upper bounds of the integer range.
* Quantity input: choose how many numbers to generate.
* Repeat toggle: decide whether numbers may repeat or must be unique.
* Seed input: base64‑encoded text seeds the pseudo‑random generator.
* Persistent state: previously used inputs are stored in a config file and
  automatically loaded when the app starts.
* Output logging: each generation writes a line to ``outputs.txt`` in the
  format ``<ISO timestamp> - <inputs/seed>: <generated numbers>``.
* Clean exit: a dedicated “Close” button lets users terminate the app.

This application uses the built‑in ``tkinter`` library for its user
interface, ``random`` for number generation, and ``json`` for
persistence.  No external dependencies are required.
"""

import base64
import datetime as dt
import json
import os
import random
import tkinter as tk
from tkinter import messagebox

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "outputs.txt")


class NumberGeneratorApp(tk.Tk):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Random Number Generator")
        self.geometry("350x300")
        self.resizable(False, False)

        # Initialize variables
        self.min_val = tk.StringVar(value="0")
        self.max_val = tk.StringVar(value="10")
        self.count = tk.StringVar(value="1")
        self.allow_repeats = tk.BooleanVar(value=True)
        self.seed_b64 = tk.StringVar(value="")

        # Load previous configuration if available
        self.load_config()

        # Build the UI
        self.create_widgets()

    def create_widgets(self) -> None:
        """Constructs all widgets in the window."""
        padding_opts = {"padx": 10, "pady": 5}

        # Range inputs
        tk.Label(self, text="Min Value:").grid(row=0, column=0, sticky="e", **padding_opts)
        tk.Entry(self, textvariable=self.min_val).grid(row=0, column=1, **padding_opts)
        tk.Label(self, text="Max Value:").grid(row=1, column=0, sticky="e", **padding_opts)
        tk.Entry(self, textvariable=self.max_val).grid(row=1, column=1, **padding_opts)

        # Count input
        tk.Label(self, text="Amount to generate:").grid(row=2, column=0, sticky="e", **padding_opts)
        tk.Entry(self, textvariable=self.count).grid(row=2, column=1, **padding_opts)

        # Repeats toggle
        tk.Checkbutton(
            self,
            text="Allow repeating numbers",
            variable=self.allow_repeats,
            onvalue=True,
            offvalue=False,
        ).grid(row=3, column=0, columnspan=2, sticky="w", **padding_opts)

        # Seed input
        tk.Label(self, text="Seed (base64):").grid(row=4, column=0, sticky="e", **padding_opts)
        tk.Entry(self, textvariable=self.seed_b64).grid(row=4, column=1, **padding_opts)

        # Generate and close buttons
        tk.Button(self, text="Generate", command=self.on_generate).grid(row=5, column=0, **padding_opts)
        tk.Button(self, text="Close", command=self.on_close).grid(row=5, column=1, **padding_opts)

        # Output display
        self.output_label = tk.Label(self, text="", wraplength=320, justify="left")
        self.output_label.grid(row=6, column=0, columnspan=2, **padding_opts)

    def save_config(self) -> None:
        """Save current input values to a JSON config file."""
        config = {
            "min_val": self.min_val.get(),
            "max_val": self.max_val.get(),
            "count": self.count.get(),
            "allow_repeats": self.allow_repeats.get(),
            "seed_b64": self.seed_b64.get(),
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")

    def load_config(self) -> None:
        """Load saved input values from the JSON config file, if present."""
        if os.path.isfile(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                self.min_val.set(config.get("min_val", self.min_val.get()))
                self.max_val.set(config.get("max_val", self.max_val.get()))
                self.count.set(config.get("count", self.count.get()))
                self.allow_repeats.set(config.get("allow_repeats", self.allow_repeats.get()))
                self.seed_b64.set(config.get("seed_b64", self.seed_b64.get()))
            except Exception:
                # Ignore corrupted config; reset to defaults
                pass

    def decode_seed(self, seed_b64: str) -> int:
        """Decode a base64 string into an integer seed for the random module.

        If decoding fails, a random seed based on system time is returned.
        The seed is generated by hashing the decoded bytes with SHA‑256 and
        converting to an integer.
        """
        if not seed_b64:
            return None  # None will trigger random seeding with system time
        try:
            decoded_bytes = base64.b64decode(seed_b64, validate=True)
            # Hash the decoded sentence to obtain a deterministic integer seed
            import hashlib

            digest = hashlib.sha256(decoded_bytes).digest()
            return int.from_bytes(digest, "big")
        except Exception:
            return None

    def on_generate(self) -> None:
        """Handle the Generate button click event."""
        # Validate numeric inputs
        try:
            min_v = int(self.min_val.get())
            max_v = int(self.max_val.get())
            if min_v > max_v:
                raise ValueError("Min value cannot be greater than max value.")
        except ValueError as e:
            messagebox.showerror("Invalid Range", f"Please enter valid integers for Min and Max.\n{e}")
            return
        try:
            count = int(self.count.get())
            if count <= 0:
                raise ValueError("Amount must be a positive integer.")
        except ValueError as e:
            messagebox.showerror("Invalid Amount", f"Please enter a valid positive integer for amount.\n{e}")
            return

        # Determine seed
        seed_int = self.decode_seed(self.seed_b64.get())
        rnd = random.Random()
        rnd.seed(seed_int)

        numbers = []
        range_size = max_v - min_v + 1
        if not self.allow_repeats.get() and count > range_size:
            messagebox.showerror(
                "Invalid Request",
                "Requested amount exceeds range size without repeats."
            )
            return

        if self.allow_repeats.get():
            for _ in range(count):
                numbers.append(rnd.randint(min_v, max_v))
        else:
            numbers = rnd.sample(range(min_v, max_v + 1), count)

        # Display the numbers
        self.output_label.config(text=", ".join(map(str, numbers)))

        # Log output to file
        timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
        inputs_summary = f"range=({min_v},{max_v}), count={count}, repeats={self.allow_repeats.get()}, seed={'provided' if self.seed_b64.get() else 'none'}"
        log_entry = f"{timestamp} - {inputs_summary}: {numbers}\n"
        try:
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            messagebox.showwarning("Logging Error", f"Failed to write to output file: {e}")

        # Persist current inputs
        self.save_config()

    def on_close(self) -> None:
        """Handle the Close button click event."""
        self.save_config()
        self.destroy()


def main() -> None:
    """Entry point for launching the application."""
    app = NumberGeneratorApp()
    app.mainloop()


if __name__ == "__main__":
    main()