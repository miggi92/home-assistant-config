---
---

# Vacations Countdown

This example shows how to create a countdown to a vacation in Lovelace. The start of the vacation can be added to home assistant with the [Anniversaries Component](https://github.com/pinkywafer/Anniversaries).

```yaml
type: custom:auto-entities
filter:
    include:
    - entity_id: sensor.anniversary_urlaub*
        options:
        type: custom:mushroom-template-card
        icon: mdi:beach
        primary: |
            {{ state_attr(entity, 'friendly_name') }}
        icon_color: blue
        secondary: |
            {%- set event_date = state_attr(entity, 'date') %}
            {%- set now = now() %}
            {%- set delta = event_date - now %}
            {%- set weeks = (delta.days // 7) %}
            {%- set days = delta.days % 7 %}
            {%- set hours = delta.seconds // 3600 %}
            {%- set minutes = (delta.seconds % 3600) // 60 %}
            {{- "{} Wochen ".format(weeks) if weeks > 0 else "" -}}
            {{- "{} Tage ".format(days) if days > 0 else "" -}}
            {{- "{} Stunden ".format(hours) if hours > 0 else "" -}}
            {{- "{} Minuten ".format(minutes) if minutes > 0 else "" -}}
        badge_icon: |-
            {%- set event = int(states(entity)) %}
            {% if (event) <= 10 %}
            mdi:exclamation-thick
            {% endif%}
        badge_color: red
        tap_action:
            action: more-info
        card_mod:
            style:
            mushroom-shape-icon$: |
                .shape {
                background: radial-gradient(var(--card-background-color) 60%, transparent 0%), conic-gradient(rgb(var(--rgb-red)) {{ (150-int(states(config.entity)))/150*100 }}% 0%, var(--card-background-color) 0% 100%);
                }
                .shape:after {
                content: "";
                height: 100%;
                width: 100%;
                position: absolute;
                border-radius: 50%;
                background: rgba(var(--rgb-{{ config.icon_color }}), 0.2);
                }
    exclude: []
sort:
    method: state
    reverse: false
    numeric: true
    count: 3
show_empty: false
card:
    type: entities
    show_header_toggle: false
    title: Urlaubscountdown
    state_color: false
    header:
    type: picture
    image: >-
        https://cdn.pixabay.com/photo/2018/01/31/16/12/beach-3121393_1280.png
    tap_action:
        action: none
    hold_action:
        action: none
```