#!/bin/sh
curl -X POST 'http://localhost:3000/function' --data-binary '@/config/js_scrapers/'$1 -H 'Content-Type: application/javascript' > /config/www/browserless/$2
