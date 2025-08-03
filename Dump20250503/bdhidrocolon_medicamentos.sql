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
-- Table structure for table `medicamentos`
--

DROP TABLE IF EXISTS `medicamentos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medicamentos` (
  `id` int NOT NULL,
  `nombre` varchar(45) DEFAULT NULL,
  `presentacion` varchar(45) DEFAULT NULL,
  `laboratorio` varchar(45) DEFAULT NULL,
  `existencias` int DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `tarjeta` float DEFAULT NULL,
  `efectivo` float DEFAULT NULL,
  `indicacion` varchar(200) DEFAULT NULL,
  `contra` varchar(200) DEFAULT NULL,
  `dosis` varchar(400) DEFAULT NULL,
  `comision` int DEFAULT NULL,
  `foto` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medicamentos`
--

LOCK TABLES `medicamentos` WRITE;
/*!40000 ALTER TABLE `medicamentos` DISABLE KEYS */;
INSERT INTO `medicamentos` VALUES (6,'Tonico Cirnatural HC','Frasco 250 ml','Hidrocolon',20,'2025-10-08',400,375,'nada','nada','nada',12,'C:\\Users\\VICTUS\\PycharmProjects\\Sistema-Hidrocolon\\logo.png'),(8,'Tónico CLR','Frasco 250 ml','Hidrocolon',80,'2025-10-08',400,375,NULL,NULL,NULL,12,NULL),(10,'Tonico Femnatural HC','Frasco 500 ml','Hidrocolon',98,'2025-10-08',550,500,NULL,NULL,NULL,NULL,NULL),(11,'Tonico Gastrinatural HC','Frasco 250 ml','Hidrocolon',89,'2025-10-08',400,375,NULL,NULL,NULL,NULL,NULL),(12,'Tonico Gastrinatural HC','Frasco 500 ml','Hidrocolon',99,'2025-10-08',550,500,NULL,NULL,NULL,NULL,NULL),(13,'Tonico Hormonal HC','Frasco 250 ml','Hidrocolon',107,'2025-10-08',400,375,NULL,NULL,NULL,NULL,NULL),(14,'Tonico Hormonal HC','Frasco 500 ml','Hidrocolon',80,'2025-10-08',550,500,NULL,NULL,NULL,NULL,NULL),(15,'Tonico Prostatis HC','Frasco 250 ml','Hidrocolon',140,'2025-10-08',400,375,NULL,NULL,NULL,NULL,NULL),(16,'Tonico Prostatis HC','Frasco 500 ml','Hidrocolon',50,'2025-10-08',550,500,NULL,NULL,NULL,NULL,NULL),(17,'Tonico Riñonatural HC','Frasco 250 ml','Hidrocolon',80,'2025-10-08',400,375,NULL,NULL,NULL,NULL,NULL),(18,'Tonico Riñonatural HC','Frasco 500 ml','Hidrocolon',70,'2025-10-08',550,500,NULL,NULL,NULL,NULL,NULL),(19,'Activa','Frasco','Farmex',100,'2025-10-08',675,630,NULL,NULL,NULL,NULL,NULL),(20,'Biotisil','Frasco','Praxis',97,'2025-10-08',400,350,NULL,NULL,NULL,NULL,NULL),(21,'Kit Detox (Regla de los 7)','Caja','Reckeweg',100,'2025-10-08',550,500,NULL,NULL,NULL,NULL,NULL),(22,'Propoleo + Equinacea','Frasco','Dipronat',100,'2025-10-08',350,300,NULL,NULL,NULL,NULL,NULL),(23,'Solución de Caléndula','Caja','Reckeweg',100,'2025-10-08',350,300,NULL,NULL,NULL,NULL,NULL),(24,'Tegoner','Frasco','Reckeweg',100,'2025-10-08',250,225,NULL,NULL,NULL,NULL,NULL),(25,'Trixi (Cefriaxona)','Frasco','Farmex',100,'2025-10-08',125,100,NULL,NULL,NULL,NULL,NULL),(26,'Tónico de Alfalfa','Frasco','Reckeweg',100,'2025-10-08',350,300,NULL,NULL,NULL,NULL,NULL),(27,'Vita C-15','Frasco','Reckeweg',99,'2025-10-08',400,350,NULL,NULL,NULL,NULL,NULL),(28,'Acido Glutamico','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(29,'Aromaterapia','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(30,'Calcio+D','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(31,'Century','Frasco','Hidrocolon',99,'2025-10-08',300,250,NULL,NULL,NULL,NULL,NULL),(32,'Cleanse','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(33,'Colageno','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(34,'Complejo B','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(35,'Crema Reuma','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(36,'Desestres','Frasco','Hidrocolon',99,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(37,'Diabetes','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(38,'Equinacea','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(39,'Extracto Ajo con perejil','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(40,'Extrato de Sabila','Frasco','Hidrocolon',100,'2025-10-08',250,225,NULL,NULL,NULL,NULL,NULL),(41,'Florales','Frasco','Hidrocolon',99,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(42,'Gastritis','Frasco','Hidrocolon',100,'2025-10-08',250,225,NULL,NULL,NULL,NULL,NULL),(43,'Glucosamina','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(44,'Isoflavonas','Frasco','Hidrocolon',100,'2025-10-08',250,200,NULL,NULL,NULL,NULL,NULL),(45,'Jalea Real','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(46,'Lecitina de Soya','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(47,'Levadura de cerveza','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(48,'Moringa','Frasco','Hidrocolon',99,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(49,'Omega 3','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(50,'Oxigenadores','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(51,'Quema grasa','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(52,'Refresal','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(53,'Tintura de ajo ruda','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(54,'Tintura de propoleo','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(55,'Tintura de valeriana con hierba de San Juan','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(56,'Uva ursi','Frasco','Hidrocolon',100,'2025-10-08',250,200,NULL,NULL,NULL,NULL,NULL),(57,'Vitamina C','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(59,'Warana+polen','Frasco','Hidrocolon',100,'2025-10-08',200,175,NULL,NULL,NULL,NULL,NULL),(60,'Energiter','Capsulas','Reckeweg',25,'2025-12-12',200,175,NULL,NULL,NULL,NULL,NULL),(61,'test medician','test','Dipronat',100,'2024-01-01',100,100,'Ninguno','hola a todos esta es un pruebaz','3 capsulas cada 3 horas',NULL,'C:/Users/VICTUS/OneDrive/Escritorio/fe 2.png');
/*!40000 ALTER TABLE `medicamentos` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-03  0:20:18
