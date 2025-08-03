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
-- Table structure for table `registro_caja`
--

DROP TABLE IF EXISTS `registro_caja`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `registro_caja` (
  `id` int NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(50) DEFAULT NULL,
  `monto` decimal(10,2) DEFAULT NULL,
  `cantidad` int DEFAULT NULL,
  `total` decimal(10,2) DEFAULT NULL,
  `fecha` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registro_caja`
--

LOCK TABLES `registro_caja` WRITE;
/*!40000 ALTER TABLE `registro_caja` DISABLE KEYS */;
INSERT INTO `registro_caja` VALUES (1,'Billetes de',200.00,5,1000.00,'2025-04-08 20:24:47'),(2,'Billetes de',100.00,6,600.00,'2025-04-08 20:24:47'),(3,'Billetes de',50.00,1,50.00,'2025-04-08 20:24:47'),(4,'Billetes de',20.00,56,1120.00,'2025-04-08 20:24:47'),(5,'Billetes de',10.00,16,160.00,'2025-04-08 20:24:47'),(6,'Billetes de',5.00,72,360.00,'2025-04-08 20:24:47'),(7,'Monedas',1.00,61,61.00,'2025-04-08 20:24:47'),(8,'Monedas',0.50,16,8.00,'2025-04-08 20:24:47'),(9,'Monedas',0.25,615,153.75,'2025-04-08 20:24:47'),(10,'Monedas',0.10,65,6.50,'2025-04-08 20:24:47'),(11,'Monedas',0.05,56,2.80,'2025-04-08 20:24:47');
/*!40000 ALTER TABLE `registro_caja` ENABLE KEYS */;
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
