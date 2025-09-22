# Multi-stage build para optimizar la imagen final
FROM golang:1.21-alpine AS builder

# Instalar dependencias de compilación
RUN apk add --no-cache git ca-certificates tzdata

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY go.mod go.sum ./

# Descargar dependencias
RUN go mod download

# Copiar código fuente
COPY src/ ./src/

# Compilar la aplicación
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main ./src/

# Imagen final mínima
FROM alpine:3.18

# Instalar certificados SSL y timezone data
RUN apk --no-cache add ca-certificates tzdata

# Crear usuario no-root
RUN adduser -D -s /bin/sh appuser

# Establecer directorio de trabajo
WORKDIR /app/

# Copiar el binario compilado desde la etapa builder
COPY --from=builder /app/main .

# Cambiar propiedad del archivo al usuario appuser
RUN chown appuser:appuser main

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8004

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8004/health || exit 1

# Comando por defecto
CMD ["./main"]
