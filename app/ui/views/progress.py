"""Progress view — activity metrics, topic mastery, weak areas."""

import streamlit as st

from app.ui.components import hero, spacer, stat

from app.progress import (
    get_progress_summary,
    get_topic_mastery,
    get_weak_topics,
    get_study_streak,
    get_recommendations,
)



def render():
    progress_summary = get_progress_summary()
    topic_mastery = get_topic_mastery()
    weak_topics = get_weak_topics()
    study_streak = get_study_streak()
    recommendations = get_recommendations()
    hero(
        eyebrow="Analytics",
        title="See what's solid and what still",
        highlight="needs work.",
        subtitle="Mastery is derived from quiz scores, revisits and the topics you ask about most.",
    )
    spacer(24)

    cols = st.columns(4)
    metrics = [
        (
           "Topics studied",
            str(progress_summary.get("topics_studied", 0)),
            "From your learning activity",
        ),
        (
           "Quizzes taken",
            str(progress_summary.get("quizzes_taken", 0)),
           "Completed attempts",
       ),
       (
           "Average score",
           f"{progress_summary.get('average_score', 0)}%",
           "Across completed quizzes",
        ),
        (
           "Study streak",
           f"{study_streak} days",
           "Keep going 🔥",
        ),
    ]
    for i, (col, m) in enumerate(zip(cols, metrics), start=1):
        with col:
            stat(m[0], m[1], m[2], delay=i)

    spacer(30)
    st.subheader("📚 Topic mastery")

    if topic_mastery:

     for topic, data in topic_mastery.items():

        score = data.get("mastery", 0)
        label = data.get("level", "Weak")

        st.markdown(
            f"<div style='display:flex;justify-content:space-between'>"
            f"<b>{topic}</b>"
            f"<span style='color:var(--muted)'>{label} · {score}%</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        st.progress(score / 100)

        spacer(6)

    else:

     st.info(
        "📚 Topic mastery will appear after you complete quizzes."
     )
    spacer(20)
    st.subheader("🧠 Weak topics")

    if weak_topics:

       cols = st.columns(
         min(len(weak_topics), 3)
       )

       for i, item in enumerate(weak_topics):

          with cols[i % len(cols)]:
            st.warning(
              f"📌 {item['topic']} — "
              f"{item['mastery']}%"
            )

    else:

       st.success(
        "🎉 No weak topics detected yet. Keep practicing!"
      )
    spacer(20)
    st.subheader("🔄 Revision recommendations")

    if recommendations:

        for recommendation in recommendations:
            st.info(
                f"💡 {recommendation['message']}"
            )

    else:

        st.success(
        "🎯 Keep practicing! Recommendations will appear as you complete quizzes and study sessions."
        )
