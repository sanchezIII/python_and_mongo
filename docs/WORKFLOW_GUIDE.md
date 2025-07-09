# 🚀 Guía de Flujo de Trabajo - Sistema de Subscripciones

Esta guía te llevará paso a paso a través de todas las funcionalidades del sistema de subscripciones implementado.

## 📋 Prerrequisitos

1. Asegúrate de que el servidor Flask esté corriendo en `http://localhost:5001`
2. MongoDB debe estar disponible
3. (Opcional) Ejecuta el script de seeding para datos de ejemplo
4. **⚠️ Importante**: Todos los endpoints `/api/*` requieren autenticación con API key

## 🔐 Autenticación

Todas las peticiones a la API requieren incluir el header `X-API-Key`:

```bash
-H "X-API-Key: demo-key-123"
```

**API Keys disponibles:**

- `demo-key-123` - Para desarrollo y pruebas
- `prod-key-456` - Para producción
- `client-key-789` - Para clientes

## 🔍 Flujo de Trabajo Completo

### 1️⃣ **Health Check**

Verifica que el sistema esté funcionando correctamente.

```bash
curl -X GET http://localhost:5001/health
```

**Respuesta esperada:**

```json
{
  "status": "healthy",
  "database": "connected",
  "version": "v1"
}
```

---

### 2️⃣ **Registrar un Cliente (Register)**

Crea un nuevo cliente en el sistema.

```bash
curl -X POST http://localhost:5001/api/customers \
-H "X-API-Key: demo-key-123" \
-H "Content-Type: application/json" \
-d '{
  "name": "María González",
  "email": "maria.gonzalez@example.com",
  "phone": "+1234567890",
  "address": "Calle Principal 123",
  "city": "Madrid",
  "country": "Spain",
  "postal_code": "28001",
  "status": "active"
}'
```

**Respuesta esperada:**

```json
{
  "_id": "507f1f77bcf86cd799439011",
  "name": "María González",
  "email": "maria.gonzalez@example.com",
  "status": "active",
  "created_at": "2024-01-15T10:00:00Z",
  ...
}
```

📝 **Guarda el `_id` del cliente para los siguientes pasos**

---

### 3️⃣ **Agregar un Producto (AddProduct)**

Crea un producto con capacidades de customización.

```bash
curl -X POST http://localhost:5001/api/products \
-H "X-API-Key: demo-key-123" \
-H "Content-Type: application/json" \
-d '{
  "name": "Plan Premium Pro",
  "description": "Plan premium con funcionalidades avanzadas y customización",
  "price": 49.99,
  "currency": "EUR",
  "billing_cycle": "monthly",
  "trial_period_days": 14,
  "features": [
    "Soporte 24/7",
    "Almacenamiento ilimitado",
    "Customización completa",
    "API avanzada"
  ],
  "is_active": true,
  "customizable": true,
  "customizable_fields": [
    "topBarColor",
    "topBarBackgroundColor",
    "topBarButtonBackgroundColor",
    "defaultLang"
  ],
  "default_settings": {
    "topBarColor": "#ffffff",
    "topBarBackgroundColor": "#000000",
    "topBarButtonBackgroundColor": "#007bff",
    "defaultLang": "es"
  }
}'
```

**Respuesta esperada:**

```json
{
  "_id": "507f1f77bcf86cd799439013",
  "name": "Plan Premium Pro",
  "price": 49.99,
  "customizable": true,
  "default_settings": {
    "topBarColor": "#ffffff",
    "topBarBackgroundColor": "#000000",
    ...
  },
  ...
}
```

📝 **Guarda el `_id` del producto para los siguientes pasos**

---

### 4️⃣ **Subscribir Cliente a Producto (Subscribe)**

Realiza una subscripción con customización personalizada.

