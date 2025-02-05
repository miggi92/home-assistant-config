import os

covers = data.get('covers')
updates = data.get('updates')
alarm = data.get('alarm')
selects = data.get('selects')
# ... (füge alle anderen Entitäten hinzu)

markdown_file = "/config/docs/config/index.md"

try:
    with open(markdown_file, 'r') as f:
        lines = f.readlines()

    with open(markdown_file, 'w') as f:
        for line in lines:
            if "Covers" in line:
                f.write(f"| Covers              |   {covers}   |\n")
            elif "Updates" in line:
                f.write(f"| Updates             |  {updates}   |\n")
            elif "Alarm" in line:
                f.write(f"| Alarm               |   {alarm}   |\n")
            elif "Selects" in line:
                f.write(f"| Selects             |  {selects}   |\n")
            # ... (füge alle anderen Entitäten hinzu)
            else:
                f.write(line)

    hass.logger.info("Markdown file updated successfully.")

except Exception as e:
    hass.logger.error(f"Error updating Markdown file: {e}")
