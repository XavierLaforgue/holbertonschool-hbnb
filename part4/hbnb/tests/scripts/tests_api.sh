#!/bin/bash

API_URL="http://127.0.0.1:5000/api/v1"
RED='\033[0;31m'  # Status code OK
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Fonction pour afficher le statut du test
assert_status() {
    local response="$1"
    local expected_status="$2"
    local test_name="$3"
    local http_status=$(echo "$response" | grep -o -E "HTTP/[0-9]\.[0-9] [0-9]{3}" | awk '{print $2}' | tail -n 1)

    if [ "$http_status" == "$expected_status" ]; then
        echo -e "${GREEN}[OK]${NC} $test_name (Status: $http_status)"
    else
        echo -e "${RED}[FAIL]${NC} $test_name (Expected: $expected_status, Got: $http_status)"
        echo "Response: $response"
    fi
}

echo "--- User API Tests ---"

# --- SCENARIOS DE CRÉATION (POST/ User) ---

echo "Scenario1: Successful user creation"
RESPONSE1=$(curl -s -i -X POST "$API_URL/users/" \
    -H "Content-Type: application/json" \
    -d "{\"first_name\": \"John\", \"last_name\": \"Doe\", \"email\": \"john@example.com\"}")
assert_status "$RESPONSE1" "201" "Create valid user 1"
USER_ID1=$(echo "$RESPONSE1" | grep -o '"id"[ ]*:[ ]*"[^\"]*"' | head -1 | cut -d '"' -f4)
echo "  User ID 1: $USER_ID1"

echo "Scenario2: Successful user creation"
RESPONSE2=$(curl -s -i -X POST "$API_URL/users/" \
    -H "Content-Type: application/json" \
    -d "{\"first_name\": \"Jane\", \"last_name\": \"Doe\", \"email\": \"jane@example.com\"}")
assert_status "$RESPONSE2" "201" "Create valid user 2"
USER_ID2=$(echo "$RESPONSE2" | grep -o '"id"[ ]*:[ ]*"[^\"]*"' | head -1 | cut -d '"' -f4)
echo "  User ID 2: $USER_ID2"

echo "Scenario3: One field with a blankspace at the end of the string"
RESPONSE3=$(curl -s -i -X POST "$API_URL/users/" \
    -H "Content-Type: application/json" \
    -d "{\"first_name\": \"Amy\", \"last_name\": \"Winehouse \", \"email\": \"club@27.com\"}")
# Supposons que ceci devrait être une création réussie (201),
# mais il est crucial que votre API gère le trim des espaces
assert_status "$RESPONSE3" "201" "Create user with blankspace at end of last_name"
USER_ID3=$(echo "$RESPONSE3" | grep -o '"id"[ ]*:[ ]*"[^\"]*"' | head -1 | cut -d '"' -f4)
echo "  User ID 3: $USER_ID3"

echo "Scenario4: One field with a blankspace at the end and email with a blankspace at the beginning"
RESPONSE4=$(curl -s -i -X POST "$API_URL/users/" \
    -H "Content-Type: application/json" \
    -d "{\"first_name\": \"Kurt \", \"last_name\": \"Cobain\", \"email\": \" again@club27.com\"}")
# Attendu: 201 si l'email est trimé et unique, sinon 400 si la validation d'email ne trimme pas
# et trouve un doublon, ou si le trim invalide le format.
# Il est préférable que l'API trimme ces espaces.
assert_status "$RESPONSE4" "201" "Create user with leading/trailing spaces"
USER_ID4=$(echo "$RESPONSE4" | grep -o '"id"[ ]*:[ ]*"[^\"]*"' | head -1 | cut -d '"' -f4)
echo "  User ID 4: $USER_ID4"

echo "Scenario5: Email with 2@"
RESPONSE5=$(curl -s -i -X POST "$API_URL/users/" \
    -H "Content-Type: application/json" \
    -d "{\"first_name\": \"Bob\", \"last_name\": \"Dylan\", \"email\": \"deadman@@heaven.fr\"}")
# Attendu: 400 si votre validation d'email est assez robuste pour détecter le double '@'
assert_status "$RESPONSE5" "400" "Create user with invalid email (double @)"
# USER_ID5 ne sera probablement pas généré en cas d'erreur 400, donc pas besoin de l'extraire.

echo "Scenario6: One field empty"
RESPONSE6=$(curl -s -i -X POST "$API_URL/users/" \
    -H "Content-Type: application/json" \
    -d "{\"first_name\": \"Kurt\", \"last_name\": \"\", \"email\": \"again@club27.com\"}")
# Attendu: 400 si le champ vide n'est pas permis pour `last_name` ou si l'email est un doublon après trim
assert_status "$RESPONSE6" "400" "Create user with empty last_name (and potentially duplicate email)"
# USER_ID6 ne sera probablement pas généré.

echo "Scenario7: blankspaces at the beginning and the end of fields"
RESPONSE7=$(curl -s -i -X POST "$API_URL/users/" \
    -H "Content-Type: application/json" \
    -d "{\"first_name\": \"   Kurt \", \"last_name\": \"    Cobain     \", \"email\": \" another@club27.com\"}")
# Attendu: 201 si l'API gère bien le trim et l'unicité de l'email, sinon 400
assert_status "$RESPONSE7" "201" "Create user with all fields having spaces"
USER_ID7=$(echo "$RESPONSE7" | grep -o '"id"[ ]*:[ ]*"[^\"]*"' | head -1 | cut -d '"' -f4)
echo "  User ID 7: $USER_ID7"

echo "Scenario8: Create user with existing email"
RESPONSE8=$(curl -s -i -X POST "$API_URL/users/" \
    -H "Content-Type: application/json" \
    -d "{\"first_name\": \"James\", \"last_name\": \"Dean\", \"email\": \"john@example.com\"}")
assert_status "$RESPONSE8" "400" "Create user with duplicate email"

echo "Scenario9: Create user with empty fields (required validation)"
RESPONSE9=$(curl -s -i -X POST "$API_URL/users/" \
    -H "Content-Type: application/json" \
    -d "{\"first_name\": \"\", \"last_name\": \"\", \"email\": \"\"}")
assert_status "$RESPONSE9" "400" "Create user with empty required fields"

echo "Scenario10: Create user with missing fields"
RESPONSE10=$(curl -s -i -X POST "$API_URL/users/" \
    -H "Content-Type: application/json" \
    -d "{\"last_name\": \"Missing\", \"email\": \"missing@example.com\"}")
assert_status "$RESPONSE10" "400" "Create user with missing first_name"

echo "Scenario11: Create user with invalid email format"
RESPONSE11=$(curl -s -i -X POST "$API_URL/users/" \
    -H "Content-Type: application/json" \
    -d "{\"first_name\": \"Bad\", \"last_name\": \"Email\", \"email\": \"bad-email-format\"}")
