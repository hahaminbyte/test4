type ApiErrorShape = {
  data?: unknown;
  message?: string;
  statusText?: string;
};

export function getApiErrorMessage(error: unknown, fallback = 'Something went wrong.'): string {
  if (!error || typeof error !== 'object') {
    return fallback;
  }

  const apiError = error as ApiErrorShape;

  if (typeof apiError.data === 'string' && apiError.data.trim()) {
    return apiError.data;
  }

  if (apiError.data && typeof apiError.data === 'object') {
    const data = apiError.data as Record<string, unknown>;
    if (typeof data.detail === 'string') {
      return data.detail;
    }
    if (typeof data.error === 'string') {
      return data.error;
    }
    if (typeof data.non_field_errors === 'object' && Array.isArray(data.non_field_errors)) {
      return String(data.non_field_errors[0]);
    }
    const firstFieldError = Object.values(data).find(
      (value) => Array.isArray(value) && value.length > 0
    );
    if (Array.isArray(firstFieldError)) {
      return String(firstFieldError[0]);
    }
  }

  if (typeof apiError.message === 'string' && apiError.message.trim()) {
    return apiError.message;
  }

  return fallback;
}
