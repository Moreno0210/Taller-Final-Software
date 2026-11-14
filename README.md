
### 1. Diagnóstico técnico del código original

### A. Identificación de los principios SOLID

  Principio de responsabilidad única

Se incumple en la clase `NotificationDispatcher` del archivo `services/notification_core.py`, porque maneja diferentes canales de notificación dentro de una misma clase. 

También se incumple en el método `process_checkout` de `routers/checkout.py`, porque realiza la gestión del inventario, los pagos, la generación de documentos y el envío de notificaciones.

  Principio abierto/cerrado 

Se incumple en `NotificationDispatcher`, porque utiliza condiciones `if`, `elif` y `else` para seleccionar los canales de notificación. Para agregar un nuevo canal es necesario modificar la clase existente.

  Principio de sustitución de Liskov 

El código original no define contratos abstractos para los servicios, por lo que no establece cómo deben comportarse sus diferentes implementaciones. Esto dificulta sustituir una implementación por otra manteniendo un comportamiento esperado.

No se identifica una violación clásica de una subclase concreta, pero sí una deficiencia en el diseño de contratos.
  Principio de segregación de interfaces 
El código original no utiliza interfaces independientes para separar las operaciones de inventario, pagos, pedidos y notificaciones. Esto genera dependencias directas entre componentes que deberían estar separados.

  Principio de inversión de dependencias

Se incumple en `routers/checkout.py`, porque depende directamente de clases concretas como `TransactionManager`, `StripePaymentGateway`, `InvoiceGenerator` y `NotificationDispatcher`.

También ocurre en `database/session_manager.py`, porque depende directamente de la instancia global `db_instance`.

### B. Impacto de las operaciones síncronas en FastAPI

El código original mezcla operaciones síncronas dentro de una aplicación asíncrona.

En `database/session_manager.py` se utiliza `time.sleep(0.5)`, que bloquea el hilo durante medio segundo.

En `services/payment_service.py` se utiliza `requests.post()`, que realiza solicitudes HTTP de manera síncrona y bloquea el Event Loop mientras espera una respuesta.

En `services/document_service.py` se ejecuta un ciclo de cinco millones de iteraciones para realizar cálculos matemáticos. Esto consume CPU y puede impedir que el servidor atienda otras solicitudes.

Estas operaciones aumentan los tiempos de respuesta, reducen la capacidad de concurrencia y afectan el rendimiento general del servidor.

Para solucionar estos problemas se utiliza `httpx.AsyncClient` en las operaciones HTTP y `ProcessPoolExecutor` para delegar los cálculos intensivos de CPU.

### C. Análisis matemático de la condición de carrera

El inventario inicial del producto `PROD-A99` es de 10 unidades.

Supongamos que dos usuarios realizan simultáneamente una compra de 7 unidades cada uno.

En el código original puede ocurrir lo siguiente:

1. El usuario A consulta el inventario y obtiene 10 unidades.
2. El usuario B consulta el inventario y también obtiene 10 unidades.
3. Ambos comprueban que existen unidades suficientes.
4. El usuario A descuenta 7 unidades y guarda un inventario de 3.
5. El usuario B también descuenta 7 unidades utilizando el valor anterior y guarda nuevamente 3.

La demanda total sería:

7 + 7 = 14 unidades.

Sin embargo, solamente existen 10 unidades.

El resultado es incorrecto porque ambas operaciones utilizan la misma lectura inicial del inventario.

Si S representa el stock inicial y q1 y q2 las cantidades solicitadas, el resultado correcto debería ser:

S - q1 - q2

Pero el código original puede terminar guardando:

S - q1 o S - q2

Esto ocurre porque una actualización sobrescribe la otra.

Para solucionar el problema se implementó `asyncio.Lock`, que protege la lectura, validación y actualización del inventario como una operación crítica.

## 2. Reestructuración de arquitectura

Se reorganizó el proyecto aplicando los principios de Arquitectura Limpia.

Las responsabilidades quedaron distribuidas de la siguiente manera:

- `domain`: contiene las entidades principales del negocio.
- `application`: contiene los casos de uso y las interfaces abstractas.
- `infrastructure`: contiene las implementaciones de persistencia, pagos, documentos y notificaciones.
- `api`: configura las dependencias de la aplicación.
- `routers`: contiene los endpoints de FastAPI.
- `tests`: contiene las pruebas automatizadas.

### Inversión de dependencias

Se implementaron interfaces abstractas utilizando `abc.ABC` y `@abstractmethod`.

Entre ellas se encuentran:

- `InventoryRepository`
- `OrderRepository`
- `PaymentGateway`
- `NotificationChannel`
- `InvoiceGenerator`

El caso de uso `CheckoutUseCase` depende de estas abstracciones y no de implementaciones concretas.

Las dependencias se configuran en `api/dependencies.py` y se inyectan en las rutas mediante `Depends`.

## 3. Patrones de diseño y concurrencia

### Patrón Strategy

Se implementó el patrón Strategy para separar los canales de notificación.

Se crearon las clases:

- `EmailChannel`
- `SMSChannel`
- `WebhookChannel`

Todas implementan la interfaz `NotificationChannel`, pero cada una tiene su propia implementación del método `send`.

Esto permite agregar nuevos canales sin modificar las clases existentes.

### Composición de notificaciones

El caso de uso recibe una colección de canales de notificación y coordina su ejecución. De esta manera, los canales pueden seleccionarse y utilizarse sin conocer sus detalles internos.

### Control de concurrencia

Se utilizó `asyncio.Lock` en `InMemoryStore` para garantizar que dos operaciones concurrentes no modifiquen el mismo inventario simultáneamente.

La reserva y devolución de unidades se realizan dentro de secciones críticas protegidas.

Cuando el pago es rechazado, las unidades reservadas se devuelven al inventario.

### Procesamiento intensivo de CPU

Se implementó `ProcessPoolExecutor` junto con `run_in_executor` para ejecutar los cálculos intensivos de generación de documentos en otro proceso.

Esto evita ejecutar el ciclo de cinco millones de iteraciones directamente en el hilo del Event Loop.

## 4. Pruebas automatizadas

Se implementaron pruebas asíncronas utilizando `pytest` y `pytest-asyncio`.

Las pruebas verifican:

1. Que dos reservas simultáneas no permitan vender más unidades de las disponibles.
2. Que la devolución de inventario restaure las unidades.
3. Que una compra exitosa descuente correctamente el inventario.
4. Que un pago rechazado devuelva las unidades reservadas.
5. Que una compra superior al stock disponible sea rechazada.

Para ejecutar las pruebas se utiliza:

```bash
python -m pytest -v
```

## 5. Ejecución del proyecto

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

Iniciar el servidor:

```bash
uvicorn main:app --reload
```

La documentación de la API estará disponible en:

http://127.0.0.1:8000/docs

El estado del servidor puede consultarse en:

http://127.0.0.1:8000/health

## 6. Consideraciones finales

El proyecto utiliza almacenamiento en memoria y una pasarela de pagos simulada para facilitar las pruebas sin utilizar credenciales reales.

El bloqueo `asyncio.Lock` protege las operaciones concurrentes dentro de una misma instancia del servidor. Para un entorno distribuido se requiere una base de datos transaccional que garantice la atomicidad entre diferentes procesos o servidores.

La implementación representa una solución académica de refactorización y separación de responsabilidades. Para producción también sería necesario implementar mecanismos de idempotencia, recuperación ante fallos y consistencia entre los pagos, los pedidos y las notificaciones.
