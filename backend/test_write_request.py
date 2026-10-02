from app.write_request import extract_write_request


print("STEP 10G - WRITE REQUEST EXTRACTION")
print("-----------------------------------")


print("\nTEST 1: VALID HR PORTAL REQUEST")

result = extract_write_request(
    "Provision HR_PORTAL access for EMP1001"
)

print(result)

assert result["employee_id"] == "EMP1001"
assert result["requested_system"] == "HR_PORTAL"

print("PASS")


print("\nTEST 2: VALID PAYROLL REQUEST")

result = extract_write_request(
    "Create PAYROLL account for employee EMP1002"
)

print(result)

assert result["employee_id"] == "EMP1002"
assert result["requested_system"] == "PAYROLL"

print("PASS")


print("\nTEST 3: VALID BENEFITS REQUEST")

result = extract_write_request(
    "Provision BENEFITS access for EMP1234"
)

print(result)

assert result["employee_id"] == "EMP1234"
assert result["requested_system"] == "BENEFITS"

print("PASS")


print("\nTEST 4: MISSING EMPLOYEE ID")

result = extract_write_request(
    "Provision HR_PORTAL access"
)

print(result)

assert result["employee_id"] == ""
assert result["requested_system"] == "HR_PORTAL"

print("PASS")


print("\nTEST 5: MISSING SYSTEM")

result = extract_write_request(
    "Provision access for EMP1001"
)

print(result)

assert result["employee_id"] == "EMP1001"
assert result["requested_system"] == ""

print("PASS")


print("\nTEST 6: UNSUPPORTED SYSTEM")

result = extract_write_request(
    "Provision EMAIL access for EMP1001"
)

print(result)

assert result["employee_id"] == "EMP1001"
assert result["requested_system"] == ""

print("PASS")


print("\nTEST 7: EMPTY REQUEST")

result = extract_write_request("")

print(result)

assert result["employee_id"] == ""
assert result["requested_system"] == ""

print("PASS")


print()
print("All Step 10G write-request tests passed.")