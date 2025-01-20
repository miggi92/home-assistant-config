#!/bin/sh
cd /config

# git config
git config --global user.name miggi92
git config --global user.email miggi92@users.noreply.github.com

git add custom_components/*
git commit -m "chore: :arrow_up: upgrade custom components"
git push origin
