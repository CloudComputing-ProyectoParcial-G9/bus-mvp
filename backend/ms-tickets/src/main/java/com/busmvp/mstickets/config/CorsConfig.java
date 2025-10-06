package com.busmvp.mstickets.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

@Configuration
public class CorsConfig {

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {

    CorsConfiguration configuration = new CorsConfiguration();
    // Permitir cualquier origen
    configuration.addAllowedOriginPattern("*");

    // Métodos HTTP permitidos
    configuration.setAllowedMethods(java.util.Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"));

    // Headers permitidos
    configuration.setAllowedHeaders(java.util.Arrays.asList("*"));
    // Headers expuestos
    configuration.setExposedHeaders(java.util.Arrays.asList("*"));

    // NO permitir credenciales para evitar problemas con wildcard
    configuration.setAllowCredentials(false);

    // Configurar tiempo de cache para preflight requests
    configuration.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}
