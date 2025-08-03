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
-- Table structure for table `ventas`
--

DROP TABLE IF EXISTS `ventas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ventas` (
  `id` int NOT NULL,
  `producto` varchar(120) DEFAULT NULL,
  `cantidad` int DEFAULT NULL,
  `total` int DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `accion` varchar(45) DEFAULT NULL,
  `doctor` varchar(45) DEFAULT NULL,
  `usuario` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas`
--

LOCK TABLES `ventas` WRITE;
/*!40000 ALTER TABLE `ventas` DISABLE KEYS */;
INSERT INTO `ventas` VALUES (1,'Consulta',1,100,'2025-01-08','Venta','Elisa',NULL),(2,'Consulta',1,100,'2025-01-08','Anulacion',NULL,'admin'),(3,'Consulta',1,100,'2025-01-08','Anulacion',NULL,'admin'),(4,'Tónico CLR',2,800,'2025-01-08','Venta','Elisa','admin'),(5,'Tonico Hormonal HC',1,400,'2025-01-08','Venta',NULL,'admin'),(6,'Fibra HC 500 gr',90,36000,'2025-01-08','Venta','Elisa','admin'),(7,'Suero + 5 catalizadores',1,1000,'2025-01-08','Venta',NULL,'admin'),(8,'Tonico Gastrinatural HC',5,0,'2025-01-08','Venta',NULL,'admin'),(9,'Suero + 5 catalizadores',1,1000,'2025-01-08','Anulacion',NULL,'admin'),(10,'Tonico Gastrinatural HC',5,0,'2025-01-08','Anulacion',NULL,'admin'),(11,'Tonico Cirnatural HC',1,375,'2025-01-09','Venta',NULL,'admin'),(12,'Tonico Gastrinatural HC',1,400,'2025-01-09','Venta',NULL,'admin'),(13,'Tonico Hormonal HC',2,750,'2025-01-10','Venta',NULL,'admin'),(14,'Fibra HC 500 gr',90,33750,'2025-01-10','Venta',NULL,'admin'),(15,'Masaje con tens',1,200,'2025-01-10','Venta',NULL,'admin'),(16,'Suero Hartman',1,150,'2025-01-10','Venta',NULL,'admin'),(17,'Moringa',1,0,'2025-01-10','Venta',NULL,'admin'),(18,'Tónico CLR',1,0,'2025-01-10','Venta',NULL,'admin'),(19,'Hidrocolon promo 3',1,1100,'2025-01-10','Venta',NULL,'admin'),(20,'Tonico Gastrinatural HC',1,375,'2025-01-10','Venta',NULL,'admin'),(21,'Consulta',1,150,'2025-01-10','Venta',NULL,'admin'),(22,'Consulta',1,150,'2025-01-10','Venta',NULL,'admin'),(23,'Activa',2,1350,'2025-01-10','Venta',NULL,'admin'),(24,'Consulta',1,0,'2025-01-10','Anulacion',NULL,'admin'),(25,'Activa',2,0,'2025-01-10','Anulacion',NULL,'admin'),(26,'Consulta',1,0,'2025-01-10','Anulacion',NULL,'admin'),(27,'Activa',2,0,'2025-01-10','Anulacion',NULL,'admin'),(28,'Consulta',1,100,'2025-02-03','Venta',NULL,'admin'),(29,'Consulta',1,100,'2025-02-03','Venta',NULL,'admin'),(30,'Tonico Gastrinatural HC',1,375,'2025-02-10','Venta',NULL,'admin'),(31,'Activa',1,630,'2025-02-10','Venta',NULL,'admin'),(32,'Biotisil',1,350,'2025-02-10','Venta',NULL,'admin'),(33,'Tonico Cirnatural HC',1,375,'2025-02-10','Venta',NULL,'admin'),(34,'Tonico Cirnatural HC',1,375,'2025-02-10','Venta',NULL,'admin'),(35,'Tonico Cirnatural HC',1,375,'2025-02-10','Venta',NULL,'admin'),(36,'Tonico Gastrinatural HC',2,750,'2025-02-10','Venta',NULL,'admin'),(37,'Tonico Cirnatural HC',2,750,'2025-02-10','Venta',NULL,'admin'),(38,'Tonico Prostatis HC',1,375,'2025-02-10','Venta',NULL,'admin'),(39,'Tónico CLR',1,375,'2025-02-10','Venta',NULL,'admin'),(40,'Tonico Cirnatural HC',5,1875,'2025-02-10','Venta',NULL,'admin');
/*!40000 ALTER TABLE `ventas` ENABLE KEYS */;
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
