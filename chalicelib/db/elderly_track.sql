-- phpMyAdmin SQL Dump
-- version 4.7.7
-- https://www.phpmyadmin.net/
--
-- Host: iot-centre-rds.crqhd2o1amcg.ap-southeast-1.rds.amazonaws.com
-- Generation Time: Jun 23, 2018 at 06:49 PM
-- Server version: 5.7.19-log
-- PHP Version: 7.2.3

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `elderly_track`
--

-- --------------------------------------------------------

--
-- Table structure for table `beacon`
--

CREATE TABLE `beacon` (
  `id` int(10) UNSIGNED NOT NULL,
  `uuid` varchar(40) NOT NULL,
  `major` int(10) UNSIGNED NOT NULL,
  `minor` int(10) UNSIGNED NOT NULL,
  `label` varchar(20) DEFAULT NULL,
  `status` smallint(2) UNSIGNED DEFAULT '1' COMMENT '1=active, 0=inactive, 2=temporarily disabled',
  `resident_id` int(10) UNSIGNED DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `beacon`
--

INSERT INTO `beacon` (`id`, `uuid`, `major`, `minor`, `label`, `status`, `resident_id`, `created_at`, `updated_at`) VALUES
(4, '4F4C9C21-03F3-457A-8A7F-5E0D09401654', 16502, 55820, NULL, 1, 1, '2018-02-27 05:49:54', '2018-06-23 14:26:43'),
(5, '4F4C9C21-03F3-457A-8A7F-5E0D09401654', 27949, 47408, NULL, 1, 1, '2018-02-27 05:47:55', '2018-04-24 16:00:17'),
(7, '4F4C9C21-03F3-457A-8A7F-5E0D09401654', 58949, 29933, NULL, 1, 6, '2017-11-07 07:36:34', '2018-04-08 09:14:55'),
(8, '4F4C9C21-03F3-457A-8A7F-5E0D09401654', 33078, 31465, NULL, 1, 7, '2018-01-03 12:56:33', '2018-04-08 09:14:55'),
(12, '4F4C9C21-03F3-457A-8A7F-5E0D09401654', 3810, 48523, NULL, 1, 8, '2017-11-07 07:36:38', '2018-04-08 09:14:55'),
(15, '4F4C9C21-03F3-457A-8A7F-5E0D09401654', 16717, 179, NULL, 1, 9, '2017-11-07 07:36:42', '2018-04-08 09:14:55'),
(16, '4F4C9C21-03F3-457A-8A7F-5E0D09401654', 43561, 43874, NULL, 1, 8, '2017-11-07 07:36:45', '2018-04-08 09:14:55'),
(19, '4F4C9C21-03F3-457A-8A7F-5E0D09401654', 24890, 6699, NULL, 1, 12, '2017-11-07 07:36:47', '2018-04-09 03:52:17');

-- --------------------------------------------------------

--
-- Table structure for table `caregiver`
--

CREATE TABLE `caregiver` (
  `id` int(10) UNSIGNED NOT NULL,
  `user_id` int(10) UNSIGNED NOT NULL,
  `resident_id` int(10) UNSIGNED NOT NULL,
  `relation` varchar(50) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `caregiver`
--

INSERT INTO `caregiver` (`id`, `user_id`, `resident_id`, `relation`, `created_at`, `updated_at`) VALUES
(1, 2, 1, 'cousin', '2017-01-22 03:30:16', '2018-06-19 08:12:19'),
(3, 1, 1, 'son', '2017-02-14 02:11:01', '2018-06-19 08:12:19'),
(4, 1, 4, 'mom', '2017-02-14 02:11:14', '2018-06-19 08:12:19'),
(5, 1, 6, 'brother', '2017-02-14 02:11:31', '2018-06-19 08:12:19'),
(6, 2, 7, 'daughter', '2017-06-08 03:51:32', '2018-06-19 08:14:18'),
(9, 2, 4, 'dad', '2017-02-17 02:09:12', '2018-06-19 08:15:03'),
(11, 2, 3, 'mom', '2017-02-23 06:38:02', '2018-06-19 08:12:51'),
(14, 1, 12, 'dad', '2017-03-22 02:59:26', '2018-06-19 08:12:19'),
(22, 1, 7, 'son', '2017-05-22 07:49:30', '2018-06-19 08:15:10'),
(23, 2, 8, 'uncle', '2017-05-22 07:49:30', '2018-06-19 08:15:15'),
(35, 1, 3, 'friend', '2017-06-05 08:38:11', '2018-06-19 08:12:49'),
(39, 1, 8, 'friend', '2017-06-05 08:38:39', '2018-06-19 08:14:11'),
(40, 1, 9, 'friend', '2017-06-05 08:38:45', '2018-06-19 08:14:03'),
(41, 2, 12, 'friend', '2017-06-05 08:38:51', '2018-06-19 08:14:00'),
(56, 2, 6, 'sister', '2018-04-21 01:58:16', '2018-06-19 08:15:08'),
(57, 2, 9, 'auntie', '2018-04-21 01:58:16', '2018-06-19 08:15:18');

-- --------------------------------------------------------

--
-- Table structure for table `gps`
--

CREATE TABLE `gps` (
  `id` int(10) UNSIGNED NOT NULL,
  `latitude` decimal(11,8) NOT NULL,
  `longitude` decimal(10,8) NOT NULL,
  `address` varchar(200) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `location`
--

CREATE TABLE `location` (
  `id` int(10) UNSIGNED NOT NULL,
  `beacon_id` int(10) UNSIGNED NOT NULL,
  `latitude` decimal(10,8) NOT NULL,
  `longitude` decimal(11,8) NOT NULL,
  `address` varchar(200) DEFAULT NULL,
  `resident_id` int(10) UNSIGNED DEFAULT NULL,
  `missing_id` int(10) UNSIGNED DEFAULT NULL,
  `locator_id` int(10) UNSIGNED DEFAULT NULL,
  `user_id` int(10) UNSIGNED DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `location`
--

INSERT INTO `location` (`id`, `beacon_id`, `latitude`, `longitude`, `address`, `resident_id`, `missing_id`, `locator_id`, `user_id`, `created_at`) VALUES
(1500, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-14 07:10:41'),
(1501, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 04:34:52'),
(1502, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 04:35:59'),
(1503, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 04:43:28'),
(1504, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 04:48:25'),
(1505, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 05:05:55'),
(1506, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 05:15:50'),
(1507, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 05:16:51'),
(1508, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 05:32:19'),
(1509, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 06:08:25'),
(1510, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 06:09:58'),
(1511, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 06:11:51'),
(1512, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 06:13:21'),
(1513, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 06:15:19'),
(1514, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 06:16:54'),
(1515, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 06:18:01'),
(1516, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 06:43:04'),
(1517, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 06:47:58'),
(1518, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 06:57:06'),
(1519, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 06:57:26'),
(1520, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 07:01:39'),
(1521, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 07:03:41'),
(1522, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 07:07:15'),
(1523, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 07:28:28'),
(1524, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 07:47:53'),
(1525, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 07:48:28'),
(1526, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-15 07:49:11'),
(1527, 4, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-15 07:49:48'),
(1528, 4, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 11, '2018-04-15 07:49:57'),
(1529, 7, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-15 07:50:48'),
(1530, 7, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-15 07:50:56'),
(1531, 7, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-15 07:51:50'),
(1532, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-15 07:52:06'),
(1533, 5, '1.34704560', '103.75410028', NULL, NULL, NULL, NULL, 321, '2018-04-15 08:34:47'),
(1534, 5, '1.34714174', '103.75405949', NULL, NULL, NULL, NULL, 321, '2018-04-15 08:43:45'),
(1535, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-15 08:44:17'),
(1536, 5, '1.34704674', '103.75409520', NULL, NULL, NULL, NULL, 321, '2018-04-15 09:06:02'),
(1537, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-15 11:47:11'),
(1538, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-16 02:27:25'),
(1539, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-16 02:27:48'),
(1540, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-16 02:27:53'),
(1541, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-16 02:34:15'),
(1542, 5, '1.34710596', '103.75403818', NULL, NULL, NULL, NULL, 321, '2018-04-16 04:49:36'),
(1543, 5, '1.34709609', '103.75397289', NULL, NULL, NULL, NULL, 321, '2018-04-16 05:11:38'),
(1544, 5, '1.34746245', '103.75528301', NULL, NULL, NULL, NULL, 321, '2018-04-16 05:23:17'),
(1545, 5, '1.34706736', '103.75404968', NULL, NULL, NULL, NULL, 321, '2018-04-16 06:25:56'),
(1546, 5, '1.34708692', '103.75404762', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:04:45'),
(1547, 5, '1.34708692', '103.75404762', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:04:47'),
(1548, 5, '1.34708692', '103.75404762', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:05:57'),
(1549, 5, '1.34708692', '103.75404762', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:06:03'),
(1550, 5, '1.34708692', '103.75404762', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:06:59'),
(1551, 5, '1.34708692', '103.75404762', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:07:00'),
(1552, 5, '1.34709191', '103.75400462', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:08:19'),
(1553, 5, '1.34709191', '103.75400462', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:08:27'),
(1554, 5, '1.34709191', '103.75400462', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:14:36'),
(1555, 5, '1.34709191', '103.75400462', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:14:42'),
(1556, 5, '1.34709191', '103.75400462', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:15:17'),
(1557, 5, '1.34709191', '103.75400462', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:15:21'),
(1558, 5, '1.34709191', '103.75400462', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:17:50'),
(1559, 5, '1.34706318', '103.75401753', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:17:56'),
(1560, 5, '1.34706318', '103.75401753', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:18:16'),
(1561, 5, '1.34706318', '103.75401753', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:18:20'),
(1562, 4, '1.34706318', '103.75401753', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:19:43'),
(1563, 4, '1.34706318', '103.75401753', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:19:44'),
(1564, 5, '1.34706318', '103.75401753', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:19:45'),
(1565, 4, '1.34706318', '103.75401753', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:20:53'),
(1566, 5, '1.34706318', '103.75401753', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:20:53'),
(1567, 4, '1.34706318', '103.75401753', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:21:06'),
(1568, 5, '1.34706318', '103.75401753', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:21:06'),
(1569, 4, '1.34706318', '103.75401753', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:21:06'),
(1570, 5, '1.34706318', '103.75401753', NULL, NULL, NULL, NULL, 321, '2018-04-16 10:21:10'),
(1579, 5, '1.34710238', '103.75401888', NULL, NULL, NULL, NULL, 321, '2018-04-16 12:53:56'),
(1580, 5, '1.34710238', '103.75401888', NULL, NULL, NULL, NULL, 321, '2018-04-16 12:54:03'),
(1581, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-16 12:54:38'),
(1582, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-16 12:58:30'),
(1583, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-16 12:59:00'),
(1584, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-16 12:59:56'),
(1585, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-16 13:00:03'),
(1586, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-16 13:02:54'),
(1587, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-16 13:03:37'),
(1588, 5, '1.34710418', '103.75399728', NULL, NULL, NULL, NULL, 321, '2018-04-16 13:05:45'),
(1589, 5, '1.34710418', '103.75399728', NULL, NULL, NULL, NULL, 321, '2018-04-16 13:05:53'),
(1590, 5, '1.34710425', '103.75396432', NULL, NULL, NULL, NULL, 321, '2018-04-16 13:12:00'),
(1591, 4, '1.34710425', '103.75396432', NULL, NULL, NULL, NULL, 321, '2018-04-16 13:15:29'),
(1592, 4, '1.34715674', '103.75393841', NULL, NULL, NULL, NULL, 321, '2018-04-16 13:33:45'),
(1593, 5, '1.34715674', '103.75393841', NULL, NULL, NULL, NULL, 321, '2018-04-16 13:33:59'),
(1594, 5, '1.34707573', '103.75405633', NULL, NULL, NULL, NULL, 321, '2018-04-16 13:52:26'),
(1595, 5, '1.34706075', '103.75400799', NULL, NULL, NULL, NULL, 321, '2018-04-17 02:13:03'),
(1596, 4, '1.34706075', '103.75400799', NULL, NULL, NULL, NULL, 321, '2018-04-17 02:16:03'),
(1597, 5, '1.34706075', '103.75400799', NULL, NULL, NULL, NULL, 321, '2018-04-17 02:18:21'),
(1598, 5, '1.34711028', '103.75406040', NULL, NULL, NULL, NULL, 321, '2018-04-17 02:29:54'),
(1599, 4, '1.34711028', '103.75406040', NULL, NULL, NULL, NULL, 321, '2018-04-17 02:30:20'),
(1600, 5, '1.34711028', '103.75406040', NULL, NULL, NULL, NULL, 321, '2018-04-17 02:35:20'),
(1601, 4, '1.34741853', '103.75510898', NULL, NULL, NULL, NULL, 321, '2018-04-17 02:35:33'),
(1602, 4, '1.34711958', '103.75412807', NULL, NULL, NULL, NULL, 321, '2018-04-17 02:39:11'),
(1603, 5, '1.34711958', '103.75412807', NULL, NULL, NULL, NULL, 321, '2018-04-17 02:39:11'),
(1604, 5, '1.34711958', '103.75412807', NULL, NULL, NULL, NULL, 321, '2018-04-17 02:43:15'),
(1605, 4, '1.34711958', '103.75412807', NULL, NULL, NULL, NULL, 321, '2018-04-17 02:43:30'),
(1606, 5, '1.34705877', '103.75405194', NULL, NULL, NULL, NULL, 321, '2018-04-17 03:07:34'),
(1607, 4, '1.34705877', '103.75405194', NULL, NULL, NULL, NULL, 321, '2018-04-17 03:07:42'),
(1609, 4, '1.34708848', '103.75399995', NULL, NULL, NULL, NULL, 321, '2018-04-17 03:16:07'),
(1610, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-17 03:26:57'),
(1611, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-17 03:27:39'),
(1612, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-17 03:27:45'),
(1613, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-17 03:27:46'),
(1614, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-17 03:27:46'),
(1615, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-17 03:27:46'),
(1616, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-17 03:27:46'),
(1617, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-17 03:27:46'),
(1618, 5, '1.34707195', '103.75403255', NULL, NULL, NULL, NULL, 321, '2018-04-18 02:03:20'),
(1619, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-04-20 13:15:58'),
(1620, 5, '1.34707228', '103.75402331', NULL, NULL, NULL, NULL, 321, '2018-04-23 03:50:56'),
(1621, 5, '1.34711817', '103.75399625', NULL, NULL, NULL, NULL, 321, '2018-04-23 03:51:01'),
(1622, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-05-01 02:59:16'),
(1623, 5, '1.34711119', '103.75401606', NULL, NULL, NULL, NULL, 321, '2018-05-19 14:06:10'),
(1624, 5, '1.34708709', '103.75408666', NULL, NULL, NULL, NULL, 321, '2018-05-19 14:13:03'),
(1625, 5, '1.34708709', '103.75408666', NULL, NULL, NULL, NULL, 321, '2018-05-19 14:16:15'),
(1626, 5, '1.34713410', '103.75403348', NULL, NULL, NULL, NULL, 321, '2018-05-19 14:30:08'),
(1627, 5, '1.34712633', '103.75403100', NULL, NULL, NULL, NULL, 321, '2018-05-19 14:38:36'),
(1628, 5, '1.34712633', '103.75403100', NULL, NULL, NULL, NULL, 321, '2018-05-19 14:39:06'),
(1629, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-05-19 14:53:36'),
(1630, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-05-19 14:56:21'),
(1631, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-05-20 05:27:17'),
(1632, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-05-20 05:27:41'),
(1633, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-05-20 05:35:32'),
(1634, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-05-20 05:38:14'),
(1635, 5, '1.00000000', '1.00000000', NULL, NULL, NULL, NULL, 321, '2018-05-20 07:24:22'),
(1636, 5, '1.00000000', '1.10000000', NULL, NULL, NULL, NULL, 321, '2018-05-20 07:31:56'),
(1637, 5, '1.00000000', '1.10000000', NULL, NULL, NULL, NULL, 321, '2018-05-20 14:33:00'),
(1638, 5, '1.34705809', '103.75405574', NULL, NULL, NULL, NULL, 321, '2018-05-20 14:56:58'),
(1639, 5, '1.34710655', '103.75400852', NULL, NULL, NULL, NULL, 321, '2018-05-20 14:59:13'),
(1640, 5, '1.33515952', '103.77656667', NULL, NULL, NULL, NULL, 321, '2018-05-24 05:29:20'),
(1641, 5, '1.33525034', '103.77659634', NULL, NULL, NULL, NULL, 321, '2018-05-24 05:30:29'),
(1642, 5, '1.33525034', '103.77659634', NULL, NULL, NULL, NULL, 321, '2018-05-24 05:31:14'),
(1643, 4, '2.00000000', '2.00000000', NULL, 1, 86, NULL, NULL, '2018-06-23 18:38:38');

-- --------------------------------------------------------

--
-- Table structure for table `locator`
--

CREATE TABLE `locator` (
  `id` int(10) UNSIGNED NOT NULL,
  `serial` varchar(50) NOT NULL,
  `label` varchar(100) NOT NULL,
  `remark` varchar(500) DEFAULT NULL,
  `latitude` decimal(10,8) DEFAULT NULL,
  `longitude` decimal(11,8) DEFAULT NULL,
  `address` varchar(200) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `locator`
--

INSERT INTO `locator` (`id`, `serial`, `label`, `remark`, `latitude`, `longitude`, `address`, `created_at`, `updated_at`) VALUES
(2, '0123456789  ', 'NP BLK 7', 'BLK 7, 535 Clementi Rd, 599489', '1.33465700', '103.77662500', NULL, '2017-05-22 09:27:33', NULL),
(3, '000000007dcfc91e', 'Bukit Panjang Neighbourhood Police Centre', '1 Segar Rd, Singapore 677738', '1.38679300', '103.77180400', NULL, '2017-05-22 09:27:33', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `missing`
--

CREATE TABLE `missing` (
  `id` int(10) UNSIGNED NOT NULL,
  `resident_id` int(10) UNSIGNED NOT NULL,
  `reported_by` int(10) UNSIGNED DEFAULT NULL,
  `reported_at` datetime NOT NULL DEFAULT '1000-01-01 00:00:00',
  `remark` varchar(500) DEFAULT NULL,
  `latitude` decimal(10,8) DEFAULT NULL,
  `longitude` decimal(11,8) DEFAULT NULL,
  `address` varchar(200) DEFAULT NULL,
  `closed_by` int(10) UNSIGNED DEFAULT NULL,
  `closed_at` datetime DEFAULT NULL,
  `closure` varchar(500) DEFAULT NULL,
  `status` int(2) UNSIGNED DEFAULT '1' COMMENT '1=active, 0=inactive',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `missing`
--

INSERT INTO `missing` (`id`, `resident_id`, `reported_by`, `reported_at`, `remark`, `latitude`, `longitude`, `address`, `closed_by`, `closed_at`, `closure`, `status`, `created_at`, `updated_at`) VALUES
(81, 6, 2, '2018-06-23 06:00:00', 'testing 6', NULL, NULL, NULL, NULL, NULL, NULL, 1, '2018-04-21 01:59:10', '2018-06-23 02:01:54'),
(82, 9, 1, '2018-06-23 09:00:00', 'testing 9', NULL, NULL, NULL, NULL, NULL, NULL, 1, '2018-04-21 01:59:14', '2018-06-23 02:01:54'),
(86, 1, 1, '2018-06-19 16:12:19', '', '2.00000000', '2.00000000', NULL, NULL, '2018-06-23 14:06:56', 'asd', 1, '2018-06-04 04:19:30', '2018-06-23 18:38:38'),
(87, 1, 321, '1000-01-01 00:00:00', 'asd', NULL, NULL, NULL, NULL, '2018-06-23 14:06:56', 'asd', 0, '2018-06-23 08:37:14', '2018-06-23 14:06:56'),
(89, 3, 321, '2018-06-23 10:37:03', 'asd', NULL, NULL, NULL, NULL, NULL, NULL, 1, '2018-06-23 10:37:03', '2018-06-23 10:37:03'),
(90, 7, 321, '2018-06-23 10:44:45', 'asd', NULL, NULL, NULL, 321, '2018-06-23 00:00:00', NULL, 0, '2018-06-23 10:44:45', '2018-06-23 11:22:46'),
(91, 7, 321, '2018-06-23 11:22:45', 'asd', NULL, NULL, NULL, 321, '2018-06-23 11:30:25', NULL, 0, '2018-06-23 11:22:46', '2018-06-23 11:30:25'),
(92, 7, 321, '2018-06-23 11:30:24', 'asd', NULL, NULL, NULL, 321, '2018-06-23 11:34:03', NULL, 0, '2018-06-23 11:30:25', '2018-06-23 11:34:03'),
(93, 7, 321, '2018-06-23 11:34:03', 'asd', NULL, NULL, NULL, 321, '2018-06-23 13:31:31', NULL, 0, '2018-06-23 11:34:03', '2018-06-23 13:31:31'),
(94, 7, 321, '2018-06-23 13:31:31', 'asd', NULL, NULL, NULL, NULL, '2018-06-23 13:49:37', NULL, 0, '2018-06-23 13:31:31', '2018-06-23 13:49:37');

-- --------------------------------------------------------

--
-- Table structure for table `resident`
--

CREATE TABLE `resident` (
  `id` int(10) UNSIGNED NOT NULL,
  `fullname` varchar(200) NOT NULL,
  `gender` smallint(5) UNSIGNED NOT NULL DEFAULT '1' COMMENT '1=male, 0=female',
  `dob` date NOT NULL,
  `nric` varchar(20) DEFAULT NULL,
  `image_path` varchar(200) DEFAULT NULL,
  `thumbnail_path` varchar(200) DEFAULT NULL,
  `hide_photo` tinyint(2) UNSIGNED DEFAULT '0' COMMENT '0 = no, 1 = yes',
  `status` tinyint(4) UNSIGNED DEFAULT '1' COMMENT '1=active, 0=inactive',
  `remark` varchar(500) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `resident`
--

INSERT INTO `resident` (`id`, `fullname`, `gender`, `dob`, `nric`, `image_path`, `thumbnail_path`, `hide_photo`, `status`, `remark`, `created_at`, `updated_at`) VALUES
(1, 'Allan Cheng', 1, '2016-12-07', 'SG0001', 'uploads/human_images/SG0001.png', 'uploads/human_images/thumbnail_SG0001.png', 1, 0, '', '2017-01-26 06:32:50', '2018-06-23 14:06:56'),
(3, 'Ma Kwei Yan', 1, '2016-12-07', 'SG1003', 'uploads/human_images/SG1003.png', 'uploads/human_images/thumbnail_SG0003.png', 1, 1, '', '2017-01-26 06:33:50', '2018-06-19 08:08:24'),
(4, 'Matthew Chung', 1, '2016-12-07', 'SG0005', 'uploads/human_images/SG1005.png', 'uploads/human_images/thumbnail_SG0005.png', 1, 1, '', '2017-01-25 10:00:49', '2018-06-19 08:08:26'),
(6, 'Alex Yew', 1, '2017-01-11', 'SG2111', 'uploads/human_images/SG1111.png', 'uploads/human_images/thumbnail_SG1111.png', 1, 1, '', '2017-01-17 07:01:16', '2018-06-19 08:08:28'),
(7, 'Yoo Qinjie', 1, '2017-01-11', 'SG1112', 'uploads/human_images/SG1112.png', 'uploads/human_images/thumbnail_SG1112.png', 0, 0, '', '2017-01-25 09:52:34', '2018-06-23 13:49:37'),
(8, 'Mike Soh', 1, '2017-01-11', 'S11653', 'uploads/human_images/S11653.png', 'uploads/human_images/thumbnail_S11653.png', 0, 1, '', '2017-01-25 06:55:36', '2018-06-19 08:08:32'),
(9, 'Martin', 1, '1980-01-04', 'SG0069', 'uploads/human_images/SG0069.png', 'uploads/human_images/thumbnail_SG0069.png', 1, 1, '', '2017-01-25 06:55:33', '2018-06-19 08:08:34'),
(12, 'Tan Soon Lee', 1, '2017-04-15', 'SG113', 'uploads/human_images/SG113.png', 'uploads/human_images/thumbnail_SG113.png', 1, 1, '', '2017-03-22 02:35:07', '2018-06-19 08:08:36');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(10) UNSIGNED NOT NULL,
  `username` varchar(50) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `endpointID` varchar(40) DEFAULT NULL,
  `pinpoint_status` tinyint(4) DEFAULT '1',
  `auth_key` varchar(32) DEFAULT '',
  `password_hash` varchar(255) DEFAULT '',
  `access_token` varchar(32) DEFAULT NULL,
  `password_reset_token` varchar(255) DEFAULT NULL,
  `email_confirm_token` varchar(255) DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `role` int(10) UNSIGNED DEFAULT '10' COMMENT '40: admin, 20: family, 10: volunteer, 5:anonymous, 2:rpi',
  `status` smallint(6) UNSIGNED DEFAULT '10',
  `allowance` int(10) UNSIGNED DEFAULT NULL,
  `timestamp` int(10) UNSIGNED DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `username`, `email`, `endpointID`, `pinpoint_status`, `auth_key`, `password_hash`, `access_token`, `password_reset_token`, `email_confirm_token`, `phone_number`, `role`, `status`, `allowance`, `timestamp`, `created_at`, `updated_at`) VALUES
(1, 'demo', 'demo.ece.np@gmail.com', NULL, 0, '', '', NULL, NULL, NULL, NULL, 20, 10, NULL, NULL, '2017-02-15 02:30:42', '2018-06-23 01:47:55'),
(2, 'qinjie.np', 'qinjie.np@gmail.com', NULL, 0, '', '', NULL, NULL, NULL, NULL, 20, 10, NULL, NULL, '2017-12-15 03:46:46', '2018-06-23 01:47:59'),
(11, 'longlp', 'long.phamlp94@gmail.com', NULL, 0, '6969', '6969', NULL, NULL, NULL, NULL, 20, 10, NULL, NULL, '2017-02-15 02:30:42', '2018-06-23 01:47:34'),
(68, 'root', 'eceiot.np@gmail.com', NULL, 0, 'aMZdn_AgoWYjmqX6PBTMHP_2K6QbxZIu', '$2y$13$N4V3s7eF9WsJjgeUoFX0YOFfoW0N9x3oKT/8UTX2aSnGaHpaWxxt2', NULL, NULL, NULL, NULL, 40, 10, NULL, NULL, '2017-02-15 02:30:42', '2018-04-16 09:04:26'),
(77, 'Xu', 'nhathuyenqt@gmail.com', NULL, 0, '', '', NULL, NULL, NULL, NULL, 20, 10, NULL, NULL, '2017-02-16 00:32:21', '2018-04-16 09:04:26'),
(126, 'police', 'abc@gmail.co', NULL, 0, '', '', NULL, NULL, NULL, NULL, 20, 10, NULL, NULL, '2017-03-21 07:29:13', '2018-04-16 09:04:26'),
(139, 'hoa', 'phuonghoatink22@gmail.com', NULL, 0, '', '', NULL, NULL, NULL, NULL, 20, 10, NULL, NULL, '2017-04-03 08:56:17', '2018-04-16 09:04:26'),
(152, 'lsc', 'metallic.dan@gmail.com', NULL, 0, '6969', '6969', NULL, NULL, NULL, NULL, 20, 10, NULL, NULL, '2017-02-15 02:30:42', '2018-04-16 09:04:26'),
(153, 'qinjie', 'mark.qj@gmail.com', NULL, 0, '6969', '6969', NULL, NULL, NULL, NULL, 20, 10, NULL, NULL, '2017-02-15 02:30:42', '2018-04-16 09:04:26'),
(163, 'anh', 'anhltse.fpt@gmail.com', NULL, 0, '', '', NULL, NULL, NULL, NULL, 20, 10, NULL, NULL, '2017-06-05 08:37:33', '2018-04-16 09:04:26'),
(317, 'Kiran ', 'kiranpittan4@gmail.com', NULL, 0, '', '', NULL, NULL, NULL, NULL, 20, 10, NULL, NULL, '2017-12-15 07:37:59', '2018-04-16 09:04:26'),
(319, 'keeve', 'keevemm@gmail.com', NULL, 0, '', '', NULL, NULL, NULL, NULL, 20, 10, NULL, NULL, '2017-12-15 07:38:28', '2018-04-16 09:04:26'),
(320, 'kyizartheint', 'kyizar777meimei@gmail.com', NULL, 0, '', '', NULL, NULL, NULL, NULL, 20, 10, NULL, NULL, '2017-12-15 07:39:28', '2018-04-16 09:04:26'),
(321, 'Kyaw Lin', 'didikyawlinn@gmail.com', '24AA24C1-A349-45A7-A5FD-BC9F742FFDF0', 1, '', '', NULL, NULL, NULL, NULL, 20, 10, NULL, NULL, '2017-12-15 07:39:57', '2018-06-04 04:51:29'),
(358, 'Nigel', 'nigel.fyp@gmail.com', NULL, 0, 'bUtQO1WqQv9oweOdaUU0Z176fKc8IK3m', '', NULL, NULL, NULL, '83383326', 20, 10, NULL, NULL, '2018-04-11 04:01:52', '2018-04-16 09:04:26'),
(361, 'abc', 'asd.gmail.com', NULL, 1, 'wXiy6m85jiPvYkzX4MRHN9E8CrQvo8Lt', '', NULL, NULL, NULL, 'asd', 20, 10, NULL, NULL, '2018-04-15 13:18:42', '2018-04-16 09:04:26'),
(380, 'test', 'NPTester.iot@gmail.com', NULL, 0, '', '', NULL, NULL, NULL, NULL, 20, 10, NULL, NULL, '2018-04-21 01:55:34', '2018-04-22 17:57:32'),
(381, 'anonymous', NULL, 'FFB1BC27-2BEB-45D3-AC0A-060CF893C2AE', 1, '', '', NULL, NULL, NULL, NULL, 5, 10, NULL, NULL, '2018-06-19 19:23:11', '2018-06-19 19:23:22');

-- --------------------------------------------------------

--
-- Table structure for table `user_profile`
--

CREATE TABLE `user_profile` (
  `id` int(10) UNSIGNED NOT NULL,
  `fullname` varchar(200) NOT NULL,
  `nric` varchar(20) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `user_id` int(10) UNSIGNED DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `user_profile`
--

INSERT INTO `user_profile` (`id`, `fullname`, `nric`, `phone`, `email`, `user_id`, `created_at`, `updated_at`) VALUES
(1, 'Relative One', 'NRIC One', '12345678', 'one@gmail.com', 1, '2018-06-19 08:11:16', '2018-06-23 02:18:31'),
(2, 'Relative Two', 'NRIC Two', '23456789', 'two@gmail.com', 2, '2018-06-19 08:11:16', '2018-06-23 02:18:31');

-- --------------------------------------------------------

--
-- Table structure for table `user_token`
--

CREATE TABLE `user_token` (
  `id` int(10) UNSIGNED NOT NULL,
  `user_id` int(10) UNSIGNED NOT NULL,
  `token` varchar(32) NOT NULL DEFAULT '',
  `label` varchar(10) DEFAULT NULL,
  `mac_address` varchar(32) DEFAULT NULL,
  `expire` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `user_token`
--

INSERT INTO `user_token` (`id`, `user_id`, `token`, `label`, `mac_address`, `expire`, `created_at`) VALUES
(1335, 77, 'HINIrD3-KAmxbkg6qDbS2wWcbQ5Isno1', 'ACCESS', '153.20.93.83', '2017-06-01 02:31:16', '2017-04-27 02:48:42'),
(1490, 1, 'HfczLM_MklF7-8gQxrxjvTYje2UrNXq0', 'ACCESS', '153.20.95.84', '2017-07-09 02:19:07', '2017-06-09 02:12:35'),
(1713, 317, 'gURIoPpDZk5aRJ63sDlK5TXiPHGUKGL9', 'ACCESS', '153.20.95.84', '2018-01-27 09:00:56', '2017-12-15 07:41:58'),
(1722, 68, 'QFfkUNGVwuIzwYEhk9yzh8Wx9MJFlPc1', 'ACCESS', '175.156.146.3', '2018-01-15 07:00:15', '2017-12-16 06:59:59'),
(1729, 11, 'HzVMc25cQmNafx944nbq4w1iZw6KVdBh', 'ACCESS', '42.114.23.0', '2018-02-04 13:25:09', '2018-01-03 17:04:10'),
(1759, 153, 'Aew4-ZS7I2rkuZfGwVn-yL0UNoxFXFiG', 'ACCESS', '153.20.95.84', '2018-02-24 08:26:13', '2018-01-25 03:39:55'),
(1763, 152, 'G8UlQrHBnveXE3oBDJMlYTFrOfikaFcw', 'ACCESS', '183.90.36.201', '2018-04-06 06:09:27', '2018-01-31 09:41:25'),
(1801, 321, 'XX1vUjf1nlBs4KE4yreegYn497hqHgo3', 'ACCESS', '175.156.146.3', '2018-04-06 05:50:47', '2018-03-05 11:53:09');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `beacon`
--
ALTER TABLE `beacon`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uuid` (`uuid`,`major`,`minor`),
  ADD KEY `resident_id` (`resident_id`);

--
-- Indexes for table `caregiver`
--
ALTER TABLE `caregiver`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `relative_id` (`user_id`,`resident_id`),
  ADD KEY `resident_id` (`resident_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `gps`
--
ALTER TABLE `gps`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `latitude` (`latitude`,`longitude`);

--
-- Indexes for table `location`
--
ALTER TABLE `location`
  ADD PRIMARY KEY (`id`),
  ADD KEY `locator_id` (`locator_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `beacon_id` (`beacon_id`),
  ADD KEY `resident_id` (`resident_id`),
  ADD KEY `missing_id` (`missing_id`);

--
-- Indexes for table `locator`
--
ALTER TABLE `locator`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `serial_number` (`serial`);

--
-- Indexes for table `missing`
--
ALTER TABLE `missing`
  ADD PRIMARY KEY (`id`),
  ADD KEY `resident_id` (`resident_id`),
  ADD KEY `closed_by` (`closed_by`),
  ADD KEY `missing_ibfk_2` (`reported_by`);

--
-- Indexes for table `resident`
--
ALTER TABLE `resident`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `user_profile`
--
ALTER TABLE `user_profile`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- Indexes for table `user_token`
--
ALTER TABLE `user_token`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `token` (`token`),
  ADD KEY `userId` (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `beacon`
--
ALTER TABLE `beacon`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT for table `caregiver`
--
ALTER TABLE `caregiver`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=58;

--
-- AUTO_INCREMENT for table `gps`
--
ALTER TABLE `gps`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `location`
--
ALTER TABLE `location`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1644;

--
-- AUTO_INCREMENT for table `locator`
--
ALTER TABLE `locator`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `missing`
--
ALTER TABLE `missing`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=95;

--
-- AUTO_INCREMENT for table `resident`
--
ALTER TABLE `resident`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=413;

--
-- AUTO_INCREMENT for table `user_profile`
--
ALTER TABLE `user_profile`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `user_token`
--
ALTER TABLE `user_token`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1832;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `beacon`
--
ALTER TABLE `beacon`
  ADD CONSTRAINT `ct_beacon_resident` FOREIGN KEY (`resident_id`) REFERENCES `resident` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `caregiver`
--
ALTER TABLE `caregiver`
  ADD CONSTRAINT `caregiver_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `ct_ur_resident` FOREIGN KEY (`resident_id`) REFERENCES `resident` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `location`
--
ALTER TABLE `location`
  ADD CONSTRAINT `location_ibfk_1` FOREIGN KEY (`beacon_id`) REFERENCES `beacon` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `location_ibfk_2` FOREIGN KEY (`locator_id`) REFERENCES `locator` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `location_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `location_ibfk_4` FOREIGN KEY (`missing_id`) REFERENCES `missing` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `location_ibfk_5` FOREIGN KEY (`resident_id`) REFERENCES `resident` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `missing`
--
ALTER TABLE `missing`
  ADD CONSTRAINT `missing_ibfk_1` FOREIGN KEY (`resident_id`) REFERENCES `resident` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `missing_ibfk_2` FOREIGN KEY (`reported_by`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `missing_ibfk_3` FOREIGN KEY (`closed_by`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `user_profile`
--
ALTER TABLE `user_profile`
  ADD CONSTRAINT `user_profile_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Constraints for table `user_token`
--
ALTER TABLE `user_token`
  ADD CONSTRAINT `usertoken_userid` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
