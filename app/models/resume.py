from typing import List, Optional
from pydantic import BaseModel, Field

class EducationEntry(BaseModel):
    institution: str = Field(description="Name of the school, university, or academy")
    degree: Optional[str] = Field(None, description="Degree obtained (e.g., B.S., M.S., Ph.D., High School Diploma)")
    field_of_study: Optional[str] = Field(None, description="Major, concentration, or field of study")
    start_date: Optional[str] = Field(None, description="Start date of education (e.g., 'Aug 2018' or '2018')")
    end_date: Optional[str] = Field(None, description="End date or graduation date (e.g., 'May 2022' or 'Present')")
    gpa: Optional[str] = Field(None, description="GPA or grade if listed")

class ExperienceEntry(BaseModel):
    company: str = Field(description="Name of the employer or organization")
    role: str = Field(description="Job title or role held")
    start_date: Optional[str] = Field(None, description="Start date of employment")
    end_date: Optional[str] = Field(None, description="End date of employment (e.g., 'Present')")
    location: Optional[str] = Field(None, description="City, state, or country of employment")
    description: List[str] = Field(default_factory=list, description="Bullet points summarizing responsibilities, achievements, and impact")

class ProjectEntry(BaseModel):
    title: str = Field(description="Name or title of the project")
    technologies: List[str] = Field(default_factory=list, description="List of technologies, frameworks, and tools used in the project")
    description: List[str] = Field(default_factory=list, description="Bullet points describing the project, implementation details, and outcomes")
    url: Optional[str] = Field(None, description="URL or repository link for the project if available")

class CertificationEntry(BaseModel):
    name: str = Field(description="Name of the certification or license")
    issuer: Optional[str] = Field(None, description="Organization that issued the certification")
    date_obtained: Optional[str] = Field(None, description="Date or year the certification was earned")

class ParsedResume(BaseModel):
    """Structured representation of a parsed resume."""
    name: str = Field(description="Full name of the candidate")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="Candidate's address, city/state, or region")
    links: List[str] = Field(default_factory=list, description="URLs found in contact info (LinkedIn, GitHub, Portfolio)")
    summary: Optional[str] = Field(None, description="Professional summary or objective statement")
    skills: List[str] = Field(default_factory=list, description="List of technical and soft skills")
    education: List[EducationEntry] = Field(default_factory=list, description="Academic background entries")
    experience: List[ExperienceEntry] = Field(default_factory=list, description="Work history entries")
    projects: List[ProjectEntry] = Field(default_factory=list, description="Personal or professional projects")
    certifications: List[CertificationEntry] = Field(default_factory=list, description="Certifications, licenses, or courses completed")
