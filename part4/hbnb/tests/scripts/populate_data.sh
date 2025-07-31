#!/bin/bash
# Script to create 5 users (with passwords), 3 places, 10 amenities, and reviews via API.

API_URL="http://127.0.0.1:5000/api/v1"
USER_IDS=()
PLACE_IDS=()

# --- Create 5 users (with password) and store their IDs ---

NUMBER_OF_USERS=4
NUMBER_OF_AMENITIES=5

echo "Creating users..."
for i in $(seq 1 $NUMBER_OF_USERS)
do
  USER_EMAIL="user$i@example.com"
  USER_PASSWORD="password" # A simple password for each user
  
  RESPONSE=$(curl -s -X POST "$API_URL/users/" \
    -H "Content-Type: application/json" \
    -d "{\"first_name\": \"User\", \"last_name\": \"Test\", \"email\": \"$USER_EMAIL\", \"password\": \"$USER_PASSWORD\"}")
  
  echo "User $i response: $RESPONSE"
  USER_ID=$(echo "$RESPONSE" | grep -o '"id"[ ]*:[ ]*"[^\"]*"' | head -1 | cut -d '"' -f4)
  
  if [ -n "$USER_ID" ]; then
    USER_IDS+=("$USER_ID")
    echo "User $i ID: $USER_ID, Email: $USER_EMAIL, Password: $USER_PASSWORD"
  else
    echo "Failed to create user $i. Response was: $RESPONSE"
  fi
  sleep 0.2
done

echo ""
echo "Collected USER_IDS: ${USER_IDS[@]}"
echo ""

# List all users
echo ""
echo "Listing all users:"
curl -s "$API_URL/users/" | jq .
echo ""

# Use the first user as owner for all places (or rotate if you want)
# OWNER_ID=${USER_IDS[0]}

echo "Logging in as each user..."

JWT_TOKENS=()
for i in $(seq 1 $NUMBER_OF_USERS)
do
  EMAIL="user$i@example.com"
  PASSWORD="string"
  RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")
  JWT=$(echo "$RESPONSE" | grep -o '"access_token"[ ]*:[ ]*"[^"]*"' | cut -d '"' -f4)
  if [ -n "$JWT" ]; then
    echo "JWT token retrieved."
    echo "JWT of User $i: $JWT"
  else
    echo "Failed to retrieve JWT token of User $i."
    echo "Response: $RESPONSE"
  fi
  JWT_TOKENS+=("$JWT")
done  

# echo ""
# echo "Collected JWT_TOKENS: ${JWT_TOKENS[@]}"
# echo ""

echo "Creating places..."
for j in $(seq 1 3)
do
  TOKEN_INDEX=$(( (j-1) % ${#JWT_TOKENS[@]} ))
  JWT="${JWT_TOKENS[$TOKEN_INDEX]}"
  for i in $(seq 1 $j)
  do
    RESPONSE=$(curl -s -X POST "$API_URL/places/" \
      -H "Authorization: Bearer $JWT" \
      -H "Content-Type: application/json" \
      -d "{\"title\": \"Place$i of User$j\", \"description\": \"A nice place $i\", \"price\": 100, \"latitude\": 10.0, \"longitude\": 20.0, \"owner_id\": \"$OWNER_ID\"}")
    echo "Place $i of User $j response: $RESPONSE"
    PLACE_ID=$(echo "$RESPONSE" | grep -o '"id"[ ]*:[ ]*"[^\"]*"' | head -1 | cut -d '"' -f4)
    if [ -n "$PLACE_ID" ]; then
      PLACE_IDS+=("$PLACE_ID")
      echo "Place $i of User $j ID: $PLACE_ID"
    else
      echo "Failed to create place $i of user $j. Response was: $RESPONSE"
    fi
    sleep 0.2
  done
done

echo ""
echo "Collected PLACE_IDS: ${PLACE_IDS[@]}"
echo ""

# List all places
echo ""
echo "Listing all places:"
curl -s "$API_URL/places/" | jq .
echo ""

# Create 5 amenities
echo "Creating amenities..."
for i in $(seq 1 $NUMBER_OF_AMENITIES)
do
  curl -s -X POST "$API_URL/amenities/" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"Amenity$i\"}" | jq
  echo
  sleep 0.2
done

# --- Create reviews: each user reviews each place once ---
echo "Creating reviews..."
REVIEW_NUM=1
for j in $(seq 1 3)
do
  TOKEN_INDEX=$(( (j-1) % ${#JWT_TOKENS[@]} ))
  JWT="${JWT_TOKENS[$TOKEN_INDEX]}"
  # USER_ID="${USER_IDS[$TOKEN_INDEX]}"
  for USER_ID in "${USER_IDS[@]}"
  do
    for PLACE_ID in "${PLACE_IDS[@]}"
    do
      RESPONSE=$(curl -s -X POST "$API_URL/reviews/" \
        -H "Authorization: Bearer $JWT" \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"Review $REVIEW_NUM by user $USER_ID for place $PLACE_ID\", \"rating\": $(( (REVIEW_NUM % 5) + 1 )), \"place_id\": \"$PLACE_ID\", \"user_id\": \"$USER_ID\"}")
      echo "Review $REVIEW_NUM response: $RESPONSE"
      ((REVIEW_NUM++))
      sleep 0.1
    done
  done
done

echo "Done."

echo ""

for USER_ID in "${USER_IDS[@]}"
do
  echo "User ID: $USER_ID"
done

echo ""

for PLACE_ID in "${PLACE_IDS[@]}"
do
  echo "Place ID: $PLACE_ID"
done
