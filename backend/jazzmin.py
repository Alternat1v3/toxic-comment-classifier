JAZZMIN_SETTINGS = {
    # Branding
    "site_title": "Chat Application",
    "site_header": "Chat Application",
    "site_brand": "Toxic Comment Classification",
    "welcome_sign": "Toxic Comment Classification Using Deep Learning",
    "copyright": "Toxic Comment Classification Using Deep Learning Built by ZOHAIB IQBAL",
    "site_logo": "dp.jpg",
    # Theme and Customization
    "theme": "darkly",  # You can use other themes or create a custom one
    "show_ui_builder": True,
    "custom_css": "custom_admin.css",  # Custom CSS file
    "custom_js": "path/to/your/custom_admin.js",  # Custom JS file (optional)
    # Navigation
    "topmenu_small": True,
    "topmenu_links": [
        {"name": "Home", "url": "http://127.0.0.1:8000/admin/", "icon": "fas fa-home"},
        {
            "name": "Users",
            "url": "http://127.0.0.1:8000/admin/chat/customuser/",
            "icon": "fas fa-home",
        },
        {
            "name": "Messages",
            "url": "http://127.0.0.1:8000/admin/chat/message/",
            "icon": "fas fa-home",
        },
    ],
    "usermenu_links": [
        {
            "name": "Support",
            "url": "https://github.com/Alternat1v3",
            "new_window": True,
        },
        {"model": "auth.user"},
    ],
    # Icons
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
    # Other Settings
    "changeform_format": "horizontal",
    "show_sidebar": True,
    "sidebar_modules": True,
    "related_modal_active": True,
    "footer": False,  # Default to True to show footer
}
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": True,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "darkly",
    "dark_mode_theme": "cyborg",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}
