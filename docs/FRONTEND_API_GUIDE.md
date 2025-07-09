# Frontend API Guide - Guía Completa de Endpoints

Esta guía proporciona todos los endpoints disponibles organizados por entidad con instrucciones completas para la implementación CRUD en el frontend.

## 🔐 Autenticación

**IMPORTANTE**: Todos los endpoints de la API requieren autenticación mediante API Key.

```javascript
// Headers requeridos en todas las requests
headers: {
  'Content-Type': 'application/json',
  'X-API-Key': 'demo-key-123'  // o tu API key configurada
}
```

## 📋 Base URL

```
http://localhost:5000/api
```

---

## 👥 CUSTOMERS (Clientes)

### 1. GET - Listar Clientes (Read/List)

```javascript
// GET /api/customers
const getCustomers = async (params = {}) => {
  const queryParams = new URLSearchParams({
    page: params.page || 1,
    per_page: params.per_page || 10,
    ...(params.status && { status: params.status }),
    ...(params.search && { search: params.search })
  });

  const response = await fetch(`${API_BASE}/customers?${queryParams}`, {
    headers: { 'X-API-Key': API_KEY }
  });
  return response.json();
};

// Respuesta:
{
  "customers": [
    {
      "_id": "64f8c1234567890abcdef123",
      "name": "Juan Pérez",
      "email": "juan@email.com",
      "status": "active",
      "created_at": "2023-09-07T10:00:00.000Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 25,
    "pages": 3
  }
}
```

### 2. POST - Crear Cliente (Create)

```javascript
// POST /api/customers
const createCustomer = async (customerData) => {
  const response = await fetch(`${API_BASE}/customers`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
    },
    body: JSON.stringify({
      name: customerData.name, // Requerido
      email: customerData.email, // Requerido, único
      phone: customerData.phone, // Opcional
      address: customerData.address, // Opcional
      city: customerData.city, // Opcional
      country: customerData.country, // Opcional
      postal_code: customerData.postal_code, // Opcional
      status: customerData.status || "active", // active, inactive, suspended
    }),
  });
  return response.json();
};

// Ejemplo de uso:
const newCustomer = await createCustomer({
  name: "María García",
  email: "maria@email.com",
  phone: "+34123456789",
  address: "Calle Principal 123",
  city: "Madrid",
  country: "España",
  postal_code: "28001",
});
```

### 3. GET - Obtener Cliente por ID (Read/Detail)

```javascript
// GET /api/customers/{id}
const getCustomer = async (customerId) => {
  const response = await fetch(`${API_BASE}/customers/${customerId}`, {
    headers: { "X-API-Key": API_KEY },
  });
  return response.json();
};
```

### 4. PUT - Actualizar Cliente (Update)

```javascript
// PUT /api/customers/{id}
const updateCustomer = async (customerId, updateData) => {
  const response = await fetch(`${API_BASE}/customers/${customerId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
    },
    body: JSON.stringify(updateData), // Solo campos a actualizar
  });
  return response.json();
};

// Ejemplo:
const updatedCustomer = await updateCustomer("64f8c1234567890abcdef123", {
  phone: "+34987654321",
  status: "inactive",
});
```

### 5. DELETE - Eliminar Cliente (Delete)

```javascript
// DELETE /api/customers/{id}
const deleteCustomer = async (customerId) => {
  const response = await fetch(`${API_BASE}/customers/${customerId}`, {
    method: "DELETE",
    headers: { "X-API-Key": API_KEY },
  });
  return response.json();
};

