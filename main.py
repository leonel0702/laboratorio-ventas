from datetime import date, time
from typing import List
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Time, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session

DATABASE_URL = "sqlite:///./ventas.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Tabla "productos"
class ProductoORM(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nombre = Column(String, nullable=False)                                  
    precio = Column(Float, nullable=False)                                    

    ventas = relationship("VentaORM", back_populates="producto")

# Tabla "ventas"s
class VentaORM(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    id_producto = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_total = Column(Float, nullable=False)

    producto = relationship("ProductoORM", back_populates="ventas")

# Crea las tablas físicamente en el archivo SQLite si no existen
Base.metadata.create_all(bind=engine)

# Para crear un producto (el cliente no envía el ID porque se crea solo)
class ProductoCreate(BaseModel):
    nombre: str
    precio: float

# Para responder con un producto (incluye el ID ya creado)
class ProductoResponse(BaseModel):
    id: int
    nombre: str
    precio: float

    class Config:
        from_attributes = True

# Para crear una venta
class VentaCreate(BaseModel):
    fecha: date
    hora: time
    id_producto: int
    cantidad: int

# Para responder con una venta (incluye el objeto producto completo adentro)
class VentaResponse(BaseModel):
    id: int
    fecha: date
    hora: time
    producto: ProductoResponse
    cantidad: int
    precio_total: float

    class Config:
        from_attributes = True

app = FastAPI(title="API - Sistema de Ventas")

        # Ejemplo 1: Crear un producto (POST)
@app.post("/productos", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def crear_producto(producto: ProductoCreate):
    db: Session = SessionLocal()
    try:
        nuevo_producto = ProductoORM(nombre=producto.nombre, precio=producto.precio)
        db.add(nuevo_producto)
        db.commit()
        db.refresh(nuevo_producto)
        return nuevo_producto
    finally:
        db.close()

# Ejemplo 2: Listar todos los productos (GET)
@app.get("/productos", response_model=List[ProductoResponse])
def listar_productos():
    db: Session = SessionLocal()
    try:
        return db.query(ProductoORM).all()
    finally:
        db.close()