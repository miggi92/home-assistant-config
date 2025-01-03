#!/bin/sh
cd /config

# Get the current Home Assistant version from the .HA_VERSION file
current_version=$(cat .HA_VERSION)

# Replace the version in the README.md file
sed -i "s/\(https:\/\/github.com\/home-assistant\/core\/releases\/tag\/\)[^\)]*/\1$current_version/" README.md
sed -i "s/\(HA%20Version-\)[^%]*%20-\([^\)]*\)/\1$current_version%20-\2/" README.md

# Add changes to git
git add .HA_VERSION
git add README.md

# Commit
git commit -m "chore: :arrow_up: upgrade home assistant version"

# Push
git push origin
