/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.11.13-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: matrix_oee_db
-- ------------------------------------------------------
-- Server version	10.11.13-MariaDB-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `clients`
--

DROP TABLE IF EXISTS `clients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `clients` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clients`
--

LOCK TABLES `clients` WRITE;
/*!40000 ALTER TABLE `clients` DISABLE KEYS */;
INSERT INTO `clients` VALUES
(2,'grammar ','2645580342');
/*!40000 ALTER TABLE `clients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `downtime_events`
--

DROP TABLE IF EXISTS `downtime_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `downtime_events` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `work_order_id` int(11) NOT NULL,
  `reason` varchar(255) NOT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime DEFAULT NULL,
  `duration_seconds` int(11) DEFAULT NULL,
  `comment` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `work_order_id` (`work_order_id`),
  CONSTRAINT `downtime_events_ibfk_1` FOREIGN KEY (`work_order_id`) REFERENCES `work_orders` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `downtime_events`
--

LOCK TABLES `downtime_events` WRITE;
/*!40000 ALTER TABLE `downtime_events` DISABLE KEYS */;
INSERT INTO `downtime_events` VALUES
(24,29,'Otro','2026-01-28 12:46:47','2026-01-28 12:46:58',11,NULL),
(25,30,'Otro','2026-01-28 12:54:41','2026-01-28 13:00:35',354,NULL),
(26,30,'Falta de Insumos','2026-01-28 12:59:10',NULL,0,NULL),
(27,31,'Descanso / Almuerzo','2026-01-28 13:23:40','2026-01-28 13:23:47',7,NULL),
(28,33,'Cambio de Paso','2026-01-28 13:42:16','2026-01-28 13:42:25',9,NULL),
(29,34,'Limpieza','2026-01-28 14:46:09','2026-01-28 14:47:01',52,NULL),
(30,35,'Falla de Máquina','2026-01-29 09:14:40','2026-01-29 09:16:18',98,NULL),
(31,43,'test','2026-01-29 09:57:38','2026-01-29 09:57:40',2,NULL),
(32,41,'Falla de Máquina','2026-01-29 09:58:41','2026-01-29 09:59:45',64,NULL),
(33,44,'Otro','2026-01-29 10:50:54','2026-01-29 10:52:06',72,'Corte de luz'),
(34,42,'Otro','2026-01-29 11:10:03','2026-01-29 11:10:17',14,'Corte de luz');
/*!40000 ALTER TABLE `downtime_events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lines`
--

DROP TABLE IF EXISTS `lines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `lines` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lines`
--

LOCK TABLES `lines` WRITE;
/*!40000 ALTER TABLE `lines` DISABLE KEYS */;
INSERT INTO `lines` VALUES
(1,'Linea 1 - Embotellado'),
(2,'Linea 2 - Sodas');
/*!40000 ALTER TABLE `lines` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `line_id` int(11) NOT NULL,
  `theoretical_cycle_seconds` float NOT NULL,
  PRIMARY KEY (`id`),
  KEY `line_id` (`line_id`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`line_id`) REFERENCES `lines` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES
(1,'Bidon 20L',1,45),
(2,'Bidon 10L',1,35),
(3,'Soda 500ml',2,10);
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `work_orders`
--

DROP TABLE IF EXISTS `work_orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `work_orders` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ot_number` varchar(50) NOT NULL,
  `client_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `status` enum('PENDING','PREPARATION','EXECUTION','FINISHED') NOT NULL,
  `operator_count` int(11) DEFAULT NULL,
  `planned_quantity` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `estimated_finish` datetime DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `total_produced` int(11) DEFAULT NULL,
  `total_defective` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ot_number` (`ot_number`),
  KEY `client_id` (`client_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `work_orders_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`),
  CONSTRAINT `work_orders_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `work_orders`
--

LOCK TABLES `work_orders` WRITE;
/*!40000 ALTER TABLE `work_orders` DISABLE KEYS */;
INSERT INTO `work_orders` VALUES
(29,'OT-2026-0001',2,2,'FINISHED',1,10,'2026-01-28 12:46:36','2026-01-28 12:51:00','2026-01-28 12:46:39','2026-01-28 12:46:58',10,0),
(30,'OT-2026-0002',2,3,'FINISHED',1,5,'2026-01-28 12:54:25','2026-01-28 12:54:00','2026-01-28 12:54:33','2026-01-28 13:00:35',5,0),
(31,'OT-2026-0003',2,2,'FINISHED',1,10,'2026-01-28 13:18:26','2026-01-28 13:24:00','2026-01-28 13:23:34','2026-01-28 13:23:47',12,0),
(32,'OT-2026-0004',2,3,'FINISHED',1,10,'2026-01-28 13:24:06','2026-01-28 18:24:00','2026-01-28 13:38:48','2026-01-28 13:38:58',10,0),
(33,'OT-2026-0005',2,2,'FINISHED',1,100,'2026-01-28 13:39:12','2026-01-28 16:39:00','2026-01-28 13:42:31','2026-01-28 14:01:51',100,0),
(34,'OT-2026-0006',2,2,'FINISHED',1,10,'2026-01-28 14:45:56','2026-01-28 17:45:00','2026-01-28 14:46:02','2026-01-28 14:47:01',10,0),
(35,'OT-2026-0007',2,1,'FINISHED',1,10,'2026-01-29 09:13:51','2026-01-29 02:13:00','2026-01-29 09:14:21','2026-01-29 09:16:18',10,0),
(41,'OT-2026-0008',2,2,'FINISHED',NULL,5,'2026-01-29 09:52:24','2026-01-29 15:58:00','2026-01-29 09:57:38','2026-01-29 09:59:45',5,0),
(42,'OT-2026-0009',2,1,'FINISHED',NULL,100,'2026-01-29 09:52:38',NULL,'2026-01-29 11:08:31','2026-01-29 11:10:17',100,0),
(43,'OT-2026-0010',2,1,'EXECUTION',NULL,100,'2026-01-29 09:57:36',NULL,'2026-01-29 09:57:36',NULL,0,0),
(44,'OT-2026-0011',2,3,'FINISHED',NULL,5,'2026-01-29 10:49:28','2026-01-29 16:55:00','2026-01-29 10:49:34','2026-01-29 10:52:20',5,0);
/*!40000 ALTER TABLE `work_orders` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-29 13:30:11
