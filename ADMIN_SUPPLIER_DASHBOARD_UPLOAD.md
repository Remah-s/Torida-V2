# Admin & Supplier Dashboard Image Upload Documentation

## Overview
Added Cloudinary image upload functionality to both admin dashboard and supplier dashboard for easy image management.

## Admin Dashboard Image Upload

### Endpoint: POST /api/admin/upload-image
Upload images for admin use (category icons, banners, promotional materials, etc.)

**Authentication:** Required (Admin only)  
**Content-Type:** multipart/form-data

**Request:**
```bash
curl -X POST http://localhost:5000/api/admin/upload-image \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -F "image=@/path/to/image.jpg"
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "image_url": "https://res.cloudinary.com/dswqa76wb/image/upload/v1234567890/torida/admin/image.jpg"
  },
  "message": "Image uploaded successfully"
}
```

**Response (Error):**
```json
{
  "status": "error",
  "message": "File type not allowed. Allowed types: jpg, jpeg, png, webp"
}
```

**Use Cases:**
- Upload category icons
- Upload promotional banners
- Upload admin-related assets
- Upload store logos/branding

**Cloudinary Folder:** `torida/admin`

---

## Supplier Dashboard

### Endpoint 1: GET /api/products/supplier/dashboard
Get supplier dashboard statistics and recent products.

**Authentication:** Required (Supplier/Seller only)  
**Method:** GET

**Request:**
```bash
curl -X GET http://localhost:5000/api/products/supplier/dashboard \
  -H "Authorization: Bearer SUPPLIER_JWT_TOKEN"
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_products": 25,
    "active_products": 20,
    "total_images": 45,
    "total_orders": 150,
    "recent_products": [
      {
        "id": 5,
        "custom_id": "PRD-001005",
        "product_name": "Laptop Pro",
        "price": 1299.99,
        "stock_quantity": 50,
        "is_active": true,
        "images": [
          {
            "id": 11,
            "image_url": "https://res.cloudinary.com/...",
            "is_primary": true
          }
        ]
      }
    ]
  }
}
```

**Returned Stats:**
- `total_products`: Total products created by supplier
- `active_products`: Number of active products
- `total_images`: Total product images uploaded
- `total_orders`: Total orders for supplier's products
- `recent_products`: Last 10 products (with images)

---

### Endpoint 2: POST /api/products/supplier/upload-image
Upload images for supplier's products via dashboard.

**Authentication:** Required (Supplier/Seller only)  
**Content-Type:** multipart/form-data

**Request:**
```bash
curl -X POST http://localhost:5000/api/products/supplier/upload-image \
  -H "Authorization: Bearer SUPPLIER_JWT_TOKEN" \
  -F "image=@/path/to/product-image.jpg"
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "image_url": "https://res.cloudinary.com/dswqa76wb/image/upload/v1234567890/torida/products/product.jpg"
  },
  "message": "Image uploaded successfully"
}
```

**Response (Error - Not Authorized):**
```json
{
  "status": "error",
  "message": "Only suppliers and companies can upload images"
}
```

**Response (Error - File Issues):**
```json
{
  "status": "error",
  "message": "File size exceeds maximum of 10.0MB"
}
```

**Use Cases:**
- Upload product images from supplier dashboard
- Add multiple images to products
- Replace product images
- Bulk image uploads

**Cloudinary Folder:** `torida/products`

---

## Complete Workflow - Admin Dashboard

### 1. Upload Category Icon
```javascript
const formData = new FormData();
formData.append('image', iconFile);

const response = await fetch('/api/admin/upload-image', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${adminToken}` },
  body: formData
});

const { data } = await response.json();
const categoryIconUrl = data.image_url;
```

### 2. Update Category with Icon
```javascript
await fetch('/api/admin/categories/1', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${adminToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    category_name: 'Electronics',
    icon_url: categoryIconUrl  // Use uploaded URL
  })
});
```

---

## Complete Workflow - Supplier Dashboard

### 1. Get Supplier Stats
```javascript
const response = await fetch('/api/products/supplier/dashboard', {
  headers: { 'Authorization': `Bearer ${supplierToken}` }
});

const { data } = await response.json();
console.log(`Total Products: ${data.total_products}`);
console.log(`Total Images: ${data.total_images}`);
console.log(`Total Orders: ${data.total_orders}`);
```

### 2. Upload Product Image
```javascript
const formData = new FormData();
formData.append('image', productImageFile);

const response = await fetch('/api/products/supplier/upload-image', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${supplierToken}` },
  body: formData
});

const { data } = await response.json();
const imageUrl = data.image_url;
```

### 3. Add Image to Product
```javascript
await fetch('/api/products/5/images', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${supplierToken}`,
    'Content-Type': 'multipart/form-data'
  },
  body: formData  // Same form with image file
});
```

### 4. Get Recent Products with Images
```javascript
// From dashboard response
const { recent_products } = await dashboardResponse.json();

