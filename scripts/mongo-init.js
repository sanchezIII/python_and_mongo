// MongoDB initialization script for Docker
print("Starting MongoDB initialization...");

// Create application database
db = db.getSiblingDB("flask_db");

// Create collections with validation
db.createCollection("customers", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "email", "status", "created_at", "updated_at"],
      properties: {
        name: {
          bsonType: "string",
          minLength: 2,
          maxLength: 100,
          description: "Customer name is required and must be 2-100 characters",
        },
        email: {
          bsonType: "string",
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+.[a-zA-Z]{2,}$",
          description: "Valid email address is required",
        },
        phone: {
          bsonType: ["string", "null"],
          maxLength: 20,
          description: "Phone number up to 20 characters",
        },
        address: {
          bsonType: ["string", "null"],
          maxLength: 200,
          description: "Address up to 200 characters",
        },
        city: {
          bsonType: ["string", "null"],
          maxLength: 100,
          description: "City up to 100 characters",
        },
        country: {
          bsonType: ["string", "null"],
          maxLength: 100,
          description: "Country up to 100 characters",
        },
        postal_code: {
          bsonType: ["string", "null"],
          maxLength: 20,
          description: "Postal code up to 20 characters",
        },
        status: {
          enum: ["active", "inactive", "suspended"],
          description: "Customer status must be active, inactive, or suspended",
        },
        created_at: {
          bsonType: "date",
          description: "Creation timestamp is required",
        },
        updated_at: {
          bsonType: "date",
          description: "Update timestamp is required",
        },
      },
    },
  },
});

db.createCollection("products", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "name",
        "price",
        "currency",
        "billing_cycle",
        "is_active",
        "created_at",
        "updated_at",
      ],
      properties: {
        name: {
          bsonType: "string",
          minLength: 2,
          maxLength: 100,
          description: "Product name is required and must be 2-100 characters",
        },
        description: {
          bsonType: ["string", "null"],
          maxLength: 500,
          description: "Product description up to 500 characters",
        },
        price: {
          bsonType: "number",
          minimum: 0,
          description: "Product price must be non-negative",
        },
        currency: {
          enum: ["USD", "EUR", "GBP", "JPY"],
          description: "Currency must be USD, EUR, GBP, or JPY",
        },
        billing_cycle: {
          enum: ["weekly", "monthly", "yearly"],
          description: "Billing cycle must be weekly, monthly, or yearly",
        },
        trial_period_days: {
          bsonType: "int",
          minimum: 0,
          maximum: 365,
          description: "Trial period in days (0-365)",
        },
        features: {
          bsonType: "array",
          items: {
            bsonType: "string",
            maxLength: 100,
          },
          description: "Array of feature strings",
        },
        is_active: {
          bsonType: "bool",
          description: "Product active status is required",
        },
        customizable: {
          bsonType: "bool",
          description: "Whether the product is customizable",
        },
        customizable_fields: {
          bsonType: "array",
          items: {
            bsonType: "string",
            maxLength: 100,
          },
          description: "Array of customizable field names",
        },
        default_settings: {
          bsonType: "object",
          description: "Default settings for customizable products",
        },
        created_at: {
          bsonType: "date",
          description: "Creation timestamp is required",
        },
        updated_at: {
          bsonType: "date",
          description: "Update timestamp is required",
        },
      },
    },
  },
});

db.createCollection("subscriptions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "customer_id",
        "status",
        "amount",
        "currency",
        "billing_cycle",
        "start_date",
        "created_at",
        "updated_at",
      ],
      properties: {
        customer_id: {
          bsonType: "objectId",
          description: "Customer ObjectId is required",
        },
        product_id: {
          bsonType: ["objectId", "null"],
          description: "Product ObjectId",
        },
        status: {
          enum: ["active", "canceled", "expired", "trial"],
          description:
            "Subscription status must be active, canceled, expired, or trial",
        },
        amount: {
          bsonType: "number",
          minimum: 0,
          description: "Subscription amount must be non-negative",
        },
        currency: {
          enum: ["USD", "EUR", "GBP", "JPY"],
          description: "Currency must be USD, EUR, GBP, or JPY",
        },
        billing_cycle: {
          enum: ["weekly", "monthly", "yearly"],
          description: "Billing cycle must be weekly, monthly, or yearly",
        },
        start_date: {
          bsonType: "date",
          description: "Start date is required",
        },
        end_date: {
          bsonType: ["date", "null"],
          description: "End date",
        },
        trial_end_date: {
          bsonType: ["date", "null"],
          description: "Trial end date",
        },
        canceled_at: {
          bsonType: ["date", "null"],
          description: "Cancellation timestamp",
        },
        created_at: {
          bsonType: "date",
          description: "Creation timestamp is required",
        },
        updated_at: {
          bsonType: "date",
          description: "Update timestamp is required",
        },
        metadata: {
          bsonType: ["object", "null"],
          description: "Additional metadata",
        },
        custom_settings: {
          bsonType: ["object", "null"],
          description: "Custom settings for subscription customization",
        },
      },
    },
  },
});

// Create indexes
print("Creating indexes...");

// Customer indexes
db.customers.createIndex({ email: 1 }, { unique: true });
db.customers.createIndex({ status: 1 });
db.customers.createIndex({ created_at: -1 });
db.customers.createIndex({ name: "text", email: "text" });

// Product indexes
db.products.createIndex({ name: 1 });
db.products.createIndex({ is_active: 1 });
db.products.createIndex({ billing_cycle: 1 });
db.products.createIndex({ created_at: -1 });

// Subscription indexes
db.subscriptions.createIndex({ customer_id: 1 });
db.subscriptions.createIndex({ product_id: 1 });
db.subscriptions.createIndex({ status: 1 });
db.subscriptions.createIndex({ billing_cycle: 1 });
db.subscriptions.createIndex({ start_date: 1 });
db.subscriptions.createIndex({ end_date: 1 });
db.subscriptions.createIndex({ created_at: -1 });

// Compound indexes for common queries
db.subscriptions.createIndex({ customer_id: 1, status: 1 });
db.subscriptions.createIndex({ status: 1, end_date: 1 });

print("MongoDB initialization completed successfully!");
