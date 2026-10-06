# Roadmap del proyecto

## Objetivo

Construir un sistema de notificaciones para usuarios autenticados con FastAPI.
El proyecto prioriza entender las decisiones de arquitectura y los conceptos
de Python que las hacen posibles. La migración de SQLite a PostgreSQL será la
última etapa, para que sea una evolución real de un producto ya funcional.

## Principios de trabajo

- Mantener el alcance actual: SQLite y SQLAlchemy hasta la fase de migración.
- Aplicar una **Clean Architecture ligera**: separar dominio, aplicación e
  infraestructura sin crear capas o abstracciones que todavía no aporten valor.
- Diseñar los canales para extenderlos sin modificar el flujo central de
  creación de notificaciones.
- Introducir cada herramienta por una necesidad concreta del producto.
- Priorizar pruebas de integración: comprobar el recorrido observable de la
  API de punto A a punto B.

## Prácticas adoptadas de repositorios de referencia

Los siguientes repositorios son inspiración técnica, no plantillas que se
copiarán literalmente:

- [cosmos-challenge](https://github.com/yaritaft/cosmos-challenge): estrategias
  intercambiables, separación entre servicio, repositorio y cliente externo,
  reintentos ante límites de la API, Docker y CI/cobertura.
- [microservices_flask_challenge_bkr](https://github.com/yaritaft/microservices_flask_challenge_bkr):
  configuración por entorno, Compose separado para desarrollo/pruebas/
  producción, migraciones, hooks de calidad y pruebas de integración que
  recorren HTTP, persistencia y respuesta.

Aplicaremos las ideas siguientes, adaptadas a un monolito modular de FastAPI:

- Documentar decisiones arquitectónicas relevantes de manera breve en
  `docs/adr/` (contexto, decisión, consecuencias y alternativas descartadas).
- Tratar Email/SMS/Push y SQS como adaptadores de infraestructura: el dominio
  no importará SDKs, `httpx` ni detalles de SQLAlchemy.
- Declarar contratos de salida (puertos) y proporcionar adaptadores concretos.
  Así los tests podrán reemplazar únicamente las fronteras externas.
- Añadir reintentos con backoff ante errores transitorios o `429`, con un
  límite explícito. Nunca reintentar validaciones del cliente (`4xx` no
  transitorios).
- Exponer el resultado como una operación con estado. Si el proveedor es lento,
  la API no mantendrá la petición HTTP abierta esperando indefinidamente: el
  paso natural será encolar con SQS y consultar el estado de entrega.
- Mantener comandos reproducibles y un README que explique cómo levantar,
  probar y verificar calidad del proyecto en contenedores.

No adoptaremos todavía la división en microservicios ni bases de datos por
servicio: aumentaría la complejidad antes de que el dominio lo justifique.
Tampoco se incluirán secretos de ejemplo funcionales en archivos Compose;
usaremos `.env.example` sin valores reales y variables de entorno.

## Convenciones transversales

Estas prácticas se incorporan de forma proporcional durante las seis fases;
no constituyen pasos que puedan cambiar su orden. Por ejemplo, los tests de
integración acompañan cada endpoint nuevo, mientras que Docker y CI se
consolidan cuando ya existe un flujo completo que ejecutar.

### Arquitectura

- Mantener una Clean Architecture ligera: dominio y casos de uso no importan
  detalles de FastAPI, SQLAlchemy, `httpx`, SDKs ni SQS.
- Crear un ADR breve para decisiones con consecuencias duraderas.
- Aplicar contratos/puertos y adaptadores solamente en fronteras externas o
  donde haya más de una implementación real.

### Calidad y pruebas

- Priorizar tests de integración de endpoints y casos de uso: request,
  persistencia, respuesta y efectos observables.
- Usar mocks/fakes únicamente en límites externos: APIs de proveedores,
  SQS y dependencias de infraestructura.
- Para cada caso importante, comprobar tanto la respuesta HTTP como el efecto
  persistido: por ejemplo, crear una notificación y verificar después su
  estado de entrega mediante el endpoint o la base de datos de pruebas.
- El entorno de tests usará servicios efímeros/contenedores aislados; no
  reutilizará datos persistentes de desarrollo.
- Configurar Ruff format y Ruff check como formatter/linter; añadir hooks de
  pre-commit antes de introducir CI.
- Configurar CI para formato, lint, tests y cobertura; publicar badges de CI y
  Coveralls en el README y exigir un mínimo de 80% de cobertura útil.

### Entornos y secretos

- Crear progresivamente `docker-compose-dev`, `docker-compose-prod` y
  `docker-compose-test`, y ejecutar también la suite desde el contenedor de
  pruebas.
- Usar healthchecks para dependencias que deban estar realmente disponibles;
  `depends_on` por sí solo no demuestra que una base de datos o un servicio
  externo esté listo.
- Mantener secretos y configuración por entorno fuera de las imágenes y del
  control de versiones, con un `.env.example` documentado y sin valores
  válidos.

## Fases principales, en orden

### 1. Arquitectura de notificaciones y eventos síncronos

- Crear el módulo de notificaciones y su modelo persistente.
- Definir los casos de uso: crear, editar, eliminar y listar las
  notificaciones del propietario.
- Al crear una notificación, emitir y manejar síncronamente un evento interno
  `NotificationCreated`.
- Registrar el ciclo de entrega: `pending`, `sent` y `failed`.
- Separar la lógica de dominio de los adaptadores de infraestructura actuales
  (SQLAlchemy, HTTP, proveedor de mensajería).
- Crear un ADR breve que describa el flujo síncrono inicial y el criterio que
  motivará su evolución a SQS.

**Resultado verificable:** una petición de creación persiste la notificación,
ejecuta el flujo de entrega y deja un estado de entrega consultable.

### 2. Canales extensibles

- Implementar Email, SMS y Push Notification como estrategias/adaptadores
  independientes.
- Email: validar destinatario, generar plantilla y registrar el envío.
- SMS: validar límite de 160 caracteres y registrar número y fecha.
- Push: validar token de dispositivo, construir payload y registrar estado.
- Usar un contrato común; añadir un canal nuevo debe requerir una
  implementación nueva, no modificar una cadena central de condicionales.
- Mantener los detalles del proveedor fuera del caso de uso; el canal devolverá
  un resultado de entrega normalizado para que el dominio no dependa de una
  respuesta HTTP concreta.

**Python a reforzar:** `Protocol` o clases abstractas, polimorfismo y
dependencia de abstracciones.

### 3. Integración con API externa usando async

- Sustituir al menos un canal simulado por un proveedor HTTP externo.
- Usar `httpx.AsyncClient` y una dependencia/lifecycle apropiados para el
  cliente HTTP.
- Configurar timeouts, traducir errores externos a errores del dominio y
  definir una política básica de reintentos.
- Implementar backoff para errores transitorios y límites de tasa (`429`), con
  número máximo de intentos y trazabilidad de cada fallo.
- Distinguir operaciones de I/O asíncrono de código bloqueante.

**Python a reforzar:** coroutines, `async`/`await`, event loop, context
managers asíncronos y propagación de excepciones.

### 4. Autenticación, autorización y seguridad

- Registro de usuarios con contraseña hasheada; nunca persistir contraseñas
  en texto plano.
- Login con token de acceso JWT y dependencia para obtener al usuario actual.
- Proteger los endpoints y garantizar ownership: cada usuario solo gestiona
  sus notificaciones.
- Guardar la clave secreta en variables de entorno/configuración, nunca en el
  repositorio ni en el código.
- Firmar y verificar JWT con algoritmo explícito, validando expiración y
  claims necesarios.

> Un JWT habitual se **firma**, no se cifra. El decodificador/verificador usa
> la clave secreta para comprobar que el token no fue alterado; no debe usarse
> para tratar el contenido del token como secreto.

**Resultado verificable:** un token válido autoriza la petición; uno alterado,
expirado o sin firma válida queda rechazado.

### 5. Procesamiento desacoplado con SQS

- Publicar trabajos de entrega en SQS en lugar de ejecutar el envío dentro de
  la petición HTTP.
- Crear un worker consumidor que ejecute los adaptadores de canal.
- Definir reintentos, idempotencia, fallos y actualización de estados.
- Conservar el contrato de los canales para que la infraestructura cambie sin
  alterar el dominio.

**Resultado verificable:** la API responde tras encolar el trabajo y el worker
actualiza el estado de la notificación de forma independiente.

### 6. Migración a PostgreSQL y Alembic

- Mover la configuración de base de datos a variables de entorno.
- Añadir Alembic, configurarlo con los metadatos de SQLAlchemy y generar una
  migración inicial desde el esquema existente.
- Aplicar la migración en una base de datos vacía y comprobar que crea el
  esquema esperado sin ejecutar `create_all()` en producción.
- Practicar una segunda migración evolutiva sobre un campo real del producto
  (añadir, transformar y, si procede, rellenar datos existentes), en lugar de
  limitarse a la migración inicial.
- Verificar que se puede hacer downgrade de forma segura cuando el cambio lo
  permita; documentar explícitamente los cambios irreversibles.
- Levantar PostgreSQL en Docker para desarrollo y pruebas apropiadas.
- Validar con tests de integración que el producto funciona tras `upgrade` y
  documentar el proceso de migración y rollback en el README.

**Resultado verificable:** una base PostgreSQL vacía alcanza la última
revisión de Alembic, la API funciona sobre ese esquema y una evolución de
modelo queda representada por una migración revisable en Git.

## Orden inmediato

El siguiente bloque de trabajo es la **Fase 1**: diseñar el dominio de
notificaciones y el flujo de evento síncrono. Antes de escribir código, se
acordará qué ocurre si el envío falla después de persistir la notificación y
cómo se resolverá el canal de envío.
