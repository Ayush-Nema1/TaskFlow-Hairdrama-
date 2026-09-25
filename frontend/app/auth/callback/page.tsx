"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";

export default function AuthCallbackPage() {
  const router = useRouter();

  useEffect(() => {
    async function checkLogin() {
      // Implicit flow automatically stores the Google session.
      const { data } = await supabase.auth.getSession();

      if (data.session) {
        router.replace("/dashboard");
      } else {
        router.replace("/");
      }
    }

    checkLogin();
  }, [router]);

  return (
    <main className="page">
      <div className="card">Signing you in...</div>
    </main>
  );
}