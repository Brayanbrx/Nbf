-- Script SQL para crear la base de datos NBF_Listados
-- Ejecutar en SQL Server Management Studio (SSMS)

-- 1. Crear la base de datos
CREATE DATABASE NBF_Listados;
GO

USE NBF_Listados;
GO

-- 2. Crear tabla Categoria
CREATE TABLE Categoria (
    Id_categoria INT IDENTITY(1,1) PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL UNIQUE,
    Descripcion VARCHAR(255) NULL,
    Activo BIT NOT NULL DEFAULT 1,
    Fecha_creacion DATETIME NOT NULL DEFAULT GETDATE()
);
GO

-- 3. Crear tabla Marca
CREATE TABLE Marca (
    Id_marca INT IDENTITY(1,1) PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL UNIQUE,
    Descripcion VARCHAR(255) NULL,
    Activo BIT NOT NULL DEFAULT 1,
    Fecha_creacion DATETIME NOT NULL DEFAULT GETDATE()
);
GO

-- 4. Crear tabla Producto
CREATE TABLE Producto (
    Id_producto INT IDENTITY(1,1) PRIMARY KEY,
    Codigo VARCHAR(50) NOT NULL UNIQUE,
    Nombre VARCHAR(150) NOT NULL,
    Descripcion VARCHAR(255) NULL,
    Url_imagen VARCHAR(500) NULL,
    Id_categoria INT NOT NULL,
    Id_marca INT NOT NULL,
    Precio_paquete_bs DECIMAL(18,2) NOT NULL DEFAULT 0,
    Precio_docena_bs DECIMAL(18,2) NOT NULL DEFAULT 0,
    Precio_caja_bs DECIMAL(18,2) NOT NULL DEFAULT 0,
    Unidades_por_paquete INT NULL,
    Unidades_por_docena INT NOT NULL DEFAULT 12,
    Unidades_por_caja INT NOT NULL,
    Activo BIT NOT NULL DEFAULT 1,
    Fecha_creacion DATETIME NOT NULL DEFAULT GETDATE(),
    Fecha_actualizacion DATETIME NOT NULL DEFAULT GETDATE(),
    Visible_catalogo_publico BIT NOT NULL DEFAULT 1,
    Mostrar_precio_paquete BIT NOT NULL DEFAULT 0,
    Mostrar_precio_docena BIT NOT NULL DEFAULT 0,
    Mostrar_precio_caja BIT NOT NULL DEFAULT 0,
    CONSTRAINT FK_Producto_Categoria FOREIGN KEY (Id_categoria) REFERENCES Categoria(Id_categoria),
    CONSTRAINT FK_Producto_Marca FOREIGN KEY (Id_marca) REFERENCES Marca(Id_marca),
    CONSTRAINT CHK_Precio_M0 CHECK (Precio_paquete_bs >= 0),
    CONSTRAINT CHK_Precio_D0 CHECK (Precio_docena_bs >= 0),
    CONSTRAINT CHK_Precio_C0 CHECK (Precio_caja_bs >= 0),
    CONSTRAINT CHK_Unid_P CHECK (Unidades_por_paquete IS NULL OR Unidades_por_paquete > 0),
    CONSTRAINT CHK_Unid_D CHECK (Unidades_por_docena > 0),
    CONSTRAINT CHK_Unid_C CHECK (Unidades_por_caja > 0)
);
GO

-- 5. Crear tabla Usuario
CREATE TABLE Usuario (
    Id_usuario INT IDENTITY(1,1) PRIMARY KEY,
    Nombre VARCHAR(120) NOT NULL,
    Email VARCHAR(150) NOT NULL UNIQUE,
    Password_hash VARCHAR(255) NOT NULL,
    Rol VARCHAR(20) NOT NULL DEFAULT 'ADMIN',
    Activo BIT NOT NULL DEFAULT 1,
    Fecha_creacion DATETIME NOT NULL DEFAULT GETDATE(),
    Ultimo_login DATETIME NULL,
    CONSTRAINT CHK_Rol CHECK (Rol IN ('ADMIN', 'EDITOR'))
);
GO

-- 6. Crear tabla HistorialEdicion (opcional, para auditoría)
CREATE TABLE HistorialEdicion (
    Id_edicion INT IDENTITY(1,1) PRIMARY KEY,
    Id_producto INT NOT NULL,
    Id_usuario INT NOT NULL,
    Cambio VARCHAR(500) NOT NULL,
    Fecha DATETIME NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_HistorialEdicion_Producto FOREIGN KEY (Id_producto) REFERENCES Producto(Id_producto),
    CONSTRAINT FK_HistorialEdicion_Usuario FOREIGN KEY (Id_usuario) REFERENCES Usuario(Id_usuario)
);
GO

-- 7. Crear índices para mejorar performance
CREATE INDEX IX_Producto_Nombre ON Producto(Nombre);
CREATE INDEX IX_Producto_Codigo ON Producto(Codigo);
CREATE INDEX IX_Producto_Categoria ON Producto(Id_categoria);
CREATE INDEX IX_Producto_Marca ON Producto(Id_marca);
CREATE INDEX IX_Producto_Activo ON Producto(Activo);
CREATE INDEX IX_Producto_Visible ON Producto(Visible_catalogo_publico);
CREATE INDEX IX_Usuario_Email ON Usuario(Email);
GO

-- 8. Insertar categorías de ejemplo (opcional)
INSERT INTO Categoria (Nombre, Descripcion, Activo) VALUES
    ('Electrónica', 'Productos electrónicos varios', 1),
    ('Ropa', 'Prendas de vestir', 1),
    ('Alimentos', 'Productos alimenticios', 1);
GO

-- 9. Insertar marcas de ejemplo (opcional)
INSERT INTO Marca (Nombre, Descripcion, Activo) VALUES
    ('Samsung', 'Marca electrónica coreana', 1),
    ('Sony', 'Marca japonesa de electrónica', 1),
    ('Generic', 'Marca genérica', 1);
GO

-- 10. Listo!
PRINT 'Base de datos NBF_Listados lista!';
