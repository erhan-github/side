import Link from "next/link";

export default function NotFound() {
    return (
        <div className="min-h-screen bg-black text-white flex items-center justify-center px-6">
            <div className="text-center">
                <div className="text-8xl font-bold text-zinc-800 mb-4">404</div>
                <h1 className="text-2xl font-bold mb-2">Page not found</h1>
                <p className="text-zinc-400 mb-8 max-w-md">
                    The strategic intelligence you&apos;re looking for doesn&apos;t exist.
                    Let&apos;s get you back on track.
                </p>
                <Link
                    href="/"
                    className="h-12 px-8 rounded-full bg-white text-black font-semibold hover:bg-zinc-200 transition-all inline-flex items-center"
                >
                    Return to Home
                </Link>
            </div>
        </div>
    );
}
