# Snapsplit PRD

## Overview

Snapsplit lets a group of friends split a restaurant bill. One person photographs the receipt, the app reads every line, and each friend taps the items they had. The app works out who owes what, including tax and tip.

## Users

Groups of friends aged 18-30 who eat out together and split bills.

## Features

1. Receipt scanning: take a photo, and the app extracts each line item and the total.
2. Item claiming: friends join the split with a link and tap their items.
3. Settle up: shows each person's share, with tax and tip split in proportion to what they ordered.

## Free tier

Free users can scan 3 receipts per day. Premium (£1.99/month) is unlimited.

## API

POST /v1/scans: upload a receipt photo. Returns `items` (name, price) and `total`.

## Auth

TODO: decide auth (magic link vs Sign in with Apple/Google?)

## Privacy

We will never sell or share receipt data with advertisers. Users trust us with where and what they eat.
