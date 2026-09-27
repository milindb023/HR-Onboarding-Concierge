from app.tools.hr_tools import (
    lookup_employee,
    search_hr_policy,
)


print("EMPLOYEE LOOKUP")
print(lookup_employee.invoke({
    "employee_id": "EMP1001"
}))

print("\nHR POLICY SEARCH")
print(search_hr_policy.invoke({
    "topic": "benefits_enrollment"
}))