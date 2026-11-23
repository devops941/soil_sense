/**
 * API client for SoilSense FastAPI backend
 */

const BASE_URL = "/api/v1";

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const headers = { ...options.headers };

  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(url, { ...options, headers });
  if (!response.ok) {
    let errorDetail = "An unexpected error occurred.";
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.message || JSON.stringify(errJson);
    } catch {
      errorDetail = await response.text();
    }
    throw new Error(errorDetail);
  }

  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  // Dashboard
  getDashboardSummary: (dataSource = "", locationId = "") => {
    const params = new URLSearchParams();
    if (dataSource && dataSource !== "all") params.append("data_source", dataSource);
    if (locationId) params.append("location_id", locationId);
    return request(`/dashboard/summary?${params.toString()}`);
  },

  // Samples
  getSamples: ({ page = 1, perPage = 20, search = "", locationId = "", dataSource = "", fertilityClass = "" } = {}) => {
    const params = new URLSearchParams();
    params.append("page", page);
    params.append("per_page", perPage);
    if (search) params.append("search", search);
    if (locationId) params.append("location_id", locationId);
    if (dataSource && dataSource !== "all") params.append("data_source", dataSource);
    if (fertilityClass && fertilityClass !== "all") params.append("fertility_class", fertilityClass);
    return request(`/samples?${params.toString()}`);
  },

  getSample: (id) => request(`/samples/${id}`),

  createSample: (sampleData) =>
    request("/samples", {
      method: "POST",
      body: JSON.stringify(sampleData),
    }),

  updateSample: (id, sampleData) =>
    request(`/samples/${id}`, {
      method: "PUT",
      body: JSON.stringify(sampleData),
    }),

  deleteSample: (id) =>
    request(`/samples/${id}`, {
      method: "DELETE",
    }),

  // Uploads
  uploadCSV: (file, dataSource = "verified", locationName = "") => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("data_source", dataSource);
    if (locationName) formData.append("location_name", locationName);
    return request("/uploads", {
      method: "POST",
      body: formData,
    });
  },

  validateCSV: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return request("/uploads/validate", {
      method: "POST",
      body: formData,
    });
  },

  getTemplateDownloadUrl: () => `${BASE_URL}/uploads/template`,

  // Analytics & Statistics
  getSummaryStats: (dataSource = "all") => {
    const params = new URLSearchParams();
    if (dataSource && dataSource !== "all") params.append("data_source", dataSource);
    return request(`/analysis/summary-stats?${params.toString()}`);
  },

  getDistribution: (parameter = "ph", bins = 15, dataSource = "all") => {
    const params = new URLSearchParams();
    params.append("parameter", parameter);
    params.append("bins", bins);
    if (dataSource && dataSource !== "all") params.append("data_source", dataSource);
    return request(`/analysis/distribution?${params.toString()}`);
  },

  getFertilityDistribution: (dataSource = "all") => {
    const params = new URLSearchParams();
    if (dataSource && dataSource !== "all") params.append("data_source", dataSource);
    return request(`/analysis/fertility-distribution?${params.toString()}`);
  },

  getCorrelationMatrix: (dataSource = "all") => {
    const params = new URLSearchParams();
    if (dataSource && dataSource !== "all") params.append("data_source", dataSource);
    return request(`/analysis/correlation?${params.toString()}`);
  },

  getLocationComparison: (parameter = "ph", dataSource = "all") => {
    const params = new URLSearchParams();
    params.append("parameter_code", parameter);
    if (dataSource && dataSource !== "all") params.append("data_source", dataSource);
    return request(`/statistics/location-comparison?${params.toString()}`);
  },

  runTTest: (body) =>
    request("/statistics/ttest", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  // Locations & Thresholds
  getLocations: () => request("/locations?per_page=100"),
  getThresholds: (standard = "TNAU") => request(`/thresholds?standard=${standard}`),

  // Reports URLs
  getSamplePdfUrl: (sampleId) => `${BASE_URL}/reports/samples/${sampleId}/pdf`,
  getDatasetPdfUrl: (dataSource = "", locationId = "") => {
    const params = new URLSearchParams();
    if (dataSource && dataSource !== "all") params.append("data_source", dataSource);
    if (locationId) params.append("location_id", locationId);
    return `${BASE_URL}/reports/dataset/pdf?${params.toString()}`;
  },
  getSamplesCsvUrl: (dataSource = "") => {
    const params = new URLSearchParams();
    if (dataSource && dataSource !== "all") params.append("data_source", dataSource);
    return `${BASE_URL}/exports/samples.csv?${params.toString()}`;
  },
  getClassificationCsvUrl: (dataSource = "") => {
    const params = new URLSearchParams();
    if (dataSource && dataSource !== "all") params.append("data_source", dataSource);
    return `${BASE_URL}/exports/classification-results.csv?${params.toString()}`;
  },
};
