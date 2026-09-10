import React, { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";

const STUDY_PLAN_STORAGE_KEY = "ai-tutor-study-plan";
const QUIZ_COUNT_STORAGE_KEY = "ai-tutor-quizzes-taken";
const STREAK_DATES_STORAGE_KEY = "ai-tutor-study-streak-dates-v3";

export const StudyPlanView = () => {
  const [activeTab, setActiveTab] = useState<"plan" | "progress">("plan");

  return (
    <div style={{ maxWidth: "900px", margin: "0 auto" }}>
      <div className="hero">
        <div className="eyebrow">Plan & Track</div>

        <h1>
          Your personalized study{" "}
          <span className="grad-text">dashboard</span>
        </h1>

        <p>
          Create study plans, track your progress, and identify weak areas — all
          in one place.
        </p>
      </div>

      <div
        style={{
          display: "flex",
          gap: "1rem",
          marginBottom: "2rem",
        }}
      >
        <button
          className={`btn ${activeTab === "plan" ? "btn-primary" : ""}`}
          onClick={() => setActiveTab("plan")}
        >
          📅 Study Plan
        </button>

        <button
          className={`btn ${activeTab === "progress" ? "btn-primary" : ""}`}
          onClick={() => setActiveTab("progress")}
        >
          📈 Progress
        </button>
      </div>

      {activeTab === "plan" ? <StudyPlanComponent /> : <ProgressComponent />}
    </div>
  );
};

// =========================================================
// STUDY PLAN COMPONENT
// =========================================================

const StudyPlanComponent = () => {
  const [goal, setGoal] = useState("");
  const [level, setLevel] = useState("Intermediate");
  const [topics, setTopics] = useState("");
  const [hours, setHours] = useState(3.0);
  const [sessions, setSessions] = useState(10);
  const [planType, setPlanType] = useState("Learning");
  const [examDate, setExamDate] = useState("");

  const [plan, setPlan] = useState<any>(() => {
    try {
      const savedPlan = localStorage.getItem(STUDY_PLAN_STORAGE_KEY);

      if (savedPlan) {
        return JSON.parse(savedPlan);
      }
    } catch (error) {
      console.error("Error loading saved study plan:", error);
    }

    return null;
  });

  const [isLoading, setIsLoading] = useState(false);

  // ---------------------------------------------------------
  // SAVE PLAN
  // ---------------------------------------------------------

  useEffect(() => {
    try {
      if (plan) {
        localStorage.setItem(
          STUDY_PLAN_STORAGE_KEY,
          JSON.stringify(plan)
        );
      }
    } catch (error) {
      console.error("Error saving study plan:", error);
    }
  }, [plan]);

  // ---------------------------------------------------------
  // GENERATE PLAN
  // ---------------------------------------------------------

  const generatePlan = async (e: React.FormEvent) => {
    e.preventDefault();

    setIsLoading(true);
    setPlan(null);

    try {
      const res = await fetch("/api/study-plan", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          goal,
          current_level: level,
          topics: topics
            .split(",")
            .map((t) => t.trim())
            .filter(Boolean),
          daily_hours: hours,
          duration_days: sessions,
          plan_type:
            planType === "Learning"
              ? "learning"
              : "exam_preparation",
          exam_date:
            planType === "Exam Preparation"
              ? examDate
              : null,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(
          data.detail || "Failed to generate study plan"
        );
      }

      setPlan(data);

      localStorage.setItem(
        STUDY_PLAN_STORAGE_KEY,
        JSON.stringify(data)
      );
    } catch (err) {
      console.error(err);
      alert("Error generating study plan");
    } finally {
      setIsLoading(false);
    }
  };

  // ---------------------------------------------------------
  // START / COMPLETE SESSION
  // ---------------------------------------------------------

  const handleSessionAction = async (
    sessionNumber: number,
    action: "start" | "complete"
  ) => {
    try {
      const res = await fetch(
        `/api/study-plan/session/${action}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            plan,
            session_number: sessionNumber,
          }),
        }
      );

      const updatedPlan = await res.json();

      if (!res.ok) {
        throw new Error(
          updatedPlan.detail ||
            `Failed to ${action} session`
        );
      }

      // -----------------------------------------------------
      // RECORD SESSION COMPLETION DATE
      // -----------------------------------------------------

      if (action === "complete") {
        try {
          const now = new Date();

          const today =
            now.getFullYear() +
            "-" +
            String(now.getMonth() + 1).padStart(2, "0") +
            "-" +
            String(now.getDate()).padStart(2, "0");

          // Store the completion date directly inside the plan.
          // This keeps the streak attached to the actual session
          // instead of relying only on a separate localStorage list.
          const planWithCompletionDate = {
            ...updatedPlan,
            study_sessions: Array.isArray(
              updatedPlan.study_sessions
            )
              ? updatedPlan.study_sessions.map(
                  (session: any) =>
                    session.session === sessionNumber
                      ? {
                          ...session,
                          completed_at: today,
                        }
                      : session
                )
              : updatedPlan.study_sessions,
          };

          // Also keep a simple list of study dates for compatibility.
          const savedDatesRaw = localStorage.getItem(
            STREAK_DATES_STORAGE_KEY
          );

          let savedDates: string[] = [];

          if (savedDatesRaw) {
            try {
              const parsed = JSON.parse(savedDatesRaw);

              if (Array.isArray(parsed)) {
                savedDates = parsed.filter(
                  (date): date is string =>
                    typeof date === "string" &&
                    /^\d{4}-\d{2}-\d{2}$/.test(date)
                );
              }
            } catch {
              savedDates = [];
            }
          }

          if (!savedDates.includes(today)) {
            savedDates.push(today);
          }

          savedDates = [...new Set(savedDates)].sort();

          localStorage.setItem(
            STREAK_DATES_STORAGE_KEY,
            JSON.stringify(savedDates)
          );

          // Use the plan containing completed_at as the source of truth.
          updatedPlan.study_sessions =
            planWithCompletionDate.study_sessions;

          console.log(
            "Study session completed on:",
            today
          );
        } catch (error) {
          console.error(
            "Error recording study completion:",
            error
          );
        }
      }

      setPlan(updatedPlan);

      localStorage.setItem(
        STUDY_PLAN_STORAGE_KEY,
        JSON.stringify(updatedPlan)
      );

      // Refresh Progress immediately when this tab is used.
      window.dispatchEvent(
        new CustomEvent("study-progress-updated")
      );
    } catch (err) {
      console.error(err);
      alert(
        `Error trying to ${action} session`
      );
    }
  };

  // ---------------------------------------------------------
  // NEW PLAN
  // ---------------------------------------------------------

  const handleNewPlan = () => {
    setPlan(null);

    localStorage.removeItem(
      STUDY_PLAN_STORAGE_KEY
    );
  };

  // ---------------------------------------------------------
  // EXISTING PLAN
  // ---------------------------------------------------------

  if (plan && plan.study_sessions) {
    const studySessions = plan.study_sessions;

    const completed = studySessions.filter(
      (s: any) =>
        s.status === "completed"
    ).length;

    const progress =
      studySessions.length > 0
        ? Math.round(
            (completed /
              studySessions.length) *
              100
          )
        : 0;

    return (
      <div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "2rem",
          }}
        >
          <h3>📖 Your Study Plan</h3>

          <button
            className="btn"
            onClick={handleNewPlan}
          >
            ← New Plan
          </button>
        </div>

        {/* SUMMARY */}

        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="card">
            <div
              style={{
                color: "var(--muted)",
                fontSize: "0.8rem",
                textTransform: "uppercase",
                marginBottom: "8px",
              }}
            >
              Total Sessions
            </div>

            <div
              style={{
                fontSize: "2rem",
                fontWeight: "bold",
              }}
            >
              {studySessions.length}
            </div>
          </div>

          <div className="card">
            <div
              style={{
                color: "var(--muted)",
                fontSize: "0.8rem",
                textTransform: "uppercase",
                marginBottom: "8px",
              }}
            >
              Completed
            </div>

            <div
              style={{
                fontSize: "2rem",
                fontWeight: "bold",
                color: "var(--primary)",
              }}
            >
              {completed}
            </div>
          </div>

          <div className="card">
            <div
              style={{
                color: "var(--muted)",
                fontSize: "0.8rem",
                textTransform: "uppercase",
                marginBottom: "8px",
              }}
            >
              Remaining
            </div>

            <div
              style={{
                fontSize: "2rem",
                fontWeight: "bold",
              }}
            >
              {studySessions.length -
                completed}
            </div>
          </div>
        </div>

        {/* PROGRESS */}

        <div style={{ marginBottom: "2rem" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: "0.5rem",
              color: "var(--muted)",
              fontSize: "0.9rem",
            }}
          >
            <span>Progress</span>
            <span>{progress}%</span>
          </div>

          <div
            style={{
              height: "12px",
              background:
                "var(--surface-strong)",
              borderRadius: "99px",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                height: "100%",
                width: `${progress}%`,
                background:
                  "linear-gradient(90deg, var(--primary), var(--primary-2))",
                transition:
                  "width 0.3s ease",
              }}
            />
          </div>
        </div>

        {/* SESSIONS */}

        <div
          style={{
            position: "relative",
            borderLeft:
              "2px solid var(--border)",
            marginLeft: "16px",
            paddingLeft: "32px",
          }}
        >
          {studySessions.map(
            (
              session: any,
              idx: number
            ) => {
              const isCompleted =
                session.status ===
                "completed";

              const isInProgress =
                session.status ===
                "in_progress";

              const isPending =
                session.status ===
                "pending";

              return (
                <div
                  key={idx}
                  className="card"
                  style={{
                    marginBottom: "1.5rem",
                    position: "relative",
                  }}
                >
                  <div
                    style={{
                      position: "absolute",
                      left: "-44px",
                      top: "24px",
                      width: "20px",
                      height: "20px",
                      borderRadius: "50%",
                      background:
                        isCompleted
                          ? "var(--primary)"
                          : "var(--surface-strong)",
                      border:
                        "4px solid var(--bg)",
                      zIndex: 2,
                    }}
                  />

                  <div
                    style={{
                      display: "flex",
                      justifyContent:
                        "space-between",
                      alignItems:
                        "flex-start",
                      marginBottom: "1rem",
                    }}
                  >
                    <div>
                      <h4
                        style={{
                          marginBottom: "4px",
                        }}
                      >
                        Session{" "}
                        {session.session}
                      </h4>

                      <span
                        style={{
                          fontSize: "0.75rem",
                          padding:
                            "2px 8px",
                          borderRadius:
                            "99px",
                          background:
                            "var(--surface-strong)",
                          color:
                            isCompleted
                              ? "var(--primary)"
                              : "var(--muted)",
                        }}
                      >
                        {session.status
                          .replace(
                            "_",
                            " "
                          )
                          .toUpperCase()}
                      </span>
                    </div>

                    {isPending && (
                      <button
                        className="btn"
                        onClick={() =>
                          handleSessionAction(
                            session.session,
                            "start"
                          )
                        }
                      >
                        ▶️ Start Session
                      </button>
                    )}

                    {isInProgress && (
                      <button
                        className="btn btn-primary"
                        onClick={() =>
                          handleSessionAction(
                            session.session,
                            "complete"
                          )
                        }
                      >
                        ✅ Complete Session
                      </button>
                    )}
                  </div>

                  <ul
                    style={{
                      listStyle: "none",
                      padding: 0,
                    }}
                  >
                    {session.tasks.map(
                      (
                        task: any,
                        tIdx: number
                      ) => (
                        <li
                          key={tIdx}
                          style={{
                            padding:
                              "0.75rem",
                            background:
                              "var(--surface-strong)",
                            borderRadius:
                              "12px",
                            marginBottom:
                              "0.5rem",
                          }}
                        >
                          <div
                            style={{
                              display:
                                "flex",
                              justifyContent:
                                "space-between",
                              alignItems:
                                "center",
                            }}
                          >
                            <strong>
                              {
                                task.topic
                              }
                            </strong>

                            <span
                              style={{
                                color:
                                  "var(--muted)",
                                fontSize:
                                  "0.85rem",
                              }}
                            >
                              ⏱️{" "}
                              {
                                task.duration_minutes
                              }{" "}
                              min
                            </span>
                          </div>

                          <p
                            style={{
                              color:
                                "var(--muted)",
                              fontSize:
                                "0.9rem",
                              marginTop:
                                "4px",
                            }}
                          >
                            {
                              task.description
                            }
                          </p>
                        </li>
                      )
                    )}
                  </ul>
                </div>
              );
            }
          )}
        </div>
      </div>
    );
  }

  // ---------------------------------------------------------
  // CREATE PLAN FORM
  // ---------------------------------------------------------

  return (
    <div className="card">
      <h3 className="mb-4">
        🎯 Create your personalized
        study plan
      </h3>

      <form
        onSubmit={generatePlan}
        style={{
          display: "flex",
          flexDirection:
            "column",
          gap: "1rem",
        }}
      >
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label
              htmlFor="planType"
              style={{
                display: "block",
                marginBottom:
                  "0.5rem",
                color:
                  "var(--muted)",
              }}
            >
              Plan type
            </label>

            <select
              id="planType"
              className="input"
              value={planType}
              onChange={(e) =>
                setPlanType(
                  e.target.value
                )
              }
            >
              <option>
                Learning
              </option>
              <option>
                Exam Preparation
              </option>
            </select>
          </div>

          <div>
            <label
              htmlFor="level"
              style={{
                display: "block",
                marginBottom:
                  "0.5rem",
                color:
                  "var(--muted)",
              }}
            >
              Current level
            </label>

            <select
              id="level"
              className="input"
              value={level}
              onChange={(e) =>
                setLevel(
                  e.target.value
                )
              }
            >
              <option>
                Beginner
              </option>
              <option>
                Intermediate
              </option>
              <option>
                Advanced
              </option>
            </select>
          </div>
        </div>

        <div>
          <label
            htmlFor="goal"
            style={{
              display: "block",
              marginBottom:
                "0.5rem",
              color:
                "var(--muted)",
            }}
          >
            What do you want to
            achieve?
          </label>

          <input
            id="goal"
            className="input"
            placeholder="e.g. Learn DSA for placement preparation"
            value={goal}
            onChange={(e) =>
              setGoal(
                e.target.value
              )
            }
            required
          />
        </div>

        <div>
          <label
            htmlFor="topics"
            style={{
              display: "block",
              marginBottom:
                "0.5rem",
              color:
                "var(--muted)",
            }}
          >
            Topics (comma separated)
          </label>

          <input
            id="topics"
            className="input"
            placeholder="e.g. Arrays, Strings, Recursion"
            value={topics}
            onChange={(e) =>
              setTopics(
                e.target.value
              )
            }
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label
              htmlFor="hours"
              style={{
                display: "block",
                marginBottom:
                  "0.5rem",
                color:
                  "var(--muted)",
              }}
            >
              Study time per
              session (hours):{" "}
              {hours}
            </label>

            <input
              id="hours"
              type="range"
              min="1"
              max="8"
              step="0.5"
              style={{
                width: "100%",
              }}
              value={hours}
              onChange={(e) =>
                setHours(
                  Number(
                    e.target.value
                  )
                )
              }
            />
          </div>

          <div>
            <label
              htmlFor="sessions"
              style={{
                display: "block",
                marginBottom:
                  "0.5rem",
                color:
                  "var(--muted)",
              }}
            >
              Number of sessions
            </label>

            <input
              id="sessions"
              type="number"
              min="1"
              max="365"
              className="input"
              value={sessions}
              onChange={(e) =>
                setSessions(
                  Number(
                    e.target.value
                  )
                )
              }
            />
          </div>
        </div>

        {planType ===
          "Exam Preparation" && (
          <div>
            <label
              htmlFor="examDate"
              style={{
                display: "block",
                marginBottom:
                  "0.5rem",
                color:
                  "var(--muted)",
              }}
            >
              Exam Date
            </label>

            <input
              id="examDate"
              type="date"
              className="input"
              value={examDate}
              onChange={(e) =>
                setExamDate(
                  e.target.value
                )
              }
              required
            />
          </div>
        )}

        <button
          type="submit"
          className="btn btn-primary"
          style={{
            marginTop: "1rem",
            fontSize: "1.15rem",
            padding: "0.85rem 1.5rem",
          }}
          disabled={isLoading}
        >
          {isLoading ? (
            <Loader2
              className="animate-spin"
              size={18}
            />
          ) : (
            "✨ Generate Personalized Study Plan"
          )}
        </button>
      </form>
    </div>
  );
};

// =========================================================
// PROGRESS COMPONENT
// =========================================================

const ProgressComponent = () => {
  const [quizzesTaken, setQuizzesTaken] =
    useState(0);

  const [studyStreak, setStudyStreak] =
    useState(0);

  const [savedPlan, setSavedPlan] =
    useState<any>(null);

  // ---------------------------------------------------------
  // CALCULATE STREAK
  // ---------------------------------------------------------

  const calculateStudyStreak = (
    dates: string[]
  ): number => {
    const validDates = [
      ...new Set(
        dates.filter(
          (date) =>
            typeof date === "string" &&
            /^\d{4}-\d{2}-\d{2}$/.test(date)
        )
      ),
    ];

    if (validDates.length === 0) {
      return 0;
    }

    const dateToNumber = (date: string) => {
      const [year, month, day] = date
        .split("-")
        .map(Number);

      return new Date(
        year,
        month - 1,
        day
      ).getTime();
    };

    const now = new Date();

    const today =
      now.getFullYear() +
      "-" +
      String(now.getMonth() + 1).padStart(2, "0") +
      "-" +
      String(now.getDate()).padStart(2, "0");

    const yesterdayDate = new Date(
      now.getFullYear(),
      now.getMonth(),
      now.getDate() - 1
    );

    const yesterday =
      yesterdayDate.getFullYear() +
      "-" +
      String(
        yesterdayDate.getMonth() + 1
      ).padStart(2, "0") +
      "-" +
      String(
        yesterdayDate.getDate()
      ).padStart(2, "0");

    // If there was no activity today, an activity yesterday
    // means the current streak is still alive.
    let currentDate: string;

    if (validDates.includes(today)) {
      currentDate = today;
    } else if (validDates.includes(yesterday)) {
      currentDate = yesterday;
    } else {
      return 0;
    }

    let streak = 0;
    let cursor = dateToNumber(currentDate);

    const dateSet = new Set(validDates);

    while (true) {
      const date = new Date(cursor);

      const key =
        date.getFullYear() +
        "-" +
        String(date.getMonth() + 1).padStart(2, "0") +
        "-" +
        String(date.getDate()).padStart(2, "0");

      if (!dateSet.has(key)) {
        break;
      }

      streak++;

      date.setDate(
        date.getDate() - 1
      );

      cursor = date.getTime();
    }

    return streak;
  };

  // ---------------------------------------------------------
  // LOAD PROGRESS
  // ---------------------------------------------------------

  useEffect(() => {
    const loadProgress = () => {
      try {
        // Quiz count
        const quizCount = Number(
          localStorage.getItem(
            QUIZ_COUNT_STORAGE_KEY
          ) || "0"
        );

        setQuizzesTaken(quizCount);

        // Study plan
        const saved =
          localStorage.getItem(
            STUDY_PLAN_STORAGE_KEY
          );

        let parsedPlan: any = null;

        if (saved) {
          parsedPlan = JSON.parse(saved);
          setSavedPlan(parsedPlan);
        } else {
          setSavedPlan(null);
        }

        // ---------------------------------------------------
        // STREAK DATES
        // ---------------------------------------------------

        const savedDatesRaw =
          localStorage.getItem(
            STREAK_DATES_STORAGE_KEY
          );

        let savedDates: string[] = [];

        if (savedDatesRaw) {
          try {
            const parsed =
              JSON.parse(savedDatesRaw);

            if (Array.isArray(parsed)) {
              savedDates = parsed;
            }
          } catch {
            savedDates = [];
          }
        }

        // Read completion dates directly from study sessions.
        if (
          parsedPlan &&
          Array.isArray(
            parsedPlan.study_sessions
          )
        ) {
          parsedPlan.study_sessions.forEach(
            (session: any) => {
              if (
                session.status === "completed" &&
                typeof session.completed_at === "string" &&
                /^\d{4}-\d{2}-\d{2}$/.test(
                  session.completed_at
                )
              ) {
                savedDates.push(
                  session.completed_at
                );
              }
            }
          );
        }

        // ---------------------------------------------------
        // MIGRATE OLD COMPLETED SESSIONS
        //
        // The old version knew that sessions were completed,
        // but did not save their dates. For the first clean
        // streak setup, treat the existing completed activity
        // as today's starting activity.
        // ---------------------------------------------------

        if (
          parsedPlan &&
          Array.isArray(
            parsedPlan.study_sessions
          ) &&
          !localStorage.getItem(
            "ai-tutor-streak-v3-initialized"
          )
        ) {
          const hasCompletedSession =
            parsedPlan.study_sessions.some(
              (session: any) =>
                session.status === "completed"
            );

          if (hasCompletedSession) {
            const now = new Date();

            const today =
              now.getFullYear() +
              "-" +
              String(now.getMonth() + 1).padStart(2, "0") +
              "-" +
              String(now.getDate()).padStart(2, "0");

            savedDates.push(today);

            // Add completed_at to legacy completed sessions.
            const migratedPlan = {
              ...parsedPlan,
              study_sessions:
                parsedPlan.study_sessions.map(
                  (session: any) =>
                    session.status === "completed" &&
                    !session.completed_at
                      ? {
                          ...session,
                          completed_at: today,
                        }
                      : session
                ),
            };

            setSavedPlan(migratedPlan);

            localStorage.setItem(
              STUDY_PLAN_STORAGE_KEY,
              JSON.stringify(migratedPlan)
            );
          }

          localStorage.setItem(
            "ai-tutor-streak-v3-initialized",
            "true"
          );
        }

        savedDates = [
          ...new Set(savedDates),
        ];

        localStorage.setItem(
          STREAK_DATES_STORAGE_KEY,
          JSON.stringify(savedDates)
        );

        setStudyStreak(
          calculateStudyStreak(savedDates)
        );
      } catch (error) {
        console.error(
          "Error loading progress data:",
          error
        );
      }
    };

    loadProgress();

    window.addEventListener(
      "study-progress-updated",
      loadProgress
    );

    window.addEventListener(
      "storage",
      loadProgress
    );

    window.addEventListener(
      "focus",
      loadProgress
    );

    return () => {
      window.removeEventListener(
        "study-progress-updated",
        loadProgress
      );

      window.removeEventListener(
        "storage",
        loadProgress
      );

      window.removeEventListener(
        "focus",
        loadProgress
      );
    };
  }, []);

  // ---------------------------------------------------------
  // SESSION PROGRESS
  // ---------------------------------------------------------

  const studySessions =
    savedPlan?.study_sessions ||
    [];

  const completedSessions =
    studySessions.filter(
      (session: any) =>
        session.status ===
        "completed"
    );

  const completedCount =
    completedSessions.length;

  const totalSessions =
    studySessions.length;

  const studyProgress =
    totalSessions > 0
      ? Math.round(
          (completedCount /
            totalSessions) *
            100
        )
      : 0;

  // ---------------------------------------------------------
  // TOPICS STUDIED
  // ---------------------------------------------------------

  const topicsStudied =
    new Set<string>();

  completedSessions.forEach(
    (session: any) => {
      if (
        Array.isArray(
          session.tasks
        )
      ) {
        session.tasks.forEach(
          (task: any) => {
            if (task.topic) {
              topicsStudied.add(
                task.topic
              );
            }
          }
        );
      }

      if (session.topic) {
        topicsStudied.add(
          session.topic
        );
      }

      if (
        Array.isArray(
          session.topics
        )
      ) {
        session.topics.forEach(
          (topic: string) => {
            if (topic) {
              topicsStudied.add(
                topic
              );
            }
          }
        );
      }
    }
  );

  // ---------------------------------------------------------
  // UI
  // ---------------------------------------------------------

  return (
    <div>
      <div className="grid grid-cols-3 gap-4 mb-8">
        {/* TOPICS */}

        <div className="card">
          <div
            style={{
              fontSize: "1.5rem",
              marginBottom: "8px",
            }}
          >
            📚
          </div>

          <div
            style={{
              color:
                "var(--muted)",
              fontSize:
                "0.8rem",
              textTransform:
                "uppercase",
            }}
          >
            Topics Studied
          </div>

          <div
            style={{
              fontSize:
                "1.5rem",
              fontWeight:
                "bold",
            }}
          >
            {topicsStudied.size}
          </div>
        </div>

        {/* QUIZZES */}

        <div className="card">
          <div
            style={{
              fontSize: "1.5rem",
              marginBottom: "8px",
            }}
          >
            📝
          </div>

          <div
            style={{
              color:
                "var(--muted)",
              fontSize:
                "0.8rem",
              textTransform:
                "uppercase",
            }}
          >
            Quizzes Taken
          </div>

          <div
            style={{
              fontSize:
                "1.5rem",
              fontWeight:
                "bold",
            }}
          >
            {quizzesTaken}
          </div>
        </div>

        {/* STREAK */}

        <div className="card">
          <div
            style={{
              fontSize: "1.5rem",
              marginBottom: "8px",
            }}
          >
            🔥
          </div>

          <div
            style={{
              color:
                "var(--muted)",
              fontSize:
                "0.8rem",
              textTransform:
                "uppercase",
            }}
          >
            Study Streak
          </div>

          <div
            style={{
              fontSize:
                "1.5rem",
              fontWeight:
                "bold",
            }}
          >
            {studyStreak}{" "}
            {studyStreak === 1
              ? "day"
              : "days"}
          </div>
        </div>
      </div>

      {/* STUDY SESSION PROGRESS */}

      <div
        className="card"
        style={{
          marginBottom:
            "2rem",
        }}
      >
        <h3
          style={{
            marginBottom:
              "1rem",
          }}
        >
          📈 Study Session
          Progress
        </h3>

        <div
          style={{
            display:
              "flex",
            justifyContent:
              "space-between",
            marginBottom:
              "0.5rem",
            color:
              "var(--muted)",
            fontSize:
              "0.9rem",
          }}
        >
          <span>
            {completedCount}{" "}
            completed
          </span>

          <span>
            {Math.max(
              totalSessions -
                completedCount,
              0
            )}{" "}
            remaining
          </span>
        </div>

        <div
          style={{
            height: "10px",
            background:
              "var(--surface-strong)",
            borderRadius:
              "99px",
            overflow:
              "hidden",
          }}
        >
          <div
            style={{
              height: "100%",
              width: `${studyProgress}%`,
              background:
                "linear-gradient(90deg, var(--primary), var(--primary-2))",
              transition:
                "width 0.3s ease",
            }}
          />
        </div>
      </div>

      {/* INFORMATION */}

      <div
        className="card"
        style={{
          marginBottom:
            "2rem",
          textAlign:
            "center",
          padding: "3rem",
        }}
      >
        {totalSessions ===
          0 &&
        quizzesTaken === 0 ? (
          <>
            <h3
              style={{
                marginBottom:
                  "1rem",
              }}
            >
              No Data
              Available Yet
            </h3>

            <p
              style={{
                color:
                  "var(--muted)",
              }}
            >
              Complete
              quizzes and
              study sessions
              to unlock your
              progress
              dashboard,
              weak topics
              analysis, and
              revision
              recommendations.
            </p>
          </>
        ) : (
          <>
            <h3
              style={{
                marginBottom:
                  "1rem",
              }}
            >
              🎉 Keep
              Learning!
            </h3>

            <p
              style={{
                color:
                  "var(--muted)",
              }}
            >
              Your study
              sessions and
              quizzes are
              being tracked
              automatically.
            </p>
          </>
        )}
      </div>
    </div>
  );
};