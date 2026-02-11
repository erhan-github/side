import { StrategicErrorBoundary } from "@/components/observability/ErrorBoundary";
import { GlobalSidebar } from "@/components/dashboard/GlobalSidebar";
import { getAuthenticatedUser } from "@/lib/dal/auth";
import { CreditReviver } from "@/components/dashboard/shell/CreditReviver";

export default async function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const user = await getAuthenticatedUser();

    return (
        <div className="flex min-h-screen bg-[#050505] text-foreground">
            <CreditReviver userId={user?.id || ""} />
            <GlobalSidebar />
            <main className="flex-1 overflow-y-auto h-screen bg-[#050505]">
                <StrategicErrorBoundary>
                    {children}
                </StrategicErrorBoundary>
            </main>
        </div>
    );
}