assert_status "$RESPONSE11" "400" "Create user with invalid email format (no @)"

echo "Scenario12: Create user with invalid email format"
RESPONSE12=$(curl -s -i -X POST "$API_URL/users/" \
    -H "Content-Type: application/json" \
    -d "{\"first_name\": \"Bad\", \"last_name\": \"Email\", \"email\": \"test@domain..com\"}")
assert_status "$RESPONSE12" "400" "Create user with invalid email format (double dot)"


# --- SCENARIOS DE LECTURE (GET) ---

echo "Scenario13: Get all users"
RESPONSE13=$(curl -s -i "$API_URL/users/")
assert_status "$RESPONSE13" "200" "Get all users"

echo "Scenario14: Get existing user by ID"
if [ -n "$USER_ID1" ]; then
    RESPONSE14=$(curl -s -i "$API_URL/users/$USER_ID1")
    assert_status "$RESPONSE14" "200" "Get existing user by ID ($USER_ID1)"
else
    echo -e "${RED}[SKIP]${NC} Get existing user: USER_ID1 not set."
fi

echo "Scenario15: Get non-existent user by ID"
RESPONSE15=$(curl -s -i "$API_URL/users/123e4567-e89b-12d3-a456-000000000000")
assert_status "$RESPONSE15" "404" "Get non-existent user"

echo "Scenario16: Get user with invalid UUID format"
RESPONSE16=$(curl -s -i "$API_URL/users/invalid-uuid-string")
assert_status "$RESPONSE16" "400" "Get user with invalid UUID format"

# --- SCENARIOS DE MISE À JOUR (PUT) ---

echo "Scenario17: Update existing user successfully"
if [ -n "$USER_ID1" ]; then
    RESPONSE17=$(curl -s -i -X PUT "$API_URL/users/$USER_ID1" \
        -H "Content-Type: application/json" \
        -d "{\"first_name\": \"Jonathan\", \"last_name\": \"Doereau\", \"email\": \"john.new@example.com\"}")
    assert_status "$RESPONSE17" "200" "Update user 1 successfully"
else
    echo -e "${RED}[SKIP]${NC} Update user successfully: USER_ID1 not set."
fi

echo "Scenario18: Update user with duplicate email (another user)"
if [ -n "$USER_ID1" ] && [ -n "$USER_ID2" ]; then
    RESPONSE18=$(curl -s -i -X PUT "$API_URL/users/$USER_ID1" \
        -H "Content-Type: application/json" \
        -d "{\"first_name\": \"John\", \"last_name\": \"Doe\", \"email\": \"jane@example.com\"}")
    assert_status "$RESPONSE18" "400" "Update user with email taken by another user"
else
    echo -e "${RED}[SKIP]${NC} Update user with duplicate email: USER_ID1 or USER_ID2 not set."
fi

echo "Scenario19: Update non-existent user"
RESPONSE19=$(curl -s -i -X PUT "$API_URL/users/123e4567-e89b-12d3-a456-000000000000" \
    -H "Content-Type: application/json" \
    -d "{\"first_name\": \"NonEx\", \"last_name\": \"Istent\", \"email\": \"nonexistent@example.com\"}")
assert_status "$RESPONSE19" "404" "Update non-existent user"

echo "Scenario20: Update user with invalid UUID format"
RESPONSE20=$(curl -s -i -X PUT "$API_URL/users/invalid-uuid-for-update" \
    -H "Content-Type: application/json" \
    -d "{\"first_name\": \"Invalid\", \"last_name\": \"UUID\", \"email\": \"invalid@example.com\"}")
assert_status "$RESPONSE20" "400" "Update user with invalid UUID format"


# --- SCENARIOS DE SUPPRESSION (DELETE) ---

echo "Scenario21: Delete existing user"
if [ -n "$USER_ID1" ]; then
    RESPONSE21=$(curl -s -i -X DELETE "$API_URL/users/$USER_ID1")
    assert_status "$RESPONSE21" "200" "Delete existing user ($USER_ID1)"
else
    echo -e "${RED}[SKIP]${NC} Delete existing user: USER_ID1 not set."
fi

echo "Scenario22: Delete non-existent user"
RESPONSE22=$(curl -s -i -X DELETE "$API_URL/users/123e4567-e89b-12d3-a456-000000000000")
assert_status "$RESPONSE22" "404" "Delete non-existent user"

echo "Scenario23: Delete user with invalid UUID format"
RESPONSE23=$(curl -s -i -X DELETE "$API_URL/users/invalid-uuid-for-delete")
assert_status "$RESPONSE23" "400" "Delete user with invalid UUID format"

echo "Scenario24: Attempt to get deleted user"
if [ -n "$USER_ID1" ]; then
    RESPONSE24=$(curl -s -i "$API_URL/users/$USER_ID1")
    assert_status "$RESPONSE24" "404" "Get deleted user ($USER_ID1) (should be 404)"
fi

echo "--- All User API Tests Completed ---"

echo "--- Amenity API Tests ---"

# --- SCENARIOS DE CRÉATION (POST/ Amenity) ---

echo "Scenario25: Successful amenity creation"
RESPONSE_AMENITY_25=$(curl -s -i -X POST "$API_URL/amenities/" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"WiFi\"}")
assert_status "$RESPONSE_AMENITY_25" "201" "Create 'WiFi' amenity"
AMENITY_ID_1=$(echo "$RESPONSE_AMENITY_25" | grep -o '"id"[ ]*:[ ]*"[^\"]*"' | head -1 | cut -d '"' -f4)
echo "  Amenity ID 1: $AMENITY_ID_25"

echo "Scenario26: Successful amenity creation"
RESPONSE_AMENITY_26=$(curl -s -i -X POST "$API_URL/amenities/" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"Swimming Pool\"}")
assert_status "$RESPONSE_AMENITY_26" "201" "Create 'Swimming Pool' amenity"
AMENITY_ID_26=$(echo "$RESPONSE_AMENITY_26" | grep -o '"id"[ ]*:[ ]*"[^\"]*"' | head -1 | cut -d '"' -f4)
echo "  Amenity ID 2: $AMENITY_ID_26"

echo "Scenario27: Attempt to create amenity with existing name (duplicate)"
# Note: Your facade currently does not have logic to enforce unique amenity names.
# This test expects 201 if duplicates are allowed, or 400 if you add that validation.
RESPONSE_AMENITY_27=$(curl -s -i -X POST "$API_URL/amenities/" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"WiFi\"}")
# If you implement uniqueness, change 201 to 400 here
assert_status "$RESPONSE_AMENITY_27" "201" "Create amenity with duplicate name (expected 201 or 400 if validated)"


echo "Scenario28: Create amenity with empty name"
RESPONSE_AMENITY_28=$(curl -s -i -X POST "$API_URL/amenities/" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"\"}")
assert_status "$RESPONSE_AMENITY_28" "400" "Create amenity with empty name"

