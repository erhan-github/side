"use client";

import { useEffect } from "react";
import { createClient } from "@/lib/supabase/client";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

interface CreditReviverProps {
    userId: string;
}

export function CreditReviver({ userId }: CreditReviverProps) {
    const router = useRouter();
    const supabase = createClient();

    useEffect(() => {
        const channel = supabase
            .channel(`credit-updates-${userId}`)
            .on(
                "postgres_changes",
                {
                    event: "UPDATE",
                    schema: "public",
                    table: "profiles",
                    filter: `id=eq.${userId}`,
                },
                (payload) => {
                    console.log("Credit update detected:", payload);
                    router.refresh();
                    toast.success("Capacity Updated", {
                        description: "Your system capacity has been refreshed."
                    });
                }
            )
            .subscribe();

        return () => {
            supabase.removeChannel(channel);
        };
    }, [userId, supabase, router]);

    return null;
}
