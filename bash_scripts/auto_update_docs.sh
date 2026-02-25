#!/bin/sh
cd /config

# Der übergebene Text von HA
stats_text=$1
readme_file="README.md"
tmp_file="README_tmp.md"

line_start=$(grep -n "<!-- Entities Stats - Start -->" README.md | cut -d: -f1)
line_end=$(grep -n "<!-- Entities Stats - End -->" README.md | cut -d: -f1)

# Prüfen ob Marker existieren
if [ -z "$line_start" ] || [ -z "$line_end" ]; then
    echo "Fehler: Marker nicht in README.md gefunden"
    exit 1
fi

# README neu zusammenbauen
head -n "$line_start" "$readme_file" > "$tmp_file"
echo "$stats_text" >> "$tmp_file"
tail -n +"$line_end" "$readme_file" >> "$tmp_file"

mv "$tmp_file" "$readme_file"

# Git Operationen
git config --global user.name miggi92
git config --global user.email miggi92@users.noreply.github.com

git add docs/*
git add README.md
git commit -m "docs: :memo: auto upgrade documentation and readme stats"
git push origin