echo "Scenario29: Create amenity with missing 'name' field"
RESPONSE_AMENITY_29=$(curl -s -i -X POST "$API_URL/amenities/" \
    -H "Content-Type: application/json" \
    -d "{}" )
assert_status "$RESPONSE_AMENITY_29" "400" "Create amenity with missing name"

echo "Scenario30: Create amenity with invalid name type (number instead of string)"
RESPONSE_AMENITY_30=$(curl -s -i -X POST "$API_URL/amenities/" \
    -H "Content-Type: application/json" \
    -d "{\"name\": 123}")
assert_status "$RESPONSE_AMENITY_30" "400" "Create amenity with invalid name type"


# --- READ SCENARIOS (GET) ---

echo "Scenario31: Retrieve all amenities"
RESPONSE_AMENITY_31=$(curl -s -i "$API_URL/amenities/")
assert_status "$RESPONSE_AMENITY_31" "200" "Retrieve all amenities"

echo "Scenario32: Retrieve existing amenity by ID"
if [ -n "$AMENITY_ID_1" ]; then
    RESPONSE_AMENITY_32=$(curl -s -i "$API_URL/amenities/$AMENITY_ID_1")
    assert_status "$RESPONSE_AMENITY_32" "200" "Retrieve amenity by ID ($AMENITY_ID_1)"
else
    echo -e "${RED}[SKIPPED]${NC} Retrieve existing amenity: AMENITY_ID_1 not set."
fi

echo "Scenario33: Attempt to retrieve non-existent amenity"
RESPONSE_AMENITY_33=$(curl -s -i "$API_URL/amenities/123e4567-e89b-12d3-a456-000000000000")
assert_status "$RESPONSE_AMENITY_33" "404" "Retrieve non-existent amenity"

echo "Scenario34: Attempt to retrieve amenity with malformed ID (non-UUID)"
RESPONSE_AMENITY_34=$(curl -s -i "$API_URL/amenities/not-a-uuid")
assert_status "$RESPONSE_AMENITY_34" "400" "Retrieve amenity with malformed ID"


# --- UPDATE SCENARIOS (PUT /amenities/<id>) ---

echo "Scenario35: Update an existing amenity successfully"
if [ -n "$AMENITY_ID_1" ]; then
    RESPONSE_AMENITY_35=$(curl -s -i -X PUT "$API_URL/amenities/$AMENITY_ID_1" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"Internet\"}")
    assert_status "$RESPONSE_AMENITY_35" "200" "Update amenity 1 to 'Internet'"
else
    echo -e "${RED}[SKIPPED]${NC} Update amenity: AMENITY_ID_1 not set."
fi

echo "Scenario36: Attempt to update a non-existent amenity"
RESPONSE_AMENITY_36=$(curl -s -i -X PUT "$API_URL/amenities/123e4567-e89b-12d3-a456-000000000000" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"Garden\"}")
assert_status "$RESPONSE_AMENITY_36" "404" "Update non-existent amenity"

echo "Scenario37: Attempt to update amenity with malformed ID"
RESPONSE_AMENITY_37=$(curl -s -i -X PUT "$API_URL/amenities/invalid-uuid-for-update" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"Parking\"}")
assert_status "$RESPONSE_AMENITY_37" "400" "Update amenity with malformed ID"

echo "Scenario38: Attempt to update amenity with an empty name"
if [ -n "$AMENITY_ID_1" ]; then
    RESPONSE_AMENITY_38=$(curl -s -i -X PUT "$API_URL/amenities/$AMENITY_ID_1" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"\"}")
    assert_status "$RESPONSE_AMENITY_38" "400" "Update amenity with empty name"
else
    echo -e "${RED}[SKIPPED]${NC} Update amenity with empty name: AMENITY_ID_1 not set."
fi

echo "Scenario39: Attempt to update amenity with a missing 'name' field"
if [ -n "$AMENITY_ID_1" ]; then
    RESPONSE_AMENITY_39=$(curl -s -i -X PUT "$API_URL/amenities/$AMENITY_ID_1" \
        -H "Content-Type: application/json" \
        -d "{}" )
    assert_status "$RESPONSE_AMENITY_39" "400" "Update amenity with missing name"
else
    echo -e "${RED}[SKIPPED]${NC} Update amenity with missing name: AMENITY_ID_1 not set."
fi


# --- DELETE SCENARIOS (DELETE /amenities/<id>) ---

echo "Scenario40: Delete an existing amenity"
if [ -n "$AMENITY_ID_2" ]; then
    RESPONSE_AMENITY_40=$(curl -s -i -X DELETE "$API_URL/amenities/$AMENITY_ID_2")
    assert_status "$RESPONSE_AMENITY_40" "200" "Delete amenity ($AMENITY_ID_2)"
else
    echo -e "${RED}[SKIPPED]${NC} Delete amenity: AMENITY_ID_2 not set."
fi

echo "Scenario41: Attempt to retrieve the deleted amenity"
if [ -n "$AMENITY_ID_2" ]; then
    RESPONSE_AMENITY_41=$(curl -s -i "$API_URL/amenities/$AMENITY_ID_2")
    assert_status "$RESPONSE_AMENITY_41" "404" "Retrieve deleted amenity (expected 404)"
else
    echo -e "${RED}[SKIPPED]${NC} Retrieve deleted amenity: AMENITY_ID_2 not set."
fi

echo "Scenario42: Attempt to delete a non-existent amenity"
RESPONSE_AMENITY_42=$(curl -s -i -X DELETE "$API_URL/amenities/123e4567-e89b-12d3-a456-000000000000")
assert_status "$RESPONSE_AMENITY_42" "404" "Delete non-existent amenity"

echo "Scenario43: Attempt to delete amenity with malformed ID"
RESPONSE_AMENITY_43=$(curl -s -i -X DELETE "$API_URL/amenities/invalid-uuid-for-delete")
assert_status "$RESPONSE_AMENITY_43" "400" "Delete amenity with malformed ID"

echo "--- All Amenities API Tests Completed ---"

echo "--- Place API Tests ---"

# Create a User and some Amenities for Place creation
RESPONSE_USER_PLACE_OWNER44=$(curl -s -i -X POST "$API_URL/users/" \
    -H "Content-Type: application/json" \
    -d "{\"first_name\": \"Place\", \"last_name\": \"Owner\", \"email\": \"place.owner@example.com\"}")
assert_status "$RESPONSE_USER_PLACE_OWNER44" "201" "Setup: Create Place Owner User"
PLACE_OWNER_ID=$(echo "$RESPONSE_USER_PLACE_OWNER44" | grep -o '"id"[ ]*:[ ]*"[^\"]*"' | head -1 | cut -d '"' -f4)
echo "  Place Owner User ID: $PLACE_OWNER_ID"

