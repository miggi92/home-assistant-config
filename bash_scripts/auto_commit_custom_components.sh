#!/bin/sh
cd /config

# git config
git config username.user miggi92
git config username.email miggi92@users.noreply.github.com

git add custom_components/*
git commit -m "chore: :arrow_up: upgrade custom components"
git push origin