```bash
curl -X POST http://localhost:5001/api/subscribe \
-H "X-API-Key: demo-key-123" \
-H "Content-Type: application/json" \
-d '{
  "customer_id": "507f1f77bcf86cd799439011",
  "product_id": "507f1f77bcf86cd799439013",
  "custom_settings": {
    "topBarColor": "#ff0000",
    "topBarBackgroundColor": "#ffffff",
    "defaultLang": "en"
  },
  "metadata": {
    "source": "workflow_test",
    "campaign": "demo_2024"
  }
}'
```

**Respuesta esperada:**

```json
{
  "_id": "507f1f77bcf86cd799439014",
  "customer_id": "507f1f77bcf86cd799439011",
  "product_id": "507f1f77bcf86cd799439013",
  "status": "active",
  "amount": 49.99,
  "currency": "EUR",
  "billing_cycle": "monthly",
  "custom_settings": {
    "topBarColor": "#ff0000",
    "topBarBackgroundColor": "#ffffff",
    "topBarButtonBackgroundColor": "#007bff",
    "defaultLang": "en"
  },
  "product_info": {
    "name": "Plan Premium Pro",
    "customizable": true
  },
  ...
}
```

📝 **Guarda el `_id` de la subscripción para los siguientes pasos**

---

### 5️⃣ **Obtener Configuraciones (GetSettings)**

Consulta las configuraciones efectivas de la subscripción.

```bash
curl -X GET http://localhost:5001/api/subscriptions/507f1f77bcf86cd799439014/settings \
-H "X-API-Key: demo-key-123"
```

**Respuesta esperada:**

```json
{
  "subscription_id": "507f1f77bcf86cd799439014",
  "product_defaults": {
    "topBarColor": "#ffffff",
    "topBarBackgroundColor": "#000000",
    "topBarButtonBackgroundColor": "#007bff",
    "defaultLang": "es"
  },
  "custom_settings": {
    "topBarColor": "#ff0000",
    "topBarBackgroundColor": "#ffffff",
    "defaultLang": "en"
  },
  "effective_settings": {
    "topBarColor": "#ff0000",
    "topBarBackgroundColor": "#ffffff",
    "topBarButtonBackgroundColor": "#007bff",
    "defaultLang": "en"
  }
}
```

---

### 6️⃣ **Obtener Estado de Subscripción (GetSubscriptionStatus)**

Verifica si la subscripción está activa o expirada.

```bash
curl -X GET http://localhost:5001/api/subscriptions/507f1f77bcf86cd799439014/status \
-H "X-API-Key: demo-key-123"
```

**Respuesta esperada:**

```json
{
  "subscription_id": "507f1f77bcf86cd799439014",
  "status": "active",
  "is_active": true,
  "is_expired": false,
  "start_date": "2024-01-15T10:00:00Z",
  "end_date": "2024-02-15T10:00:00Z",
  "trial_end_date": "2024-01-29T10:00:00Z"
}
```

---

### 7️⃣ **Editar Subscripción (EditSubscription)**

Modifica las configuraciones personalizadas de la subscripción.

```bash
curl -X PUT http://localhost:5001/api/subscriptions/507f1f77bcf86cd799439014/settings \
-H "X-API-Key: demo-key-123" \
-H "Content-Type: application/json" \
-d '{
  "custom_settings": {
    "topBarColor": "#00ff00",
    "topBarBackgroundColor": "#333333",
    "topBarButtonBackgroundColor": "#ff6600",
    "defaultLang": "fr"
  }
}'
```

**Respuesta esperada:**

```json
{
  "_id": "507f1f77bcf86cd799439014",
  "custom_settings": {
    "topBarColor": "#00ff00",
    "topBarBackgroundColor": "#333333",
    "topBarButtonBackgroundColor": "#ff6600",
    "defaultLang": "fr"
  },
  "updated_at": "2024-01-15T11:00:00Z",
  ...
}
```

---

### 8️⃣ **Extender Subscripción (ExtendSubscription)**

Establece una nueva fecha de expiración para la subscripción.

**Opción A: Extender por días**

```bash
curl -X POST http://localhost:5001/api/subscriptions/507f1f77bcf86cd799439014/extend \
-H "X-API-Key: demo-key-123" \
-H "Content-Type: application/json" \
-d '{
  "extension_days": 60
}'
```

