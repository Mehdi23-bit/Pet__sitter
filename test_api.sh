#!/bin/bash

# =========================================
# Pet Sitter API — Full End-to-End Test
# =========================================
# Usage: ./test_api.sh
# Requires: curl, jq (sudo apt install jq)

BASE="http://localhost:3001/api"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

step() {
    echo -e "\n${YELLOW}==> $1${NC}"
}

check() {
    if [ "$1" -ge 200 ] && [ "$1" -lt 300 ]; then
        echo -e "${GREEN}OK ($1)${NC}"
    else
        echo -e "${RED}FAILED ($1)${NC}"
    fi
}



# -----------------------------------------
step "1. Register OWNER"
RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE/auth/register/" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$OWNER_EMAIL\",\"username\":\"owner_test\",\"password\":\"$PASSWORD\",\"role\":\"owner\",\"phone\":\"0600000001\",\"city\":\"Agadir\"}")
CODE=$(echo "$RESP" | tail -n1)
BODY=$(echo "$RESP" | sed '$d')
echo "$BODY" | jq .
check "$CODE"

# -----------------------------------------
step "2. Register SITTER"
RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE/auth/register/" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$SITTER_EMAIL\",\"username\":\"sitter_test\",\"password\":\"$PASSWORD\",\"role\":\"sitter\",\"phone\":\"0600000002\",\"city\":\"Agadir\",\"cin\": \"JM10299\"}")
CODE=$(echo "$RESP" | tail -n1)
BODY=$(echo "$RESP" | sed '$d')
echo "$BODY" | jq .
check "$CODE"

# -----------------------------------------
step "3. Check your server logs / console.email backend for OTP codes"
echo "If EMAIL_BACKEND is console, check your Django runserver terminal for the OTP codes now."
read -p "Enter OWNER OTP: " OWNER_OTP
read -p "Enter SITTER OTP: " SITTER_OTP

# -----------------------------------------
step "4. Verify OWNER OTP"
RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE/otp/verify/" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$OWNER_EMAIL\",\"otp\":\"$OWNER_OTP\"}")
CODE=$(echo "$RESP" | tail -n1)
echo "$RESP" | sed '$d' | jq .
check "$CODE"

step "5. Verify SITTER OTP"
RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE/otp/verify/" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$SITTER_EMAIL\",\"otp\":\"$SITTER_OTP\"}")
CODE=$(echo "$RESP" | tail -n1)
echo "$RESP" | sed '$d' | jq .
check "$CODE"

# -----------------------------------------
step "6. Login OWNER"
RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE/auth/login/" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$OWNER_EMAIL\",\"password\":\"$PASSWORD\"}")
CODE=$(echo "$RESP" | tail -n1)
BODY=$(echo "$RESP" | sed '$d')
echo "$BODY" | jq .
check "$CODE"
OWNER_TOKEN=$(echo "$BODY" | jq -r .access)

step "7. Login SITTER"
RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE/auth/login/" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$SITTER_EMAIL\",\"password\":\"$PASSWORD\"}")
CODE=$(echo "$RESP" | tail -n1)
BODY=$(echo "$RESP" | sed '$d')
echo "$BODY" | jq .
check "$CODE"
SITTER_TOKEN=$(echo "$BODY" | jq -r .access)

echo -e "\n${YELLOW}OWNER_TOKEN=${OWNER_TOKEN:0:20}...${NC}"
echo -e "${YELLOW}SITTER_TOKEN=${SITTER_TOKEN:0:20}...${NC}"

# -----------------------------------------
step "8. OWNER creates a pet"
RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE/pet/" \
  -H "Authorization: Bearer $OWNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Rex","species":"dog","breed":"Husky","age":3}')
CODE=$(echo "$RESP" | tail -n1)
BODY=$(echo "$RESP" | sed '$d')
echo "$BODY" | jq .
check "$CODE"
PET_ID=$(echo "$BODY" | jq -r .id)

# -----------------------------------------
step "9. Get SITTER user id (via /me/)"
RESP=$(curl -s -w "\n%{http_code}" -X GET "$BASE/me/" \
  -H "Authorization: Bearer $SITTER_TOKEN")
CODE=$(echo "$RESP" | tail -n1)
BODY=$(echo "$RESP" | sed '$d')
echo "$BODY" | jq .
check "$CODE"
SITTER_ID=$(echo "$BODY" | jq -r .id)

# -----------------------------------------
step "10. Search sitters (public)"
RESP=$(curl -s -w "\n%{http_code}" -X GET "$BASE/sitters/?city=Agadir")
CODE=$(echo "$RESP" | tail -n1)
echo "$RESP" | sed '$d' | jq .
check "$CODE"

# -----------------------------------------
step "11. OWNER sends contact request to SITTER"
RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE/contact/" \
  -H "Authorization: Bearer $OWNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"sitter\":$SITTER_ID,\"pets\":[$PET_ID],\"message\":\"Need weekend care\",\"start_date\":\"2026-07-10\",\"end_date\":\"2026-07-12\"}")
CODE=$(echo "$RESP" | tail -n1)
BODY=$(echo "$RESP" | sed '$d')
echo "$BODY" | jq .
check "$CODE"
REQUEST_ID=$(echo "$BODY" | jq -r .id)

# -----------------------------------------
step "12. SITTER accepts the request"
RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE/contact/change_status/" \
  -H "Authorization: Bearer $SITTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"request_id\":$REQUEST_ID,\"status\":\"accepted\"}")
CODE=$(echo "$RESP" | tail -n1)
echo "$RESP" | sed '$d' | jq .
check "$CODE"

# -----------------------------------------
step "13. OWNER sends a message"
RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE/contact/message/$REQUEST_ID/" \
  -H "Authorization: Bearer $OWNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Hi! Are you free this weekend?"}')
CODE=$(echo "$RESP" | tail -n1)
echo "$RESP" | sed '$d' | jq .
check "$CODE"

# -----------------------------------------
step "14. SITTER replies"
RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE/contact/message/$REQUEST_ID/" \
  -H "Authorization: Bearer $SITTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Yes! What time works for you?"}')
CODE=$(echo "$RESP" | tail -n1)
echo "$RESP" | sed '$d' | jq .
check "$CODE"

# -----------------------------------------
step "15. OWNER lists messages"
RESP=$(curl -s -w "\n%{http_code}" -X GET "$BASE/contact/message/$REQUEST_ID/" \
  -H "Authorization: Bearer $OWNER_TOKEN")
CODE=$(echo "$RESP" | tail -n1)
echo "$RESP" | sed '$d' | jq .
check "$CODE"

# -----------------------------------------
step "16. OWNER leaves a review"
RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE/contact/review/$REQUEST_ID/" \
  -H "Authorization: Bearer $OWNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"request\":$REQUEST_ID,\"rating\":5,\"comment\":\"Great sitter!\"}")
CODE=$(echo "$RESP" | tail -n1)
echo "$RESP" | sed '$d' | jq .
check "$CODE"

# -----------------------------------------
step "17. Check sitter rating updated (search again)"
RESP=$(curl -s -w "\n%{http_code}" -X GET "$BASE/sitters/?city=Agadir")
CODE=$(echo "$RESP" | tail -n1)
echo "$RESP" | sed '$d' | jq .
check "$CODE"

echo -e "\n${GREEN}=== TEST FLOW COMPLETE ===${NC}"