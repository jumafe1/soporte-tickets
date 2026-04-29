# Sistema de tickets de soporte

Aplicación web desarrollada con Django para crear, consultar y administrar tickets de soporte.

## Requisitos

- Python 3.11 o superior
- pip
- Git

## Pasos para ejecutar el proyecto localmente

### 1. Clonar el repositorio

```bash
git clone URL_DEL_REPOSITORIO
cd NOMBRE_DEL_REPOSITORIO
```

Si ya tienes la carpeta del proyecto, entra a la carpeta donde está `manage.py`:

```bash
cd soporte
```

### 2. Verificar que estás en la carpeta correcta

```bash
ls
```

Debes ver archivos como `manage.py`, `requirements.txt` y la carpeta `tickets`.

### 3. Crear y activar el entorno virtual

En macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

En Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Crear el archivo `.env`

```bash
cp .env.example .env
```

En Windows, si `cp` no funciona:

```bash
copy .env.example .env
```

### 6. Crear la base de datos

```bash
python manage.py migrate
```

### 7. Crear usuarios y datos de prueba

```bash
python manage.py seed
```

Este comando crea los usuarios de prueba, categorías y tickets iniciales.

### 8. Ejecutar el servidor

```bash
python manage.py runserver
```

Abrir en el navegador:

```text
http://127.0.0.1:8000/login/
```

## Usuarios de prueba

### Administrador

```text
Usuario: admin
Contraseña: admin123
```

El administrador entra al panel Kanban en:

```text
http://127.0.0.1:8000/admin-panel/
```

### Usuario normal 1

```text
Usuario: user1
Contraseña: user1123
```

### Usuario normal 2

```text
Usuario: user2
Contraseña: user2123
```

Los usuarios normales entran a:

```text
http://127.0.0.1:8000/mis-tickets/
```

## Comandos útiles

Crear base de datos:

```bash
python manage.py migrate
```

Cargar datos de prueba:

```bash
python manage.py seed
```

Ejecutar servidor:

```bash
python manage.py runserver
```

Entrar al panel admin nativo de Django:

```text
http://127.0.0.1:8000/admin/
```

## Notas

- La base de datos local es SQLite y se crea automáticamente con `migrate`.
- Si se borra la base de datos, se puede reconstruir ejecutando otra vez:

```bash
python manage.py migrate
python manage.py seed
```
