#!/bin/bash

# Configuration
HOST="http://127.0.0.1:8000"
GET_ENDPOINT="$HOST/"
POST_ENDPOINT="$HOST/update"

# Optional: Update rate limit before testing
read -p "Update rate limit before testing? (y/n): " UPDATE

if [[ "$UPDATE" == "y" || "$UPDATE" == "Y" ]]; then
    read -p "Enter new capacity: " CAPACITY
    read -p "Enter new refill_rate (tokens/sec, supports fractions like 1/3): " RAW_REFILL_RATE

    # Convert fraction to decimal using bc
    REFILL_RATE=$(printf "%.4f" "$(echo "scale=6; $RAW_REFILL_RATE" | bc)")
    echo "Parsed refill_rate: $REFILL_RATE"

    echo "Updating rate limit to capacity=$CAPACITY, refill_rate=$REFILL_RATE..."
    curl -s -X POST "$POST_ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "{\"capacity\": $CAPACITY, \"refill_rate\": $REFILL_RATE}" \
        | jq
    echo
fi

# Ask how many requests to send
read -p "How many test requests should we send to GET http://127.0.0.1:8000/ ? " REQUEST_COUNT

echo "Sending $REQUEST_COUNT requests to $GET_ENDPOINT ..."
for ((i = 1; i <= REQUEST_COUNT; i++)); do
    echo "[$i] Sending request..."
    curl -s -o /dev/null -w "Status: %{http_code}\n" "$GET_ENDPOINT"
    sleep 0.5  # Adjust this to test refill rate behavior
done