RESPONSE_AMENITY_A45=$(curl -s -i -X POST "$API_URL/amenities/" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"Parking\"}")
assert_status "$RESPONSE_AMENITY_A45" "201" "Setup: Create Amenity 'Parking'"
AMENITY_ID_A45=$(echo "$RESPONSE_AMENITY_A45" | grep -o '"id"[ ]*:[ ]*"[^\"]*"' | head -1 | cut -d '"' -f4)
echo "  Amenity A ID: $AMENITY_ID_A45"

RESPONSE_AMENITY_B46=$(curl -s -i -X POST "$API_URL/amenities/" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"Gym\"}")
assert_status "$RESPONSE_AMENITY_B46" "201" "Setup: Create Amenity 'Gym'"
AMENITY_ID_B46=$(echo "$RESPONSE_AMENITY_B46" | grep -o '"id"[ ]*:[ ]*"[^\"]*"' | head -1 | cut -d '"' -f4)
echo "  Amenity B ID: $AMENITY_ID_B46"


# --- CREATE SCENARIOS (POST /places/) ---

echo "Scenario47: Successful place creation with owner and amenities"
if [ -n "$PLACE_OWNER_ID" ] && [ -n "$AMENITY_ID_A" ] && [ -n "$AMENITY_ID_B" ]; then
    RESPONSE_PLACE_47=$(curl -s -i -X POST "$API_URL/places/" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"Cozy Apartment\", \"description\": \"A lovely place\", \"address\": \"123 Main St\", \"city\": \"Anytown\", \"latitude\": 34.05, \"longitude\": -118.25, \"number_of_rooms\": 2, \"number_of_bathrooms\": 1, \"price_per_night\": 100, \"max_guests\": 4, \"owner_id\": \"$PLACE_OWNER_ID\", \"amenities\": [\"$AMENITY_ID_A\", \"$AMENITY_ID_B\"]}")
    assert_status "$RESPONSE_PLACE_47" "201" "Create Place 1 (Cozy Apartment)"
    PLACE_ID_1=$(echo "$RESPONSE_PLACE_47" | grep -o '"id"[ ]*:[ ]*"[^\"]*"' | head -1 | cut -d '"' -f4)
    echo "  Place ID 1: $PLACE_ID_1"
else
    echo -e "${RED}[SKIPPED]${NC} Create Place 1: Dependencies (Owner/Amenities) not set."
fi

echo "Scenario48: Successful place creation without amenities"
if [ -n "$PLACE_OWNER_ID" ]; then
    RESPONSE_PLACE_48=$(curl -s -i -X POST "$API_URL/places/" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"Modern Studio\", \"description\": \"Great downtown location\", \"address\": \"456 Elm St\", \"city\": \"Anytown\", \"latitude\": 34.00, \"longitude\": -118.00, \"number_of_rooms\": 1, \"number_of_bathrooms\": 1, \"price_per_night\": 80, \"max_guests\": 2, \"owner_id\": \"$PLACE_OWNER_ID\"}")
    assert_status "$RESPONSE_PLACE_48" "201" "Create Place 2 (Modern Studio)"
    PLACE_ID_2=$(echo "$RESPONSE_PLACE_48" | grep -o '"id"[ ]*:[ ]*"[^\"]*"' | head -1 | cut -d '"' -f4)
    echo "  Place ID 2: $PLACE_ID_2"
else
    echo -e "${RED}[SKIPPED]${NC} Create Place 2: Owner dependency not set."
fi

echo "Scenario49: Create place with missing 'owner_id'"
RESPONSE_PLACE_49=$(curl -s -i -X POST "$API_URL/places/" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"No Owner Place\", \"description\": \"\", \"address\": \"\", \"city\": \"\", \"latitude\": 0, \"longitude\": 0, \"number_of_rooms\": 1, \"number_of_bathrooms\": 1, \"price_per_night\": 50, \"max_guests\": 1}")
assert_status "$RESPONSE_PLACE_49" "400" "Create Place with missing owner_id"

echo "Scenario50: Create place with non-existent 'owner_id'"
RESPONSE_PLACE_50=$(curl -s -i -X POST "$API_URL/places/" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"Bad Owner Place\", \"description\": \"\", \"address\": \"\", \"city\": \"\", \"latitude\": 0, \"longitude\": 0, \"number_of_rooms\": 1, \"number_of_bathrooms\": 1, \"price_per_night\": 50, \"max_guests\": 1, \"owner_id\": \"123e4567-e89b-12d3-a456-000000000000\"}")
assert_status "$RESPONSE_PLACE_50" "400" "Create Place with non-existent owner_id"

echo "Scenario51: Create place with malformed 'owner_id'"
RESPONSE_PLACE_51=$(curl -s -i -X POST "$API_URL/places/" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"Malformed Owner Place\", \"description\": \"\", \"address\": \"\", \"city\": \"\", \"latitude\": 0, \"longitude\": 0, \"number_of_rooms\": 1, \"number_of_bathrooms\": 1, \"price_per_night\": 50, \"max_guests\": 1, \"owner_id\": \"not-a-uuid\"}")
assert_status "$RESPONSE_PLACE_51" "400" "Create Place with malformed owner_id"

echo "Scenario52: Create place with invalid amenity ID"
if [ -n "$PLACE_OWNER_ID" ]; then
    RESPONSE_PLACE_52=$(curl -s -i -X POST "$API_URL/places/" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"Invalid Amenity Place\", \"description\": \"\", \"address\": \"\", \"city\": \"\", \"latitude\": 0, \"longitude\": 0, \"number_of_rooms\": 1, \"number_of_bathrooms\": 1, \"price_per_night\": 50, \"max_guests\": 1, \"owner_id\": \"$PLACE_OWNER_ID\", \"amenities\": [\"not-a-valid-amenity-id\"]}")
    assert_status "$RESPONSE_PLACE_52" "400" "Create Place with invalid amenity ID format"
else
    echo -e "${RED}[SKIPPED]${NC} Create Place with invalid amenity ID: Owner dependency not set."
fi

echo "Scenario53: Create place with non-existent amenity ID"
if [ -n "$PLACE_OWNER_ID" ]; then
    RESPONSE_PLACE_53=$(curl -s -i -X POST "$API_URL/places/" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"Non-existent Amenity Place\", \"description\": \"\", \"address\": \"\", \"city\": \"\", \"latitude\": 0, \"longitude\": 0, \"number_of_rooms\": 1, \"number_of_bathrooms\": 1, \"price_per_night\": 50, \"max_guests\": 1, \"owner_id\": \"$PLACE_OWNER_ID\", \"amenities\": [\"123e4567-e89b-12d3-a456-000000000000\"]}")
    assert_status "$RESPONSE_PLACE_53" "400" "Create Place with non-existent amenity ID"
else
    echo -e "${RED}[SKIPPED]${NC} Create Place with non-existent amenity ID: Owner dependency not set."
fi

