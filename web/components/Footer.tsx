import Link from "next/link";
import { Github } from "lucide-react";

export function Footer() {
    const currentYear = new Date().getFullYear();

    return (
        <footer className="w-full border-t border-white/5 bg-black/50 backdrop-blur-xl mt-32">
            <div className="max-w-7xl mx-auto px-6 py-12">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
                    {/* Product */}
                    <div>
                        <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Product</h3>
                        <ul className="space-y-3">
                            <li>
                                <Link href="/docs" className="text-sm text-white/40 hover:text-white transition-colors">
                                    Get Started
                                </Link>
                            </li>
                            <li>
                                <Link href="/pricing" className="text-sm text-white/40 hover:text-white transition-colors">
                                    Pricing
                                </Link>
                            </li>
                            <li>
                                <Link href="/changelog" className="text-sm text-white/40 hover:text-white transition-colors">
                                    Changelog
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* Company */}
                    <div>
                        <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Company</h3>
                        <ul className="space-y-3">
                            <li>
                                <Link href="/about" className="text-sm text-white/40 hover:text-white transition-colors">
                                    About
                                </Link>
                            </li>
                            <li>
                                <a href="mailto:hello@sidelith.com" className="text-sm text-white/40 hover:text-white transition-colors">
                                    Contact
                                </a>
                            </li>
                        </ul>
                    </div>

                    {/* Legal */}
                    <div>
                        <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Legal</h3>
                        <ul className="space-y-3">
                            <li>
                                <Link href="/privacy" className="text-sm text-white/40 hover:text-white transition-colors">
                                    Privacy
                                </Link>
                            </li>
                            <li>
                                <Link href="/terms" className="text-sm text-white/40 hover:text-white transition-colors">
                                    Terms
                                </Link>
                            </li>
                            <li>
                                <Link href="/security" className="text-sm text-white/40 hover:text-white transition-colors">
                                    Security
                                </Link>
                            </li>
                        </ul>
                    </div>


                </div>

                {/* Bottom Bar */}
                <div className="pt-8 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-4">
                    <div className="text-sm text-white/30">
                        © {currentYear} Sidelith. All rights reserved.
                    </div>
                    <div className="text-xs text-white/20 font-mono">
                        Intelligence that Remembers.
                    </div>
                </div>
            </div>
        </footer>
    );
}
