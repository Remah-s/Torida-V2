# TORIDA Cloudinary Image Upload API - Example Requests

## 1. Upload Image Only

### cURL
```bash
curl -X POST http://localhost:5000/api/products/upload-image \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "image=@/path/to/image.jpg"
```

### Response
```json
{
  "status": "success",
  "data": {
    "image_url": "https://res.cloudinary.com/dswqa76wb/image/upload/v1234567890/torida/products/image.jpg"
  },
  "message": "Image uploaded successfully"
}
```

---

## 2. Create Product with Image

### cURL
```bash
curl -X POST http://localhost:5000/api/products \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": 1,
    "product_name": "Laptop Pro",
    "description": "High-performance laptop",
    "price": 1299.99,
    "stock_quantity": 50,
    "is_active": true,
    "image_url": "https://res.cloudinary.com/dswqa76wb/image/upload/v1234567890/torida/products/image.jpg"
  }'
```

### Response
```json
{
  "status": "success",
  "data": {
    "id": 5,
    "code": "001005",
    "custom_id": "PRD-001005",
    "product_name": "Laptop Pro",
    "description": "High-performance laptop",
    "price": 1299.99,
    "stock_quantity": 50,
    "category_id": 1,
    "company_id": 3,
    "is_active": true,
    "created_at": "2024-01-15T10:30:00"
  },
  "message": "Product created successfully"
}
```

---

## 3. Add Additional Image to Existing Product

### cURL
```bash
curl -X POST http://localhost:5000/api/products/5/images \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "image=@/path/to/image2.png" \
  -F "is_primary=false"
```

### Response
```json
{
  "status": "success",
  "data": {
    "id": 12,
    "product_id": 5,
    "image_url": "https://res.cloudinary.com/dswqa76wb/image/upload/v1234567891/torida/products/image2.png",
    "is_primary": false,
    "created_at": "2024-01-15T10:35:00"
  },
  "message": "Image added successfully"
}
```

---

## 4. Get Product with All Images

### cURL
```bash
curl -X GET http://localhost:5000/api/products/5 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Response
```json
{
  "status": "success",
  "data": {
    "id": 5,
    "product_name": "Laptop Pro",
    "price": 1299.99,
    "images": [
      {
        "id": 11,
        "product_id": 5,
        "image_url": "https://res.cloudinary.com/dswqa76wb/image/upload/v1234567890/torida/products/image.jpg",
        "is_primary": true,
        "created_at": "2024-01-15T10:30:00"
      },
      {
        "id": 12,
        "product_id": 5,
        "image_url": "https://res.cloudinary.com/dswqa76wb/image/upload/v1234567891/torida/products/image2.png",
        "is_primary": false,
        "created_at": "2024-01-15T10:35:00"
      }
    ]
  }
}
```

---

## 5. Get Product Images Only

### cURL
```bash
curl -X GET http://localhost:5000/api/products/5/images \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Response
```json
{
  "status": "success",
  "data": [
    {
      "id": 11,
      "product_id": 5,
      "image_url": "https://res.cloudinary.com/dswqa76wb/image/upload/v1234567890/torida/products/image.jpg",
      "is_primary": true,
      "created_at": "2024-01-15T10:30:00"
    },
    {
      "id": 12,
      "product_id": 5,
      "image_url": "https://res.cloudinary.com/dswqa76wb/image/upload/v1234567891/torida/products/image2.png",
      "is_primary": false,
      "created_at": "2024-01-15T10:35:00"
    }
  ]
}
```

---

## 6. Delete Product Image (from Cloudinary + Database)

### cURL
```bash
curl -X DELETE http://localhost:5000/api/products/5/images/12 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Response
```json
{
  "status": "success",
  "message": "Image deleted successfully"
}
```

---

## Error Examples

### Missing Image File
```
curl -X POST http://localhost:5000/api/products/upload-image \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

Response (400):
{
  "status": "error",
  "message": "No image file provided"
}
```

### Invalid File Type
```
curl -X POST http://localhost:5000/api/products/upload-image \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "image=@document.pdf"

Response (400):
{
  "status": "error",
  "message": "File type not allowed. Allowed types: jpg, jpeg, png, webp"
}
```

### File Too Large (> 10MB)
```
Response (400):
{
  "status": "error",
  "message": "File size exceeds maximum of 10.0MB"
}
```

### Not Authorized (Not Product Owner)
```
Response (403):
{
  "status": "error",
  "message": "Not authorized to add images to this product"
}
```

### Product Not Found
```
Response (404):
{
  "status": "error",
  "message": "Product not found"
}
```

---

## JavaScript/Fetch Examples

### Upload Image
```javascript
const formData = new FormData();
formData.append('image', imageFile); // File object from input

const response = await fetch('http://localhost:5000/api/products/upload-image', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const result = await response.json();
console.log(result.data.image_url);
```

### Create Product with Image
```javascript
const response = await fetch('http://localhost:5000/api/products', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    category_id: 1,
    product_name: 'Laptop Pro',
    description: 'High-performance laptop',
    price: 1299.99,
    stock_quantity: 50,
    image_url: 'https://res.cloudinary.com/...' // From upload response
  })
});

const result = await response.json();
console.log(result.data);
```

### Add Image to Product
```javascript
const formData = new FormData();
formData.append('image', imageFile);
formData.append('is_primary', false);

const response = await fetch('http://localhost:5000/api/products/5/images', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const result = await response.json();
console.log(result.data.image_url);
```

### Delete Image
```javascript
const response = await fetch('http://localhost:5000/api/products/5/images/12', {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const result = await response.json();
console.log(result.message);
```

---

## Testing Notes

1. Replace `YOUR_JWT_TOKEN` with an actual JWT token from login endpoint
2. Replace `YOUR_PRODUCT_ID` and `IMAGE_ID` with actual IDs
3. Ensure Cloudinary credentials are set in environment variables
4. Test with different image formats: JPG, PNG, WEBP
5. Test file size limits (try > 10MB file)
6. Test authorization checks (use different user's token)
