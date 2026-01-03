# Template Structure Diagram

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        base.j2                              │
│                   (Main Container)                          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │             <head> Section                          │  │
│  │  • Meta tags                                        │  │
│  │  • {% block header %} - External libraries          │  │
│  │  • {% include '_styles.j2' %} ────────────┐        │  │
│  │  • <title>{% block title %}</title>       │        │  │
│  └────────────────────────────────────────────┼────────┘  │
│                                               │            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │             <body> Section                          │  │
│  │                                                     │  │
│  │  ┌──────────────────────────────────────────────┐ │  │
│  │  │  {% include '_header.j2' %}                  │ │  │
│  │  │  • Logo + Navigation                         │ │  │
│  │  │  • User Info / Auth Buttons                  │ │  │
│  │  └──────────────────────────────────────────────┘ │  │
│  │                                                     │  │
│  │  ┌──────────────────────────────────────────────┐ │  │
│  │  │  {% include '_theme_toggle.j2' %}            │ │  │
│  │  │  • Theme Toggle Button (Fixed)               │ │  │
│  │  └──────────────────────────────────────────────┘ │  │
│  │                                                     │  │
│  │  ┌──────────────────────────────────────────────┐ │  │
│  │  │  {% block content %}                         │ │  │
│  │  │  ← Child templates inject content here       │ │  │
│  │  │  (home.j2, login.j2, etc.)                   │ │  │
│  │  └──────────────────────────────────────────────┘ │  │
│  │                                                     │  │
│  │  ┌──────────────────────────────────────────────┐ │  │
│  │  │  {% include '_footer.j2' %}                  │ │  │
│  │  │  • Quick Links + Resources                   │ │  │
│  │  │  • Social Links + Copyright                  │ │  │
│  │  └──────────────────────────────────────────────┘ │  │
│  │                                                     │  │
│  │  ┌──────────────────────────────────────────────┐ │  │
│  │  │  {% include '_scripts.j2' %}                 │ │  │
│  │  │  • Theme Toggle JS                           │ │  │
│  │  │  • {% block javascript %}                    │ │  │
│  │  └──────────────────────────────────────────────┘ │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

                            │
                            ├─► _styles.j2
                            │   ├─ CSS Variables (Theme)
                            │   ├─ Global Resets
                            │   ├─ Header Styles
                            │   ├─ Footer Styles
                            │   ├─ Button Styles
                            │   ├─ Responsive Media Queries
                            │   └─ {% block css %} ← Child styles
                            │
                            └─► _scripts.j2
                                ├─ Theme Toggle Logic
                                ├─ LocalStorage Management
                                └─ {% block javascript %} ← Child scripts
```

## Template Inheritance Flow

```
                    ┌──────────────┐
                    │   base.j2    │
                    │  (Parent)    │
                    └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┬───────────────┐
         │                 │                 │               │
    ┌────▼────┐      ┌─────▼─────┐    ┌─────▼─────┐   ┌────▼────┐
    │ home.j2 │      │ login.j2  │    │signup.j2  │   │ ...etc  │
    │(extends)│      │ (extends) │    │(extends)  │   │(extends)│
    └─────────┘      └───────────┘    └───────────┘   └─────────┘
         │                 │                 │               │
         └─────────────────┴─────────────────┴───────────────┘
                           │
                  Inherits everything from base.j2
                  Can override specific blocks:
                  • {% block title %}
                  • {% block css %}
                  • {% block content %}
                  • {% block javascript %}
```

## Component Relationship

```
┌─────────────────────────────────────────────────────────┐
│                    Client Browser                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Django/Jinja2 Engine │
         └───────────┬───────────┘
                     │
      ┌──────────────┼──────────────┐
      │              │              │
      ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│Pages (.j2)│  │Components│  │ Blocks   │
│          │  │  (_*.j2) │  │{% block %}│
├──────────┤  ├──────────┤  ├──────────┤
│ home     │  │ _header  │  │ title    │
│ login    │  │ _footer  │  │ css      │
│ signup   │  │ _styles  │  │ content  │
│ basket_* │  │ _scripts │  │javascript│
└──────────┘  └──────────┘  └──────────┘
      │              │              │
      └──────────────┼──────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   Rendered HTML       │
         │   Sent to Browser     │
         └───────────────────────┘
