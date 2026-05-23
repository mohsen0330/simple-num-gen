#simple-num-gen

Features of the app

Inputs: min value, max value, number of values to generate, repeat toggle, base64‑encoded seed.
Persistence: remembers previous inputs via ```config.json```.
Seed decoding: decodes base64 and hashes it for seeding; falls back to system time if omitted/invalid.
Unique sampling: when repeats are disallowed, uses random.sample to produce unique numbers.
Logging: appends each run to outputs.txt in the format “ISO date – inputs/seed: [numbers]”.
UI: simple tkinter interface with Generate and Close buttons.

Run the app with ```python3 num_gen_app.py```. It will create both ```config.json``` and ```outputs.txt``` in the same directory.