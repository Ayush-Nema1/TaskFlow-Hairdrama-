"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { apiRequest } from "@/lib/api";
import { supabase } from "@/lib/supabase";

interface User {
  id: string;
  name: string;
  email: string;
  avatar_url?: string | null;
}

interface Task {
  id: number;
  title: string;
  description: string;
  status: "pending" | "completed";
  created_at: string;
  created_by: string;
  assigned_to: string;
  creator?: User | null;
  assignee?: User | null;
}

interface SessionUser {
  id: string;
  email?: string;
  user_metadata?: Record<string, string>;
}

export default function DashboardPage() {
  const router = useRouter();

  const [currentUser, setCurrentUser] = useState<SessionUser | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [assignedTo, setAssignedTo] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  const myTasks = useMemo(
    () => tasks.filter((task) => task.assigned_to === currentUser?.id),
    [tasks, currentUser?.id]
  );

  async function loadData() {
    const [taskData, userData] = await Promise.all([
      apiRequest<Task[]>("/api/tasks"),
      apiRequest<User[]>("/api/users"),
    ]);

    setTasks(taskData);
    setUsers(userData);

    if (!assignedTo && userData.length > 0) {
      setAssignedTo(userData[0].id);
    }
  }

  useEffect(() => {
    async function start() {
      const { data } = await supabase.auth.getUser();

      if (!data.user) {
        router.replace("/");
        return;
      }

      setCurrentUser({
        id: data.user.id,
        email: data.user.email,
        user_metadata: data.user.user_metadata,
      });

      try {
        // Make sure the user also exists in our own users table.
        await apiRequest("/api/users/sync", { method: "POST" });
        await loadData();
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Could not load data");
      } finally {
        setLoading(false);
      }
    }

    start();
  }, [router]);

  async function createTask(event: React.FormEvent) {
    event.preventDefault();
    setMessage("");

    if (!title.trim() || !assignedTo) {
      setMessage("Please enter a title and choose a user.");
      return;
    }

    setSaving(true);

    try {
      await apiRequest("/api/tasks", {
        method: "POST",
        body: JSON.stringify({
          title,
          description,
          assigned_to: assignedTo,
        }),
      });

      setTitle("");
      setDescription("");
      await loadData();
      setMessage("Task created and email notification sent/queued.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not create task");
    } finally {
      setSaving(false);
    }
  }

  async function completeTask(taskId: number) {
    setMessage("");

    try {
      await apiRequest(`/api/tasks/${taskId}/complete`, {
        method: "PATCH",
      });
      await loadData();
      setMessage("Task completed and creator notified.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not complete task");
    }
  }

  async function logout() {
    await supabase.auth.signOut();
    router.replace("/");
  }

  if (loading) {
    return <main className="page"><div className="container">Loading...</div></main>;
  }

  const name = currentUser?.user_metadata?.full_name || currentUser?.user_metadata?.name || currentUser?.email || "User";
  const avatar = currentUser?.user_metadata?.avatar_url || currentUser?.user_metadata?.picture || "";

  return (
    <main className="page">
      <div className="container">
        <header className="header">
          <div>
            <h1>Task Dashboard</h1>
            <div className="muted">Create, assign and complete tasks.</div>
          </div>

          <div className="user-box">
            {avatar ? <img className="avatar" src={avatar} alt="Profile" /> : <div className="avatar" />}
            <div>
              <strong>{name}</strong>
              <div className="muted">{currentUser?.email}</div>
            </div>
            <button className="secondary" onClick={logout}>Logout</button>
          </div>
        </header>

        {message && <div className="message">{message}</div>}

        <div className="grid">
          <section className="card">
            <h2 className="form-title">Create task</h2>

            <form onSubmit={createTask}>
              <div className="field">
                <label className="label" htmlFor="title">Title</label>
                <input
                  id="title"
                  className="input"
                  value={title}
                  onChange={(event) => setTitle(event.target.value)}
                  placeholder="e.g. Finish API documentation"
                />
              </div>

              <div className="field">
                <label className="label" htmlFor="description">Description</label>
                <textarea
                  id="description"
                  className="textarea"
                  value={description}
                  onChange={(event) => setDescription(event.target.value)}
                  placeholder="Add a short description"
                />
              </div>

              <div className="field">
                <label className="label" htmlFor="assignee">Assign to</label>
                <select
                  id="assignee"
                  className="select"
                  value={assignedTo}
                  onChange={(event) => setAssignedTo(event.target.value)}
                >
                  <option value="">Select user</option>
                  {users.map((user) => (
                    <option key={user.id} value={user.id}>
                      {user.name} - {user.email}
                    </option>
                  ))}
                </select>
              </div>

              <button className="primary" disabled={saving || users.length === 0}>
                {saving ? "Creating..." : "Create Task"}
              </button>
            </form>
          </section>

          <section className="card">
            <h2 className="section-title">All your tasks</h2>

            {tasks.length === 0 ? (
              <div className="empty">No tasks yet.</div>
            ) : (
              <div className="tasks">
                {tasks.map((task) => (
                  <article className="task" key={task.id}>
                    <div className="task-top">
                      <div>
                        <h3>{task.title}</h3>
                        <p>{task.description || "No description"}</p>
                      </div>
                      <span className="badge">{task.status}</span>
                    </div>

                    <div className="task-meta">
                      <span>Created by: {task.creator?.name || "Unknown"}</span>
                      <span>Assigned to: {task.assignee?.name || "Unknown"}</span>
                    </div>

                    {task.status === "pending" && task.assigned_to === currentUser?.id && (
                      <div className="task-actions">
                        <button className="primary" onClick={() => completeTask(task.id)}>
                          Mark as completed
                        </button>
                      </div>
                    )}
                  </article>
                ))}
              </div>
            )}

            {myTasks.length > 0 && (
              <p className="muted" style={{ marginTop: 18 }}>
                You have {myTasks.length} assigned task{myTasks.length === 1 ? "" : "s"}.
              </p>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}
