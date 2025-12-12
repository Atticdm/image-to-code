"""
Shared prompt blocks for code generation.

Goal: keep prompt text consistent across stacks and avoid copy/paste drift.
These are plain string fragments assembled by the per-stack prompt modules.
"""

# Common instructions (screenshot-based generation)
SCREENSHOT_COMMON_BULLETS_APP = """- Make sure the app looks exactly like the screenshot.
- Pay close attention to background color, text color, font size, font family, 
padding, margin, border, etc. Match the colors and sizes exactly.
- Use the exact text from the screenshot.
- Do not add comments in the code such as "<!-- Add other navigation links as needed -->" and "<!-- ... other news items ... -->" in place of writing the full code. WRITE THE FULL CODE.
- Repeat elements as needed to match the screenshot. For example, if there are 15 items, the code should have 15 items. DO NOT LEAVE comments like "<!-- Repeat for each news item -->" or bad things will happen.
- For images, use placeholder images from https://placehold.co and include a detailed description of the image in the alt text so that an image generation AI can generate the image later.
"""

SCREENSHOT_COMMON_BULLETS_SVG = """- Make sure the SVG looks exactly like the screenshot.
- Pay close attention to background color, text color, font size, font family, 
padding, margin, border, etc. Match the colors and sizes exactly.
- Use the exact text from the screenshot.
- Do not add comments in the code such as "<!-- Add other navigation links as needed -->" and "<!-- ... other news items ... -->" in place of writing the full code. WRITE THE FULL CODE.
- Repeat elements as needed to match the screenshot. For example, if there are 15 items, the code should have 15 items. DO NOT LEAVE comments like "<!-- Repeat for each news item -->" or bad things will happen.
- For images, use placeholder images from https://placehold.co and include a detailed description of the image in the alt text so that an image generation AI can generate the image later.
"""

# Common instructions (imported-code update flow)
IMPORTED_CODE_COMMON_BULLETS = """- Do not add comments in the code such as "<!-- Add other navigation links as needed -->" and "<!-- ... other news items ... -->" in place of writing the full code. WRITE THE FULL CODE.
- Repeat elements as needed. For example, if there are 15 items, the code should have 15 items. DO NOT LEAVE comments like "<!-- Repeat for each news item -->" or bad things will happen.
- For images, use placeholder images from https://placehold.co and include a detailed description of the image in the alt text so that an image generation AI can generate the image later.
"""

IMPORTED_CODE_SVG_BULLETS = """- Do not add comments in the code such as "<!-- Add other navigation links as needed -->" and "<!-- ... other news items ... -->" in place of writing the full code. WRITE THE FULL CODE.
- Repeat elements as needed to match the screenshot. For example, if there are 15 items, the code should have 15 items. DO NOT LEAVE comments like "<!-- Repeat for each news item -->" or bad things will happen.
- For images, use placeholder images from https://placehold.co and include a detailed description of the image in the alt text so that an image generation AI can generate the image later.
- You can use Google Fonts
"""

# Library blocks
LIB_GOOGLE_FONTS = "- You can use Google Fonts"
LIB_FONT_AWESOME = (
    '- Font Awesome for icons: <link rel="stylesheet" '
    'href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css"></link>'
)

LIB_TAILWIND_SCRIPT = (
    '- Use this script to include Tailwind: <script src="https://cdn.tailwindcss.com"></script>'
)

LIB_BOOTSTRAP_LINK = (
    '- Use this script to include Bootstrap: <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" '
    'rel="stylesheet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">'
)

LIB_REACT_SCRIPTS = """- Use these script to include React so that it can run on a standalone page:
    <script src="https://cdn.jsdelivr.net/npm/react@18.0.0/umd/react.development.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/react-dom@18.0.0/umd/react-dom.development.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@babel/standalone/babel.js"></script>"""

LIB_IONIC_SCRIPTS = """- Use these script to include Ionic so that it can run on a standalone page:
    <script type="module" src="https://cdn.jsdelivr.net/npm/@ionic/core/dist/ionic/ionic.esm.js"></script>
    <script nomodule src="https://cdn.jsdelivr.net/npm/@ionic/core/dist/ionic/ionic.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@ionic/core/css/ionic.bundle.css" />"""

LIB_IONIC_IONICONS = """- ionicons for icons, add the following <script > tags near the end of the page, right before the closing </body> tag:
    <script type="module">
        import ionicons from 'https://cdn.jsdelivr.net/npm/ionicons/+esm'
    </script>
    <script nomodule src="https://cdn.jsdelivr.net/npm/ionicons/dist/esm/ionicons.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/ionicons/dist/collection/components/icon/icon.min.css" rel="stylesheet">"""

LIB_VUE_SCRIPT = """- Use these script to include Vue so that it can run on a standalone page:
  <script src="https://registry.npmmirror.com/vue/3.3.11/files/dist/vue.global.js"></script>"""

VUE_GLOBAL_BUILD_EXAMPLE = """- Use Vue using the global build like so:

<div id="app">{{ message }}</div>
<script>
  const { createApp, ref } = Vue
  createApp({
    setup() {
      const message = ref('Hello vue!')
      return {
        message
      }
    }
  }).mount('#app')
</script>
"""

# Format blocks
FORMAT_HTML = """Return only the full code in <html></html> tags.
Do not include markdown "```" or "```html" at the start or end.
"""

FORMAT_HTML_ONLY_CODE = """Return only the full code in <html></html> tags.
Do not include markdown "```" or "```html" at the start or end.
The return result must only include the code.
"""

FORMAT_SVG = """Return only the full code in <svg></svg> tags.
Do not include markdown "```" or "```svg" at the start or end.
"""

