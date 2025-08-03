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
-- Table structure for table `terapias`
--

DROP TABLE IF EXISTS `terapias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `terapias` (
  `id` int NOT NULL,
  `nombre` varchar(45) DEFAULT NULL,
  `tarjeta` float DEFAULT NULL,
  `efectivo` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `terapias`
--

LOCK TABLES `terapias` WRITE;
/*!40000 ALTER TABLE `terapias` DISABLE KEYS */;
INSERT INTO `terapias` VALUES (-1,'-',0,0),(2,'Consulta',8,90),(3,'Biopuntura Reckewerg',350,325),(4,'Hemoterapia Reckewerg',350,325),(5,'Desintoxicacion',250,225),(6,'Hidrocolon',525,490),(7,'Lavativa + irrigador',525,490),(8,'Suero catalizadores 10',2200,2000),(9,'Suero + 5 catalizadores',1500,1000),(10,'Suero 6 Ampollas',2000,1800),(11,'Suero 4/7 (4 ampollas)',1700,1600),(12,'Suero 4/7 (Promoción)',550,500),(13,'SUERO + 1 ampolla Reckeweg o Hell',600,500),(14,'Suero+Barmicil',600,500),(15,'Suero+Cefriaxona (Trixi o furosemida)',550,500),(16,'Suero+Complejo B',500,450),(17,'Suero Hartman',200,150),(18,'Suero Vitaminado',225,200),(19,'Nebulizaciòn+ ampolla',250,175),(20,'Inyección',25,25),(21,'Glucometría',20,15),(22,'Masaje Quiropráctico',300,250),(23,'Masaje Quiro-relajante',350,300),(24,'Masaje relajante',250,200),(25,'Masaje Linfatico',250,200),(26,'Masaje del nervio ciático',250,200),(27,'Masaje relajante con ventosas',375,350),(28,'Masaje facial con ventosas',375,350),(29,'Lápiz de acupuntura',225,200),(30,'Levantamiento de gluteos',375,350),(31,'Masaje con tens',225,200),(32,'Rejuvenecimiento facial (3 ampollas)',975,900);
/*!40000 ALTER TABLE `terapias` ENABLE KEYS */;
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
