#!/bin/sh
cd /config

line_start=$(grep -n "<!-- Entities Stats - Start -->" README.md | cut -d: -f1)
line_end=$(grep -n "<!-- Entities Stats - End -->" README.md | cut -d: -f1)

head -n "$line_start" README.md > README_tmp.md
cat spook_stats.md >> README_tmp.md
tail -n +"$line_end" README.md >> README_tmp.md

mv README_tmp.md README.md

git config --global user.name miggi92
git config --global user.email miggi92@users.noreply.github.com

git add docs/*
git add README.md
git commit -m "docs: :memo: auto upgrade documentation and readme stats"
git push origin
