from app.graph import graph


test_questions = [
    "What documents do I need to submit for onboarding?",
    "I cannot access the HR portal.",
    "How do I enroll in employee health benefits?",
    "When will I receive my first salary?",
]


for question in test_questions:
    print("\n" + "=" * 70)
    print(f"QUESTION: {question}")

    result = graph.invoke({
        "question": question
    })

    print(f"CATEGORY: {result['category']}")
    print(f"RESPONSE: {result['response']}")