```

## File Size Comparison

### Before Refactoring
```
base.j2: 14,837 bytes (496 lines)
  └─ All HTML, CSS, JS in one file
```

### After Refactoring
```
base.j2:              875 bytes (25 lines) ─┐
_header.j2:         1,340 bytes            │
_footer.j2:         2,720 bytes            ├─ Total: 13,404 bytes
_styles.j2:         7,105 bytes            │  (10% reduction)
_scripts.j2:        1,135 bytes            │
_theme_toggle.j2:     229 bytes            ─┘

Benefits:
✓ 89% reduction in base.j2 size
✓ Modular components (easier to maintain)
✓ Better organization
✓ Reusable across templates
```

## Request Flow Example

```
User visits /login/
       │
       ▼
Django routes to login_view()
       │
       ▼
Renders 'stocks/login.j2'
       │
       ├─► Extends 'stocks/base.j2'
       │        │
       │        ├─► Includes '_header.j2'      (User sees: Login/Signup buttons)
       │        ├─► Includes '_theme_toggle.j2' (User sees: Theme toggle)
       │        ├─► Includes '_styles.j2'       (Page styled with CSS)
       │        ├─► Includes '_footer.j2'       (Footer with links)
       │        └─► Includes '_scripts.j2'      (Theme toggle works)
       │
       └─► Inserts login form in {% block content %}
       
       ▼
Complete HTML sent to browser
       │
       ▼
User sees fully styled login page with header, footer, and theme toggle
```

## Theme System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  localStorage                           │
│                theme: "light" | "dark"                  │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
    ┌────────────────────┐
    │ _scripts.j2        │
    │ Theme Toggle Logic │
    └────────┬───────────┘
             │
             ▼
    ┌────────────────────┐
    │ HTML Element       │
    │ data-theme="light" │
    │ data-theme="dark"  │
    └────────┬───────────┘
             │
             ▼
    ┌────────────────────┐
    │ _styles.j2         │
    │ CSS Variables      │
    ├────────────────────┤
    │ :root[data-theme]  │
    │   --bg-color       │
    │   --text-color     │
    │   --border-color   │
    └────────────────────┘
             │
             ▼
    All components styled dynamically
    based on active theme
```

## Component Communication

```
┌──────────────┐
│  _header.j2  │
│              │  Shares context:
│ Uses:        │  • request.user
│ • url()      │  • is_authenticated
│ • request    │  
└──────┬───────┘
       │
       ├─────────────┐
       │             │
       ▼             ▼
┌──────────────┐  ┌──────────────┐
│  _footer.j2  │  │  _styles.j2  │
│              │  │              │
│ Uses:        │  │ Defines:     │
│ • url()      │  │ • .logo      │
│ • request    │  │ • .nav-menu  │
│              │  │ • .user-info │
└──────────────┘  └──────┬───────┘
                         │
                         │ CSS classes used by
                         │ all components
                         ▼
                  ┌──────────────┐
                  │  Components  │
                  │ use classes  │
                  └──────────────┘
```

## Responsive Design Flow

```
Desktop (> 768px)           Mobile (≤ 768px)
─────────────────           ────────────────

┌─────────────────┐         ┌──────────┐
│ Logo | Nav | User│        │   Logo   │
└─────────────────┘         ├──────────┤
                             │   Nav    │
Horizontal layout            ├──────────┤
                             │   User   │
                             └──────────┘

                             Vertical stack

Media query in _styles.j2:
@media (max-width: 768px) {
  .header-container { flex-direction: column; }
  .nav-menu { width: 100%; }
}
```

## Extension Points

Child templates can customize via blocks:

```
┌─────────────────────────────────┐
│ {% block title %}               │ ← Page title
├─────────────────────────────────┤
│ {% block header %}              │ ← External libraries
├─────────────────────────────────┤
│ {% block css %}                 │ ← Custom styles
├─────────────────────────────────┤
│ {% block content %}             │ ← Main content
├─────────────────────────────────┤
│ {% block javascript %}          │ ← Custom scripts
└─────────────────────────────────┘

Example usage in child:
{% block css %}
{{ super() }}  ← Include parent styles
.my-class { color: red; }
{% endblock %}
```
