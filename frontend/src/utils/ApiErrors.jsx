export function formatApiError(data) {
    if (!data) return "";
    if (typeof data === "string") return data;

    if (typeof data.detail === "string") return data.detail;

    if (typeof data === "object") {
      const parts = [];
      for (const [field, value] of Object.entries(data)) {
        if (Array.isArray(value)) {
          parts.push(`${value.join(" ")}`);
        } else if (typeof value === "string") {
          parts.push(`${value}`);
        }
      }
      return parts.join("\n");
    }

    return "";
}