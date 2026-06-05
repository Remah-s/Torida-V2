# Supplier Local Photo Upload To Cloudinary Report

## Purpose

Supplier dashboard and supplier profile screens should let the supplier choose photos from their local PC, upload them to the backend as `multipart/form-data`, and let the backend send them to Cloudinary.

Important frontend rule:

- Use `FormData`.
- Append the local file under the field name `image`.
- Do not manually set the `Content-Type` header when sending `FormData`.
- Keep the `Authorization` header.

## Product Photos Already Supported

Use this endpoint when the supplier wants to upload a product image and only needs the Cloudinary URL back.

```http
POST /api/products/supplier/upload-image
```

Form data:

| Field | Type | Required | Notes |
|---|---|---:|---|
| `image` | file | yes | Local image from the user's PC |

Success response:

```json
{
  "success": true,
  "message": "Image uploaded successfully",
  "data": {
    "image_url": "https://res.cloudinary.com/.../torida/products/file.jpg"
  }
}
```

Use this endpoint when the supplier wants to upload and attach the local image directly to an existing product.

```http
POST /api/products/<product_id>/images
```

Form data:

| Field | Type | Required | Notes |
|---|---|---:|---|
| `image` | file | yes | Local image from the user's PC |
| `is_primary` | string | no | Send `true` to make it the primary product image |

Success response:

```json
{
  "success": true,
  "message": "Image added successfully",
  "data": {
    "id": 11,
    "product_id": 5,
    "image_url": "https://res.cloudinary.com/.../torida/products/file.jpg",
    "is_primary": true,
    "created_at": "2026-06-05T12:00:00"
  }
}
```

## Supplier Profile Photos Added

Use this endpoint when the supplier wants to upload a business logo or cover image from their local PC and save it on their business profile.

```http
POST /api/business-profiles/me/upload-photo
```

Form data:

| Field | Type | Required | Notes |
|---|---|---:|---|
| `image` | file | yes | Local image from the user's PC |
| `photo_type` | string | no | `logo`, `cover`, `profile`, `business_logo`, or `cover_image`. Defaults to `logo` |

Cloudinary folder:

```text
torida/business-profiles/<user_id>
```

Success response:

```json
{
  "success": true,
  "message": "Profile photo uploaded successfully",
  "data": {
    "image_url": "https://res.cloudinary.com/.../torida/business-profiles/1/file.jpg",
    "photo_type": "logo",
    "profile_field": "logo_url",
    "profile": {
      "user_id": 1,
      "business_name": "Supplier Store",
      "tax_number": "123",
      "commercial_register": "456",
      "address": "Cairo",
      "logo_url": "https://res.cloudinary.com/.../file.jpg",
      "cover_image_url": null,
      "created_at": "2026-06-05T12:00:00"
    }
  }
}
```

Error examples:

```json
{
  "success": false,
  "message": "No image file provided"
}
```

```json
{
  "success": false,
  "message": "Only suppliers and companies can upload profile photos"
}
```

```json
{
  "success": false,
  "message": "Business profile not found. Create profile before uploading photos"
}
```

## Frontend Example

```javascript
async function uploadSupplierProfilePhoto(file, photoType = 'logo') {
  const formData = new FormData();
  formData.append('image', file);
  formData.append('photo_type', photoType);

  const response = await fetch('/api/business-profiles/me/upload-photo', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${localStorage.getItem('supplierToken')}`
    },
    body: formData
  });

  const result = await response.json();

  if (!response.ok || result.success === false) {
    throw new Error(result.message || result.error || 'Photo upload failed');
  }

  return result.data;
}
```

```javascript
function SupplierPhotoInput({ photoType = 'logo', onUploaded }) {
  async function handleChange(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    const data = await uploadSupplierProfilePhoto(file, photoType);
    onUploaded(data.profile);
  }

  return (
    <input
      type="file"
      accept="image/png,image/jpeg,image/jpg,image/webp"
      onChange={handleChange}
    />
  );
}
```

## Product Image Frontend Example

```javascript
async function addProductImage(productId, file, isPrimary = false) {
  const formData = new FormData();
  formData.append('image', file);
  formData.append('is_primary', String(isPrimary));

  const response = await fetch(`/api/products/${productId}/images`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${localStorage.getItem('supplierToken')}`
    },
    body: formData
  });

  const result = await response.json();

  if (!response.ok || result.success === false) {
    throw new Error(result.message || result.error || 'Product image upload failed');
  }

  return result.data;
}
```

## Database Update Required

Existing databases need these columns added to `business_profiles`:

```sql
ALTER TABLE business_profiles
  ADD COLUMN logo_url VARCHAR(500) NULL,
  ADD COLUMN cover_image_url VARCHAR(500) NULL;
```

For a new empty database, `db.create_all()` will create these columns automatically.

## Acceptance Checklist

- Supplier can choose a local image file for product images.
- Supplier can choose a local image file for profile logo.
- Supplier can choose a local image file for profile cover image.
- Frontend sends `image` in `FormData`.
- Frontend does not manually set `Content-Type` for `FormData`.
- Backend uploads to Cloudinary and returns `image_url`.
- Business profile response includes `logo_url` and `cover_image_url`.
- Upload errors are displayed from backend `message`.