// Nota: No se puede eliminar un cliente con suscripciones activas
```

---

## 🎯 PRODUCTS (Productos)

### 1. GET - Listar Productos (Read/List)

```javascript
// GET /api/products
const getProducts = async (params = {}) => {
  const queryParams = new URLSearchParams({
    page: params.page || 1,
    per_page: params.per_page || 10,
    ...(params.is_active !== undefined && { is_active: params.is_active }),
    ...(params.billing_cycle && { billing_cycle: params.billing_cycle }),
    ...(params.customizable !== undefined && {
      customizable: params.customizable,
    }),
    ...(params.search && { search: params.search }),
  });

  const response = await fetch(`${API_BASE}/products?${queryParams}`, {
    headers: { "X-API-Key": API_KEY },
  });
  return response.json();
};
```

### 2. POST - Crear Producto (Create)

```javascript
// POST /api/products
const createProduct = async (productData) => {
  const response = await fetch(`${API_BASE}/products`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
    },
    body: JSON.stringify({
      name: productData.name, // Requerido, único
      description: productData.description, // Opcional
      price: productData.price, // Requerido, decimal
      currency: productData.currency || "EUR", // USD, EUR, etc.
      billing_cycle: productData.billing_cycle, // monthly, yearly
      is_active: productData.is_active ?? true,
      trial_days: productData.trial_days || 0,
      customizable: productData.customizable ?? false,
      customizable_fields: productData.customizable_fields || [],
      default_settings: productData.default_settings || {},
      metadata: productData.metadata,
    }),
  });
  return response.json();
};

