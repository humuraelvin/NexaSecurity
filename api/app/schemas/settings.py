from pydantic import BaseModel

class UserSettings(BaseModel):
    name: str
    email: str
    company: str
    jobTitle: str
    phone: str

class NotificationPreferences(BaseModel):
    securityAlerts: bool
    weeklyReports: bool
    productUpdates: bool
    marketingEmails: bool

class SecuritySettings(BaseModel):
    twoFactorAuth: bool
    sessionTimeout: str
    ipRestriction: bool
    allowedIPs: str 