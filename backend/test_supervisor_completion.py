from app.supervisor import supervisor_route


print("STEP 10D - SUPERVISOR COMPLETION ROUTING")
print("------------------------------------------")


print("\nTEST 1: NORMAL REQUEST ROUTES TO SPECIALIST")

state = {
    "category": "ACCESS",
    "delegation_count": 0,
    "specialists_completed": False,
}

assert supervisor_route(state) == "ACCESS"

print("PASS")


print("\nTEST 2: COMPLETED SPECIALISTS ROUTE TO FINISH")

state = {
    "category": "ACCESS",
    "delegation_count": 1,
    "specialists_completed": True,
}

assert supervisor_route(state) == "FINISH"

print("PASS")


print("\nTEST 3: COMPLETION OVERRIDES CATEGORY")

state = {
    "category": "PAYROLL",
    "delegation_count": 0,
    "specialists_completed": True,
}

assert supervisor_route(state) == "FINISH"

print("PASS")


print("\nTEST 4: MAX DELEGATIONS STILL FINISHES")

state = {
    "category": "BENEFITS",
    "delegation_count": 3,
    "specialists_completed": False,
}

assert supervisor_route(state) == "FINISH"

print("PASS")


print()
print("All Step 10D supervisor completion tests passed.")