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
