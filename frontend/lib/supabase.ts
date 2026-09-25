import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

// This client runs in the browser and never contains the service-role key.
export const supabase = createClient(supabaseUrl, supabaseKey, {
  auth: {
    flowType: "implicit",
  },
});