// Ejemplo con customización:
const newProduct = await createProduct({
  name: "Plan Premium",
  description: "Plan premium con todas las funcionalidades",
  price: 29.99,
  currency: "EUR",
  billing_cycle: "monthly",
  trial_days: 7,
  customizable: true,
  customizable_fields: ["topBarColor", "topBarBackgroundColor", "defaultLang"],
  default_settings: {
    topBarColor: "#ffffff",
    topBarBackgroundColor: "#007bff",
    defaultLang: "es",
  },
});
```

### 3. GET - Obtener Producto por ID (Read/Detail)

```javascript
// GET /api/products/{id}
const getProduct = async (productId) => {
  const response = await fetch(`${API_BASE}/products/${productId}`, {
    headers: { "X-API-Key": API_KEY },
  });
  return response.json();
};
```

### 4. PUT - Actualizar Producto (Update)

```javascript
// PUT /api/products/{id}
const updateProduct = async (productId, updateData) => {
  const response = await fetch(`${API_BASE}/products/${productId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
    },
    body: JSON.stringify(updateData),
  });
  return response.json();
};
```

### 5. DELETE - Eliminar Producto (Delete)

```javascript
// DELETE /api/products/{id}
const deleteProduct = async (productId) => {
  const response = await fetch(`${API_BASE}/products/${productId}`, {
    method: "DELETE",
    headers: { "X-API-Key": API_KEY },
  });
  return response.json();
};

// Nota: No se puede eliminar un producto con suscripciones activas
```

### 6. POST - Activar Producto

```javascript
// POST /api/products/{id}/activate
const activateProduct = async (productId) => {
  const response = await fetch(`${API_BASE}/products/${productId}/activate`, {
    method: "POST",
    headers: { "X-API-Key": API_KEY },
  });
  return response.json();
};
```

### 7. POST - Desactivar Producto

```javascript
// POST /api/products/{id}/deactivate
const deactivateProduct = async (productId) => {
  const response = await fetch(`${API_BASE}/products/${productId}/deactivate`, {
    method: "POST",
    headers: { "X-API-Key": API_KEY },
  });
  return response.json();
};
```

---

## 📄 SUBSCRIPTIONS (Suscripciones)

### 1. GET - Listar Suscripciones (Read/List)

```javascript
// GET /api/subscriptions
const getSubscriptions = async (params = {}) => {
  const queryParams = new URLSearchParams({
    page: params.page || 1,
    per_page: params.per_page || 10,
    ...(params.status && { status: params.status }),
    ...(params.customer_id && { customer_id: params.customer_id }),
  });

  const response = await fetch(`${API_BASE}/subscriptions?${queryParams}`, {
    headers: { "X-API-Key": API_KEY },
  });
  return response.json();
};
```

### 2. POST - Suscribir (Create - Recomendado)

```javascript
// POST /api/subscribe - Endpoint avanzado con herencia automática
const subscribe = async (subscriptionData) => {
  const response = await fetch(`${API_BASE}/subscribe`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
    },
    body: JSON.stringify({
      customer_id: subscriptionData.customer_id, // Requerido
      product_id: subscriptionData.product_id, // Requerido

      // Campos opcionales - se heredan del producto si no se especifican
      amount: subscriptionData.amount, // Hereda de product.price
      currency: subscriptionData.currency, // Hereda de product.currency
      billing_cycle: subscriptionData.billing_cycle, // Hereda de product.billing_cycle

      // Customización
      custom_settings: subscriptionData.custom_settings || {},

      // Fechas específicas
      end_date: subscriptionData.end_date, // Sobrescribe cálculo automático
      trial_end_date: subscriptionData.trial_end_date,

      // Configuración
      auto_renew: subscriptionData.auto_renew ?? true,
      metadata: subscriptionData.metadata,
    }),
  });
  return response.json();
};

// Ejemplo mínimo (hereda todo del producto):
const basicSubscription = await subscribe({
  customer_id: "64f8c1234567890abcdef123",
  product_id: "64f8c9876543210fedcba987",
});

// Ejemplo con customización:
const customSubscription = await subscribe({
  customer_id: "64f8c1234567890abcdef123",
  product_id: "64f8c9876543210fedcba987",
  custom_settings: {
    topBarColor: "#ff0000",
    defaultLang: "en",
  },
  metadata: { campaign: "summer2023" },
});
```

### 3. POST - Crear Suscripción (Create - Básico)

```javascript
// POST /api/subscriptions - Endpoint básico
const createSubscription = async (subscriptionData) => {
  const response = await fetch(`${API_BASE}/subscriptions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
    },
    body: JSON.stringify({
      customer_id: subscriptionData.customer_id, // Requerido
      product_id: subscriptionData.product_id, // Opcional
      amount: subscriptionData.amount, // Requerido
      currency: subscriptionData.currency, // Requerido
      billing_cycle: subscriptionData.billing_cycle, // monthly, yearly
      status: subscriptionData.status || "active",
      custom_settings: subscriptionData.custom_settings || {},
    }),
  });
  return response.json();
};
```

### 4. GET - Obtener Suscripción por ID (Read/Detail)

```javascript
// GET /api/subscriptions/{id}
const getSubscription = async (subscriptionId) => {
  const response = await fetch(`${API_BASE}/subscriptions/${subscriptionId}`, {
    headers: { "X-API-Key": API_KEY },
  });
  return response.json();
};
```

### 5. PUT - Actualizar Suscripción (Update)

```javascript
// PUT /api/subscriptions/{id}
const updateSubscription = async (subscriptionId, updateData) => {
  const response = await fetch(`${API_BASE}/subscriptions/${subscriptionId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
    },
    body: JSON.stringify(updateData),
  });
  return response.json();
};
```

### 6. DELETE - Eliminar Suscripción (Delete)

```javascript
// DELETE /api/subscriptions/{id}
const deleteSubscription = async (subscriptionId) => {
  const response = await fetch(`${API_BASE}/subscriptions/${subscriptionId}`, {
    method: "DELETE",
    headers: { "X-API-Key": API_KEY },
  });
  return response.json();
};
```

### 7. GET - Obtener Configuraciones de Suscripción

```javascript
// GET /api/subscriptions/{id}/settings
const getSubscriptionSettings = async (subscriptionId) => {
  const response = await fetch(`${API_BASE}/subscriptions/${subscriptionId}/settings`, {
    headers: { 'X-API-Key': API_KEY }
  });
  return response.json();
};

// Respuesta:
{
  "subscription_id": "64f8c...",
  "product_defaults": { "topBarColor": "#ffffff" },
  "custom_settings": { "topBarColor": "#ff0000" },
  "effective_settings": { "topBarColor": "#ff0000" }
}
```

### 8. PUT - Actualizar Configuraciones de Suscripción

```javascript
// PUT /api/subscriptions/{id}/settings
const updateSubscriptionSettings = async (subscriptionId, customSettings) => {
  const response = await fetch(
    `${API_BASE}/subscriptions/${subscriptionId}/settings`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
      },
      body: JSON.stringify({
        custom_settings: customSettings,
      }),
    }
  );
  return response.json();
};
```

### 9. POST - Aplicar Configuraciones por Defecto del Producto

```javascript
// POST /api/subscriptions/{id}/apply-defaults
const applyProductDefaults = async (subscriptionId) => {
  const response = await fetch(
    `${API_BASE}/subscriptions/${subscriptionId}/apply-defaults`,
    {
      method: "POST",
      headers: { "X-API-Key": API_KEY },
    }
  );
  return response.json();
};
```

### 10. GET - Obtener Estado de Suscripción

```javascript
// GET /api/subscriptions/{id}/status
const getSubscriptionStatus = async (subscriptionId) => {
  const response = await fetch(`${API_BASE}/subscriptions/${subscriptionId}/status`, {
    headers: { 'X-API-Key': API_KEY }
  });
  return response.json();
};

// Respuesta:
{
  "subscription_id": "64f8c...",
  "status": "active",
  "is_active": true,
  "is_expired": false,
  "start_date": "2023-09-01T00:00:00.000Z",
  "end_date": "2023-10-01T00:00:00.000Z"
}
```

### 11. POST - Extender Suscripción

```javascript
// POST /api/subscriptions/{id}/extend
const extendSubscription = async (subscriptionId, extensionData) => {
  const response = await fetch(
    `${API_BASE}/subscriptions/${subscriptionId}/extend`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
      },
      body: JSON.stringify({
        // Opción 1: Fecha específica
        end_date: "2024-01-01T00:00:00.000Z",

        // Opción 2: Días de extensión
        // extension_days: 30
      }),
    }
  );
  return response.json();
};
```

### 12. POST - Cancelar Suscripción

```javascript
// POST /api/subscriptions/{id}/cancel
const cancelSubscription = async (subscriptionId) => {
  const response = await fetch(
    `${API_BASE}/subscriptions/${subscriptionId}/cancel`,
    {
      method: "POST",
      headers: { "X-API-Key": API_KEY },
    }
  );
  return response.json();
};
```

### 13. POST - Renovar Suscripción

```javascript
// POST /api/subscriptions/{id}/renew
const renewSubscription = async (subscriptionId) => {
  const response = await fetch(
    `${API_BASE}/subscriptions/${subscriptionId}/renew`,
    {
      method: "POST",
      headers: { "X-API-Key": API_KEY },
    }
  );
  return response.json();
};
```

---

## 📊 ANALYTICS & STATS

### 1. GET - Estadísticas de Suscripciones

```javascript
// GET /api/subscriptions/stats
const getSubscriptionStats = async () => {
  const response = await fetch(`${API_BASE}/subscriptions/stats`, {
    headers: { 'X-API-Key': API_KEY }
  });
  return response.json();
};

// Respuesta:
{
  "total_subscriptions": 156,
  "active_subscriptions": 123,
  "monthly_revenue": 2847.50,
  "status_breakdown": [
    { "_id": "active", "count": 123 },
    { "_id": "canceled", "count": 20 },
    { "_id": "expired", "count": 13 }
  ]
}
```

### 2. GET - Métricas Financieras Avanzadas

```javascript
// GET /api/analytics/financial-metrics
const getFinancialMetrics = async (periodMonths = 12) => {
  const response = await fetch(`${API_BASE}/analytics/financial-metrics?period_months=${periodMonths}`, {
    headers: { 'X-API-Key': API_KEY }
  });
  return response.json();
};

// Respuesta:
{
  "period_months": 12,
  "mrr": { "value": 2847.50, "description": "Monthly Recurring Revenue", "unit": "EUR/month" },
  "arr": { "value": 34170.00, "description": "Annual Recurring Revenue", "unit": "EUR/year" },
  "arpu": { "value": 23.15, "description": "Average Revenue Per User", "unit": "EUR/month" },
  "clv": { "value": 277.80, "description": "Customer Lifetime Value", "unit": "EUR" },
  "crr": { "value": 0.89, "description": "Customer Retention Rate", "unit": "ratio" },
  "churn_rate": { "value": 0.11, "description": "Customer Churn Rate", "unit": "ratio" },
  "aov": { "value": 29.99, "description": "Average Order Value", "unit": "EUR" },
  "rpr": { "value": 0.75, "description": "Repeat Purchase Rate", "unit": "ratio" }
}
```

---

## 🛠️ UTILITY ENDPOINTS

### Health Check

```javascript
// GET /health
const healthCheck = async () => {
  const response = await fetch(`${API_BASE_ROOT}/health`);
  return response.json();
};
```

### Root Info

```javascript
// GET /
const getRootInfo = async () => {
  const response = await fetch(`${API_BASE_ROOT}/`);
  return response.json();
};
```

---

## 🎨 Guía de Implementación para Frontend

### 1. Configuración Base

```javascript
// config/api.js
const API_BASE_ROOT = "http://localhost:5000";
const API_BASE = `${API_BASE_ROOT}/api`;
const API_KEY = process.env.REACT_APP_API_KEY || "demo-key-123";

// Configuración de fetch con interceptores
const apiCall = async (url, options = {}) => {
  const config = {
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "API Error");
    }

    return data;
  } catch (error) {
    console.error("API Call Error:", error);
    throw error;
  }
};
```

### 2. Servicios por Entidad

```javascript
// services/customerService.js
export const customerService = {
  getAll: (params) =>
    apiCall(`${API_BASE}/customers?${new URLSearchParams(params)}`),
  getById: (id) => apiCall(`${API_BASE}/customers/${id}`),
  create: (data) =>
    apiCall(`${API_BASE}/customers`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id, data) =>
    apiCall(`${API_BASE}/customers/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  delete: (id) => apiCall(`${API_BASE}/customers/${id}`, { method: "DELETE" }),
};

// services/productService.js
export const productService = {
  getAll: (params) =>
    apiCall(`${API_BASE}/products?${new URLSearchParams(params)}`),
  getById: (id) => apiCall(`${API_BASE}/products/${id}`),
  create: (data) =>
    apiCall(`${API_BASE}/products`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id, data) =>
    apiCall(`${API_BASE}/products/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  delete: (id) => apiCall(`${API_BASE}/products/${id}`, { method: "DELETE" }),
  activate: (id) =>
    apiCall(`${API_BASE}/products/${id}/activate`, { method: "POST" }),
  deactivate: (id) =>
    apiCall(`${API_BASE}/products/${id}/deactivate`, { method: "POST" }),
};

// services/subscriptionService.js
export const subscriptionService = {
  getAll: (params) =>
    apiCall(`${API_BASE}/subscriptions?${new URLSearchParams(params)}`),
  getById: (id) => apiCall(`${API_BASE}/subscriptions/${id}`),
  subscribe: (data) =>
    apiCall(`${API_BASE}/subscribe`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  create: (data) =>
    apiCall(`${API_BASE}/subscriptions`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id, data) =>
    apiCall(`${API_BASE}/subscriptions/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  delete: (id) =>
    apiCall(`${API_BASE}/subscriptions/${id}`, { method: "DELETE" }),
  getSettings: (id) => apiCall(`${API_BASE}/subscriptions/${id}/settings`),
  updateSettings: (id, settings) =>
    apiCall(`${API_BASE}/subscriptions/${id}/settings`, {
      method: "PUT",
      body: JSON.stringify({ custom_settings: settings }),
    }),
  getStatus: (id) => apiCall(`${API_BASE}/subscriptions/${id}/status`),
  extend: (id, data) =>
    apiCall(`${API_BASE}/subscriptions/${id}/extend`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  cancel: (id) =>
    apiCall(`${API_BASE}/subscriptions/${id}/cancel`, { method: "POST" }),
  renew: (id) =>
    apiCall(`${API_BASE}/subscriptions/${id}/renew`, { method: "POST" }),
  getStats: () => apiCall(`${API_BASE}/subscriptions/stats`),
};

// services/analyticsService.js
export const analyticsService = {
  getFinancialMetrics: (periodMonths = 12) =>
    apiCall(
      `${API_BASE}/analytics/financial-metrics?period_months=${periodMonths}`
    ),
};
```

### 3. Hooks de React (opcional)

```javascript
// hooks/useCustomers.js
import { useState, useEffect } from "react";
import { customerService } from "../services/customerService";

export const useCustomers = (params = {}) => {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({});

  useEffect(() => {
    const fetchCustomers = async () => {
      try {
        setLoading(true);
        const response = await customerService.getAll(params);
        setCustomers(response.customers);
        setPagination(response.pagination);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchCustomers();
  }, [JSON.stringify(params)]);

  return { customers, loading, error, pagination };
};
```

### 4. Manejo de Errores

```javascript
// utils/errorHandler.js
export const handleApiError = (error) => {
  if (error.response) {
    // Error de respuesta del servidor
    switch (error.response.status) {
      case 400:
        return "Datos inválidos. Verifica los campos.";
      case 401:
        return "API Key inválida o faltante.";
      case 404:
        return "Recurso no encontrado.";
      case 409:
        return "El recurso ya existe.";
      case 500:
        return "Error interno del servidor.";
      default:
        return error.response.data?.error || "Error desconocido";
    }
  }
  return "Error de conexión. Verifica tu internet.";
};
```

### 5. Estados y Constantes

```javascript
// constants/api.js
export const CUSTOMER_STATUS = {
  ACTIVE: "active",
  INACTIVE: "inactive",
  SUSPENDED: "suspended",
};

export const SUBSCRIPTION_STATUS = {
  ACTIVE: "active",
  TRIAL: "trial",
  CANCELED: "canceled",
  EXPIRED: "expired",
  PENDING: "pending",
};

export const BILLING_CYCLES = {
  MONTHLY: "monthly",
  YEARLY: "yearly",
};

export const CURRENCIES = ["USD", "EUR", "GBP", "CAD", "AUD"];
```

---

## 🚀 Flujo de Trabajo Recomendado

### 1. Dashboard Principal

```javascript
// Obtener métricas para dashboard
const dashboardData = await Promise.all([
  subscriptionService.getStats(),
  analyticsService.getFinancialMetrics(12),
  customerService.getAll({ page: 1, per_page: 5 }),
  subscriptionService.getAll({ status: "active", page: 1, per_page: 5 }),
]);
```

### 2. Crear Nueva Suscripción (Flujo Completo)

```javascript
// 1. Obtener clientes y productos
const customers = await customerService.getAll();
const products = await productService.getAll({ is_active: true });

// 2. Suscribir usando el endpoint avanzado
const subscription = await subscriptionService.subscribe({
  customer_id: selectedCustomerId,
  product_id: selectedProductId,
  custom_settings: {
    topBarColor: "#ff0000",
    defaultLang: "es",
  },
});

// 3. Confirmar y mostrar configuraciones efectivas
const settings = await subscriptionService.getSettings(subscription._id);
```

### 3. Gestión de Configuraciones

```javascript
// Obtener configuraciones actuales
const settings = await subscriptionService.getSettings(subscriptionId);

// Actualizar configuraciones específicas
await subscriptionService.updateSettings(subscriptionId, {
  topBarColor: "#00ff00",
  positionIndex: 2,
});

// Resetear a defaults del producto
await subscriptionService.applyDefaults(subscriptionId);
```

---

Esta guía te proporciona todo lo necesario para implementar un frontend completo que interactúe con la API. Cada endpoint está documentado con ejemplos prácticos y patrones de uso recomendados.
