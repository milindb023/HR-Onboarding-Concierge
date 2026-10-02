from app.severity import can_provision


print("STEP 10B - SEVERITY GATING")
print("---------------------------")


print("\nTEST 1: LOW SEVERITY IS ALLOWED")

assert can_provision("LOW") is True

print("PASS")


print("\nTEST 2: MEDIUM SEVERITY IS ALLOWED")

assert can_provision("MEDIUM") is True

print("PASS")


print("\nTEST 3: HIGH SEVERITY IS BLOCKED")

assert can_provision("HIGH") is False

print("PASS")


print("\nTEST 4: CRITICAL SEVERITY IS BLOCKED")

assert can_provision("CRITICAL") is False

print("PASS")


print("\nTEST 5: LOWERCASE INPUT IS NORMALIZED")

assert can_provision("low") is True
assert can_provision("medium") is True
assert can_provision("high") is False

print("PASS")


print("\nTEST 6: UNKNOWN SEVERITY IS BLOCKED")

assert can_provision("UNKNOWN") is False
assert can_provision("") is False

print("PASS")


print()
print("All Step 10B severity tests passed.")