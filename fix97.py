with open('.venv/Lib/site-packages/arc_agi/base.py', 'r') as f:
    text = f.read()

bad = '''    def _fetch_from_api(self) -> None:
        """Fetch available environments from the API and merge with local environments."""
        if not self.arc_api_key:
            # Skip API call if no API key is provided
            return'''
good = '''    def _fetch_from_api(self) -> None:
        """Fetch available environments from the API and merge with local environments."""
        return # Offline mode enforcement
        if not self.arc_api_key:
            # Skip API call if no API key is provided
            return'''

if bad in text:
    text = text.replace(bad, good)
    with open('.venv/Lib/site-packages/arc_agi/base.py', 'w') as f:
        f.write(text)
    print("Patched _fetch_from_api")
else:
    print("Could not find block!")
