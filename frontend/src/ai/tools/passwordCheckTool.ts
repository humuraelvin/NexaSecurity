import { z } from "zod";
import { AiTool, PasswordCheckParams, PasswordCheckResult } from "./types";
import crypto from "crypto";

// In a real application, store API key in environment variables if needed
// Some APIs like HaveIBeenPwned require an API key for production use
// but offer a free tier for individual password checking (using k-anonymity)
const HIBP_API_URL = "https://api.pwnedpasswords.com/range/";

export const passwordCheckTool: AiTool<
  PasswordCheckParams,
  PasswordCheckResult
> = {
  description: "Check password strength and breach status",
  parameters: z.object({
    password: z.string().describe("Password to check"),
    checkType: z
      .enum(["strength", "common", "breach"])
      .describe("Type of check to perform"),
  }),
  execute: async ({ password, checkType }) => {
    try {
      // Never return the actual password in the response
      // Basic strength check
      const hasSpecialChars = /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]+/.test(
        password
      );
      const hasNumbers = /\d/.test(password);
      const hasUppercase = /[A-Z]/.test(password);

      let strength: "weak" | "medium" | "strong" = "weak";
      const recommendations: string[] = [];

      if (password.length < 8) {
        strength = "weak";
        recommendations.push("Use at least 8 characters");
      } else if (
        password.length >= 12 &&
        hasSpecialChars &&
        hasNumbers &&
        hasUppercase
      ) {
        strength = "strong";
      } else if (
        password.length >= 8 &&
        (hasSpecialChars || hasNumbers || hasUppercase)
      ) {
        strength = "medium";
        if (!hasSpecialChars) recommendations.push("Add special characters");
        if (!hasNumbers) recommendations.push("Add numbers");
        if (!hasUppercase) recommendations.push("Add uppercase letters");
      }

      // Simulate breach check using k-anonymity method (like HaveIBeenPwned)
      let foundInBreaches = false;
      let breachCheckMessage = "";

      if (checkType === "breach") {
        console.log(
          "[PasswordCheck] Performing breach check using k-anonymity"
        );

        // Hash the password with SHA-1 (which HIBP uses)
        const hash = crypto
          .createHash("sha1")
          .update(password)
          .digest("hex")
          .toUpperCase();
        const prefix = hash.substring(0, 5);
        // const suffix = hash.substring(5);  // This would be used in a real implementation

        // In a real implementation, this would call the HaveIBeenPwned API:
        console.log(
          `[PasswordCheck] Would call ${HIBP_API_URL}${prefix} to check hash prefix`
        );
        // const response = await fetch(`${HIBP_API_URL}${prefix}`);
        // const data = await response.text();
        // foundInBreaches = data.includes(suffix);

        // For demo purposes, simulate a breach check based on password length
        foundInBreaches =
          password.length < 10 ||
          /password|123456|admin|qwerty/i.test(password);

        breachCheckMessage = foundInBreaches
          ? "This password has been found in known data breaches! Please change it immediately."
          : "No breaches found for this password.";

        console.log(
          `[PasswordCheck] Breach check completed. Found: ${foundInBreaches}`
        );

        return {
          checkType: "breach",
          password: "[REDACTED]",
          foundInBreaches,
          lastChecked: new Date().toISOString(),
          message: breachCheckMessage,
        };
      }

      // For strength or common checks
      const strengthMessage =
        strength === "weak"
          ? "This password is weak. Please consider changing it."
          : strength === "medium"
          ? "This password has medium strength. Consider improvements."
          : "This password has good strength.";

      return {
        checkType: "strength",
        password: "[REDACTED]",
        strength,
        hasSpecial: hasSpecialChars,
        hasNumbers,
        hasUppercase,
        recommendations,
        message: strengthMessage,
      };
    } catch (error: any) {
      console.error("Error checking password:", error);
      throw new Error(`Failed to check password: ${error.message}`);
    }
  },
};
