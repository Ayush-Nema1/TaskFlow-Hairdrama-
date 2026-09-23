"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";

export default function HomePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  useEffect(() => {
    // If a session already exists, skip the login screen.
    supabase.auth.getSession().then(({ data }) => {
      if (data.session) {
        router.replace("/dashboard");
      } else {
        setLoading(false);
      }
    });
  }, [router]);

  async function loginWithGoogle() {
    setMessage("");
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    });

    if (error) {
      setMessage(error.message);
    }
  }

  if (loading) {
    return <main className="page" />;
  }

  return (
    <main className="page">
      <section className="card auth-card">
        <div className="logo">TaskFlow</div>
        <p className="muted">Simple task management for teams.</p>

        {message && <div className="message">{message}</div>}

        <button className="primary google-btn" onClick={loginWithGoogle}>
          Continue with Google
        </button>
      </section>
    </main>
  );
}
