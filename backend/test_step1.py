from app.graph import graph


test_questions = [
    "What documents do I need to submit for onboarding?",
    "I cannot access the HR portal.",
    "How do I enroll in employee health benefits?",
    "When will I receive my first salary?",
]


for index, question in enumerate(test_questions, start=1):
    print("\n" + "=" * 70)
    print(f"TEST {index}")
    print(f"QUESTION: {question}")

    thread_id = f"step1-test-{index}"

    result = graph.invoke(
        {
            "question": question
        },
        config={
            "configurable": {
                "thread_id": thread_id
            }
        },
    )

    print(f"THREAD ID: {thread_id}")
    print(f"CATEGORY: {result['category']}")
    print(f"RESPONSE: {result['response']}")