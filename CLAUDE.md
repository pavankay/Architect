# Architect AI Site Planning Tool - Claude Assistant Context

## Project Overview
This is an AI-powered site planning and architecture tool built with Astro frontend and Python FastAPI backend. The application helps users create, visualize, and manage web project architectures.

## Current Font Implementation Task

### Status: IN PROGRESS
I am currently implementing the new **Antikor Mono Light** font for all titles throughout the application.

### Task Requirements
1. ✅ **COMPLETED**: Add Antikor Mono Light font to the project
2. ✅ **COMPLETED**: Update CSS to include the new font  
3. 🔄 **IN PROGRESS**: Replace all title fonts with Antikor Mono Light
4. ⏳ **PENDING**: Ensure all text using this font is capitalized

### Font Implementation Details

#### Font Location
- Font file: `/home/aj/code/site_helper/fonts/antikor-mono/Taner Ardali  Antikor Mono Light.ttf`
- Copied to: `/home/aj/code/site_helper/frontend/src/fonts/Taner Ardali  Antikor Mono Light.ttf`

#### CSS Implementation
Added to `/home/aj/code/site_helper/frontend/src/styles/global.css`:
```css
@font-face {
  font-family: 'Antikor Mono Light';
  src: url('../fonts/Taner Ardali  Antikor Mono Light.ttf') format('truetype');
  font-weight: 300;
  font-style: normal;
  font-display: swap;
}

.font-antikor-title {
  font-family: 'Antikor Mono Light', monospace;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
```

### Files Updated So Far
- ✅ `/home/aj/code/site_helper/frontend/src/pages/index.astro` - Main page titles
- ✅ `/home/aj/code/site_helper/frontend/src/pages/create.astro` - Create page titles  
- ✅ `/home/aj/code/site_helper/frontend/src/pages/project/[id]/index.astro` - Project overview titles
- ✅ `/home/aj/code/site_helper/frontend/src/pages/project/[id]/sitemap.astro` - Sitemap page titles
- ✅ `/home/aj/code/site_helper/frontend/src/pages/project/[id]/architecture.astro` - Architecture page titles
- ✅ `/home/aj/code/site_helper/frontend/src/pages/project/[id]/backend.astro` - Backend page titles
- ✅ `/home/aj/code/site_helper/frontend/src/components/ProjectCard.astro` - Project card titles

### Still Need to Update
The following files still have titles that need to be converted to use the Antikor Mono Light font:

#### React Components (TypeScript files)
- `/home/aj/code/site_helper/frontend/src/components/SiteMapViewer.tsx` - Multiple h2, h3 titles need updating

#### Modal Component  
- `/home/aj/code/site_helper/frontend/src/components/CreateProjectModal.astro` - Modal titles (though this might be deprecated since we moved to dedicated create page)

### Implementation Pattern
Replace `font-mono` with `font-antikor-title` for all heading elements (h1, h2, h3, etc.):

**Before:**
```html
<h1 class="font-mono text-4xl mb-2">Title</h1>
```

**After:**
```html  
<h1 class="font-antikor-title text-4xl mb-2">Title</h1>
```

The CSS class automatically:
1. Applies the Antikor Mono Light font
2. Transforms text to UPPERCASE
3. Adds proper letter spacing

## Recent Major Changes
1. **Light Mode Bug Fixes**: Fixed all visual bugs in light mode including sidebar theming, form visibility, and button contrast
2. **Sidebar Grid Pattern Removal**: Made project page sidebars clean black/white instead of grid pattern
3. **Create Project Page**: Moved from modal to dedicated page with larger description field
4. **Keyboard Shortcuts**: Added "1" key to delete all projects with confirmation

## Development Commands
- Frontend dev: `npm run dev` (in frontend directory)
- Backend dev: `uvicorn main:app --reload --port 5000` (in backend directory)  
- Test URL: `http://localhost:3000`

## Key Features Implemented
- Dark/Light theme toggle
- Project creation with AI-powered architecture generation
- Interactive site maps, frontend, and backend visualization
- Clean, modern UI with proper theming
- Responsive design with Tailwind CSS

## Next Steps for Font Implementation
1. Update remaining React component titles in SiteMapViewer.tsx
2. Verify all titles are properly capitalized
3. Test font loading across all pages
4. Ensure proper fallbacks are in place

---
*Last updated: Current font implementation task in progress*