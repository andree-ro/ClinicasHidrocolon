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
-- Table structure for table `carrito`
--

DROP TABLE IF EXISTS `carrito`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `carrito` (
  `id` int NOT NULL,
  `nombre` varchar(45) DEFAULT NULL,
  `existencias` int DEFAULT NULL,
  `tarjeta` float DEFAULT NULL,
  `efectivo` float DEFAULT NULL,
  `medicamentos_id` int NOT NULL,
  `terapias_id` int NOT NULL,
  `promociones_id` int NOT NULL,
  `jordas_id` int NOT NULL,
  `ultrasonidos_id` int NOT NULL,
  `consumibles_id` int NOT NULL,
  PRIMARY KEY (`id`,`medicamentos_id`,`terapias_id`,`promociones_id`,`jordas_id`,`ultrasonidos_id`,`consumibles_id`),
  KEY `fk_carrito_medicamentos1_idx` (`medicamentos_id`),
  KEY `fk_carrito_terapias1_idx` (`terapias_id`),
  KEY `fk_carrito_promociones1_idx` (`promociones_id`),
  KEY `fk_carrito_jordas1_idx` (`jordas_id`),
  KEY `fk_carrito_ultrasonidos1_idx` (`ultrasonidos_id`),
  KEY `fk_carrito_consumibles1_idx` (`consumibles_id`),
  CONSTRAINT `fk_carrito_jordas1` FOREIGN KEY (`jordas_id`) REFERENCES `jornadas` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `carrito`
--

LOCK TABLES `carrito` WRITE;
/*!40000 ALTER TABLE `carrito` DISABLE KEYS */;
INSERT INTO `carrito` VALUES (1,'Tónico CLR',19,7600,7125,8,-1,-1,-1,-1,-1);
/*!40000 ALTER TABLE `carrito` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-03  0:20:17
