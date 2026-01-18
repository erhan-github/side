export default function DashboardLoading() {
    return (
        <div className="min-h-screen bg-black text-white">
            {/* Sidebar Skeleton */}
            <aside className="fixed left-0 top-0 bottom-0 w-64 border-r border-white/10 bg-black/50 backdrop-blur-xl z-50">
                <div className="p-6">
                    <div className="flex items-center gap-2 mb-8">
                        <div className="h-6 w-6 bg-white rounded-sm" />
                        <span className="font-bold tracking-tight">CSO.ai</span>
                    </div>
                    <div className="flex flex-col gap-2">
                        {[1, 2, 3, 4].map((i) => (
                            <div key={i} className="h-10 bg-zinc-900 rounded-md animate-pulse" />
                        ))}
                    </div>
                </div>
            </aside>

            {/* Main Content Skeleton */}
            <main className="pl-64">
                <header className="h-16 border-b border-white/10 flex items-center px-8 bg-black/50">
                    <div className="h-6 w-32 bg-zinc-800 rounded animate-pulse" />
                </header>

                <div className="p-8">
                    {/* Stats Grid */}
                    <div className="grid grid-cols-3 gap-6 mb-8">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="h-32 bg-zinc-900 rounded-2xl animate-pulse" />
                        ))}
                    </div>

                    {/* Main Content */}
                    <div className="grid grid-cols-2 gap-6">
                        <div className="h-64 bg-zinc-900 rounded-2xl animate-pulse" />
                        <div className="h-64 bg-zinc-900 rounded-2xl animate-pulse" />
                    </div>
                </div>
            </main>
        </div>
    );
}
