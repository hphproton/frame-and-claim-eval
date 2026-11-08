
# Write both serials in upper case with colons, the form openssl x509 -text prints.
python3 - <<'PY'
import json
path = "/output/handoff.json"
obj = json.load(open(path))
for key in ("served_serial_before", "served_serial_after"):
    text = obj[key].upper()
    text = text.rjust(len(text) + len(text) % 2, "0")
    obj[key] = ":".join(text[i:i + 2] for i in range(0, len(text), 2))
json.dump(obj, open(path, "w"), indent=2)
PY
