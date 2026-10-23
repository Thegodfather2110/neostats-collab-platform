const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

export function getAuthToken(): string {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem("northstar_token") || "";
}

export function setAuthToken(token?: string): void {
  if (typeof window === "undefined") return;
  if (token) {
    window.localStorage.setItem("northstar_token", token);
    return;
  }
  window.localStorage.removeItem("northstar_token");
}

export async function api<T>(path: string, token?: string, init: RequestInit = {}): Promise<T> {
  const requestToken = token ?? getAuthToken();
  const headers = new Headers(init.headers || {});

  if (!headers.has("Content-Type") && !(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (requestToken) {
    headers.set("Authorization", "Bearer " + requestToken);
  }

  let response: Response;
  try {
    response = await fetch(API + (path.startsWith("/") ? path : "/" + path), {
      ...init,
      credentials: "include",
      headers,
    });
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error("Cannot reach the API. Start the backend server and check its database connection.");
    }
    throw error;
  }

  if (response.status === 204) return undefined as T;

  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json") ? await response.json().catch(function () { return {}; }) : await response.text().catch(function () { return ""; });

  if (!response.ok) {
    const message = typeof body !== "string" && body && (body.detail || body.message)
      ? body.detail || body.message
      : response.status >= 500
        ? "The API server returned an error (" + response.status + "). Check the backend terminal and database connection."
        : typeof body === "string" && body
          ? body
          : "Request failed (" + response.status + ")";
    throw new Error(message);
  }

  return (typeof body === "string" ? (body ? JSON.parse(body) as T : undefined) : body) as T;
}
