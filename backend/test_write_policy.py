from app.write_policy import determine_severity


print("STEP 10G - WRITE POLICY")
print("-----------------------")


assert determine_severity("What documents do I need?") == "LOW"
print("TEST 1: LOW severity - PASS")


assert determine_severity(
    "Please provision my HR portal account"
) == "MEDIUM"
print("TEST 2: MEDIUM severity - PASS")


assert determine_severity(
    "I am locked out of the HR portal"
) == "HIGH"
print("TEST 3: HIGH severity - PASS")


assert determine_severity(
    "There has been a security breach"
) == "CRITICAL"
print("TEST 4: CRITICAL severity - PASS")

assert determine_severity(
    "What documents do I need for onboarding?"
) == "LOW"
print("TEST 5: NORMAL ONBOARDING QUESTION REMAINS LOW - PASS")

print()
print("All Step 10G write-policy tests passed.")