echo "Scenario54: Create place with missing required fields (e.g., name)"
if [ -n "$PLACE_OWNER_ID" ]; then
    RESPONSE_PLACE_54=$(curl -s -i -X POST "$API_URL/places/" \
        -H "Content-Type: application/json" \
        -d "{\"description\": \"Missing name\", \"address\": \"\", \"city\": \"\", \"latitude\": 0, \"longitude\": 0, \"number_of_rooms\": 1, \"number_of_bathrooms\": 1, \"price_per_night\": 50, \"max_guests\": 1, \"owner_id\": \"$PLACE_OWNER_ID\"}")
    assert_status "$RESPONSE_PLACE_54" "400" "Create Place with missing 'name' field"
else
    echo -e "${RED}[SKIPPED]${NC} Create Place with missing name: Owner dependency not set."
fi

echo "Scenario55: Create place with invalid data type for a field (e.g., price_per_night as string)"
if [ -n "$PLACE_OWNER_ID" ]; then
    RESPONSE_PLACE_55=$(curl -s -i -X POST "$API_URL/places/" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"Invalid Type Place\", \"description\": \"\", \"address\": \"\", \"city\": \"\", \"latitude\": 0, \"longitude\": 0, \"number_of_rooms\": 1, \"number_of_bathrooms\": 1, \"price_per_night\": \"one hundred\", \"max_guests\": 1, \"owner_id\": \"$PLACE_OWNER_ID\"}")
    assert_status "$RESPONSE_PLACE_55" "400" "Create Place with invalid data type for price_per_night"
else
    echo -e "${RED}[SKIPPED]${NC} Create Place with invalid type: Owner dependency not set."
fi


# --- READ SCENARIOS (GET) ---

echo "Scenario56: Retrieve all places"
RESPONSE_GET_ALL_PLACES56=$(curl -s -i "$API_URL/places/")
assert_status "$RESPONSE_GET_ALL_PLACES56" "200" "Retrieve all places"

echo "Scenario57: Retrieve existing place by ID"
if [ -n "$PLACE_ID_1" ]; then
    RESPONSE_PLACE57=$(curl -s -i "$API_URL/places/$PLACE_ID_1")
    assert_status "$RESPONSE_PLACE57" "200" "Retrieve Place by ID ($PLACE_ID_1)"
else
    echo -e "${RED}[SKIPPED]${NC} Retrieve existing place: PLACE_ID_1 not set."
fi

echo "Scenario58: Attempt to retrieve non-existent place"
RESPONSE_PLACE58=$(curl -s -i "$API_URL/places/123e4567-e89b-12d3-a456-000000000000")
assert_status "$RESPONSE_PLACE58" "404" "Retrieve non-existent place"

echo "Scenario59: Attempt to retrieve place with malformed ID (non-UUID)"
RESPONSE_PLACE59=$(curl -s -i "$API_URL/places/not-a-uuid")
assert_status "$RESPONSE_PLACE59" "400" "Retrieve place with malformed ID"


# --- UPDATE SCENARIOS (PUT /places/<id>) ---

echo "Scenario60: Update an existing place successfully (name and price)"
if [ -n "$PLACE_ID_1" ] && [ -n "$PLACE_OWNER_ID" ]; then
    RESPONSE_PLACE60=$(curl -s -i -X PUT "$API_URL/places/$PLACE_ID_1" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"Super Cozy Apartment\", \"description\": \"A truly lovely place\", \"address\": \"123 Main St\", \"city\": \"Anytown\", \"latitude\": 34.05, \"longitude\": -118.25, \"number_of_rooms\": 2, \"number_of_bathrooms\": 1, \"price_per_night\": 120, \"max_guests\": 4, \"owner_id\": \"$PLACE_OWNER_ID\"}")
    assert_status "$RESPONSE_PLACE60" "200" "Update Place 1 name and price"
else
    echo -e "${RED}[SKIPPED]${NC} Update Place 1: Dependencies not set."
fi

echo "Scenario61: Update place and change owner"
if [ -n "$PLACE_ID_2" ]; then
    # Create a new owner for the update
    RESPONSE_NEW_OWNER61=$(curl -s -i -X POST "$API_URL/users/" \
        -H "Content-Type: application/json" \
        -d "{\"first_name\": \"New\", \"last_name\": \"Owner\", \"email\": \"new.owner@example.com\"}")
    assert_status "$RESPONSE_NEW_OWNER61" "201" "Setup: Create New Owner for update test"
    NEW_OWNER_ID=$(echo "$RESPONSE_NEW_OWNER61" | grep -o '"id"[ ]*:[ ]*"[^\"]*"' | head -1 | cut -d '"' -f4)
    echo "  New Owner ID: $NEW_OWNER_ID"

    if [ -n "$NEW_OWNER_ID" ]; then
        RESPONSE_CHANGE_OWNER61=$(curl -s -i -X PUT "$API_URL/places/$PLACE_ID_2" \
            -H "Content-Type: application/json" \
            -d "{\"name\": \"Modern Studio\", \"description\": \"Updated location\", \"address\": \"456 Elm St\", \"city\": \"Anytown\", \"latitude\": 34.00, \"longitude\": -118.00, \"number_of_rooms\": 1, \"number_of_bathrooms\": 1, \"price_per_night\": 80, \"max_guests\": 2, \"owner_id\": \"$NEW_OWNER_ID\"}")
        assert_status "$RESPONSE_CHANGE_OWNER61" "200" "Update Place 2 and change owner"
    else
        echo -e "${RED}[SKIPPED]${NC} Change Place Owner: New Owner ID not set."
    fi
else
    echo -e "${RED}[SKIPPED]${NC} Change Place Owner: PLACE_ID_2 not set."
fi

echo "Scenario62: Update place with new amenities"
if [ -n "$PLACE_ID_1" ] && [ -n "$PLACE_OWNER_ID" ] && [ -n "$AMENITY_ID_A" ]; then
    # Assume we remove AMENITY_B and add AMENITY_A
    RESPONSE_UPDATE_AMENITIES62=$(curl -s -i -X PUT "$API_URL/places/$PLACE_ID_1" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"Super Cozy Apartment\", \"description\": \"A truly lovely place\", \"address\": \"123 Main St\", \"city\": \"Anytown\", \"latitude\": 34.05, \"longitude\": -118.25, \"number_of_rooms\": 2, \"number_of_bathrooms\": 1, \"price_per_night\": 120, \"max_guests\": 4, \"owner_id\": \"$PLACE_OWNER_ID\", \"amenities\": [\"$AMENITY_ID_A\"]}")
    assert_status "$RESPONSE_UPDATE_AMENITIES62" "200" "Update Place 1 amenities"
else
    echo -e "${RED}[SKIPPED]${NC} Update Place amenities: Dependencies not set."
fi

