#!/bin/sh
cd /config

readme_file="README.md"
stats_file="spook_stats.md"
tmp_file="README_tmp.md"

awk '
// {
    print
    while ((getline line < "spook_stats.md") > 0)
        print line
    close("spook_stats.md")
    skip=1
    next
}
// {
    skip=0
}
!skip { print }
' "$readme_file" > "$tmp_file" && mv "$tmp_file" "$readme_file"

git config --global user.name miggi92
git config --global user.email miggi92@users.noreply.github.com

git add docs/*
git add README.md
git commit -m "docs: :memo: auto upgrade documentation and readme stats"
git push origin
