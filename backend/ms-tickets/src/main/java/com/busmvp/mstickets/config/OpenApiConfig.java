package com.busmvp.mstickets.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Bus MVP - Tickets Service API")
                        .version("1.0.0")
                        .description("API para gestión de boletos del sistema Bus MVP. " +
                                "Permite crear, consultar, actualizar y eliminar tickets de pasajeros.")
                        .contact(new Contact()
                                .name("Bus MVP Team")
                                .email("dev@busmvp.com"))
                        .license(new License()
                                .name("MIT License")
                                .url("https://opensource.org/licenses/MIT")))
                .servers(List.of(
                        new Server()
                                .url("http://localhost:8003")
                                .description("Servidor de desarrollo"),
                        new Server()
                                .url("http://localhost:8080")
                                .description("Load Balancer")
                ));
    }
}
