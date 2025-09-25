Detalle de cada aplicación:

1. accounts/ (Gestión de usuarios)

   Modelos: UserProfile, CreatorProfile, FollowerRelationship

   Funcionalidades: registro, login, perfiles, seguimiento de usuarios

2. content/ (Gestión de contenido)

   Modelos: Post, Media, Comment, Like, Category

   Funcionalidades: feed, contenido premium, interacciones

3. subscriptions/ (Sistema de pagos)

   Modelos: SubscriptionPlan, Payment, Transaction

   Funcionalidades: planes de suscripción, procesamiento de pagos, historial

4. messaging/ (Mensajería)

   Modelos: Conversation, Message

   Funcionalidades: chat entre usuarios y creadores

5. notifications/ (Notificaciones)

   Modelos: Notification

   Funcionalidades: notificaciones en tiempo real, emails

6. core/ (Funcionalidades comunes)

   Middlewares, utilidades, configuraciones comunes

7. analytics/ (Analíticas)

   Modelos: ViewerStats, EarningsReport

   Funcionalidades: métricas para creadores

templates/
└── content/
├── base/ # Plantillas base y componentes reutilizables
│ ├── base.html # Base principal
│ ├── header.html # Header específico de content
│ ├── sidebar.html # Sidebar de navegación
│ ├── post_card.html # Componente de tarjeta de post
│ ├── comment_item.html # Componente de comentario
│ ├── media_gallery.html # Galería de medios
│ └── pagination.html # Componente de paginación
│
├── feeds/ # Plantillas de feeds
│ ├── feed_home.html # Feed principal
│ ├── feed_discover.html # Feed de descubrimiento
│ ├── feed_creator.html # Feed de creador
│ └── feed_category.html # Feed por categoría
│
├── posts/ # Gestión de posts
│ ├── post_list.html # Lista de posts
│ ├── post_detail.html # Detalle de post
│ ├── post_form.html # Formulario crear/editar post
│ ├── post_confirm_delete.html
│ └── post_draft_list.html
│
├── interactions/ # Interacciones
│ ├── comments.html # Sección de comentarios
│ ├── likes_modal.html # Modal de likes
│ └── bookmarks.html # Página de bookmarks
│
├── moderation/ # Moderación
│ ├── moderation_dashboard.html
│ ├── report_list.html
│ ├── review_report.html
│ └── report_modal.html
│
└── dashboard/ # Dashboards
├── dashboard.html # Dashboard principal
├── creator_dashboard.html
└── analytics.html
