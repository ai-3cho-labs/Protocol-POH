# Branding Assets

Replace these files to customize the deployment branding.

## Required Files

| File | Dimensions | Purpose |
|------|------------|---------|
| `logo.jpg` | 1024x1024 | Main logo (high-res) |
| `logo-small.jpg` | 256x256 | Header logo |
| `icon.jpg` | 192x192 | Favicon / app icon |
| `og-image.jpg` | 1200x630 | Open Graph / social sharing |

## Notes

- Current files are copies of the default CPU logo
- Replace with your own branding for white-label deployments
- Supported formats: .jpg, .png, .webp
- If using different extensions, update references in:
  - `src/app/layout.tsx`
  - `src/components/layout/Header.tsx`
