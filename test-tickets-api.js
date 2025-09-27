// Script de prueba para verificar la conectividad del API de tickets
const API_BASE_URL = 'http://localhost:8003'; // Backend de tickets

async function testTicketsAPI() {
  console.log('🧪 Probando conectividad con el backend de tickets...\n');

  // Test 1: Health Check
  try {
    console.log('1. 🏥 Health Check...');
    const healthResponse = await fetch(`${API_BASE_URL}/tickets/health`);
    const healthData = await healthResponse.text();
    console.log(`   ✅ Estado: ${healthResponse.status}`);
    console.log(`   📄 Respuesta: ${healthData}`);
  } catch (error) {
    console.log(`   ❌ Error en Health Check: ${error.message}`);
  }

  // Test 2: Obtener tickets con paginación
  try {
    console.log('\n2. 📋 Obtener tickets...');
    const ticketsResponse = await fetch(`${API_BASE_URL}/tickets?page=1&limit=10`);
    const ticketsData = await ticketsResponse.json();
    console.log(`   ✅ Estado: ${ticketsResponse.status}`);
    console.log(`   📊 Datos:`, JSON.stringify(ticketsData, null, 2));
  } catch (error) {
    console.log(`   ❌ Error obteniendo tickets: ${error.message}`);
  }

  console.log('\n🎯 Fin de las pruebas');
}

// Ejecutar las pruebas
testTicketsAPI();