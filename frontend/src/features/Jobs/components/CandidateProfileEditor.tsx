/**
 * Lisa AIOS — Candidate Profile Editor (Manual Entry, Method A)
 * Uses real backend CandidateProfile Pydantic schema.
 * Skills stored in nested SkillCategory object; flattened to all_normalized_skills by backend on save.
 */

import { useState, useEffect } from "react"
import {
  GraduationCap,
  Code2,
  Briefcase,
  Layers,
  Target,
  ChevronDown,
  ChevronUp,
  Plus,
  X,
  Loader2,
  CheckCircle2,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useSaveCandidateProfileMutation } from "../queries"
import type { CandidateProfile, SkillCategory } from "../types"

interface CandidateProfileEditorProps {
  existingProfile?: CandidateProfile | null
  onSaved: (profile: CandidateProfile) => void
}

function SkillTagInput({
  label,
  skills,
  onChange,
}: {
  label: string
  skills: string[]
  onChange: (updated: string[]) => void
}) {
  const [inputValue, setInputValue] = useState("")
  const addSkill = () => {
    const trimmed = inputValue.trim()
    if (trimmed && !skills.includes(trimmed)) onChange([...skills, trimmed])
    setInputValue("")
  }
  return (
    <div className="space-y-1.5">
      <label className="text-xs font-semibold text-muted-foreground">{label}</label>
      <div className="flex gap-2">
        <Input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter" || e.key === ",") { e.preventDefault(); addSkill() } }}
          placeholder={`Add ${label.toLowerCase()}...`}
          className="h-8 text-sm flex-1"
        />
        <Button type="button" variant="outline" size="sm" onClick={addSkill} className="h-8 px-3">
          <Plus className="h-3.5 w-3.5" />
        </Button>
      </div>
      {skills.length > 0 && (
        <div className="flex flex-wrap gap-1.5 pt-1">
          {skills.map((skill) => (
            <span key={skill} className="flex items-center gap-1 text-xs px-2.5 py-0.5 rounded-full bg-secondary border border-border/60 text-foreground">
              {skill}
              <button type="button" onClick={() => onChange(skills.filter((s) => s !== skill))} className="text-muted-foreground hover:text-destructive transition-colors">
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  )
}

type Section = "personal" | "education" | "skills" | "projects" | "experience" | "preferences"

const SECTIONS: { id: Section; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { id: "personal", label: "Personal Info", icon: Target },
  { id: "education", label: "Education", icon: GraduationCap },
  { id: "skills", label: "Skills by Category", icon: Code2 },
  { id: "projects", label: "Projects", icon: Layers },
  { id: "experience", label: "Experience & Internships", icon: Briefcase },
  { id: "preferences", label: "Job Preferences", icon: Target },
]

function emptySkillCategory(): SkillCategory {
  return { programming_languages: [], ai_ml_skills: [], frameworks: [], databases: [], cloud_devops: [], tools: [] }
}

function emptyProfile(): CandidateProfile {
  return {
    name: "", email: "", phone: "",
    education: [],
    skills: emptySkillCategory(),
    all_normalized_skills: [],
    projects: [], experiences: [], certifications: [], achievements: [],
    preferred_roles: [], preferred_locations: [],
    remote_preference: "any",
    expected_salary_or_stipend: "",
    availability: "immediate",
    experience_level: "entry_level",
    raw_resume_text: null,
    extracted_from_resume: false,
    is_confirmed_by_user: true,
  }
}

/** Rebuild all_normalized_skills from the nested SkillCategory for the backend. */
function buildAllSkills(profile: CandidateProfile): string[] {
  const s = profile.skills
  const all = [...s.programming_languages, ...s.ai_ml_skills, ...s.frameworks, ...s.databases, ...s.cloud_devops, ...s.tools]
  return Array.from(new Set(all))
}

export function CandidateProfileEditor({ existingProfile, onSaved }: CandidateProfileEditorProps) {
  const [profile, setProfile] = useState<CandidateProfile>(
    existingProfile ? { ...existingProfile } : emptyProfile()
  )

  useEffect(() => {
    if (existingProfile) {
      setProfile({ ...existingProfile })
    }
  }, [existingProfile])

  const [openSection, setOpenSection] = useState<Section>("personal")
  const saveMutation = useSaveCandidateProfileMutation()

  const toggleSection = (section: Section) => setOpenSection((prev) => prev === section ? "personal" : section)

  const updateSkillCategory = (field: keyof SkillCategory, value: string[]) => {
    const updated = { ...profile.skills, [field]: value }
    setProfile({ ...profile, skills: updated, all_normalized_skills: buildAllSkills({ ...profile, skills: updated }) })
  }

  const handleSave = async () => {
    const merged = { ...profile, all_normalized_skills: buildAllSkills(profile), is_confirmed_by_user: true }
    try {
      const saved = await saveMutation.mutateAsync(merged)
      onSaved(saved)
    } catch { /* error shown by mutation state */ }
  }

  const renderSection = (section: Section) => {
    const isOpen = openSection === section
    const sectionInfo = SECTIONS.find((s) => s.id === section)
    const SectionIcon = sectionInfo?.icon

    return (
      <div key={section} className="border border-border/70 rounded-xl overflow-hidden">
        <button
          type="button"
          onClick={() => toggleSection(section)}
          className="w-full flex items-center justify-between px-4 py-3 bg-card/60 hover:bg-secondary/40 transition-colors"
        >
          <div className="flex items-center gap-2.5">
            {SectionIcon && <SectionIcon className="h-4 w-4 text-primary" />}
            <span className="text-sm font-semibold text-foreground">{sectionInfo?.label}</span>
          </div>
          {isOpen ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
        </button>

        {isOpen && (
          <div className="px-4 pb-4 pt-3 space-y-4 bg-card/30">
            {section === "personal" && (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {[
                  { label: "Full Name *", key: "name" as const, placeholder: "Your full name" },
                  { label: "Email", key: "email" as const, placeholder: "your@email.com" },
                  { label: "Phone", key: "phone" as const, placeholder: "+91 XXXX" },
                ].map(({ label, key, placeholder }) => (
                  <div key={key} className="space-y-1">
                    <label className="text-xs font-semibold text-muted-foreground">{label}</label>
                    <Input value={(profile[key] as string) || ""} onChange={(e) => setProfile({ ...profile, [key]: e.target.value })} placeholder={placeholder} className="h-9 text-sm" />
                  </div>
                ))}
              </div>
            )}

            {section === "education" && (
              <div className="space-y-3">
                {profile.education.map((edu, idx) => (
                  <div key={idx} className="grid grid-cols-2 sm:grid-cols-3 gap-2 p-3 rounded-lg bg-card border border-border/50">
                    <Input value={edu.college} onChange={(e) => { const ed = [...profile.education]; ed[idx] = { ...ed[idx], college: e.target.value }; setProfile({ ...profile, education: ed }) }} placeholder="College / University" className="h-8 text-sm col-span-2 sm:col-span-1" />
                    <Input value={edu.degree} onChange={(e) => { const ed = [...profile.education]; ed[idx] = { ...ed[idx], degree: e.target.value }; setProfile({ ...profile, education: ed }) }} placeholder="Degree (B.Tech)" className="h-8 text-sm" />
                    <Input value={edu.branch || ""} onChange={(e) => { const ed = [...profile.education]; ed[idx] = { ...ed[idx], branch: e.target.value }; setProfile({ ...profile, education: ed }) }} placeholder="Branch / Major" className="h-8 text-sm" />
                    <Input value={edu.graduation_year?.toString() || ""} onChange={(e) => { const ed = [...profile.education]; ed[idx] = { ...ed[idx], graduation_year: e.target.value ? parseInt(e.target.value) : null }; setProfile({ ...profile, education: ed }) }} placeholder="Year (2025)" className="h-8 text-sm" />
                    <Input value={edu.cgpa?.toString() || ""} onChange={(e) => { const ed = [...profile.education]; ed[idx] = { ...ed[idx], cgpa: e.target.value ? parseFloat(e.target.value) : null }; setProfile({ ...profile, education: ed }) }} placeholder="CGPA (8.5)" className="h-8 text-sm" />
                    <Input value={edu.current_semester || ""} onChange={(e) => { const ed = [...profile.education]; ed[idx] = { ...ed[idx], current_semester: e.target.value }; setProfile({ ...profile, education: ed }) }} placeholder="Semester (6th)" className="h-8 text-sm" />
                  </div>
                ))}
                <Button type="button" variant="outline" size="sm" onClick={() => setProfile({ ...profile, education: [...profile.education, { college: "", degree: "", branch: "", graduation_year: null, cgpa: null, current_semester: null }] })} className="gap-2 w-full">
                  <Plus className="h-3.5 w-3.5" />Add Education
                </Button>
              </div>
            )}

            {section === "skills" && (
              <div className="space-y-4">
                <SkillTagInput label="Programming Languages" skills={profile.skills.programming_languages} onChange={(v) => updateSkillCategory("programming_languages", v)} />
                <SkillTagInput label="AI / ML / Data Skills" skills={profile.skills.ai_ml_skills} onChange={(v) => updateSkillCategory("ai_ml_skills", v)} />
                <SkillTagInput label="Frameworks & Libraries" skills={profile.skills.frameworks} onChange={(v) => updateSkillCategory("frameworks", v)} />
                <SkillTagInput label="Databases" skills={profile.skills.databases} onChange={(v) => updateSkillCategory("databases", v)} />
                <SkillTagInput label="Cloud & DevOps" skills={profile.skills.cloud_devops} onChange={(v) => updateSkillCategory("cloud_devops", v)} />
                <SkillTagInput label="Tools" skills={profile.skills.tools} onChange={(v) => updateSkillCategory("tools", v)} />
                <p className="text-xs text-muted-foreground flex items-center gap-1.5">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  {profile.all_normalized_skills.length} total unique skills tracked
                </p>
              </div>
            )}

            {section === "projects" && (
              <div className="space-y-3">
                {profile.projects.map((proj, idx) => (
                  <div key={idx} className="p-3 rounded-lg bg-card border border-border/50 space-y-2">
                    <Input value={proj.title} onChange={(e) => { const ps = [...profile.projects]; ps[idx] = { ...ps[idx], title: e.target.value }; setProfile({ ...profile, projects: ps }) }} placeholder="Project Title" className="h-8 text-sm" />
                    <Input value={proj.description} onChange={(e) => { const ps = [...profile.projects]; ps[idx] = { ...ps[idx], description: e.target.value }; setProfile({ ...profile, projects: ps }) }} placeholder="Description" className="h-8 text-sm" />
                    {/* Backend field: tech_stack */}
                    <Input value={proj.tech_stack.join(", ")} onChange={(e) => { const ps = [...profile.projects]; ps[idx] = { ...ps[idx], tech_stack: e.target.value.split(",").map((s) => s.trim()).filter(Boolean) }; setProfile({ ...profile, projects: ps }) }} placeholder="Tech stack (Python, React, ...)" className="h-8 text-sm" />
                    <Input value={proj.github_url || ""} onChange={(e) => { const ps = [...profile.projects]; ps[idx] = { ...ps[idx], github_url: e.target.value }; setProfile({ ...profile, projects: ps }) }} placeholder="GitHub URL" className="h-8 text-sm" />
                  </div>
                ))}
                <Button type="button" variant="outline" size="sm" onClick={() => setProfile({ ...profile, projects: [...profile.projects, { title: "", description: "", tech_stack: [], github_url: null, live_url: null }] })} className="gap-2 w-full">
                  <Plus className="h-3.5 w-3.5" />Add Project
                </Button>
              </div>
            )}

            {section === "experience" && (
              <div className="space-y-3">
                {/* Backend field: experiences (unified list), is_internship flag */}
                {profile.experiences.map((exp, idx) => (
                  <div key={idx} className="p-3 rounded-lg bg-card border border-border/50 space-y-2">
                    <div className="grid grid-cols-2 gap-2">
                      <Input value={exp.role} onChange={(e) => { const es = [...profile.experiences]; es[idx] = { ...es[idx], role: e.target.value }; setProfile({ ...profile, experiences: es }) }} placeholder="Role" className="h-8 text-sm" />
                      <Input value={exp.company} onChange={(e) => { const es = [...profile.experiences]; es[idx] = { ...es[idx], company: e.target.value }; setProfile({ ...profile, experiences: es }) }} placeholder="Company" className="h-8 text-sm" />
                    </div>
                    <Input value={exp.duration || ""} onChange={(e) => { const es = [...profile.experiences]; es[idx] = { ...es[idx], duration: e.target.value }; setProfile({ ...profile, experiences: es }) }} placeholder="Duration (e.g. Jun 2024 – Aug 2024)" className="h-8 text-sm" />
                    <Input value={exp.description || ""} onChange={(e) => { const es = [...profile.experiences]; es[idx] = { ...es[idx], description: e.target.value }; setProfile({ ...profile, experiences: es }) }} placeholder="Description" className="h-8 text-sm" />
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <input type="checkbox" checked={exp.is_internship} onChange={(e) => { const es = [...profile.experiences]; es[idx] = { ...es[idx], is_internship: e.target.checked }; setProfile({ ...profile, experiences: es }) }} className="rounded" />
                      <span>Mark as Internship</span>
                    </div>
                  </div>
                ))}
                <Button type="button" variant="outline" size="sm" onClick={() => setProfile({ ...profile, experiences: [...profile.experiences, { company: "", role: "", duration: null, description: null, is_internship: false, skills_used: [] }] })} className="gap-2 w-full">
                  <Plus className="h-3.5 w-3.5" />Add Experience / Internship
                </Button>
              </div>
            )}

            {section === "preferences" && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-muted-foreground">Experience Level</label>
                  <select value={profile.experience_level} onChange={(e) => setProfile({ ...profile, experience_level: e.target.value })} className="w-full h-9 text-sm rounded-md border border-input bg-background px-3 text-foreground">
                    <option value="entry_level">Entry-level</option>
                    <option value="student">Student / Intern</option>
                    <option value="junior">Junior</option>
                    <option value="mid">Mid-level</option>
                    <option value="senior">Senior</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-muted-foreground">Remote Preference</label>
                  <select value={profile.remote_preference} onChange={(e) => setProfile({ ...profile, remote_preference: e.target.value })} className="w-full h-9 text-sm rounded-md border border-input bg-background px-3 text-foreground">
                    <option value="any">Open to Any</option>
                    <option value="remote_only">Remote Only</option>
                    <option value="hybrid">Hybrid</option>
                    <option value="on_site">On-site Only</option>
                  </select>
                </div>
                <SkillTagInput label="Preferred Roles" skills={profile.preferred_roles} onChange={(v) => setProfile({ ...profile, preferred_roles: v })} />
                <SkillTagInput label="Preferred Locations" skills={profile.preferred_locations} onChange={(v) => setProfile({ ...profile, preferred_locations: v })} />
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-muted-foreground">Expected Salary / Stipend</label>
                  <Input value={profile.expected_salary_or_stipend || ""} onChange={(e) => setProfile({ ...profile, expected_salary_or_stipend: e.target.value })} placeholder="e.g. ₹15 LPA, $80k, ₹25k/mo stipend" className="h-9 text-sm" />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-muted-foreground">Availability</label>
                  <Input value={profile.availability || ""} onChange={(e) => setProfile({ ...profile, availability: e.target.value })} placeholder="e.g. Immediately, 1 month notice" className="h-9 text-sm" />
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {SECTIONS.map((s) => renderSection(s.id))}

      {saveMutation.isError && (
        <p className="text-xs text-destructive">{saveMutation.error?.message || "Failed to save profile."}</p>
      )}

      <div className="flex justify-end pt-2">
        <Button onClick={handleSave} disabled={saveMutation.isPending || !profile.name.trim()} className="gap-2">
          {saveMutation.isPending
            ? <><Loader2 className="h-4 w-4 animate-spin" />Saving...</>
            : <><CheckCircle2 className="h-4 w-4" />Save Profile</>}
        </Button>
      </div>
    </div>
  )
}
