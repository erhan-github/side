import { ArtifactGallery } from "@/components/artifacts/ArtifactGallery";
import { PageHeader } from "@/components/dashboard/shell/PageHeader";
import { Shield } from "lucide-react";

export default function AuditPage() {
    return (
        <div className="p-4 md:p-8 max-w-[1600px] mx-auto min-h-screen flex flex-col gap-6 mt-16 md:mt-0">
            <PageHeader
                title="Security Audit"
                description="Recent security scans and code analysis results."
                icon={Shield}
                iconColor="text-purple-400"
            />

            <div className="flex-1">
                <ArtifactGallery />
            </div>
        </div>
    );
}
