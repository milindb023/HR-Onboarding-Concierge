from app.write_request_node import write_request_node


print("STEP 10G - WRITE REQUEST NODE")
print("-----------------------------")


print("\nTEST 1: VALID REQUEST")

result = write_request_node(
    {
        "question": "Provision HR_PORTAL access for EMP1001"
    }
)

print(result)

assert result["employee_id"] == "EMP1001"
assert result["requested_system"] == "HR_PORTAL"
assert result["write_request_valid"] is True

print("PASS")


print("\nTEST 2: MISSING EMPLOYEE")

result = write_request_node(
    {
        "question": "Provision HR_PORTAL access"
    }
)

print(result)

assert result["employee_id"] == ""
assert result["requested_system"] == "HR_PORTAL"
assert result["write_request_valid"] is False

print("PASS")


print("\nTEST 3: MISSING SYSTEM")

result = write_request_node(
    {
        "question": "Provision access for EMP1001"
    }
)

print(result)

assert result["employee_id"] == "EMP1001"
assert result["requested_system"] == ""
assert result["write_request_valid"] is False

print("PASS")


print("\nTEST 4: UNSUPPORTED SYSTEM")

result = write_request_node(
    {
        "question": "Provision EMAIL access for EMP1001"
    }
)

print(result)

assert result["employee_id"] == "EMP1001"
assert result["requested_system"] == ""
assert result["write_request_valid"] is False

print("PASS")


print()
print("All Step 10G write-request-node tests passed.")