# Multi-stage Dockerfile for ms-tickets (Spring Boot, Java 17)
FROM maven:3.9.4-eclipse-temurin-17 AS build
WORKDIR /workspace

# Cache dependencies
COPY pom.xml ./
COPY src ./src

# Build the application and create an executable jar
RUN mvn -B -DskipTests package spring-boot:repackage

FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy jar from build stage
COPY --from=build /workspace/target/*.jar app.jar

EXPOSE 8003

USER appuser
ENTRYPOINT ["java","-jar","/app/app.jar"]
# TODO: Completar según stack elegido
# Este Dockerfile será completado cuando el equipo elija el lenguaje y framework

# Ejemplo para Node.js:
# FROM node:18-alpine
# WORKDIR /app
# COPY package*.json ./
# RUN npm ci --only=production
# COPY . .
# EXPOSE 8003
# CMD ["npm", "start"]

# Ejemplo para Python:
# FROM python:3.11-slim
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . .
# EXPOSE 8003
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]

# Ejemplo para Java:
# FROM openjdk:17-jre-slim
# WORKDIR /app
# COPY target/*.jar app.jar
# EXPOSE 8003
# ENTRYPOINT ["java", "-jar", "app.jar"]

# Variables de entorno requeridas:
# - NOSQL_URL
# - NOSQL_DB

# TODO:
# 1. Elegir imagen base según lenguaje
# 2. Configurar instalación de dependencias
# 3. Configurar health check
# 4. Configurar multi-stage build si es necesario
# 5. Configurar usuario no-root para seguridad
