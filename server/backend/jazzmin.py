"""Theme for the Django admin (django-jazzmin), where moderators review flagged messages."""

JAZZMIN_SETTINGS = {
    "site_title": "Chat moderation",
    "site_header": "Chat moderation",
    "site_brand": "Toxic Comment Classifier",
    "welcome_sign": "Review users, messages and the labels the model gave them",
    "site_logo": "dp.jpg",
    "theme": "darkly",
    "custom_css": "custom_admin.css",
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "icon": "fas fa-home"},
        {"model": "chat.User"},
        {"model": "chat.Message"},
    ],
    "icons": {
        "chat.User": "fas fa-user",
        "chat.Message": "fas fa-comments",
        "chat.Feedback": "fas fa-comment-dots",
        "auth.Group": "fas fa-users",
    },
    "order_with_respect_to": ["chat.Message", "chat.User", "chat.Feedback"],
    "changeform_format": "horizontal",
    "show_sidebar": True,
    "navigation_expanded": True,
    "related_modal_active": True,
}

JAZZMIN_UI_TWEAKS = {
    "body_small_text": True,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "sidebar": "sidebar-dark-primary",
    "theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}