**Opción B: Fecha específica**

```bash
curl -X POST http://localhost:5001/api/subscriptions/507f1f77bcf86cd799439014/extend \
-H "X-API-Key: demo-key-123" \
-H "Content-Type: application/json" \
-d '{
  "end_date": "2024-12-31T23:59:59Z"
}'
```

**Respuesta esperada:**

```json
{
  "_id": "507f1f77bcf86cd799439014",
  "end_date": "2024-12-31T23:59:59Z",
  "updated_at": "2024-01-15T11:05:00Z",
  ...
}
```

---

### 9️⃣ **Verificar Configuraciones Actualizadas**

Confirma que todos los cambios se aplicaron correctamente.

```bash
curl -X GET http://localhost:5001/api/subscriptions/507f1f77bcf86cd799439014/settings \
-H "X-API-Key: demo-key-123"
```

---

### 🔟 **Obtener Todas las Subscripciones**

Lista todas las subscripciones para verificar el estado general.

```bash
curl -X GET "http://localhost:5001/api/subscriptions?customer_id=507f1f77bcf86cd799439011" \
-H "X-API-Key: demo-key-123"
```

---

### 1️⃣1️⃣ **Cancelar Subscripción (Opcional)**

Si deseas cancelar la subscripción de prueba.

```bash
curl -X POST http://localhost:5001/api/subscriptions/507f1f77bcf86cd799439014/cancel \
-H "X-API-Key: demo-key-123"
```

---

## 📊 Casos de Uso Adicionales

### 🔄 **Subscripción con Herencia Automática**

Crea una subscripción que herede automáticamente las propiedades del producto:

```bash
curl -X POST http://localhost:5001/api/subscribe \
-H "X-API-Key: demo-key-123" \
-H "Content-Type: application/json" \
-d '{
  "customer_id": "507f1f77bcf86cd799439011",
  "product_id": "507f1f77bcf86cd799439013"
}'
```

### 📅 **Subscripción con Fecha Específica**

Crea una subscripción con una fecha de finalización personalizada:

```bash
curl -X POST http://localhost:5001/api/subscribe \
-H "X-API-Key: demo-key-123" \
-H "Content-Type: application/json" \
-d '{
  "customer_id": "507f1f77bcf86cd799439011",
  "product_id": "507f1f77bcf86cd799439013",
  "end_date": "2024-12-31T23:59:59Z",
  "custom_settings": {
    "topBarColor": "#purple"
  }
}'
```

### 📈 **Estadísticas de Subscripciones**

Obtén estadísticas del sistema:

```bash
curl -X GET http://localhost:5001/api/subscriptions/stats \
-H "X-API-Key: demo-key-123"
```

---

## 🎯 Puntos Clave del Flujo

1. **Autenticación**: Todas las peticiones `/api/*` requieren header `X-API-Key`
2. **Herencia Automática**: Las subscripciones heredan automáticamente precio, moneda y ciclo de facturación del producto
3. **Customización Inteligente**: Los `default_settings` del producto se combinan con `custom_settings` de la subscripción
4. **Validación**: El sistema valida que los campos de customización sean válidos según el producto
5. **Flexibilidad**: Puedes sobrescribir cualquier propiedad del producto en la subscripción
6. **Trazabilidad**: Cada operación actualiza automáticamente el campo `updated_at`

## 🚀 Scripts de Automatización

Para ejecutar todo el flujo automáticamente, puedes usar el script incluido:

```bash
python examples/test_subscribe_endpoint.py
```

---

## 📝 Notas Importantes

- **🔐 API Key**: Todos los endpoints `/api/*` requieren header `X-API-Key`
- Reemplaza los IDs de ejemplo con los IDs reales generados en tu sistema
- Asegúrate de que el servidor esté corriendo antes de ejecutar los comandos
- Los campos de customización deben coincidir con los `customizable_fields` del producto
- Las fechas deben estar en formato ISO 8601 con timezone UTC
