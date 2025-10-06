const { Sequelize } = require('sequelize');
const { Client: PgClient } = require('pg');
const { MongoClient } = require('mongodb');
const CONFIG = require('./constants');

class DatabaseManager {
  constructor() {
    this.mysqlConn = null;
    this.pgClient = null;
    this.mongoClient = null;
    this.mongoDB = null;
  }

  async connectAll() {
    console.log('🔌 Conectando a las bases de datos...\n');

    try {
      await this.connectMySQL();
      await this.connectPostgreSQL();
      await this.connectMongoDB();
      
      console.log('✅ Todas las conexiones establecidas\n');
    } catch (error) {
      console.error('❌ Error conectando bases de datos:', error.message);
      throw error;
    }
  }

  async connectMySQL() {
    this.mysqlConn = new Sequelize(
      CONFIG.mysql.database,
      CONFIG.mysql.user,
      CONFIG.mysql.password,
      {
        host: CONFIG.mysql.host,
        port: CONFIG.mysql.port,
        dialect: 'mysql',
        logging: false,
        define: {
          timestamps: true,
          underscored: true,
          freezeTableName: true
        }
      }
    );

    await this.mysqlConn.authenticate();
    console.log(`✅ MySQL conectado (${CONFIG.mysql.host}:${CONFIG.mysql.port})`);
  }

  async connectPostgreSQL() {
    this.pgClient = new PgClient({
      host: CONFIG.postgres.host,
      port: CONFIG.postgres.port,
      database: CONFIG.postgres.database,
      user: CONFIG.postgres.user,
      password: CONFIG.postgres.password
    });

    await this.pgClient.connect();
    console.log(`✅ PostgreSQL conectado (${CONFIG.postgres.host}:${CONFIG.postgres.port})`);
  }

  async connectMongoDB() {
    this.mongoClient = new MongoClient(CONFIG.mongodb.url);
    await this.mongoClient.connect();
    this.mongoDB = this.mongoClient.db(CONFIG.mongodb.database);
    
    console.log(`✅ MongoDB conectado (${CONFIG.mongodb.database})`);
  }

  async cleanAll() {
    console.log('🧹 Limpiando bases de datos...\n');

    try {
      // Limpiar MySQL (trips y routes)
      await this.mysqlConn.query('SET FOREIGN_KEY_CHECKS = 0');
      await this.mysqlConn.query('TRUNCATE TABLE trips');
      await this.mysqlConn.query('TRUNCATE TABLE routes');
      await this.mysqlConn.query('SET FOREIGN_KEY_CHECKS = 1');
      console.log('✅ MySQL limpio (routes, trips)');

      // Limpiar PostgreSQL (passengers)
      await this.pgClient.query('TRUNCATE TABLE passengers RESTART IDENTITY CASCADE');
      console.log('✅ PostgreSQL limpio (passengers)');

      // Limpiar MongoDB (tickets)
      await this.mongoDB.collection('tickets').deleteMany({});
      console.log('✅ MongoDB limpio (tickets)\n');

    } catch (error) {
      console.error('❌ Error limpiando bases de datos:', error.message);
      throw error;
    }
  }

  async closeAll() {
    console.log('\n🔌 Cerrando conexiones...');
    
    try {
      if (this.mysqlConn) {
        await this.mysqlConn.close();
        console.log('✅ MySQL desconectado');
      }
      
      if (this.pgClient) {
        await this.pgClient.end();
        console.log('✅ PostgreSQL desconectado');
      }
      
      if (this.mongoClient) {
        await this.mongoClient.close();
        console.log('✅ MongoDB desconectado');
      }
    } catch (error) {
      console.error('❌ Error cerrando conexiones:', error.message);
    }
  }

  // Getters para acceso a las conexiones
  get mysql() { return this.mysqlConn; }
  get postgres() { return this.pgClient; }
  get mongo() { return this.mongoDB; }
}

module.exports = DatabaseManager;