echo "Scenario63: Attempt to update a non-existent place"
RESPONSE_PLACE63=$(curl -s -i -X PUT "$API_URL/places/123e4567-e89b-12d3-a456-000000000000" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"Ghost Place\", \"description\": \"\", \"address\": \"\", \"city\": \"\", \"latitude\": 0, \"longitude\": 0, \"number_of_rooms\": 1, \"number_of_bathrooms\": 1, \"price_per_night\": 10, \"max_guests\": 1, \"owner_id\": \"$PLACE_OWNER_ID\"}")
assert_status "$RESPONSE_PLACE63" "404" "Update non-existent place"

echo "Scenario64: Attempt to update place with malformed ID"
if [ -n "$PLACE_OWNER_ID" ]; then
    RESPONSE_PLACE64=$(curl -s -i -X PUT "$API_URL/places/invalid-place-uuid" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"Invalid ID Place\", \"description\": \"\", \"address\": \"\", \"city\": \"\", \"latitude\": 0, \"longitude\": 0, \"number_of_rooms\": 1, \"number_of_bathrooms\": 1, \"price_per_night\": 10, \"max_guests\": 1, \"owner_id\": \"$PLACE_OWNER_ID\"}")
    assert_status "$RESPONSE_PLACE64" "400" "Update place with malformed ID"
else
    echo -e "${RED}[SKIPPED]${NC} Update place with malformed ID: Owner dependency not set."
fi

echo "Scenario65: Update place with non-existent owner_id"
if [ -n "$PLACE_ID_1" ]; then
    RESPONSE_PLACE65=$(curl -s -i -X PUT "$API_URL/places/$PLACE_ID_1" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"Cozy Apartment\", \"description\": \"A lovely place\", \"address\": \"123 Main St\", \"city\": \"Anytown\", \"latitude\": 34.05, \"longitude\": -118.25, \"number_of_rooms\": 2, \"number_of_bathrooms\": 1, \"price_per_night\": 100, \"max_guests\": 4, \"owner_id\": \"123e4567-e89b-12d3-a456-000000000001\"}")
    assert_status "$RESPONSE_PLACE65" "400" "Update Place with non-existent owner_id"
else
    echo -e "${RED}[SKIPPED]${NC} Update Place with non-existent owner: PLACE_ID_1 not set."
fi


# --- DELETE SCENARIOS (DELETE /places/<id>) ---

echo "Scenario66: Delete an existing place"
if [ -n "$PLACE_ID_2" ]; then
    RESPONSE_PLACE66=$(curl -s -i -X DELETE "$API_URL/places/$PLACE_ID_2")
    assert_status "$RESPONSE_PLACE66" "200" "Delete Place ($PLACE_ID_2)"
else
    echo -e "${RED}[SKIPPED]${NC} Delete Place: PLACE_ID_2 not set."
fi

echo "Scenario67: Attempt to retrieve the deleted place"
if [ -n "$PLACE_ID_2" ]; then
    RESPONSE_GET_DELETED_PLACE67=$(curl -s -i "$API_URL/places/$PLACE_ID_2")
    assert_status "$RESPONSE_GET_DELETED_PLACE67" "404" "Retrieve deleted Place (expected 404)"
else
    echo -e "${RED}[SKIPPED]${NC} Retrieve deleted Place: PLACE_ID_2 not set."
fi

echo "Scenario68: Attempt to delete a non-existent place"
RESPONSE_DELETE_NON_EXISTENT_PLACE_2=$(curl -s -i -X DELETE "$API_URL/places/123e4567-e89b-12d3-a456-000000000002")
assert_status "$RESPONSE_DELETE_NON_EXISTENT_PLACE_2" "404" "Delete non-existent place"

echo "Scenario69: Attempt to delete place with malformed ID"
RESPONSE_DELETE_MALFORMED_PLACE_ID=$(curl -s -i -X DELETE "$API_URL/places/invalid-uuid-for-delete")
assert_status "$RESPONSE_DELETE_MALFORMED_PLACE_ID" "400" "Delete place with malformed ID"

echo "--- All Places API Tests Completed ---"

echo "--- Starting Reviews API Tests ---"

# Create a User and a Place for Review creation
RESPONSE_REVIEW_USER70=$(curl -s -i -X POST "$API_URL/users/" \
    -H "Content-Type: application/json" \
    -d "{\"first_name\": \"Reviewer\", \"last_name\": \"User\", \"email\": \"reviewer@example.com\"}")
assert_status "$RESPONSE_REVIEW_USER70" "201" "Setup: Create Reviewer User"
REVIEW_USER_ID=$(echo "$RESPONSE_REVIEW_USER70" | grep -o '"id"[ ]*:[ ]*"[^\"]*"' | head -1 | cut -d '"' -f4)
echo "  Reviewer User ID: $REVIEW_USER_ID"

RESPONSE_PLACE_FOR_REVIEW71=$(curl -s -i -X POST "$API_URL/places/" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"Reviewable Place\", \"description\": \"A place to leave reviews\", \"address\": \"789 Review Lane\", \"city\": \"Reviewville\", \"latitude\": 40.0, \"longitude\": -75.0, \"number_of_rooms\": 3, \"number_of_bathrooms\": 2, \"price_per_night\": 150, \"max_guests\": 6, \"owner_id\": \"$REVIEW_USER_ID\"}")
assert_status "$RESPONSE_PLACE_FOR_REVIEW71" "201" "Setup: Create Place for Review"
REVIEW_PLACE_ID=$(echo "$RESPONSE_PLACE_FOR_REVIEW71" | grep -o '"id"[ ]*:[ ]*"[^\"]*"' | head -1 | cut -d '"' -f4)
echo "  Review Place ID: $REVIEW_PLACE_ID"


# --- CREATE SCENARIOS (POST /places/<place_id>/reviews/) ---

echo "Scenario72: Successful review creation"
if [ -n "$REVIEW_USER_ID" ] && [ -n "$REVIEW_PLACE_ID" ]; then
    RESPONSE_REVIEW_72=$(curl -s -i -X POST "$API_URL/places/$REVIEW_PLACE_ID/reviews/" \
        -H "Content-Type: application/json" \
        -d "{\"user_id\": \"$REVIEW_USER_ID\", \"rating\": 5, \"comment\": \"Excellent place, highly recommend!\"}")
    assert_status "$RESPONSE_REVIEW_72" "201" "Create Review 1 for Place"
    REVIEW_ID_1=$(echo "$RESPONSE_REVIEW_72" | grep -o '"id"[ ]*:[ ]*"[^\"]*"' | head -1 | cut -d '"' -f4)
    echo "  Review ID 1: $REVIEW_ID_1"
else
    echo -e "${RED}[SKIPPED]${NC} Create Review 1: Dependencies (User/Place) not set."
fi

echo "Scenario73: Create review with missing 'user_id'"
if [ -n "$REVIEW_PLACE_ID" ]; then
    RESPONSE_REVIEW_73=$(curl -s -i -X POST "$API_URL/places/$REVIEW_PLACE_ID/reviews/" \
        -H "Content-Type: application/json" \
        -d "{\"rating\": 4, \"comment\": \"Good place.\"}")
    assert_status "$RESPONSE_REVIEW_73" "400" "Create Review with missing user_id"
