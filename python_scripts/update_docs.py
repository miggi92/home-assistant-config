import json
import re

json_file_path = "/config/spook_stats.json"
readme_file_path = "/config/README.md"

with open(json_file_path, "r") as json_file:
    spook_data = json.load(json_file)

markdown_content = (
    "### Home Assistant Spook Counters\n"
    f"- Covers: {spook_data.get('covers', 0)}\n"
    f"- Lights: {spook_data.get('lights', 0)}\n"
    f"- Automations: {spook_data.get('automations', 0)}\n"
)

with open(readme_file_path, "r") as readme_file:
    readme_text = readme_file.read()

pattern = r"(\n).*?()"
replacement = rf"\1{markdown_content}\2"
updated_readme_text = re.sub(pattern, replacement, readme_text, flags=re.DOTALL)

with open(readme_file_path, "w") as readme_file:
    readme_file.write(updated_readme_text)
