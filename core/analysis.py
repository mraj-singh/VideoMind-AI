from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate

from core.llm import get_llm


class AIReport(BaseModel):
    """
    Structured AI report returned by the LLM.
    """

    title: str = Field(
        description="A concise title of maximum 8 words."
    )

    summary: str = Field(
        description="Professional markdown report."
    )


SYSTEM_PROMPT = """
You are VideoMind AI.

You are an expert AI analyst capable of understanding
meetings, technical videos, lectures, podcasts,
interviews, tutorials and educational content.

Generate a professional report from the transcript.

Guidelines:

1. Title
- Maximum 8 words.
- Clear and descriptive.

2. Summary
Return valid Markdown using this structure.

# 📌 Executive Summary

A concise overview (4–6 lines).

---

## 🎯 Main Topics

Bullet list.

---

## 🧠 Key Takeaways

Bullet list.

---

## 💡 Important Insights

Explain the most valuable ideas.

---

## ✅ Action Items

Include ONLY if applicable.

---

## 📍 Decisions

Include ONLY if applicable.

---

## ❓ Follow-ups

Include ONLY if applicable.

---

## 🎓 Final Thoughts

2–4 line conclusion.

Never invent facts.
Only use information present in the transcript.
"""


def analyze_transcript(transcript: str) -> dict:
    """
    Generate a structured AI report from the transcript.
    """

    llm = get_llm().with_structured_output(AIReport)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "{transcript}"),
        ]
    )

    chain = prompt | llm

    report = chain.invoke(
        {
            # Limit prompt size for long videos.
            "transcript": transcript[:10000],
        }
    )

    return {
        "title": report.title.strip(),
        "summary": report.summary.strip(),
    }