else
    echo -e "${RED}[SKIPPED]${NC} Create Review with missing user_id: Place dependency not set."
fi

echo "Scenario74: Create review with non-existent 'user_id'"
if [ -n "$REVIEW_PLACE_ID" ]; then
    RESPONSE_REVIEW_74=$(curl -s -i -X POST "$API_URL/places/$REVIEW_PLACE_ID/reviews/" \
        -H "Content-Type: application/json" \
        -d "{\"user_id\": \"123e4567-e89b-12d3-a456-000000000000\", \"rating\": 3, \"comment\": \"Non-existent user review.\"}")
    assert_status "$RESPONSE_REVIEW_74" "400" "Create Review with non-existent user_id"
else
    echo -e "${RED}[SKIPPED]${NC} Create Review with non-existent user_id: Place dependency not set."
fi

echo "Scenario75: Create review with malformed 'user_id'"
if [ -n "$REVIEW_PLACE_ID" ]; then
    RESPONSE_REVIEW_75=$(curl -s -i -X POST "$API_URL/places/$REVIEW_PLACE_ID/reviews/" \
        -H "Content-Type: application/json" \
        -d "{\"user_id\": \"not-a-uuid\", \"rating\": 2, \"comment\": \"Malformed user ID review.\"}")
    assert_status "$RESPONSE_REVIEW_75" "400" "Create Review with malformed user_id"
else
    echo -e "${RED}[SKIPPED]${NC} Create Review with malformed user_id: Place dependency not set."
fi

echo "Scenario76: Create review with missing 'rating'"
if [ -n "$REVIEW_USER_ID" ] && [ -n "$REVIEW_PLACE_ID" ]; then
    RESPONSE_REVIEW_76=$(curl -s -i -X POST "$API_URL/places/$REVIEW_PLACE_ID/reviews/" \
        -H "Content-Type: application/json" \
        -d "{\"user_id\": \"$REVIEW_USER_ID\", \"comment\": \"Missing rating.\"}")
    assert_status "$RESPONSE_REVIEW_76" "400" "Create Review with missing rating"
else
    echo -e "${RED}[SKIPPED]${NC} Create Review with missing rating: Dependencies not set."
fi

echo "Scenario77: Create review with invalid 'rating' (out of range, e.g., 0)"
if [ -n "$REVIEW_USER_ID" ] && [ -n "$REVIEW_PLACE_ID" ]; then
    RESPONSE_REVIEW_77=$(curl -s -i -X POST "$API_URL/places/$REVIEW_PLACE_ID/reviews/" \
        -H "Content-Type: application/json" \
        -d "{\"user_id\": \"$REVIEW_USER_ID\", \"rating\": 0, \"comment\": \"Rating too low.\"}")
    assert_status "$RESPONSE_REVIEW_77" "400" "Create Review with invalid rating (0)"
else
    echo -e "${RED}[SKIPPED]${NC} Create Review with invalid rating (0): Dependencies not set."
fi

echo "Scenario78: Create review with invalid 'rating' (out of range, e.g., 6)"
if [ -n "$REVIEW_USER_ID" ] && [ -n "$REVIEW_PLACE_ID" ]; then
    RESPONSE_REVIEW_78=$(curl -s -i -X POST "$API_URL/places/$REVIEW_PLACE_ID/reviews/" \
        -H "Content-Type: application/json" \
        -d "{\"user_id\": \"$REVIEW_USER_ID\", \"rating\": 6, \"comment\": \"Rating too high.\"}")
    assert_status "$RESPONSE_REVIEW_78" "400" "Create Review with invalid rating (6)"
else
    echo -e "${RED}[SKIPPED]${NC} Create Review with invalid rating (6): Dependencies not set."
fi

echo "Scenario79: Create review for non-existent place"
if [ -n "$REVIEW_USER_ID" ]; then
    RESPONSE_REVIEW_79=$(curl -s -i -X POST "$API_URL/places/123e4567-e89b-12d3-a456-000000000000/reviews/" \
        -H "Content-Type: application/json" \
        -d "{\"user_id\": \"$REVIEW_USER_ID\", \"rating\": 5, \"comment\": \"Review for a ghost place.\"}")
    assert_status "$RESPONSE_REVIEW_79" "404" "Create Review for non-existent place"
else
    echo -e "${RED}[SKIPPED]${NC} Create Review for non-existent place: User dependency not set."
fi

echo "Scenario80: Create review for malformed place ID"
if [ -n "$REVIEW_USER_ID" ]; then
    RESPONSE_REVIEW_80=$(curl -s -i -X POST "$API_URL/places/not-a-place-uuid/reviews/" \
        -H "Content-Type: application/json" \
        -d "{\"user_id\": \"$REVIEW_USER_ID\", \"rating\": 5, \"comment\": \"Review for a malformed place ID.\"}")
    assert_status "$RESPONSE_REVIEW_80" "400" "Create Review for malformed place ID"
else
    echo -e "${RED}[SKIPPED]${NC} Create Review for malformed place ID: User dependency not set."
fi


# --- READ SCENARIOS (GET) ---

echo "Scenario81: Retrieve all reviews for a place"
if [ -n "$REVIEW_PLACE_ID" ]; then
    RESPONSE_GET_ALL_REVIEWS_FOR_PLACE81=$(curl -s -i "$API_URL/places/$REVIEW_PLACE_ID/reviews/")
    assert_status "$RESPONSE_GET_ALL_REVIEWS_FOR_PLACE81" "200" "Retrieve all reviews for a place ($REVIEW_PLACE_ID)"
else
    echo -e "${RED}[SKIPPED]${NC} Retrieve all reviews for a place: Place dependency not set."
fi

echo "Scenario82: Retrieve a specific review by its ID"
if [ -n "$REVIEW_ID_1" ]; then
    RESPONSE_REVIEW_82=$(curl -s -i "$API_URL/reviews/$REVIEW_ID_1")
    assert_status "$RESPONSE_REVIEW_82" "200" "Retrieve Review by ID ($REVIEW_ID_1)"
else
    echo -e "${RED}[SKIPPED]${NC} Retrieve Review by ID: REVIEW_ID_1 not set."
fi

echo "Scenario83: Attempt to retrieve non-existent review by ID"
RESPONSE_REVIEW_83=$(curl -s -i "$API_URL/reviews/123e4567-e89b-12d3-a456-000000000000")
assert_status "$RESPONSE_REVIEW_83" "404" "Retrieve non-existent Review"

echo "Scenario84: Attempt to retrieve review with malformed ID"
RESPONSE_REVIEW_84=$(curl -s -i "$API_URL/reviews/not-a-review-uuid")
assert_status "$RESPONSE_REVIEW_84" "400" "Retrieve Review with malformed ID"


