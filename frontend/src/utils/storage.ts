/**
 * Reads and parses JSON from localStorage.
 * Returns the provided fallback when data is missing or invalid.
 */
export function loadJson<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return fallback;
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

/**
 * Serializes and saves a value into localStorage as JSON.
 * Silently ignores write failures (for example quota or privacy mode).
 */
export function saveJson(key: string, value: unknown) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Ignore storage write errors.
  }
}
