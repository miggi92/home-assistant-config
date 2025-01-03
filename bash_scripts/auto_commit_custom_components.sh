#!/bin/sh
cd /config
git add custom_components/*
git commit -m "chore: :arrow_up: upgrade custom components"
git push origin