# --- UPDATE SCENARIOS (PUT /reviews/<review_id>) ---

echo "Scenario85: Update an existing review successfully (comment and rating)"
if [ -n "$REVIEW_ID_1" ] && [ -n "$REVIEW_USER_ID" ] && [ -n "$REVIEW_PLACE_ID" ]; then
    RESPONSE_REVIEW_85=$(curl -s -i -X PUT "$API_URL/reviews/$REVIEW_ID_1" \
        -H "Content-Type: application/json" \
        -d "{\"user_id\": \"$REVIEW_USER_ID\", \"place_id\": \"$REVIEW_PLACE_ID\", \"rating\": 4, \"comment\": \"Updated comment: Still good, but not perfect.\"}")
    assert_status "$RESPONSE_REVIEW_85" "200" "Update Review 1 comment and rating"
else
    echo -e "${RED}[SKIPPED]${NC} Update Review 1: Dependencies not set."
fi

echo "Scenario86: Attempt to update review with invalid 'rating' type"
if [ -n "$REVIEW_ID_1" ] && [ -n "$REVIEW_USER_ID" ] && [ -n "$REVIEW_PLACE_ID" ]; then
    RESPONSE_REVIEW_86=$(curl -s -i -X PUT "$API_URL/reviews/$REVIEW_ID_1" \
        -H "Content-Type: application/json" \
        -d "{\"user_id\": \"$REVIEW_USER_ID\", \"place_id\": \"$REVIEW_PLACE_ID\", \"rating\": \"four\", \"comment\": \"Invalid rating type.\"}")
    assert_status "$RESPONSE_REVIEW_86" "400" "Update Review with invalid rating type"
else
    echo -e "${RED}[SKIPPED]${NC} Update Review with invalid rating type: Dependencies not set."
fi

echo "Scenario87: Attempt to update non-existent review"
if [ -n "$REVIEW_USER_ID" ] && [ -n "$REVIEW_PLACE_ID" ]; then
    RESPONSE_REVIEW_87=$(curl -s -i -X PUT "$API_URL/reviews/123e4567-e89b-12d3-a456-000000000000" \
        -H "Content-Type: application/json" \
        -d "{\"user_id\": \"$REVIEW_USER_ID\", \"place_id\": \"$REVIEW_PLACE_ID\", \"rating\": 1, \"comment\": \"Update for a ghost review.\"}")
    assert_status "$RESPONSE_REVIEW_87" "404" "Update non-existent Review"
else
    echo -e "${RED}[SKIPPED]${NC} Update non-existent Review: Dependencies not set."
fi

echo "Scenario88: Attempt to update review with malformed ID"
if [ -n "$REVIEW_USER_ID" ] && [ -n "$REVIEW_PLACE_ID" ]; then
    RESPONSE_REVIEW_88=$(curl -s -i -X PUT "$API_URL/reviews/invalid-review-uuid" \
        -H "Content-Type: application/json" \
        -d "{\"user_id\": \"$REVIEW_USER_ID\", \"place_id\": \"$REVIEW_PLACE_ID\", \"rating\": 3, \"comment\": \"Update for malformed ID.\"}")
    assert_status "$RESPONSE_REVIEW_88" "400" "Update Review with malformed ID"
else
    echo -e "${RED}[SKIPPED]${NC} Update Review with malformed ID: Dependencies not set."
fi

echo "Scenario89: Attempt to update review to a non-existent user_id"
if [ -n "$REVIEW_ID_1" ] && [ -n "$REVIEW_PLACE_ID" ]; then
    RESPONSE_REVIEW_89=$(curl -s -i -X PUT "$API_URL/reviews/$REVIEW_ID_1" \
        -H "Content-Type: application/json" \
        -d "{\"user_id\": \"123e4567-e89b-12d3-a456-000000000001\", \"place_id\": \"$REVIEW_PLACE_ID\", \"rating\": 5, \"comment\": \"Update to non-existent user.\"}")
    assert_status "$RESPONSE_REVIEW_89" "400" "Update Review to non-existent user_id"
else
    echo -e "${RED}[SKIPPED]${NC} Update Review to non-existent user_id: Dependencies not set."
fi

echo "Scenario90: Attempt to update review to a non-existent place_id"
if [ -n "$REVIEW_ID_1" ] && [ -n "$REVIEW_USER_ID" ]; then
    RESPONSE_REVIEW_90=$(curl -s -i -X PUT "$API_URL/reviews/$REVIEW_ID_1" \
        -H "Content-Type: application/json" \
        -d "{\"user_id\": \"$REVIEW_USER_ID\", \"place_id\": \"123e4567-e89b-12d3-a456-000000000001\", \"rating\": 5, \"comment\": \"Update to non-existent place.\"}")
    assert_status "$RESPONSE_REVIEW_90" "400" "Update Review to non-existent place_id"
else
    echo -e "${RED}[SKIPPED]${NC} Update Review to non-existent place_id: Dependencies not set."
fi


# --- DELETE SCENARIOS (DELETE /reviews/<review_id>) ---

echo "Scenario91: Delete an existing review"
if [ -n "$REVIEW_ID_1" ]; then
    RESPONSE_REVIEW_91=$(curl -s -i -X DELETE "$API_URL/reviews/$REVIEW_ID_1")
    assert_status "$RESPONSE_REVIEW_91" "200" "Delete Review ($REVIEW_ID_1)"
else
    echo -e "${RED}[SKIPPED]${NC} Delete Review: REVIEW_ID_1 not set."
fi

echo "Scenario92: Attempt to retrieve the deleted review"
if [ -n "$REVIEW_ID_1" ]; then
    RESPONSE_GET_DELETED_REVIEW92=$(curl -s -i "$API_URL/reviews/$REVIEW_ID_1")
    assert_status "$RESPONSE_GET_DELETED_REVIEW92" "404" "Retrieve deleted Review (expected 404)"
else
    echo -e "${RED}[SKIPPED]${NC} Retrieve deleted Review: REVIEW_ID_1 not set."
fi

echo "Scenario93: Attempt to delete a non-existent review"
RESPONSE_DELETE_NON_EXISTENT_REVIEW_93=$(curl -s -i -X DELETE "$API_URL/reviews/123e4567-e89b-12d3-a456-000000000002")
assert_status "$RESPONSE_DELETE_NON_EXISTENT_REVIEW_93" "404" "Delete non-existent Review"

echo "Scenario94: Attempt to delete review with malformed ID"
RESPONSE_DELETE_MALFORMED_REVIEW_ID94=$(curl -s -i -X DELETE "$API_URL/reviews/invalid-uuid-for-delete")
assert_status "$RESPONSE_DELETE_MALFORMED_REVIEW_ID94" "400" "Delete Review with malformed ID"

echo "--- All Reviews API Tests Completed ---"

echo "--- Tests Complete ---"