recent_products.forEach(product => {
  console.log(`Product: ${product.product_name}`);
  product.images.forEach(img => {
    console.log(`Image URL: ${img.image_url}`);
  });
});
```

---

## Validation & Security

### File Validation
✅ **Allowed Types:** jpg, jpeg, png, webp  
✅ **Max Size:** 10MB  
✅ **No Empty Files**  
✅ **Extension Check**  

### Authentication & Authorization
✅ **Admin Endpoint:** Admin role required  
✅ **Supplier Endpoints:** Seller/Supplier role required  
✅ **Token Validation:** JWT token required  
✅ **Error Messages:** Generic for security  

### Cloudinary Storage
✅ **Admin Images:** `torida/admin` folder  
✅ **Product Images:** `torida/products` folder  
✅ **Auto Optimization:** Quality auto-optimized  
✅ **CDN Distribution:** Served from Cloudinary CDN  

---

## Error Codes

| Code | Message | Cause |
|------|---------|-------|
| 400 | No image file provided | Missing image in request |
| 400 | No image file selected | Empty filename |
| 400 | File type not allowed | Invalid file extension |
| 400 | File size exceeds maximum | File > 10MB |
| 403 | Only admins can access this | Non-admin trying to access admin endpoint |
| 403 | Only suppliers can upload images | Non-supplier trying to upload |
| 500 | Image upload failed | Cloudinary API error |

---

## API Integration Examples

### React Example - Admin Upload
```javascript
import React, { useState } from 'react';

function AdminImageUpload() {
  const [image, setImage] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [imageUrl, setImageUrl] = useState('');

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('image', file);

    setUploading(true);
    try {
      const response = await fetch('/api/admin/upload-image', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: formData
      });

      const result = await response.json();
      if (result.status === 'success') {
        setImageUrl(result.data.image_url);
        alert('Image uploaded successfully!');
      } else {
        alert(`Upload failed: ${result.message}`);
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <input 
        type="file" 
        onChange={handleUpload} 
        accept="image/*"
        disabled={uploading}
      />
      {uploading && <p>Uploading...</p>}
      {imageUrl && <img src={imageUrl} alt="Uploaded" style={{ maxWidth: '200px' }} />}
    </div>
  );
}

export default AdminImageUpload;
```

### React Example - Supplier Dashboard
```javascript
import React, { useEffect, useState } from 'react';

function SupplierDashboard() {
  const [dashboard, setDashboard] = useState(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      const response = await fetch('/api/products/supplier/dashboard', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supplierToken')}`
        }
      });

      const result = await response.json();
      if (result.status === 'success') {
        setDashboard(result.data);
      }
    };

    fetchDashboard();
  }, []);

  if (!dashboard) return <p>Loading...</p>;

  return (
    <div className="dashboard">
      <h1>Supplier Dashboard</h1>
      
      <div className="stats">
        <div className="stat-card">
          <h3>Total Products</h3>
          <p className="stat-value">{dashboard.total_products}</p>
        </div>
        
        <div className="stat-card">
          <h3>Active Products</h3>
          <p className="stat-value">{dashboard.active_products}</p>
        </div>
        
        <div className="stat-card">
          <h3>Total Images</h3>
          <p className="stat-value">{dashboard.total_images}</p>
        </div>
        
        <div className="stat-card">
          <h3>Total Orders</h3>
          <p className="stat-value">{dashboard.total_orders}</p>
        </div>
      </div>

      <div className="recent-products">
        <h2>Recent Products</h2>
        {dashboard.recent_products.map(product => (
          <div key={product.id} className="product-card">
            <h3>{product.product_name}</h3>
            <p>Price: ${product.price}</p>
            <p>Stock: {product.stock_quantity}</p>
            <div className="product-images">
              {product.images.map(img => (
                <img key={img.id} src={img.image_url} alt={product.product_name} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default SupplierDashboard;
```

---

## Testing

### Test Admin Upload
```bash
# 1. Get admin token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@torida.com","password":"password"}'

# 2. Upload image
curl -X POST http://localhost:5000/api/admin/upload-image \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -F "image=@test.jpg"
```

### Test Supplier Dashboard
```bash
# 1. Get supplier token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"supplier@torida.com","password":"password"}'

# 2. Get dashboard
curl -X GET http://localhost:5000/api/products/supplier/dashboard \
  -H "Authorization: Bearer SUPPLIER_TOKEN"

# 3. Upload image
curl -X POST http://localhost:5000/api/products/supplier/upload-image \
  -H "Authorization: Bearer SUPPLIER_TOKEN" \
  -F "image=@product.jpg"
```

---

## Summary

| Feature | Admin | Supplier |
|---------|-------|----------|
| Upload Endpoint | ✅ `/api/admin/upload-image` | ✅ `/api/products/supplier/upload-image` |
| Dashboard Endpoint | ✅ `/api/admin/dashboard` | ✅ `/api/products/supplier/dashboard` |
| Cloudinary Folder | `torida/admin` | `torida/products` |
| Max File Size | 10MB | 10MB |
| Auth Required | Yes (Admin) | Yes (Seller) |
| Use Cases | Categories, Banners | Product Images |
