#!/bin/sh
cd /config

# git config
git config --global user.name miggi92
git config --global user.email miggi92@users.noreply.github.com

git add docs/*
git commit -m "docs: :memo: auto upgrade documentation"
git push origin
