-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: localhost    Database: bdhidrocolon
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cierre`
--

DROP TABLE IF EXISTS `cierre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cierre` (
  `id` int NOT NULL,
  `nombre` varchar(45) DEFAULT NULL,
  `cantidad` int DEFAULT NULL,
  `tarjeta` int DEFAULT NULL,
  `efectivo` int DEFAULT NULL,
  `monto` int DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `usuario` varchar(45) DEFAULT NULL,
  `carrito_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_cierre_carrito1_idx` (`carrito_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COMMENT='			';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cierre`
--

LOCK TABLES `cierre` WRITE;
/*!40000 ALTER TABLE `cierre` DISABLE KEYS */;
INSERT INTO `cierre` VALUES (1,'Hidrocolon',1,0,490,490,'2025-01-08','admin',1),(2,'Biopuntura Reckewerg',1,0,325,325,'2025-01-08','admin',1),(3,'Hidrocolon',1,0,490,490,'2025-01-08','admin',2),(4,'Biopuntura Reckewerg',1,0,325,325,'2025-01-08','admin',2),(5,'Hidrocolon',1,0,490,490,'2025-01-08','admin',3),(6,'Biopuntura Reckewerg',1,0,325,325,'2025-01-08','admin',3),(7,'Desintoxicacion',1,0,225,225,'2025-01-08','admin',4),(8,'Hidrocolon',1,0,490,490,'2025-01-08','admin',5),(9,'Desintoxicacion',1,0,225,225,'2025-01-08','admin',6),(10,'Tonico Cirnatural HC',2,800,0,800,'2025-01-08','admin',7),(11,'Desintoxicacion',1,250,0,250,'2025-01-08','admin',8),(12,'Tonico Femnatural HC',2,0,1000,1000,'2025-01-08','admin',9),(13,'Consulta',1,100,0,100,'2025-01-08','admin',10),(14,'Desintoxicacion',1,250,0,250,'2025-01-08','admin',10),(15,'Biotisil',3,0,0,0,'2025-01-08','admin',10),(16,'Century',1,0,0,0,'2025-01-08','admin',10),(17,'Prueba',1,330,0,330,'2025-01-08','admin',11),(18,'Fibra HC 500 gr',2,800,0,800,'2025-01-08','admin',12),(19,'Inyección',1,0,25,25,'2025-01-08','vende',13),(20,'Vita C-15',1,0,0,0,'2025-01-08','vende',13),(21,'Lavativa + irrigador',1,525,0,525,'2025-01-08','admin',14),(22,'Tonico Cirnatural HC',1,0,0,0,'2025-01-08','admin',14),(23,'Tonico Hormonal HC',1,0,0,0,'2025-01-08','admin',14),(24,'Lavativa + irrigador',1,525,0,525,'2025-01-08','admin',15),(25,'Tonico Cirnatural HC',1,0,0,0,'2025-01-08','admin',15),(26,'Tonico Hormonal HC',1,0,0,0,'2025-01-08','admin',15),(27,'Fibra HC 500 gr',90,0,33750,33750,'2025-01-08','admin',16),(28,'Consulta',1,0,100,100,'2025-01-08','admin',16),(29,'Fibra HC 500 gr',90,0,33750,33750,'2025-01-08','admin',17),(30,'Consulta',1,0,100,100,'2025-01-08','admin',17),(31,'Fibra HC 500 gr',90,0,33750,33750,'2025-01-08','admin',18),(32,'Consulta',1,0,100,100,'2025-01-08','admin',18),(33,'Fibra HC 500 gr',90,0,33750,33750,'2025-01-08','admin',19),(34,'Consulta',1,0,100,100,'2025-01-08','admin',19),(35,'Fibra HC 500 gr',90,0,33750,33750,'2025-01-08','admin',20),(36,'Consulta',1,0,100,100,'2025-01-08','admin',20),(38,'Consulta',1,0,100,100,'2025-01-08','admin',21),(39,'Consulta',1,0,100,100,'2025-01-08','admin',22),(40,'Consulta',1,0,100,100,'2025-01-08','admin',23),(41,'Prueba',1,0,240,240,'2025-01-08','admin',24),(42,'Consulta',1,0,100,100,'2025-01-08','admin',25),(43,'Tónico CLR',2,800,0,800,'2025-01-08','admin',26),(44,'Tonico Hormonal HC',1,400,0,400,'2025-01-08','admin',26),(45,'Tónico CLR',2,800,0,800,'2025-01-08','admin',27),(46,'Tonico Hormonal HC',1,400,0,400,'2025-01-08','admin',27),(47,'Fibra HC 500 gr',90,36000,0,36000,'2025-01-08','admin',28),(48,'Tonico Cirnatural HC',1,0,375,375,'2025-01-09','admin',29),(49,'Tonico Cirnatural HC',1,0,375,375,'2025-01-09','admin',30),(50,'Tonico Gastrinatural HC',1,400,0,400,'2025-01-09','admin',31),(51,'Tonico Hormonal HC',2,0,750,750,'2025-01-10','admin',32),(52,'Fibra HC 500 gr',90,0,33750,33750,'2025-01-10','admin',32),(53,'Masaje con tens',1,0,200,200,'2025-01-10','admin',32),(54,'Suero Hartman',1,0,150,150,'2025-01-10','admin',32),(55,'Moringa',1,0,0,0,'2025-01-10','admin',32),(56,'Tónico CLR',1,0,0,0,'2025-01-10','admin',32),(57,'Hidrocolon promo 3',1,0,1100,1100,'2025-01-10','admin',32),(58,'Tonico Gastrinatural HC',1,0,375,375,'2025-01-10','admin',33),(59,'Consulta',1,150,0,150,'2025-01-10','admin',34),(60,'Consulta',1,150,0,150,'2025-01-10','admin',35),(61,'Activa',2,1350,0,1350,'2025-01-10','admin',35),(62,'Consulta',1,0,100,100,'2025-02-03','admin',36),(63,'Consulta',1,0,100,100,'2025-02-03','admin',37),(64,'Tonico Gastrinatural HC',1,0,375,375,'2025-02-10','admin',38),(65,'Activa',1,0,630,630,'2025-02-10','admin',38),(66,'Biotisil',1,0,350,350,'2025-02-10','admin',38),(67,'Tonico Gastrinatural HC',1,0,375,375,'2025-02-10','admin',39),(68,'Activa',1,0,630,630,'2025-02-10','admin',39),(69,'Biotisil',1,0,350,350,'2025-02-10','admin',39),(70,'Tonico Gastrinatural HC',1,0,375,375,'2025-02-10','admin',40),(71,'Activa',1,0,630,630,'2025-02-10','admin',40),(72,'Biotisil',1,0,350,350,'2025-02-10','admin',40),(73,'Tonico Gastrinatural HC',1,0,375,375,'2025-02-10','admin',41),(74,'Activa',1,0,630,630,'2025-02-10','admin',41),(75,'Biotisil',1,0,350,350,'2025-02-10','admin',41),(76,'Tonico Cirnatural HC',1,0,375,375,'2025-02-10','admin',42),(77,'Tonico Cirnatural HC',1,0,375,375,'2025-02-10','admin',43),(78,'Tonico Cirnatural HC',1,0,375,375,'2025-02-10','admin',44),(79,'Tonico Gastrinatural HC',2,0,750,750,'2025-02-10','admin',45),(80,'Tonico Cirnatural HC',2,0,750,750,'2025-02-10','admin',45),(81,'Tonico Prostatis HC',1,0,375,375,'2025-02-10','admin',45),(82,'Tónico CLR',1,0,375,375,'2025-02-10','admin',45),(83,'Tonico Cirnatural HC',5,0,1875,1875,'2025-02-10','admin',46),(84,'Tónico CLR',19,0,7125,7125,'2025-04-15','admin',47);
/*!40000 ALTER TABLE `cierre` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-03  0:20:19
